# src/multi_location_search.py - Nuevo archivo para búsqueda en múltiples ubicaciones
import json
import os
import time
from datetime import datetime

class MultiLocationSearch:
    """Maneja búsquedas en múltiples ubicaciones"""
    
    def __init__(self, app):
        self.app = app
        self.locations = []
        self.config_file = "search_locations.json"
        self.location_caches = {}
        self.rotation_index = 0
        self._path_exists_cache = {} # Cache para no bloquear con os.path.exists
        self.load_locations()
        self._start_existence_checker()

    def _start_existence_checker(self):
        """Hilo para verificar existencia de rutas sin bloquear UI"""
        def _check():
            while True:
                for loc in self.locations:
                    path = loc.get('path')
                    if path:
                        try:
                            # Operación potencialmente lenta en red
                            self._path_exists_cache[path] = os.path.exists(path)
                        except:
                            self._path_exists_cache[path] = False
                time.sleep(30) # Solo verificar cada 30 segundos
        
        import threading
        threading.Thread(target=_check, daemon=True).start()
    
    def load_locations(self):
        """Carga ubicaciones desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    locations_data = json.load(f)
                    self.locations = locations_data
                    # Inicializar cache de existencia para evitar None
                    for loc in self.locations:
                        p = loc.get('path')
                        if p and p not in self._path_exists_cache:
                            self._path_exists_cache[p] = True # Asumir True hasta el primer check
            else:
                self.locations = []
        except Exception as e:
            print(f"Error cargando ubicaciones: {e}")
            self.locations = []
    
    def get_enabled_locations(self):
        """Obtiene ubicaciones habilitadas usando cache de existencia"""
        return [loc for loc in self.locations if loc.get('enabled', True) and self._path_exists_cache.get(loc['path'], True)]
    
    def search_in_all_locations(self, criterio):
        """Busca en todas las ubicaciones habilitadas"""
        enabled_locations = self.get_enabled_locations()
        
        # Si no hay ubicaciones configuradas, usar búsqueda tradicional
        if not enabled_locations:
            return None
        
        all_results = []
        
        for location in enabled_locations:
            try:
                # Buscar en cada ubicación
                location_results = self._search_in_location(location, criterio)
                
                # Agregar metadatos de ubicación a cada resultado
                for result in location_results:
                    if isinstance(result, tuple) and len(result) >= 3:
                        nombre, ruta_rel, ruta_abs = result[:3]
                        # Agregar nombre de ubicación como cuarto elemento
                        enhanced_result = (nombre, ruta_rel, ruta_abs, location['name'])
                        all_results.append(enhanced_result)
                
            except Exception as e:
                print(f"Error buscando en {location['name']}: {e}")
                continue
        
        return all_results
    
    def _search_in_location(self, location, criterio):
        """Busca en una ubicación específica"""
        # Crear SearchEngine temporal para esta ubicación
        from .search_engine import SearchEngine
        
        temp_engine = SearchEngine(location['path'])
        results = temp_engine.buscar_tradicional(criterio)
        
        return results[:100]  # Limitar resultados por ubicación
    
    def get_locations_summary(self):
        """Obtiene resumen de todas las ubicaciones"""
        enabled_locations = self.get_enabled_locations()
        
        return {
            'total_locations': len(self.locations),
            'active_count': len(enabled_locations),
            'total_cache_size': sum(loc.get('cache_size', 0) for loc in enabled_locations),
            'locations_names': [loc['name'] for loc in enabled_locations]
        }
    
    def get_rotation_text(self):
        """Obtiene texto rotativo de ubicaciones"""
        enabled_locations = self.get_enabled_locations()
        
        if not enabled_locations:
            return "📂 Configure ubicaciones de búsqueda"
        
        if len(enabled_locations) == 1:
            loc = enabled_locations[0]
            cache_size = loc.get('cache_size', 0)
            cache_text = f": {cache_size:,} dirs" if cache_size > 0 else ": Sin cache"
            return f"📂 {loc['name']}{cache_text}"
        
        # Rotación entre ubicaciones
        if self.rotation_index >= len(enabled_locations):
            self.rotation_index = 0
        
        current_location = enabled_locations[self.rotation_index]
        cache_size = current_location.get('cache_size', 0)
        cache_text = f": {cache_size:,} dirs" if cache_size > 0 else ": Sin cache"
        
        # Incrementar para próxima rotación
        self.rotation_index = (self.rotation_index + 1) % len(enabled_locations)
        
        return f"📂 {current_location['name']}{cache_text}"
    
    def get_tooltip_text(self):
        """Obtiene texto completo para tooltip"""
        enabled_locations = self.get_enabled_locations()
        
        if not enabled_locations:
            return "No hay ubicaciones configuradas\n\nClick para configurar ubicaciones"
        
        tooltip_lines = ["Ubicaciones de búsqueda configuradas:", ""]
        
        for loc in enabled_locations:
            status = "✓ Activa" if loc.get('enabled', True) else "○ Inactiva"
            cache_size = loc.get('cache_size', 0)
            cache_text = f" ({cache_size:,} dirs)" if cache_size > 0 else " (Sin cache)"
            
            tooltip_lines.append(f"{status} {loc['name']}{cache_text}")
            tooltip_lines.append(f"    {loc['path']}")
            tooltip_lines.append("")
        
        tooltip_lines.append("Click para configurar ubicaciones")
        tooltip_lines.append("Ctrl+U para abrir configuración")
        
        return "\n".join(tooltip_lines)
    
    def reload_locations(self):
        """Recarga ubicaciones desde archivo"""
        self.load_locations()
        self.rotation_index = 0

    def update_location_cache_size(self, path, size):
        """Actualiza el tamaño de cache para una ubicación y guarda en el JSON"""
        modified = False
        for loc in self.locations:
            if os.path.normpath(loc['path']).lower() == os.path.normpath(path).lower():
                loc['cache_size'] = size
                loc['last_scanned'] = datetime.now().strftime("%H:%M:%S")
                modified = True
        
        if modified:
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.locations, f, indent=2)
                print(f"[MULTI-SEARCH] Metadata actualizada para: {path} ({size} carpetas)")
            except Exception as e:
                print(f"[ERROR] No se pudo guardar search_locations.json: {e}")
