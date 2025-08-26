# src/cache_manager.py - Gestor de Cache V.4.1 (Progreso Corregido)
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
    
    def is_expired(self, max_age_hours=24):
        """Verifica si el cache ha expirado"""
        if not self.valido:
            return True
        
        age = time.time() - self.timestamp
        return age > (max_age_hours * 3600)

class CacheManager:
    """Gestor de cache de carpetas"""
    
    def __init__(self, ruta_base=None):
        self.ruta_base = ruta_base
        self.cache_file = "carpetas_cache.pkl"
        self.cache = CacheData()
        self.construyendo = False
        self.callback_progreso = None
        
    def cargar_cache(self):
        """Carga el cache desde archivo"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                
                # Verificar que el cache sea para la misma ruta base
                if self.cache.ruta_base != self.ruta_base:
                    self.invalidar_cache()
                    return False
                
                # Verificar si ha expirado
                if self.cache.is_expired():
                    self.invalidar_cache()
                    return False
                
                return True
        except Exception:
            self.invalidar_cache()
            
        return False
    
    def guardar_cache(self):
        """Guarda el cache a archivo"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception:
            pass
    
    def invalidar_cache(self):
        """Invalida el cache actual"""
        self.cache = CacheData()
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except Exception:
                pass
    
    def _estimar_total_directorios(self, ruta_base, max_sample=100):
        """Estima el total de directorios haciendo un muestreo rápido"""
        try:
            sample_count = 0
            sample_dirs = 0
            
            for root, dirs, files in os.walk(ruta_base):
                sample_dirs += len(dirs)
                sample_count += 1
                
                # Limitar el muestreo para no tardar mucho
                if sample_count >= max_sample:
                    break
            
            # Estimación basada en la muestra
            if sample_count > 0:
                promedio_dirs_por_nivel = sample_dirs / sample_count
                # Estimación conservadora multiplicando por factores de profundidad
                estimacion = int(promedio_dirs_por_nivel * sample_count * 1.5)
                return max(estimacion, 100)  # Mínimo 100 para evitar divisiones por 0
            
            return 1000  # Valor por defecto
            
        except Exception:
            return 1000  # Valor por defecto en caso de error
    
    def construir_cache(self):
        """Construye el cache de carpetas con progreso granular"""
        if self.construyendo:
            return False
        
        self.construyendo = True
        
        try:
            if not self.ruta_base or not os.path.exists(self.ruta_base):
                return False
            
            # PASO 1: Estimar total de directorios (0-5%)
            if self.callback_progreso:
                self.callback_progreso(0, 100, "Estimando directorios...")
            
            total_estimado = self._estimar_total_directorios(self.ruta_base)
            
            if self.callback_progreso:
                self.callback_progreso(5, 100, "Iniciando escaneo...")
            
            # PASO 2: Escanear carpetas (5-95%)
            carpetas = []
            total_procesados = 0
            ultimo_porcentaje_reportado = 5
            
            for root, dirs, files in os.walk(self.ruta_base):
                for dirname in dirs:
                    ruta_completa = os.path.join(root, dirname)
                    ruta_relativa = os.path.relpath(ruta_completa, self.ruta_base)
                    
                    carpetas.append({
                        'nombre': dirname,
                        'ruta_relativa': ruta_relativa,
                        'ruta_absoluta': ruta_completa
                    })
                    
                    total_procesados += 1
                    
                    # Callback de progreso GRANULAR (cada 0.5%)
                    if self.callback_progreso:
                        # Calcular progreso entre 5% y 95%
                        progreso_escaneo = min((total_procesados / total_estimado) * 90, 90)
                        porcentaje_actual = 5 + progreso_escaneo
                        
                        # Reportar cada 0.5% de progreso
                        if porcentaje_actual - ultimo_porcentaje_reportado >= 0.5:
                            self.callback_progreso(
                                int(porcentaje_actual), 
                                100, 
                                f"Escaneando... {total_procesados:,} carpetas"
                            )
                            ultimo_porcentaje_reportado = porcentaje_actual
                        
                        # Si ya procesamos más de lo estimado, ajustar
                        if total_procesados > total_estimado:
                            total_estimado = total_procesados + 100
            
            # PASO 3: Finalizar (95-100%)
            if self.callback_progreso:
                self.callback_progreso(95, 100, "Guardando cache...")
            
            # Actualizar cache
            self.cache.directorios = {
                'directorios': carpetas,
                'total': len(carpetas),
                'timestamp': time.time()
            }
            self.cache.timestamp = time.time()
            self.cache.ruta_base = self.ruta_base
            self.cache.valido = True
            
            if self.callback_progreso:
                self.callback_progreso(98, 100, "Escribiendo archivo...")
            
            # Guardar a archivo
            self.guardar_cache()
            
            # COMPLETADO (100%)
            if self.callback_progreso:
                self.callback_progreso(100, 100, f"Completado: {len(carpetas):,} carpetas")
            
            return True
            
        except Exception as e:
            if self.callback_progreso:
                self.callback_progreso(0, 100, f"Error: {str(e)}")
            self.invalidar_cache()
            return False
        finally:
            self.construyendo = False
    
    def recargar_cache(self):
        """Recarga el cache escaneando las carpetas (alias para construir_cache)"""
        return self.construir_cache()
    
    def buscar_en_cache(self, criterio):
        """Busca carpetas en el cache"""
        if not self.cache.valido:
            # Intentar cargar cache
            if not self.cargar_cache():
                # Si no hay cache válido, retornar None para forzar búsqueda tradicional
                return None
        
        criterio_lower = criterio.lower()
        resultados = []
        
        # Obtener lista de carpetas del cache
        carpetas = self.cache.directorios.get('directorios', [])
        
        for carpeta in carpetas:
            if criterio_lower in carpeta['nombre'].lower():
                resultados.append((
                    carpeta['nombre'],
                    carpeta['ruta_relativa'], 
                    carpeta['ruta_absoluta']
                ))
        
        return resultados
    
    def get_cache_stats(self):
        """Obtiene estadísticas del cache"""
        if not self.cache.valido:
            return {
                'valido': False,
                'carpetas': 0,
                'edad': 'No disponible',
                'ruta_base': 'No disponible'
            }
        
        edad_segundos = time.time() - self.cache.timestamp
        edad_horas = int(edad_segundos // 3600)
        edad_minutos = int((edad_segundos % 3600) // 60)
        
        if edad_horas > 0:
            edad_str = f"{edad_horas}h {edad_minutos}m"
        else:
            edad_str = f"{edad_minutos}m"
        
        total_carpetas = self.cache.directorios.get('total', 0)
        
        return {
            'valido': True,
            'carpetas': total_carpetas,
            'edad': edad_str,
            'ruta_base': self.cache.ruta_base
        }
    
    def limpiar(self):
        """Limpia el cache completamente"""
        self.invalidar_cache()
        self.construyendo = False