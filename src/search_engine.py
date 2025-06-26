# src/search_engine.py - Motor de Búsqueda
"""
Maneja las operaciones de búsqueda tanto en cache como tradicional
"""

import os
import time

class SearchEngine:
    def __init__(self):
        self.processed_dirs = 0

    def buscar_en_cache(self, criterio, cache_directorios):
        """Busca en el cache - Ultra rápido"""
        if not cache_directorios or 'directorios' not in cache_directorios:
            return None
        
        criterio = criterio.lower()
        resultados = []
        
        for dir_name, ruta_relativa, path_completo in cache_directorios['directorios']:
            if criterio in dir_name.lower():
                resultados.append((dir_name, ruta_relativa, path_completo))
        
        return resultados

    def buscar_tradicional(self, criterio, ruta_carpeta, progress_callback, cancel_check):
        """Busca usando recorrido tradicional del sistema de archivos"""
        criterio = criterio.lower()
        resultados = []
        self.processed_dirs = 0
        inicio = time.time()
        
        try:
            for root, dirs, _ in os.walk(ruta_carpeta):
                if cancel_check():
                    break
                
                for dir_name in dirs:
                    self.processed_dirs += 1
                    
                    if criterio in dir_name.lower():
                        path = os.path.join(root, dir_name)
                        ruta_relativa = os.path.relpath(path, ruta_carpeta)
                        resultados.append((dir_name, ruta_relativa, path))
                    
                    # Actualizar progreso cada 50 directorios
                    if self.processed_dirs % 50 == 0:
                        tiempo_transcurrido = time.time() - inicio
                        velocidad = self.processed_dirs / tiempo_transcurrido if tiempo_transcurrido > 0 else 0
                        progress_callback(self.processed_dirs, len(resultados), tiempo_transcurrido, velocidad)
                        time.sleep(0.01)  # Micro pausa para UI
                        
        except Exception as e:
            raise Exception(f"Error durante búsqueda: {str(e)}")
        
        return resultados