# src/cache.py - Gestor de Cache
"""
Maneja el cache de estructura de directorios en memoria
"""

import time

class CacheManager:
    def __init__(self):
        self.ruta_carpeta = ""
        self.cache_directorios = {}
        self.cache_valido = False
        self.cache_timestamp = 0
        self.construyendo_cache = False

    def guardar_cache(self, directorios_temp):
        """Guarda el cache en memoria"""
        self.cache_directorios = {
            'ruta_base': self.ruta_carpeta,
            'timestamp': time.time(),
            'total': len(directorios_temp),
            'directorios': directorios_temp
        }
        self.cache_valido = True
        self.cache_timestamp = time.time()

    def limpiar_cache(self):
        """Limpia el cache de memoria"""
        self.cache_directorios = {}
        self.cache_valido = False
        self.cache_timestamp = 0

    def es_cache_valido_para_ruta(self, ruta):
        """Verifica si el cache es válido para la ruta dada"""
        if not self.cache_valido or not self.cache_directorios:
            return False
        return self.cache_directorios.get('ruta_base') == ruta

    def obtener_estadisticas_cache(self):
        """Obtiene estadísticas del cache actual"""
        if not self.cache_valido or not self.cache_directorios:
            return None
        
        return {
            'total_directorios': self.cache_directorios['total'],
            'ruta_base': self.cache_directorios['ruta_base'],
            'timestamp': self.cache_directorios['timestamp']
        }