# src/core/content_indexer.py - Motor de Indexación V.9.0 (PERSISTENCE RELOADED)
import os
import sqlite3
import threading
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

try:
    from pypdf import PdfReader
    import docx
    import openpyxl
except ImportError:
    PdfReader = None
    docx = None
    openpyxl = None

class ContentIndexer:
    def __init__(self, app=None):
        self.app = app
        app_data = os.environ.get('LOCALAPPDATA', os.environ.get('APPDATA', os.path.expanduser("~")))
        self.db_path = os.path.join(app_data, "BusquedaCarpetas", "content_index.db")
        self.db_lock = threading.Lock()
        self.stop_requested = False
        self._init_db()

    def _init_db(self):
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('PRAGMA journal_mode = WAL')
            cursor.execute('PRAGMA synchronous = NORMAL')
            cursor.execute('PRAGMA cache_size = -10000')
            cursor.execute('''CREATE TABLE IF NOT EXISTS file_metadata (
                path TEXT PRIMARY KEY, mtime REAL, indexed_at TIMESTAMP)''')
            cursor.execute('CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(path, content)')
            conn.commit()
            conn.close()

    def stop_indexing(self):
        self.stop_requested = True

    def _extract_text(self, file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            text = ""
            if ext == '.pdf' and PdfReader:
                reader = PdfReader(file_path)
                text = " ".join([p.extract_text() or "" for p in reader.pages[:10]])
            elif ext == '.docx' and docx:
                doc = docx.Document(file_path)
                text = " ".join([p.text for p in doc.paragraphs[:100] if p.text.strip()])
            elif ext == '.xlsx' and openpyxl:
                wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                texts = []
                for sheet in list(wb.worksheets)[:2]:
                    for row in sheet.iter_rows(max_row=500, values_only=True):
                        if self.stop_requested: break
                        texts.extend([str(c) for c in row if c is not None])
                text = " ".join(texts)
            elif ext in ['.txt', '.py', '.sql', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read(10000)
            return text.strip()
        except: return ""

    def search(self, query, search_field=None):
        """Busca texto/nombres y devuelve resultados en el formato esperado por la UI"""
        if not query: return []
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                search_query = f"{query}*"
                
                if search_field == "path":
                    # Búsqueda LITERAL en la columna de ruta/nombre (Evita problemas con guiones)
                    # Usamos LIKE en lugar de MATCH para que '2014-710' sea tratado como texto exacto
                    cursor.execute("""
                        SELECT path, content
                        FROM content_fts 
                        WHERE path LIKE ? 
                        ORDER BY path ASC
                        LIMIT 10000
                    """, (f"%{query}%",))
                else:
                    # Búsqueda por CONTENIDO (aquí sí usamos MATCH para velocidad de texto)
                    cursor.execute("""
                        SELECT path, snippet(content_fts, 1, '<b>', '</b>', '...', 64) 
                        FROM content_fts 
                        WHERE content_fts MATCH ? 
                        ORDER BY rank
                        LIMIT 10000
                    """, (f"content:{search_query}",))
                
                rows = cursor.fetchall()
                conn.close()
                
                results = []
                for path, snippet in rows:
                    is_folder = (snippet == "[FOLDER]")
                    norm_path = os.path.normpath(path)
                    results.append({
                        'name': os.path.basename(norm_path),
                        'path': norm_path,
                        'abs_path': norm_path,
                        'snippet': "" if is_folder else (snippet or ""),
                        'is_folder': is_folder
                    })
                return results
        except Exception as e:
            print(f"[SEARCH] Error: {e}")
            return []

    def get_index_stats(self):
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM file_metadata")
                total = cursor.fetchone()[0]
                conn.close()
                return {'total_files': total}
        except: return {'total_files': 0}

    def index_folder(self, folder_path, progress_callback=None, skip_content=False):
        self.stop_requested = False
        folder_name = os.path.basename(folder_path)
        try:
            files_to_index = []
            folders_to_index = []
            supported_exts = {'.pdf', '.docx', '.xlsx', '.txt', '.py', '.sql', '.csv'}
            
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT path, mtime FROM file_metadata WHERE path LIKE ?", (folder_path + '%',))
                existing_metadata = {row[0]: row[1] for row in cursor.fetchall()}
                conn.close()

            if progress_callback: progress_callback(f"Escaneando {folder_name}...", 0)

            for root, dirs, files in os.walk(folder_path):
                if self.stop_requested: break
                
                # RELECTAR CARPETAS
                for d in dirs:
                    if d.startswith('.') or d.startswith('~$'): continue
                    dir_path = os.path.join(root, d)
                    if dir_path not in existing_metadata:
                        folders_to_index.append(dir_path)
                
                # RECOLECTAR ARCHIVOS
                for f in files:
                    if f.startswith('~$') or f.startswith('.~'): continue
                    ext = os.path.splitext(f)[1].lower()
                    if ext in supported_exts:
                        full_path = os.path.normpath(os.path.join(root, f))
                        try:
                            mtime = os.path.getmtime(full_path)
                            if full_path not in existing_metadata or abs(existing_metadata[full_path] - mtime) > 0.1:
                                files_to_index.append((full_path, mtime))
                        except: continue

            total_files = len(files_to_index)
            total_folders = len(folders_to_index)
            
            if total_files == 0 and total_folders == 0:
                if progress_callback: progress_callback(f"{folder_name} al día", 100)
                return True

            # --- PASO 1: GUARDAR CARPETAS (Súper rápido) ---
            if folders_to_index:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('PRAGMA journal_mode = WAL')
                cursor.execute('PRAGMA synchronous = OFF')
                
                batch_meta = []
                batch_fts = []
                for i, p in enumerate(folders_to_index):
                    batch_meta.append((p, 0, datetime.now().isoformat()))
                    batch_fts.append((p, "[FOLDER]"))
                    if len(batch_meta) >= 500:
                        with self.db_lock:
                            cursor.executemany("INSERT OR REPLACE INTO file_metadata VALUES (?, 0, ?)", batch_meta)
                            cursor.executemany("INSERT INTO content_fts (path, content) VALUES (?, ?)", batch_fts)
                            conn.commit()
                        batch_meta, batch_fts = [], []
                        if progress_callback: progress_callback(f"Carpetas: {i}/{total_folders}", 0)
                
                if batch_meta:
                    with self.db_lock:
                        cursor.executemany("INSERT OR REPLACE INTO file_metadata VALUES (?, 0, ?)", batch_meta)
                        cursor.executemany("INSERT INTO content_fts (path, content) VALUES (?, ?)", batch_fts)
                        conn.commit()
                conn.close()

            # --- PASO 2: GUARDAR ARCHIVOS ---
            if total_files > 0:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('PRAGMA journal_mode = WAL')
                cursor.execute('PRAGMA synchronous = OFF')

                if skip_content:
                    batch_meta, batch_fts = [], []
                    for i, (path, mtime) in enumerate(files_to_index):
                        if self.stop_requested: break
                        batch_meta.append((path, mtime, datetime.now().isoformat()))
                        batch_fts.append((path, ""))
                        if len(batch_meta) >= 500:
                            with self.db_lock:
                                cursor.executemany("INSERT OR REPLACE INTO file_metadata VALUES (?, ?, ?)", batch_meta)
                                cursor.executemany("INSERT INTO content_fts (path, content) VALUES (?, ?)", batch_fts)
                                conn.commit()
                            batch_meta, batch_fts = [], []
                            if progress_callback: progress_callback(f"Archivos: {i}/{total_files}", (i/total_files)*100)
                    if batch_meta:
                        with self.db_lock:
                            cursor.executemany("INSERT OR REPLACE INTO file_metadata VALUES (?, ?, ?)", batch_meta)
                            cursor.executemany("INSERT INTO content_fts (path, content) VALUES (?, ?)", batch_fts)
                            conn.commit()
                else:
                    # Indexación con contenido (Hilos)
                    processed = 0
                    batch_meta, batch_fts = [], []
                    with ThreadPoolExecutor(max_workers=12) as executor:
                        futures = {executor.submit(self._extract_text, item[0]): item for item in files_to_index}
                        for future in as_completed(futures):
                            if self.stop_requested: break
                            path, mtime = futures[future]
                            content = future.result() or ""
                            processed += 1
                            batch_meta.append((path, mtime, datetime.now().isoformat()))
                            batch_fts.append((path, content))
                            if len(batch_meta) >= 250:
                                with self.db_lock:
                                    cursor.executemany("INSERT OR REPLACE INTO file_metadata VALUES (?, ?, ?)", batch_meta)
                                    cursor.executemany("INSERT INTO content_fts (path, content) VALUES (?, ?)", batch_fts)
                                    conn.commit()
                                batch_meta, batch_fts = [], []
                                if progress_callback: progress_callback(f"Contenido: {processed}/{total_files}", (processed/total_files)*100)
                    if batch_meta:
                        with self.db_lock:
                            cursor.executemany("INSERT OR REPLACE INTO file_metadata VALUES (?, ?, ?)", batch_meta)
                            cursor.executemany("INSERT INTO content_fts (path, content) VALUES (?, ?)", batch_fts)
                            conn.commit()
                conn.close()

            return not self.stop_requested
        except Exception as e:
            print(f"[CONTENT] Error: {e}")
            return False

    def clear_all_index(self):
        try:
            if os.path.exists(self.db_path):
                for suffix in ['', '-wal', '-shm']:
                    path = self.db_path + suffix
                    if os.path.exists(path):
                        try: os.remove(path)
                        except: pass
            self._init_db()
            return True
        except: return False

    def purge_location(self, folder_path):
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM file_metadata WHERE path LIKE ?", (folder_path + '%',))
                cursor.execute("DELETE FROM content_fts WHERE path LIKE ?", (folder_path + '%',))
                conn.commit()
                conn.close()
            return True
        except: return False
