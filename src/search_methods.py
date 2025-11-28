# src/search_methods.py - Lógica de búsqueda extraída
import os
import time
import threading
import hashlib

class SearchMethods:
    """Maneja todos los métodos de búsqueda"""
    
    def __init__(self, app):
        self.app = app
    
    def ejecutar_busqueda(self, criterio):
        """Punto de entrada principal para búsquedas"""
        self.app.ui_callbacks.limpiar_resultados()
        self.app.ui_callbacks.actualizar_estado("Buscando...")
        
        # 1. Multi-ubicaciones
        if hasattr(self.app, 'multi_location_search'):
            enabled_locations = self.app.multi_location_search.get_enabled_locations()
            if enabled_locations:
                self.app.master.after(5, lambda: self.buscar_multi_ubicaciones(criterio))
                return
        
        # 2. Cache principal
        if self._tiene_cache_valido():
            resultados = self._buscar_cache(criterio)
            if resultados:
                from .results_display import ResultsDisplay
                resultados = self._enriquecer_con_bd(resultados, criterio)
                ResultsDisplay(self.app).mostrar_instantaneos(resultados, criterio, "Cache")
                return
        
        # 3. Búsqueda tradicional
        if hasattr(self.app, 'search_coordinator'):
            self.app.search_coordinator.ejecutar_busqueda(criterio)
    
    def buscar_multi_ubicaciones(self, criterio):
        """Búsqueda asíncrona en múltiples ubicaciones"""
        def worker():
            all_results = []
            enabled_locations = self.app.multi_location_search.get_enabled_locations()
            
            for location in enabled_locations:
                try:
                    results = self._buscar_ubicacion(location, criterio)
                    for result in results:
                        if isinstance(result, tuple) and len(result) >= 3:
                            nombre, ruta_rel, ruta_abs = result[:3]
                            all_results.append((nombre, ruta_rel, ruta_abs, location['name']))
                    
                    if len(all_results) >= 100:
                        break
                except Exception as e:
                    continue
            
            all_results = self._enriquecer_con_bd(all_results, criterio)
            
            from .results_display import ResultsDisplay
            self.app.master.after(0, lambda: 
                ResultsDisplay(self.app).mostrar_multi(all_results, criterio))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _buscar_ubicacion(self, location, criterio):
        """Busca en una ubicación específica"""
        # Generar cache único
        path_hash = hashlib.md5(location['path'].encode()).hexdigest()[:8]
        cache_filename = f"cache_{path_hash}.pkl"
        
        from .cache_manager import CacheManager
        temp_cache = CacheManager(location['path'])
        temp_cache.cache_file = cache_filename
        
        # Intentar cache
        cache_loaded = temp_cache.cargar_cache()
        if cache_loaded and temp_cache.cache.valido:
            try:
                stats = temp_cache.cache.directorios
                if stats.get('total', 0) > 0:
                    results = temp_cache.buscar_en_cache(criterio)
                    if results:
                        return results[:20]
            except:
                pass
        
        # Búsqueda directa
        return self._buscar_directo(location['path'], criterio)
    
    def _buscar_directo(self, path, criterio):
        """Búsqueda directa con os.walk"""
        if not os.path.exists(path):
            return []
        
        results = []
        criterio_lower = criterio.lower()
        
        for root, dirs, files in os.walk(path):
            for dirname in dirs[:15]:
                if criterio_lower in dirname.lower():
                    ruta_completa = os.path.join(root, dirname)
                    ruta_relativa = os.path.relpath(ruta_completa, path)
                    results.append((dirname, ruta_relativa, ruta_completa))
                    
                    if len(results) >= 20:
                        break
            break  # Solo primer nivel
        
        return results
    
    def buscar_tradicional_fallback(self, criterio):
        """Búsqueda tradicional cuando multi-ubicaciones falla"""
        # 1. Intentar cache
        if self._tiene_cache_valido():
            resultados = self._buscar_cache(criterio)
            if resultados:
                from .results_display import ResultsDisplay
                resultados = self._enriquecer_con_bd(resultados, criterio)
                ResultsDisplay(self.app).mostrar_instantaneos(resultados, criterio, "Cache")
                return
        
        # 2. Búsqueda directa
        def worker():
            if not hasattr(self.app, 'ruta_carpeta') or not self.app.ruta_carpeta:
                self.app.master.after(0, lambda: [
                    self.app.ui_callbacks.actualizar_estado("No se encontraron resultados"),
                    self.app.ui_callbacks.habilitar_busqueda()
                ])
                return
            
            resultados = []
            criterio_lower = criterio.lower()
            
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
            
            from .results_display import ResultsDisplay
            self.app.master.after(0, lambda: 
                ResultsDisplay(self.app).mostrar_tradicionales(resultados, criterio))
        
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
        """Convierte formato AAAA-EXP a radicado de 23 dígitos
        
        Formato: 110013105017 + AAAA (año) + NNNNN (expediente 5 dígitos) + 00
        Ejemplo: 2025-10212 → 11001310501720251021200
        """
        import re
        # Detectar formato AAAA-EXP (año-expediente)
        match = re.match(r'(\d{4})-(\d+)$', criterio)
        if not match:
            return None
        
        año = match.group(1)  # 4 dígitos del año
        exp = match.group(2).zfill(5)  # Expediente con padding a 5 dígitos
        
        # Formato completo: prefijo (12) + año (4) + exp (5) + sufijo (2) = 23 dígitos
        radicado = f"110013105017{año}{exp}00"
        
        # Verificar que sea exactamente 23 dígitos
        return radicado if len(radicado) == 23 else None
    
    def _enriquecer_con_bd(self, resultados, criterio):
        """Enriquece resultados con datos de la base de datos"""
        if not hasattr(self.app, 'database_manager') or not self.app.database_manager:
            # Sin database manager, retornar con valores vacíos
            return [(r[0], r[1], r[2], "", "") if len(r) == 3 else 
                    (r[0], r[1], r[2], r[3], "", "") if len(r) == 4 else r 
                    for r in resultados]
        
        # Intentar convertir criterio a radicado
        radicado = self._convertir_a_radicado(criterio)
        if not radicado:
            # Si no es formato AAAA-EXP, retornar con valores vacíos
            return [(r[0], r[1], r[2], "", "") if len(r) == 3 else 
                    (r[0], r[1], r[2], r[3], "", "") if len(r) == 4 else r 
                    for r in resultados]
        
        # Consultar base de datos
        demandante, demandado = self.app.database_manager.obtener_info_proceso(radicado)
        
        # Enriquecer resultados
        # Tuplas pueden ser de 3 elementos (nombre, ruta_rel, ruta_abs) 
        # o 4 elementos (nombre, ruta_rel, ruta_abs, ubicacion) para multi-ubicación
        resultados_enriquecidos = []
        for resultado in resultados:
            if len(resultado) == 3:
                # Búsqueda cache/tradicional: (nombre, ruta_rel, ruta_abs)
                resultados_enriquecidos.append((
                    resultado[0], resultado[1], resultado[2], demandante, demandado
                ))
            elif len(resultado) == 4:
                # Búsqueda multi-ubicación: (nombre, ruta_rel, ruta_abs, ubicacion)
                resultados_enriquecidos.append((
                    resultado[0], resultado[1], resultado[2], resultado[3], demandante, demandado
                ))
            else:
                resultados_enriquecidos.append(resultado)
        
        return resultados_enriquecidos