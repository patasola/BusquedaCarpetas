# src/cache_manager.py - Gestor de Cache V.4.2 (Refactorizado y Optimizado)
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
        return not self.valido or (time.time() - self.timestamp > max_age_hours * 3600)

class CacheManager:
    """Gestor de cache de carpetas optimizado"""
    
    def __init__(self, ruta_base=None):
        self.ruta_base = ruta_base
        self.cache_file = "carpetas_cache.pkl"
        self.cache = CacheData()
        self.construyendo = False
        self.callback_progreso = None
        
        self.cargar_cache()
        
    def cargar_cache(self):
        """Carga el cache desde archivo"""
        try:
            if not os.path.exists(self.cache_file):
                return False
                
            with open(self.cache_file, 'rb') as f:
                self.cache = pickle.load(f)
            
            # Verificar validez
            if self.cache.ruta_base != self.ruta_base:
                self.invalidar_cache()
                return False
            
            if self.cache.is_expired(48):
                print("Cache expirado, pero manteniéndolo disponible")
                return True
            
            print(f"Cache válido cargado: {self.cache.directorios.get('total', 0)} directorios")
            return True
            
        except Exception as e:
            print(f"Error cargando cache: {e}")
            self.invalidar_cache()
            return False
    
    def guardar_cache(self):
        """Guarda el cache a archivo"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            print(f"Error guardando cache: {e}")
    
    def invalidar_cache(self):
        """Invalida el cache actual"""
        self.cache = CacheData()
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except:
                pass
    
    def construir_cache(self):
        """Construye el cache optimizado para velocidad"""
        if self.construyendo:
            return False
        
        self.construyendo = True
        
        try:
            if not self.ruta_base or not os.path.exists(self.ruta_base):
                return False
            
            # Estimación rápida
            if self.callback_progreso:
                self.callback_progreso(0, 100, "Iniciando escaneo...")
            
            total_estimado = self._estimar_carpetas()
            
            # Escaneo optimizado
            carpetas = []
            procesados = 0
            start_time = time.time()
            
            # Límites estrictos
            MAX_CARPETAS, MAX_TIEMPO, MAX_PROFUNDIDAD = 50000, 30, 6
            
            for root, dirs, files in os.walk(self.ruta_base):
                # Verificar límites
                if (time.time() - start_time > MAX_TIEMPO or 
                    len(carpetas) >= MAX_CARPETAS):
                    break
                
                # Controlar profundidad
                depth = root.replace(self.ruta_base, '').count(os.sep)
                if depth >= MAX_PROFUNDIDAD:
                    dirs.clear()
                    continue
                
                # Procesar directorios
                for dirname in dirs[:]:
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
                        
                        procesados += 1
                        
                        # Progreso cada 100 carpetas
                        if self.callback_progreso and procesados % 100 == 0:
                            progreso = min(3 + (procesados / total_estimado) * 92, 95)
                            if progreso % 5 == 0:  # Solo cada 5%
                                self.callback_progreso(int(progreso), 100, 
                                                     f"Escaneando... {procesados:,} carpetas")
                        
                        # Ajustar estimación
                        if procesados > total_estimado:
                            total_estimado = int(procesados * 1.2)
                            
                    except (PermissionError, OSError):
                        continue
            
            # Finalizar
            if self.callback_progreso:
                self.callback_progreso(95, 100, "Finalizando...")
            
            self.cache.directorios = {
                'directorios': carpetas,
                'total': len(carpetas),
                'timestamp': time.time()
            }
            self.cache.timestamp = time.time()
            self.cache.ruta_base = self.ruta_base
            self.cache.valido = True
            
            self.guardar_cache()
            
            tiempo_total = time.time() - start_time
            mensaje_final = f"Completado: {len(carpetas):,} carpetas en {tiempo_total:.1f}s"
            
            if self.callback_progreso:
                self.callback_progreso(100, 100, mensaje_final)
            
            print(f"Cache construido exitosamente: {mensaje_final}")
            return True
            
        except Exception as e:
            print(f"Error construyendo cache: {e}")
            if self.callback_progreso:
                self.callback_progreso(0, 100, f"Error: {str(e)}")
            self.invalidar_cache()
            return False
        finally:
            self.construyendo = False
    
    def _estimar_carpetas(self):
        """Estimación rápida del total de directorios"""
        try:
            if not os.path.exists(self.ruta_base):
                return 1000
            
            # Contar solo primer nivel
            primer_nivel = sum(1 for item in os.listdir(self.ruta_base) 
                             if os.path.isdir(os.path.join(self.ruta_base, item)))
            
            return max(primer_nivel * 50, 100)
            
        except Exception:
            return 1000
    
    def buscar_en_cache(self, criterio):
        """Busca carpetas en el cache"""
        if not self.cache.valido:
            if not self.cargar_cache():
                return None
        
        criterio_lower = criterio.lower()
        resultados = []
        carpetas = self.cache.directorios.get('directorios', [])
        
        # Búsqueda con límite
        MAX_RESULTADOS = 2000
        
        for carpeta in carpetas:
            if len(resultados) >= MAX_RESULTADOS:
                break
                
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
        
        # Formatear edad
        if edad_segundos < 3600:
            edad_str = f"{int(edad_segundos // 60)}m"
        elif edad_segundos < 86400:
            horas = int(edad_segundos // 3600)
            minutos = int((edad_segundos % 3600) // 60)
            edad_str = f"{horas}h {minutos}m"
        else:
            dias = int(edad_segundos // 86400)
            horas = int((edad_segundos % 86400) // 3600)
            edad_str = f"{dias}d {horas}h"
        
        return {
            'valido': True,
            'carpetas': self.cache.directorios.get('total', 0),
            'edad': edad_str,
            'ruta_base': self.cache.ruta_base
        }
    
    def necesita_construccion(self):
        """Verifica si el cache necesita ser construido"""
        return not self.cache.valido or len(self.cache.directorios.get('directorios', [])) == 0
    
    def recargar_cache(self):
        """Recarga el cache escaneando las carpetas"""
        return self.construir_cache()
    
    def limpiar(self):
        """Limpia el cache completamente"""
        self.invalidar_cache()
        self.construyendo = False