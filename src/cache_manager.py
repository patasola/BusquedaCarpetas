# src/cache_manager.py - Gestor de Cache V.4.5.3 - ULTRA OPTIMIZADO
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
    """Gestor de cache de carpetas optimizado con scandir"""
    
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
                    if "onedrive" in ruta_cache_norm and "onedrive" in ruta_actual_norm:
                         print(f"[CACHE] OneDrive path variation detected, keeping cache: {self.cache_file}")
                         self.cache.ruta_base = self.ruta_base
                    else:
                         print(f"[CACHE] Path mismatch in {self.cache_file}, but keeping for best-effort search")
            
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
        """Construye el cache usando scandir recursivo (ULTRA RÁPIDO)"""
        if self.construyendo:
            return False
        
        self.construyendo = True
        try:
            if not self.ruta_base or not os.path.exists(self.ruta_base):
                return False
            
            print(f"[CACHE] Construyendo cache (scandir) para: {self.ruta_base}")
            carpetas = []
            start_time = time.time()
            max_carpetas = 100000
            
            def scan_recursive(path):
                if len(carpetas) >= max_carpetas:
                    return
                try:
                    with os.scandir(path) as it:
                        for entry in it:
                            if len(carpetas) >= max_carpetas:
                                break
                            if entry.is_dir():
                                try:
                                    ruta_relativa = os.path.relpath(entry.path, self.ruta_base)
                                    carpetas.append({
                                        'nombre': entry.name,
                                        'ruta_relativa': ruta_relativa,
                                        'ruta_absoluta': entry.path
                                    })
                                    # Llamada recursiva
                                    scan_recursive(entry.path)
                                except:
                                    continue
                except PermissionError:
                    pass
                except Exception as e:
                    print(f"[CACHE] Error escaneando {path}: {e}")
            
            scan_recursive(self.ruta_base)
            
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
                if len(resultados) >= 1000: # Límite aumentado
                    break
        
        return resultados

    def get_cache_stats(self):
        """Retorna estadísticas del cache completas"""
        try:
            # Calcular edad
            edad_str = "N/A"
            if self.cache.timestamp > 0:
                diff = time.time() - self.cache.timestamp
                if diff < 60: edad_str = f"{int(diff)}s"
                elif diff < 3600: edad_str = f"{int(diff/60)}m"
                else: edad_str = f"{int(diff/3600)}h"

            return {
                'carpetas': self.cache.directorios.get('total', 0),
                'total': self.cache.directorios.get('total', 0),
                'timestamp': self.cache.timestamp,
                'valido': self.cache.valido,
                'ruta_base': self.cache.ruta_base,
                'edad': edad_str # Requerido por search_coordinator.py
            }
        except:
            return {'carpetas': 0, 'total': 0, 'valido': False, 'edad': "Error"}

    def necesita_construccion(self):
        return not self.cache.valido or len(self.cache.directorios.get('directorios', [])) == 0

    def limpiar(self):
        """Alias para limpiar para compatibilidad"""
        self.invalidar_cache()