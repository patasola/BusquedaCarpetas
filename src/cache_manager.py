import os
import time
from .cache import Cache

class CacheManager:
    def __init__(self, ruta_base=""):
        self.cache = Cache()
        self.ruta_base = os.path.normpath(ruta_base) if ruta_base else ""
        self.construyendo = False
        self.callback_progreso = None  # Callback para progreso de construcción
    
    def construir_cache(self, ruta_base=None):
        if ruta_base:
            self.ruta_base = os.path.normpath(ruta_base)
        
        try:
            # Verificaciones exhaustivas
            if not self.ruta_base:
                print("Error: Ruta base no especificada")
                return False
                
            if not os.path.exists(self.ruta_base):
                print(f"Error: La ruta no existe - {self.ruta_base}")
                return False
                
            if not os.path.isdir(self.ruta_base):
                print(f"Error: No es un directorio - {self.ruta_base}")
                return False
                
            self.construyendo = True
            print(f"Iniciando construcción de cache para: {self.ruta_base}")
            
            # FASE 1: Contar directorios totales para el progreso
            print("Fase 1: Contando directorios totales...")
            total_dirs = 0
            
            for root, dirs, _ in os.walk(self.ruta_base, onerror=lambda e: print(f"Error accediendo: {e}")):
                if not self.construyendo:
                    print("Construcción de cache cancelada en fase de conteo")
                    return False
                total_dirs += len(dirs)
            
            print(f"Total de directorios encontrados: {total_dirs}")
            
            if total_dirs == 0:
                print("Advertencia: No se encontraron directorios para cachear")
                return False
            
            # FASE 2: Procesar directorios con progreso
            print("Fase 2: Procesando directorios...")
            cache_temp = []
            procesados = 0
            
            # Actualizar progreso inicial
            if self.callback_progreso:
                self.callback_progreso(0, total_dirs)
            
            for root, dirs, _ in os.walk(self.ruta_base, onerror=lambda e: print(f"Error accediendo: {e}")):
                if not self.construyendo:
                    print("Construcción de cache cancelada durante procesamiento")
                    return False
                    
                for dir_name in dirs:
                    try:
                        full_path = os.path.join(root, dir_name)
                        if os.path.isdir(full_path):
                            rel_path = os.path.relpath(full_path, self.ruta_base)
                            cache_temp.append((dir_name, rel_path, full_path))
                            procesados += 1
                            
                            # Actualizar progreso cada 100 directorios o al final
                            if self.callback_progreso and (procesados % 100 == 0 or procesados >= total_dirs):
                                self.callback_progreso(procesados, total_dirs)
                                print(f"Progreso construcción: {procesados}/{total_dirs} ({(procesados/total_dirs)*100:.1f}%)")
                                
                    except Exception as e:
                        print(f"Error procesando {dir_name}: {str(e)}")
                        continue
            
            # Finalizar progreso
            if self.callback_progreso:
                self.callback_progreso(total_dirs, total_dirs)
            
            if cache_temp:
                self.cache.actualizar({
                    'ruta_base': self.ruta_base,
                    'timestamp': time.time(),
                    'total': len(cache_temp),
                    'directorios': cache_temp
                })
                print(f"✓ Cache construido exitosamente con {len(cache_temp)} directorios")
                return True
                
            print("Advertencia: No se procesaron directorios para cachear")
            return False
            
        except Exception as e:
            print(f"Error crítico en construcción de cache: {str(e)}")
            return False
        finally:
            self.construyendo = False
    
    def buscar_en_cache(self, criterio):
        """Búsqueda optimizada en cache - instantánea"""
        if not self.cache.valido or not self.cache.directorios:
            print("Cache no válido o vacío - fallback a búsqueda tradicional")
            return None
            
        try:
            criterio_lower = criterio.lower()
            resultados = []
            
            # Obtener directorios del cache
            directorios_cache = self.cache.directorios.get('directorios', [])
            total_dirs = len(directorios_cache)
            
            print(f"Buscando '{criterio}' en cache con {total_dirs} directorios...")
            
            # Búsqueda optimizada
            inicio_busqueda = time.time()
            
            for nombre, ruta_rel, ruta_abs in directorios_cache:
                if criterio_lower in nombre.lower():
                    resultados.append((nombre, ruta_rel, ruta_abs))
            
            tiempo_busqueda = time.time() - inicio_busqueda
            print(f"✓ Búsqueda en cache completada en {tiempo_busqueda:.3f}s - {len(resultados)} resultados")
            
            # Retornar resultados incluso si es lista vacía (0 resultados)
            return resultados
            
        except Exception as e:
            print(f"Error en búsqueda de cache: {str(e)} - usando búsqueda tradicional")
            return None