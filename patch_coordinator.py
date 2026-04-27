import os

target_path = r'd:\OneDrive - Elkin\OneDrive - Consejo Superior de la Judicatura\Abrir archivos\BusquedaCarpetas4.5\BusquedaCarpetas4.5\src\managers\search_coordinator.py'

new_code = """

    def pre_cargar_ubicaciones_adicionales(self):
        \"\"\"Inicia carga paralela de caches para ubicaciones externas durante el arranque\"\"\"
        if not hasattr(self.app, 'multi_location_search'):
            return
            
        enabled_locations = self.app.multi_location_search.get_enabled_locations()
        if not enabled_locations:
            return
            
        print(f"[INIT] Lanzando precarga paralela para {len(enabled_locations)} ubicaciones...")
        import threading
        for loc in enabled_locations:
            path = loc['path']
            # Evitar recargar la principal si ya se está cargando por otro hilo
            if hasattr(self.app, 'ruta_carpeta') and path == self.app.ruta_carpeta:
                continue
                
            thread = threading.Thread(
                target=self._solo_cargar_una_ubicacion,
                args=(loc,),
                daemon=True,
                name=f"Loader-{loc['name']}"
            )
            thread.start()

    def _solo_cargar_una_ubicacion(self, loc):
        \"\"\"Worker individual para cargar caché de una ubicación sin bloquear\"\"\"
        try:
            path = loc['path']
            if path not in self._multi_cache_managers:
                from ..core.cache_manager import CacheManager
                cache_file = self._get_cache_filename(path)
                mgr = CacheManager(path, cache_file)
                self._multi_cache_managers[path] = mgr
                
                # Cargar el archivo .pkl en memoria
                mgr.cargar_cache()
                if mgr.cache.valido:
                    stats = mgr.get_cache_stats()
                    print(f"[MULTI-CACHE] '{loc['name']}' cargado: {stats.get('carpetas', 0)} registros.")
        except Exception as e:
            print(f"[ERROR] Falló precarga de {loc.get('name')}: {e}")
"""

with open(target_path, 'a', encoding='utf-8') as f:
    f.write(new_code)
print("Parche aplicado con éxito.")
