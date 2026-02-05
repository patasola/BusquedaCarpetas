# src/search_methods.py - Lógica de búsqueda extraída
import os
import time
import threading
import hashlib

class SearchMethods:
    """Maneja todos los métodos de búsqueda"""
    
    def __init__(self, app):
        self.app = app
    
    def ejecutar_busqueda(self, criterio, silenciosa=False):
        """Punto de entrada principal para búsquedas - DELEGADO A COORDINATOR"""
        if hasattr(self.app, 'search_coordinator'):
            self.app.search_coordinator.ejecutar_busqueda(criterio, silenciosa=silenciosa)
        else:
            # Fallback de seguridad si no hay coordinator
            self.buscar_tradicional_fallback(criterio)
    
    def buscar_multi_ubicaciones(self, criterio):
        """Redirige a SearchCoordinator para consistencia"""
        if hasattr(self.app, 'search_coordinator'):
            self.app.search_coordinator.ejecutar_busqueda(criterio)
        else:
            # Fallback si no está inicializado
            self.buscar_tradicional_fallback(criterio)
    
    def _buscar_ubicacion(self, location, criterio):
        """Busca en una ubicación específica"""
        # Generar cache único
        path_hash = hashlib.md5(location['path'].encode()).hexdigest()[:8]
        cache_filename = f"cache_{path_hash}.pkl"
        
        from ..core.cache_manager import CacheManager
        # Usar el constructor que acepta cache_file
        temp_cache = CacheManager(location['path'], cache_file=cache_filename)
        
        # Intentar cache
        cache_loaded = temp_cache.cargar_cache()
        if cache_loaded and temp_cache.cache.valido:
            try:
                stats = temp_cache.cache.directorios
                if stats.get('total', 0) > 0:
                    results = temp_cache.buscar_en_cache(criterio)
                    # SIEMPRE retornar resultados del cache si existe y es válido
                    return results if results else []
            except:
                pass
        
        # Búsqueda directa (Solo si no hay cache o falló)
        return self._buscar_directo(location['path'], criterio)
    
    def _buscar_directo(self, path, criterio):
        """Búsqueda directa con os.walk (limitada a primer nivel para velocidad)"""
        if not os.path.exists(path):
            return []
        
        results = []
        criterio_lower = criterio.lower()
        
        try:
            # Usar os.scandir para mayor velocidad en el primer nivel
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_dir() and criterio_lower in entry.name.lower():
                        results.append((entry.name, entry.name, entry.path))
                        if len(results) >= 100:
                            break
        except Exception as e:
            print(f"[ERROR] Error en búsqueda directa: {e}")
            
        return results
    
    def buscar_tradicional_fallback(self, criterio):
        """Búsqueda tradicional cuando multi-ubicaciones falla"""
        # 1. Intentar cache
        if self._tiene_cache_valido():
            resultados = self._buscar_cache(criterio)
            if resultados:
                from ..ui.results_display import ResultsDisplay
                resultados = self._enriquecer_con_bd(resultados, criterio)
                ResultsDisplay(self.app).mostrar_instantaneos(resultados, criterio, "Cache")
                
                # Registrar en historial
                if hasattr(self.app, 'historial_manager'):
                    self.app.historial_manager.agregar_busqueda(criterio, "Cache", len(resultados), 0.01)
                return
        
        # 2. Búsqueda directa
        def worker():
            start_time = time.time()
            if not hasattr(self.app, 'ruta_carpeta') or not self.app.ruta_carpeta:
                self.app.master.after(0, lambda: [
                    self.app.ui_manager.actualizar_estado("No se encontraron resultados"),
                    self.app.ui_manager.habilitar_busqueda()
                ])
                return
            
            resultados = []
            criterio_lower = criterio.lower()
            
            # Búsqueda profunda (os.walk) - Solo como último recurso
            for root, dirs, files in os.walk(self.app.ruta_carpeta):
                for dirname in dirs:
                    if criterio_lower in dirname.lower():
                        ruta_completa = os.path.join(root, dirname)
                        ruta_relativa = os.path.relpath(ruta_completa, self.app.ruta_carpeta)
                        resultados.append((dirname, ruta_relativa, ruta_completa))
                        
                        if len(resultados) >= 100:
                            break
                
                if len(resultados) >= 100:
                    break
            
            resultados = self._enriquecer_con_bd(resultados, criterio)
            
            print(f"[PROFILE] Fin búsqueda (encontrados {len(resultados)}): {time.time()}")
            from ..ui.results_display import ResultsDisplay
            self.app.master.after(0, lambda: 
                ResultsDisplay(self.app).mostrar_tradicionales(resultados, criterio))
            
            # Registrar en historial
            if hasattr(self.app, 'historial_manager'):
                tiempo_total = time.time() - start_time
                self.app.master.after(0, lambda: 
                    self.app.historial_manager.agregar_busqueda(criterio, "Tradicional", len(resultados), tiempo_total))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _tiene_cache_valido(self):
        """Verifica cache válido"""
        try:
            return (hasattr(self.app, 'cache_manager') and 
                    self.app.cache_manager.cache.valido and 
                    len(self.app.cache_manager.cache.directorios.get('directorios', [])) > 0)
        except:
            return False
    
    def _buscar_cache(self, criterio):
        """Búsqueda en cache"""
        try:
            resultados = self.app.cache_manager.buscar_en_cache(criterio)
            return resultados[:50] if resultados else []
        except:
            return []

    def _convertir_a_radicado(self, criterio):
        """Convierte formato AAAA-EXP a radicado de 23 dígitos"""
        import re
        match = re.match(r'(\d{4})-(\d+)$', criterio)
        if not match:
            return None
        
        año = match.group(1)
        exp = match.group(2).zfill(5)
        radicado = f"110013105017{año}{exp}00"
        return radicado if len(radicado) == 23 else None
    
    def _enriquecer_con_bd(self, resultados, criterio):
        """Enriquece resultados con datos de la base de datos"""
        if not hasattr(self.app, 'database_manager') or not self.app.database_manager:
            return [(r[0], r[1], r[2], "", "") if len(r) == 3 else 
                    (r[0], r[1], r[2], r[3], "", "") if len(r) == 4 else r 
                    for r in resultados]
        
        radicado = self._convertir_a_radicado(criterio)
        if not radicado:
            return [(r[0], r[1], r[2], "", "") if len(r) == 3 else 
                    (r[0], r[1], r[2], r[3], "", "") if len(r) == 4 else r 
                    for r in resultados]
        
        # Consultar base de datos
        demandante, demandado = self.app.database_manager.obtener_info_proceso(radicado)
        
        resultados_enriquecidos = []
        for resultado in resultados:
            if len(resultado) == 3:
                resultados_enriquecidos.append((
                    resultado[0], resultado[1], resultado[2], demandante, demandado
                ))
            elif len(resultado) == 4:
                resultados_enriquecidos.append((
                    resultado[0], resultado[1], resultado[2], resultado[3], demandante, demandado
                ))
            else:
                resultados_enriquecidos.append(resultado)
        
        return resultados_enriquecidos