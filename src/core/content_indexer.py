# src/core/content_indexer.py - Motor de Búsqueda de Contenido V.6.1
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
        self._executor = None
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
                # V.6.1 - Indexamos 'path' para permitir búsquedas por nombre de archivo
                cursor.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
                    path, content, tokenize="unicode61 tokenchars '-._0123456789'")''')
                
                # MIGRACIÓN AUTOMÁTICA: Detectar si 'path' está UNINDEXED (esquema V.6.0)
                needs_migration = False
                try:
                    cursor.execute("SELECT path FROM content_fts WHERE path MATCH 'schema_check_6_1' LIMIT 1")
                except sqlite3.OperationalError:
                    needs_migration = True
                
                if needs_migration:
                    print("[CONTENT] Detectado esquema antiguo (path UNINDEXED). Migrando a V.6.1...")
                    cursor.execute("DROP TABLE IF EXISTS content_fts")
                    cursor.execute('''CREATE VIRTUAL TABLE content_fts USING fts5(
                        path, content, tokenize="unicode61 tokenchars '-._0123456789'")''')
                    cursor.execute("DELETE FROM file_metadata")
                    print("[CONTENT] Migración completada. Re-indexación necesaria.")
                    
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
        import warnings
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                if ext in ('.txt', '.log'):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                elif ext == '.pdf':
                    from pypdf import PdfReader
                    import logging
                    # Silenciar TODOS los loggers relacionados con pypdf
                    logging.getLogger("pypdf").setLevel(logging.CRITICAL)
                    for log_name in logging.root.manager.loggerDict:
                        if 'pypdf' in log_name:
                            logging.getLogger(log_name).setLevel(logging.CRITICAL)
                            
                    reader = PdfReader(file_path, strict=False)
                    pages = reader.pages
                    
                    sample = ""
                    for page in pages[:3]:
                        try:
                            t = page.extract_text()
                            if t: sample += t
                        except: pass
                    
                    if not sample.strip():
                        return ""  # PDF escaneado
                    
                    texts = [sample]
                    max_pages = 50  # Limitar a máximo 50 páginas indexadas para evitar bloqueos
                    for page in pages[3:max_pages]:
                        if self.stop_requested: break
                        try:
                            t = page.extract_text()
                            if t: texts.append(t)
                        except: pass
                    text = " ".join(texts)
                    
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
            pass # Silenciar errores de extracción individuales para no saturar consola
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
            logging.getLogger("pypdf").setLevel(logging.CRITICAL)
            logging.getLogger("pypdf").propagate = False
            
            max_workers = 6
            processed_count = 0
            batch_size = 50
            pending_batch = []
            last_ui_update = 0
            
            self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
            with self._executor as executor:
                future_to_path = {executor.submit(self._extract_text, p): (p, m) for p, m in files_to_index}
                
                for future in concurrent.futures.as_completed(future_to_path):
                    processed_count += 1
                    if self.stop_requested: break
                    path, mtime = future_to_path[future]
                    try:
                        content = future.result(timeout=30)
                        percent = (processed_count / total) * 100
                        if percent - last_ui_update >= 1 or processed_count == total:
                            if progress_callback: progress_callback(f"[{folder_name}] {processed_count}/{total}", percent)
                            last_ui_update = percent
                        
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
                self.conn.execute("VACUUM")
                print("[CONTENT] Índice borrado por completo y optimizado (VACUUM)")
            return True
        except Exception as e:
            print(f"[CONTENT] Error borrando índice completo: {e}")
            return False

    def purge_location(self, folder_path):
        """Elimina todos los archivos del índice que pertenezcan a esta carpeta"""
        try:
            prefix = os.path.abspath(folder_path)
            if not prefix.endswith(os.sep): prefix += os.sep
            
            with self.db_lock:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM file_metadata WHERE path LIKE ? OR path = ?", (prefix + '%', folder_path))
                cursor.execute("DELETE FROM content_fts WHERE path LIKE ? OR path = ?", (prefix + '%', folder_path))
                self.conn.commit()
                print(f"[CONTENT] Índice purgado para: {folder_path}")
            return True
        except Exception as e:
            print(f"[CONTENT] Error purgando índice: {e}")
            return False

    def search(self, query, search_field="content"):
        """
        Búsqueda unificada:
        - search_field='content': FTS5 en el cuerpo de los archivos (con snippet resaltado)
        - search_field='path':    SQL LIKE en la ruta del archivo (todos los indexados,
                                  incluyendo archivos sin contenido extraíble)
        """
        if not self.conn or not query.strip():
            return []
        query = query.strip()

        try:
            with self.db_lock:
                cursor = self.conn.cursor()

                if search_field == "path":
                    # Buscar por NOMBRE DE ARCHIVO únicamente (no por ruta completa)
                    # Filtramos en Python para usar basename limpio
                    cursor.execute("SELECT path FROM file_metadata ORDER BY path LIMIT 50000")
                    rows = cursor.fetchall()
                    q_lower = query.lower()
                    results = []
                    for (p,) in rows:
                        if q_lower in os.path.basename(p).lower() and os.path.exists(p):
                            results.append({
                                'name': os.path.basename(p),
                                'path': os.path.relpath(p, self.app.ruta_carpeta) if hasattr(self.app, 'ruta_carpeta') else p,
                                'abs_path': p,
                                'snippet': p
                            })
                    return results

                else:
                    # Búsqueda FTS5 en el contenido de los archivos
                    is_exact = query.startswith('"') and query.endswith('"')
                    normalized = self.normalize_text(query.strip('"'))
                    if not normalized:
                        return []
                    fts_query = f'"{normalized}"' if is_exact else normalized

                    cursor.execute("""
                        SELECT path, snippet(content_fts, 1, '[', ']', '...', 8)
                        FROM content_fts
                        WHERE content MATCH ?
                        LIMIT 10000""", (fts_query,))
                    rows = cursor.fetchall()
                    results = []
                    for p, snippet in rows:
                        if os.path.exists(p):
                            results.append({
                                'name': os.path.basename(p),
                                'path': os.path.relpath(p, self.app.ruta_carpeta) if hasattr(self.app, 'ruta_carpeta') else p,
                                'abs_path': p,
                                'snippet': snippet
                            })
                    return results

        except Exception as e:
            print(f"[CONTENT] Error en búsqueda ({search_field}): {e}")
            return []

    def stop_indexing(self):
        """Detiene la indexación de forma inmediata cancelando futuros pendientes"""
        self.stop_requested = True
        if hasattr(self, '_executor') and self._executor:
            try:
                self._executor.shutdown(wait=False, cancel_futures=True)
            except TypeError:
                self._executor.shutdown(wait=False)
            except Exception:
                pass
