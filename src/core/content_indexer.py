# src/core/content_indexer.py - Motor de Búsqueda de Contenido V.1.2
import os
import sqlite3
import threading
import unicodedata
import time
import concurrent.futures
from datetime import datetime

class ContentIndexer:
    """Maneja la indexación de contenido de archivos usando SQLite FTS5"""
    
    def __init__(self, app, db_name="content_index.db"):
        self.app = app
        app_data = os.environ.get('LOCALAPPDATA', os.environ.get('APPDATA', os.path.expanduser("~")))
        self.db_dir = os.path.join(app_data, "BusquedaCarpetas")
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir, exist_ok=True)
            
        self.db_path = os.path.join(self.db_dir, db_name)
        self.conn = None
        self.db_lock = threading.Lock()
        self.indexing_in_progress = False
        self.stop_requested = False
        self._init_db()

    def _init_db(self, retry=True):
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            
            try:
                cursor.execute("SELECT count(*) FROM sqlite_master")
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='content_fts'")
                if cursor.fetchone(): cursor.execute("SELECT count(*) FROM content_fts LIMIT 1")
            except sqlite3.DatabaseError as de:
                if "malformed" in str(de).lower() and retry:
                    self.conn.close()
                    if os.path.exists(self.db_path):
                        try:
                            os.remove(self.db_path)
                            for s in ["-wal", "-shm"]:
                                if os.path.exists(self.db_path+s): os.remove(self.db_path+s)
                        except: pass
                    return self._init_db(retry=False)
                raise de

            cursor.execute('''CREATE TABLE IF NOT EXISTS file_metadata (
                path TEXT PRIMARY KEY, mtime REAL, indexed_at TIMESTAMP)''')
            try:
                cursor.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
                    path UNINDEXED, content, tokenize="unicode61")''')
            except sqlite3.OperationalError as oe:
                if "malformed" in str(oe).lower() and retry:
                    self.conn.close()
                    if os.path.exists(self.db_path): os.remove(self.db_path)
                    return self._init_db(retry=False)
            self.conn.commit()
        except Exception as e:
            print(f"[CONTENT] Error inicializando DB: {e}")

    def normalize_text(self, text):
        if not text: return ""
        text = str(text)
        nfkd_form = unicodedata.normalize('NFD', text)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

    def _extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        try:
            if ext in ('.txt', '.log'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f: text = f.read()
            elif ext == '.pdf':
                from pypdf import PdfReader
                reader = PdfReader(file_path)
                text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
            elif ext == '.docx':
                import docx
                doc = docx.Document(file_path)
                text = " ".join([p.text for p in doc.paragraphs])
            elif ext == '.xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
                texts = []
                for sheet in wb:
                    for row in sheet.iter_rows(values_only=True):
                        texts.extend([str(c) for c in row if c is not None])
                text = " ".join(texts)
        except Exception as e:
            print(f"[CONTENT] Error extrayendo texto de {file_path}: {e}")
        return self.normalize_text(text)

    def index_folder(self, folder_path, progress_callback=None):
        self.stop_requested = False
        try:
            existing_metadata = {}
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute("SELECT path, mtime FROM file_metadata")
                existing_metadata = {row[0]: row[1] for row in cursor.fetchall()}

            files_to_index = []
            supported_exts = {'.pdf', '.docx', '.xlsx', '.txt', '.log'}
            folder_name = os.path.basename(folder_path)
            
            if progress_callback: progress_callback(f"Escaneando {folder_name}...", 0)

            for root, _, files in os.walk(folder_path):
                if self.stop_requested: break
                for f in files:
                    if f.startswith('~$') or f.startswith('.~'): continue
                    ext = os.path.splitext(f)[1].lower()
                    if ext in supported_exts:
                        full_path = os.path.join(root, f)
                        try:
                            mtime = os.path.getmtime(full_path)
                            cached_mtime = existing_metadata.get(full_path)
                            if cached_mtime is None or abs(cached_mtime - mtime) > 0.1:
                                files_to_index.append((full_path, mtime))
                        except: continue

            total = len(files_to_index)
            if total == 0:
                if progress_callback: progress_callback(f"{folder_name} al día", 100)
                return True

            import logging
            logging.getLogger("pypdf").setLevel(logging.ERROR)
            
            max_workers = 6
            processed_count = 0
            batch_size = 50
            pending_batch = []
            last_ui_update = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_path = {executor.submit(self._extract_text, p): (p, m) for p, m in files_to_index}
                
                for future in concurrent.futures.as_completed(future_to_path):
                    processed_count += 1
                    if self.stop_requested: break
                    path, mtime = future_to_path[future]
                    try:
                        content = future.result(timeout=30) # Más tiempo para archivos pesados
                        percent = (processed_count / total) * 100
                        if percent - last_ui_update >= 1 or processed_count == total:
                            if progress_callback: progress_callback(f"[{folder_name}] {processed_count}/{total}", percent)
                            last_ui_update = percent
                        
                        # Guardar siempre en lote, incluso si content es ""
                        pending_batch.append((path, content, mtime))
                            
                        if len(pending_batch) >= batch_size or processed_count >= total:
                            with self.db_lock:
                                cursor = self.conn.cursor()
                                for b_path, b_content, b_mtime in pending_batch:
                                    if b_content.strip():
                                        cursor.execute("INSERT OR REPLACE INTO content_fts (path, content) VALUES (?, ?)", (b_path, b_content))
                                    cursor.execute("INSERT OR REPLACE INTO file_metadata (path, mtime, indexed_at) VALUES (?, ?, ?)", 
                                                 (b_path, b_mtime, datetime.now().isoformat()))
                                self.conn.commit()
                            pending_batch = []
                            time.sleep(0.005)
                    except Exception as e:
                        print(f"[CONTENT] Ignorado {path}: {e}")

            return not self.stop_requested
        except Exception as e:
            print(f"[CONTENT] Error: {e}")
            return False

    def clear_all_index(self):
        """Borra absolutamente TODO el contenido del índice y optimiza el espacio"""
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM content_fts")
                cursor.execute("DELETE FROM file_metadata")
                self.conn.commit()
                # VACUUM debe ir fuera de una transacción
                self.conn.execute("VACUUM")
                print("[CONTENT] Índice borrado por completo y optimizado (VACUUM)")
            return True
        except Exception as e:
            print(f"[CONTENT] Error borrando índice completo: {e}")
            return False

    def purge_location(self, folder_path):
        """Elimina todos los archivos del índice que pertenezcan a esta carpeta"""
        try:
            # Asegurar que la ruta termine en separador para match exacto de subcarpetas
            prefix = os.path.abspath(folder_path)
            if not prefix.endswith(os.sep): prefix += os.sep
            
            with self.db_lock:
                cursor = self.conn.cursor()
                # 1. Borrar de metadata
                cursor.execute("DELETE FROM file_metadata WHERE path LIKE ? OR path = ?", (prefix + '%', folder_path))
                # 2. Borrar de FTS
                cursor.execute("DELETE FROM content_fts WHERE path LIKE ? OR path = ?", (prefix + '%', folder_path))
                self.conn.commit()
                print(f"[CONTENT] Índice purgado para: {folder_path}")
            return True
        except Exception as e:
            print(f"[CONTENT] Error purgando índice: {e}")
            return False

    def search(self, query):
        if not self.conn: return []
        is_exact = query.startswith('"') and query.endswith('"')
        normalized_query = self.normalize_text(query.strip('"'))
        if not normalized_query: return []
        
        fts_query = f'"{normalized_query}"' if is_exact else normalized_query
        try:
            with self.db_lock:
                cursor = self.conn.cursor()
                # USAR SNIPPET NATIVO PARA CONTEXTO PERFECTO
                cursor.execute("""
                    SELECT path, snippet(content_fts, 1, '[', ']', '...', 8) 
                    FROM content_fts 
                    WHERE content MATCH ? 
                    LIMIT 10000""", (fts_query,))
                rows = cursor.fetchall()
            
            results = []
            for row in rows:
                p = row[0]
                snippet = row[1]
                if os.path.exists(p):
                    results.append({
                        'name': os.path.basename(p),
                        'path': os.path.relpath(p, self.app.ruta_carpeta) if hasattr(self.app, 'ruta_carpeta') else p,
                        'abs_path': p,
                        'snippet': snippet
                    })
            return results
        except: return []

    def stop_indexing(self):
        self.stop_requested = True
