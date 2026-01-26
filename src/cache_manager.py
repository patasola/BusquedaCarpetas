# src/cache_manager.py - Gestor de Cache V.4.5 - OPTIMIZADO
import os
import pickle
import time
import threading
from datetime import datetime, timedelta

class CacheData:
    """Estructura de datos del cache"""
    def __init__(self):
        self.directorios = {'directorios': [], 'total': 0, 'timestamp': 0}
        self.timestamp = time.time()
        self.ruta_base = ""
        self.valido = False
    
    def is_expired(self, max_age_hours=48):
        """Verifica si el cache ha expirado"""
        if not self.valido:
            return True
        return (time.time() - self.timestamp > max_age_hours * 3600)

class CacheManager:
    """Gestor de cache de carpetas optimizado"""
    
    def __init__(self, ruta_base=None, cache_file=None):
        self.ruta_base = ruta_base
        self.cache_file = cache_file if cache_file else "carpetas_cache.pkl"
        self.cache = CacheData()
        self.construyendo = False
        self.callback_progreso = None
        
        # Cargar cache automáticamente si existe
        self._cargar_cache_automatico()
        
    def _cargar_cache_automatico(self):
        """Carga cache automáticamente al inicializar"""
        try:
            if os.path.exists(self.cache_file):
                self.cargar_cache()
        except Exception as e:
            print(f"[CACHE] Error en carga automática: {e}")
        
    def cargar_cache(self):
        """Carga el cache desde archivo"""
        try:
            if not os.path.exists(self.cache_file):
                return False
                
            with open(self.cache_file, 'rb') as f:
                self.cache = pickle.load(f)
            
            # Verificar validez con normalización de rutas
            if self.ruta_base:
                ruta_cache_norm = os.path.normpath(self.cache.ruta_base).lower()
                ruta_actual_norm = os.path.normpath(self.ruta_base).lower()
                
                if ruta_cache_norm != ruta_actual_norm:
                    # NO invalidar automáticamente si es solo un cambio de nombre de carpeta padre similar (OneDrive)
                    if "onedrive" in ruta_cache_norm and "onedrive" in ruta_actual_norm:
                         print(f"[CACHE] OneDrive path variation detected, keeping cache: {self.cache_file}")
                         self.cache.ruta_base = self.ruta_base # Actualizar ruta sin borrar datos
                    else:
                         print(f"[CACHE] Path mismatch in {self.cache_file}, but keeping for best-effort search")
                         # No invalidar, permitir búsqueda aunque sea en rutas viejas (el buscador las validará)
            
            carpetas_count = self.cache.directorios.get('total', 0)
            if carpetas_count > 0:
                self.cache.valido = True
                return True
            return False
            
        except Exception as e:
            print(f"[CACHE] Error cargando cache {self.cache_file}: {e}")
            return False
    
    def guardar_cache(self):
        """Guarda el cache a archivo"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
            print(f"[CACHE] Cache guardado: {self.cache_file}")
        except Exception as e:
            print(f"[CACHE] Error guardando cache: {e}")
    
    def invalidar_cache(self):
        """Invalida el cache actual"""
        self.cache = CacheData()
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except:
                pass
    
    def construir_cache(self):
        """Construye el cache escaneando el sistema de archivos"""
        if self.construyendo:
            return False
        
        self.construyendo = True
        try:
            if not self.ruta_base or not os.path.exists(self.ruta_base):
                return False
            
            print(f"[CACHE] Construyendo cache para: {self.ruta_base}")
            carpetas = []
            start_time = time.time()
            
            # Límite de seguridad
            MAX_CARPETAS = 100000
            
            for root, dirs, files in os.walk(self.ruta_base):
                for dirname in dirs:
                    if len(carpetas) >= MAX_CARPETAS:
                        break
                    
                    try:
                        ruta_completa = os.path.join(root, dirname)
                        ruta_relativa = os.path.relpath(ruta_completa, self.ruta_base)
                        
                        carpetas.append({
                            'nombre': dirname,
                            'ruta_relativa': ruta_relativa,
                            'ruta_absoluta': ruta_completa
                        })
                    except:
                        continue
                
                if len(carpetas) >= MAX_CARPETAS:
                    break
            
            self.cache.directorios = {
                'directorios': carpetas,
                'total': len(carpetas),
                'timestamp': time.time()
            }
            self.cache.timestamp = time.time()
            self.cache.ruta_base = self.ruta_base
            self.cache.valido = True
            
            self.guardar_cache()
            print(f"[CACHE] Construcción finalizada: {len(carpetas)} carpetas en {time.time() - start_time:.1f}s")
            return True
        finally:
            self.construyendo = False
    
    def buscar_en_cache(self, criterio):
        """Busca carpetas en el cache"""
        if not self.cache.directorios.get('directorios'):
            return []
        
        criterio_lower = criterio.lower()
        resultados = []
        carpetas = self.cache.directorios.get('directorios', [])
        
        for carpeta in carpetas:
            if criterio_lower in carpeta['nombre'].lower():
                resultados.append((
                    carpeta['nombre'],
                    carpeta['ruta_relativa'], 
                    carpeta['ruta_absoluta']
                ))
                if len(resultados) >= 100: # Límite de resultados por ubicación
                    break
        
        return resultados

    def get_cache_stats(self):
        """Retorna estadísticas del cache"""
        return {
            'carpetas': self.cache.directorios.get('total', 0), # Para locations_config_modal.py
            'total': self.cache.directorios.get('total', 0),    # Alias común
            'timestamp': self.cache.timestamp,
            'valido': self.cache.valido,
            'ruta_base': self.cache.ruta_base
        }

    def necesita_construccion(self):
        return not self.cache.valido or len(self.cache.directorios.get('directorios', [])) == 0