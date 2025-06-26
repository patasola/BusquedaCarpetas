"""
Motor de búsqueda para la aplicación Búsqueda Rápida de Carpetas
"""

import os
import time
import threading
from .constants import SEARCH_CHUNK_SIZE, PROGRESS_UPDATE_INTERVAL, RESULT_UPDATE_INTERVAL

class SearchEngine:
    """Motor de búsqueda tradicional para cuando no hay caché"""
    
    def __init__(self, progress_callback=None, status_callback=None, results_callback=None):
        self.busqueda_activa = False
        self.busqueda_cancelada = False
        self.search_thread = None
        self.tiempo_inicio = 0
        self.total_dirs = 0
        self.processed_dirs = 0
        self.last_progress_update = 0
        self.dirs_per_second = 0
        
        # Callbacks para actualizar UI
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.results_callback = results_callback
    
    def is_searching(self):
        """Verifica si hay una búsqueda activa"""
        return self.busqueda_activa
    
    def search_async(self, ruta_carpeta, criterio, completion_callback=None):
        """Inicia una búsqueda asíncrona"""
        if self.busqueda_activa:
            return False
        
        self._prepare_search(criterio)
        
        self.search_thread = threading.Thread(
            target=self._search_worker,
            args=(ruta_carpeta, criterio, completion_callback),
            daemon=True
        )
        self.search_thread.start()
        return True
    
    def _prepare_search(self, criterio):
        """Prepara la búsqueda"""
        self.tiempo_inicio = time.time()
        self.busqueda_activa = True
        self.busqueda_cancelada = False
        self.total_dirs = 0
        self.processed_dirs = 0
        self.last_progress_update = 0
        self.dirs_per_second = 0
        
        if self.progress_callback:
            self.progress_callback(0, "0%")
        
        if self.status_callback:
            self.status_callback(f"Caché no disponible. Búsqueda tradicional de '{criterio}'...")
    
    def _search_worker(self, ruta_carpeta, criterio, completion_callback):
        """Worker thread para ejecutar la búsqueda"""
        try:
            criterio = criterio.lower()
            resultados = []
            processed_dirs = 0
            
            if self.status_callback:
                self.status_callback(f"Iniciando búsqueda de '{criterio}'...")
            
            # Recopilar directorios para procesar
            dirs_to_process = []
            for root, dirs, _ in os.walk(ruta_carpeta):
                if self.busqueda_cancelada:
                    break
                for dir_name in dirs:
                    dirs_to_process.append((root, dir_name))
            
            total_dirs = len(dirs_to_process)
            self.total_dirs = total_dirs
            
            # Procesar en chunks
            for i in range(0, len(dirs_to_process), SEARCH_CHUNK_SIZE):
                if self.busqueda_cancelada:
                    break
                
                chunk = dirs_to_process[i:i + SEARCH_CHUNK_SIZE]
                chunk_matches = self._process_directory_chunk(chunk, criterio, resultados, ruta_carpeta)
                processed_dirs += len(chunk)
                self.processed_dirs = processed_dirs
                
                # Actualizar progreso
                tiempo_transcurrido = time.time() - self.tiempo_inicio
                if tiempo_transcurrido > 0:
                    self.dirs_per_second = processed_dirs / tiempo_transcurrido
                    
                    # Actualizar estado cada segundo
                    if tiempo_transcurrido - self.last_progress_update >= PROGRESS_UPDATE_INTERVAL:
                        progreso = min(95, 20 * (tiempo_transcurrido ** 0.3))
                        
                        if self.progress_callback:
                            self.progress_callback(progreso, f"{int(progreso)}%")
                        
                        if self.status_callback:
                            self.status_callback(
                                f"Procesados {processed_dirs:,} directorios ({self.dirs_per_second:.0f}/s) - "
                                f"{len(resultados)} coincidencias"
                            )
                        self.last_progress_update = tiempo_transcurrido
                
                # Actualizar resultados cada 5 coincidencias
                if chunk_matches > 0 and len(resultados) % RESULT_UPDATE_INTERVAL == 0:
                    if self.results_callback:
                        self.results_callback(resultados.copy())
                
                # Micro-pausa para UI
                time.sleep(0.01)
            
            if not self.busqueda_cancelada:
                self._finalize_search(resultados, criterio, completion_callback)
            
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Error: {str(e)}")
            if completion_callback:
                completion_callback(False, [])
        finally:
            self.busqueda_activa = False
    
    def _process_directory_chunk(self, dirs_chunk, criterio, resultados, ruta_carpeta):
        """Procesa un chunk de directorios"""
        chunk_matches = 0
        
        for root, dir_name in dirs_chunk:
            if self.busqueda_cancelada:
                break
            
            if criterio in dir_name.lower():
                path = os.path.join(root, dir_name)
                ruta_relativa = os.path.relpath(path, ruta_carpeta)
                resultados.append((dir_name, ruta_relativa, path))
                chunk_matches += 1
        
        return chunk_matches
    
    def _finalize_search(self, resultados, criterio, completion_callback):
        """Finaliza la búsqueda"""
        tiempo = time.time() - self.tiempo_inicio
        
        if self.status_callback:
            self.status_callback(
                f"Búsqueda completada: {len(resultados)} resultados encontrados en {self.processed_dirs:,} directorios "
                f"({tiempo:.1f}s)"
            )
        
        if self.progress_callback:
            self.progress_callback(100, f"100% • {tiempo:.1f}s")
        
        if completion_callback:
            completion_callback(True, resultados)
    
    def cancel_search(self):
        """Cancela la búsqueda activa"""
        if self.busqueda_activa:
            self.busqueda_cancelada = True
            tiempo = time.time() - self.tiempo_inicio
            if self.status_callback:
                self.status_callback(f"Búsqueda cancelada ({tiempo:.1f} segundos)")
            return True
        return False