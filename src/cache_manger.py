"""
Gestión de caché para la aplicación Búsqueda Rápida de Carpetas
"""

import os
import time
import threading
from .constants import CHUNK_SIZE

class CacheManager:
    """Gestiona el caché de directorios en memoria"""
    
    def __init__(self, progress_callback=None, status_callback=None):
        self.cache_directorios = {}
        self.cache_valido = False
        self.cache_timestamp = 0
        self.construyendo_cache = False
        self.ruta_base = None
        
        # Callbacks para actualizar UI
        self.progress_callback = progress_callback
        self.status_callback = status_callback
    
    def is_cache_valid(self, ruta_carpeta):
        """Verifica si el caché es válido para la ruta dada"""
        return (self.cache_valido and 
                self.cache_directorios and 
                self.cache_directorios.get('ruta_base') == ruta_carpeta)
    
    def invalidate_cache(self):
        """Invalida el caché actual"""
        self.cache_valido = False
        self.cache_directorios = {}
        self.cache_timestamp = 0
        self.ruta_base = None
    
    def build_cache_async(self, ruta_carpeta, completion_callback=None):
        """Construye el caché de forma asíncrona"""
        if self.construyendo_cache:
            return False
        
        self.construyendo_cache = True
        self.ruta_base = ruta_carpeta
        
        cache_thread = threading.Thread(
            target=self._build_cache_worker,
            args=(ruta_carpeta, completion_callback),
            daemon=True
        )
        cache_thread.start()
        return True
    
    def _build_cache_worker(self, ruta_carpeta, completion_callback):
        """Worker thread para construir el caché"""
        try:
            if self.status_callback:
                self.status_callback("Construyendo caché de directorios...")
            
            if self.progress_callback:
                self.progress_callback(0, "0%")
            
            inicio = time.time()
            cache_temp = []
            processed_dirs = 0
            
            # Recopilar todos los directorios
            for root, dirs, _ in os.walk(ruta_carpeta):
                if not self.construyendo_cache:  # Permitir cancelación
                    return
                
                for dir_name in dirs:
                    path = os.path.join(root, dir_name)
                    ruta_relativa = os.path.relpath(path, ruta_carpeta)
                    cache_temp.append((dir_name, ruta_relativa, path))
                    processed_dirs += 1
                    
                    # Actualizar progreso cada chunk
                    if processed_dirs % CHUNK_SIZE == 0:
                        tiempo_transcurrido = time.time() - inicio
                        progreso = min(95, 20 * (tiempo_transcurrido ** 0.3))
                        
                        if self.progress_callback:
                            self.progress_callback(progreso, f"{progreso:.0f}%")
                        
                        velocidad = processed_dirs / tiempo_transcurrido if tiempo_transcurrido > 0 else 0
                        if self.status_callback:
                            self.status_callback(
                                f"Construyendo caché: {processed_dirs:,} directorios ({velocidad:.0f}/s)"
                            )
                        
                        # Pequeña pausa para UI
                        time.sleep(0.01)
            
            if self.construyendo_cache:
                # Guardar caché en memoria
                self.cache_directorios = {
                    'ruta_base': ruta_carpeta,
                    'timestamp': time.time(),
                    'total': len(cache_temp),
                    'directorios': cache_temp
                }
                self.cache_valido = True
                self.cache_timestamp = time.time()
                
                tiempo_total = time.time() - inicio
                if self.progress_callback:
                    self.progress_callback(100, "100%")
                
                if self.status_callback:
                    self.status_callback(
                        f"Caché construido: {len(cache_temp):,} directorios en {tiempo_total:.1f}s"
                    )
                
                # Llamar callback de completación
                if completion_callback:
                    completion_callback(True, len(cache_temp))
                
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"Error construyendo caché: {str(e)}")
            if completion_callback:
                completion_callback(False, 0)
        finally:
            self.construyendo_cache = False
    
    def search_in_cache(self, criterio, status_callback=None):
        """Busca en el caché de memoria - ULTRA RÁPIDO"""
        if not self.cache_valido or not self.cache_directorios:
            return None
        
        if status_callback:
            status_callback(f"Buscando '{criterio}' en caché...")
        
        inicio = time.time()
        criterio = criterio.lower()
        resultados = []
        
        # Búsqueda ultra rápida en memoria
        for dir_name, ruta_relativa, path_completo in self.cache_directorios['directorios']:
            if criterio in dir_name.lower():
                resultados.append((dir_name, ruta_relativa, path_completo))
        
        tiempo = time.time() - inicio
        total_cache = self.cache_directorios['total']
        
        if status_callback:
            status_callback(
                f"Búsqueda en caché completada: {len(resultados)} resultados en {tiempo:.3f}s "
                f"(revisados {total_cache:,} directorios)"
            )
        
        return resultados
    
    def get_cache_info(self):
        """Obtiene información del caché"""
        if not self.cache_valido or not self.cache_directorios:
            return None
        
        return {
            'total_directories': self.cache_directorios['total'],
            'timestamp': self.cache_directorios['timestamp'],
            'ruta_base': self.cache_directorios['ruta_base']
        }
    
    def cancel_build(self):
        """Cancela la construcción del caché"""
        self.construyendo_cache = False
    
    def clear_cache(self):
        """Limpia el caché completamente"""
        self.invalidate_cache()
        if self.status_callback:
            self.status_callback("Caché limpiado")