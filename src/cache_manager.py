# src/cache_manager.py - Gestor de Cache V.4.5 - OPTIMIZADO CON CARGA AUTOMÁTICA
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
    """Gestor de cache de carpetas optimizado - CON CARGA AUTOMÁTICA AL INICIO"""
    
    def __init__(self, ruta_base=None):
        self.ruta_base = ruta_base
        self.cache_file = "carpetas_cache.pkl"
        self.cache = CacheData()
        self.construyendo = False
        self.callback_progreso = None
        
        # CAMBIO PRINCIPAL: Cargar cache automáticamente al crear la instancia
        self._cargar_cache_automatico()
        
    def _cargar_cache_automatico(self):
        """Carga cache automáticamente al inicializar - NUEVO MÉTODO"""
        try:
            print("[CACHE] Iniciando carga automática...")
            
            # Intentar cargar cache existente
            cache_cargado = self.cargar_cache()
            
            if cache_cargado and self.cache.valido:
                carpetas_count = self.cache.directorios.get('total', 0)
                if carpetas_count > 0:
                    print(f"[CACHE] Cache válido cargado automáticamente: {carpetas_count:,} carpetas")
                    return True
                else:
                    print("[CACHE] Cache cargado pero vacío")
            else:
                print("[CACHE] No se encontró cache válido")
            
            return False
            
        except Exception as e:
            print(f"[CACHE] Error en carga automática: {e}")
            return False
        
    def cargar_cache(self):
        """Carga el cache desde archivo - OPTIMIZADO"""
        try:
            if not os.path.exists(self.cache_file):
                print(f"[CACHE] Archivo cache no existe: {self.cache_file}")
                return False
                
            with open(self.cache_file, 'rb') as f:
                self.cache = pickle.load(f)
            
            # Verificar validez
            if self.cache.ruta_base != self.ruta_base:
                print(f"[CACHE] Ruta base cambió de {self.cache.ruta_base} a {self.ruta_base}")
                self.invalidar_cache()
                return False
            
            if self.cache.is_expired(48):
                print("[CACHE] Cache expirado (>48h), pero manteniéndolo disponible")
                # No invalidar, solo marcar como expirado pero usable
                
            carpetas_count = self.cache.directorios.get('total', 0)
            if carpetas_count > 0:
                print(f"[CACHE] Cache válido cargado: {carpetas_count:,} directorios")
                return True
            else:
                print("[CACHE] Cache cargado pero sin directorios")
                return False
            
        except Exception as e:
            print(f"[CACHE] Error cargando cache: {e}")
            self.invalidar_cache()
            return False
    
    def guardar_cache(self):
        """Guarda el cache a archivo"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
            print(f"[CACHE] Cache guardado exitosamente en {self.cache_file}")
        except Exception as e:
            print(f"[CACHE] Error guardando cache: {e}")
    
    def invalidar_cache(self):
        """Invalida el cache actual"""
        print("[CACHE] Invalidando cache...")
        self.cache = CacheData()
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
                print(f"[CACHE] Archivo cache eliminado: {self.cache_file}")
            except Exception as e:
                print(f"[CACHE] Error eliminando cache: {e}")
    
    def construir_cache(self):
        """Construye el cache optimizado para velocidad - MEJORADO"""
        if self.construyendo:
            print("[CACHE] Ya se está construyendo cache, ignorando solicitud")
            return False
        
        self.construyendo = True
        
        try:
            if not self.ruta_base or not os.path.exists(self.ruta_base):
                print(f"[CACHE] Ruta base inválida: {self.ruta_base}")
                return False
            
            print(f"[CACHE] Iniciando construcción para: {self.ruta_base}")
            
            # Estimación rápida
            if self.callback_progreso:
                self.callback_progreso(0, 100, "Iniciando escaneo...")
            
            total_estimado = self._estimar_carpetas()
            print(f"[CACHE] Estimación inicial: {total_estimado} carpetas")
            
            # Escaneo optimizado
            carpetas = []
            procesados = 0
            start_time = time.time()
            
            # Límites estrictos pero permitir más tiempo para construcción inicial
            MAX_CARPETAS, MAX_TIEMPO, MAX_PROFUNDIDAD = 50000, 60, 8  # Aumentado tiempo y profundidad
            
            for root, dirs, files in os.walk(self.ruta_base):
                # Verificar límites
                if (time.time() - start_time > MAX_TIEMPO or 
                    len(carpetas) >= MAX_CARPETAS):
                    print(f"[CACHE] Límite alcanzado - Tiempo: {time.time() - start_time:.1f}s, Carpetas: {len(carpetas)}")
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
                        
                        # Progreso cada 200 carpetas (menos frecuente)
                        if self.callback_progreso and procesados % 200 == 0:
                            try:
                                progreso = min(5 + (procesados / total_estimado) * 90, 95) if total_estimado > 0 else 5
                                if progreso % 10 == 0:  # Solo cada 10%
                                    self.callback_progreso(int(progreso), 100, 
                                                         f"Escaneando... {procesados:,} carpetas")
                            except Exception:
                                pass
                        
                        # Ajustar estimación dinámicamente
                        if procesados > total_estimado:
                            total_estimado = int(procesados * 1.3)
                            
                    except (PermissionError, OSError):
                        continue
                
                if len(carpetas) >= MAX_CARPETAS:
                    break
                    
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
            
            # Guardar cache
            self.guardar_cache()
            
            tiempo_total = time.time() - start_time
            mensaje_final = f"Cache construido: {len(carpetas):,} carpetas en {tiempo_total:.1f}s"
            
            if self.callback_progreso:
                self.callback_progreso(100, 100, mensaje_final)
            
            print(f"[CACHE] {mensaje_final}")
            return True
            
        except Exception as e:
            print(f"[CACHE] Error construyendo cache: {e}")
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
            
            # Estimación más conservadora
            estimacion = max(primer_nivel * 100, 500)
            print(f"[CACHE] Primer nivel: {primer_nivel} carpetas, estimación total: {estimacion}")
            return estimacion
            
        except Exception:
            return 1000
    
    def buscar_en_cache(self, criterio):
        """Busca carpetas en el cache - OPTIMIZADO"""
        if not self.cache.valido:
            print("[CACHE] Cache no válido para búsqueda")
            return None
        
        criterio_lower = criterio.lower()
        resultados = []
        carpetas = self.cache.directorios.get('directorios', [])
        
        if not carpetas:
            print("[CACHE] No hay carpetas en cache")
            return []
        
        # Búsqueda con límite
        MAX_RESULTADOS = 2000
        start_time = time.time()
        
        for carpeta in carpetas:
            if len(resultados) >= MAX_RESULTADOS:
                break
                
            if criterio_lower in carpeta['nombre'].lower():
                resultados.append((
                    carpeta['nombre'],
                    carpeta['ruta_relativa'], 
                    carpeta['ruta_absoluta']
                ))
        
        search_time = time.time() - start_time
        print(f"[CACHE] Búsqueda completada: {len(resultados)} resultados en {search_time:.3f}s")
        
        return resultados
    
    def get_cache_stats(self):
        """Obtiene estadísticas del cache - MEJORADO"""
        if not self.cache.valido:
            return {
                'valido': False,
                'carpetas': 0,
                'edad': 'No disponible',
                'ruta_base': 'No disponible',
                'archivo_existe': os.path.exists(self.cache_file)
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
            'ruta_base': self.cache.ruta_base,
            'archivo_existe': os.path.exists(self.cache_file),
            'expirado': self.cache.is_expired(),
            'archivo_cache': self.cache_file
        }
    
    def necesita_construccion(self):
        """Verifica si el cache necesita ser construido"""
        needs_build = not self.cache.valido or len(self.cache.directorios.get('directorios', [])) == 0
        print(f"[CACHE] ¿Necesita construcción? {needs_build}")
        return needs_build
    
    def recargar_cache(self):
        """Recarga el cache escaneando las carpetas"""
        print("[CACHE] Recargando cache...")
        return self.construir_cache()
    
    def limpiar(self):
        """Limpia el cache completamente"""
        print("[CACHE] Limpiando cache...")
        self.invalidar_cache()
        self.construyendo = False
    
    def is_cache_ready(self):
        """Verifica si el cache está listo para uso"""
        ready = (self.cache.valido and 
                len(self.cache.directorios.get('directorios', [])) > 0 and
                not self.construyendo)
        return ready
    
    def get_cache_file_info(self):
        """Obtiene información del archivo de cache"""
        try:
            if os.path.exists(self.cache_file):
                stat = os.stat(self.cache_file)
                return {
                    'existe': True,
                    'tamaño_bytes': stat.st_size,
                    'tamaño_mb': stat.st_size / (1024 * 1024),
                    'modificado': datetime.fromtimestamp(stat.st_mtime)
                }
            else:
                return {'existe': False}
        except Exception as e:
            return {'existe': False, 'error': str(e)}