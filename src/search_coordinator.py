# src/search_coordinator.py - Coordinador de Búsquedas V.4.5 - OPTIMIZADO
import time
import threading
import os

class SearchCoordinator:
    """Coordina las búsquedas sin bloquear la UI - OPTIMIZADO sin redundancias"""
    
    def __init__(self, app):
        self.app = app
        self.criterio_actual = ""
        self.tiempo_inicio_busqueda = 0
        self.busqueda_silenciosa = False
        self.current_search_thread = None
        self.search_cancelled = False
    
    def ejecutar_busqueda(self, criterio, silenciosa=False):
        """Ejecuta búsqueda completamente asíncrona"""
        if not criterio:
            if not silenciosa:
                self.app.ui_callbacks.mostrar_advertencia("Ingrese un criterio de búsqueda")
            return
        
        self.busqueda_silenciosa = silenciosa
        self.criterio_actual = criterio
        self.tiempo_inicio_busqueda = time.time()
        
        # Cancelar búsqueda anterior
        if self.current_search_thread and self.current_search_thread.is_alive():
            self.cancel_search()
            
        self.search_cancelled = False
        
        if not silenciosa:
            # Actualizar UI inmediatamente SIN bloquear
            self.app.ui_callbacks.deshabilitar_busqueda()
            self.app.ui_callbacks.limpiar_resultados()
            self.app.ui_callbacks.actualizar_estado("Iniciando búsqueda...")
        
        # TODO en background thread
        self.current_search_thread = threading.Thread(
            target=self._perform_search_async,
            args=(criterio, silenciosa),
            daemon=True
        )
        self.current_search_thread.start()
    
    def _perform_search_async(self, criterio, silenciosa):
        """Realiza búsqueda completamente en background"""
        try:
            start_time = time.time()
            
            # Actualizar UI de forma asíncrona
            if not silenciosa:
                self.app.master.after(0, lambda: self.app.ui_callbacks.actualizar_estado("Buscando..."))
            
            # 1. INTENTAR BÚSQUEDA EN MÚLTIPLES UBICACIONES PRIMERO
            multi_results = None
            metodo = "Multi"
            
            try:
                if hasattr(self.app, 'multi_location_search'):
                    # Verificar si hay ubicaciones múltiples configuradas
                    enabled_locations = self.app.multi_location_search.get_enabled_locations()
                    if enabled_locations:
                        multi_results = self._search_multi_locations_fast(criterio)
                        metodo = "Multi"
            except Exception as e:
                print(f"[DEBUG] Error en búsqueda múltiple: {e}")
                multi_results = None
            
            # 2. FALLBACK A BÚSQUEDA NORMAL SI NO HAY RESULTADOS MÚLTIPLES
            if not multi_results:
                if self._should_use_cache(criterio):
                    multi_results = self._search_from_cache(criterio)
                    metodo = "Cache"
                else:
                    multi_results = self._search_traditional(criterio)
                    metodo = "Tradicional"
            
            search_time = time.time() - start_time
            
            if not self.search_cancelled:
                # Programar actualización de UI
                self.app.master.after(0, self._on_search_completed_async, 
                                    multi_results, criterio, metodo, search_time, silenciosa)
                
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            if not self.search_cancelled:
                self.app.master.after(0, self._on_search_error, str(e))
    
    def _search_multi_locations_fast(self, criterio):
        """Búsqueda rápida en múltiples ubicaciones SIN bloquear"""
        all_results = []
        
        try:
            enabled_locations = self.app.multi_location_search.get_enabled_locations()
            
            for location in enabled_locations:
                if self.search_cancelled:
                    break
                
                # Búsqueda super rápida por ubicación (max 50ms cada una)
                location_results = self._search_single_location_fast(location, criterio)
                
                # Agregar metadatos de ubicación
                for result in location_results:
                    if isinstance(result, tuple) and len(result) >= 3:
                        nombre, ruta_rel, ruta_abs = result[:3]
                        enhanced_result = (nombre, ruta_rel, ruta_abs, location['name'])
                        all_results.append(enhanced_result)
                
                # Límite total para evitar sobrecarga
                if len(all_results) >= 200:
                    break
            
        except Exception as e:
            print(f"[DEBUG] Error en búsqueda multi-ubicaciones: {e}")
            return []
        
        return all_results
    
    def _search_single_location_fast(self, location, criterio):
        """Búsqueda ultra-rápida en una sola ubicación"""
        try:
            print(f"[DEBUG] Buscando en ubicación: {location['name']} - {location['path']}")
            
            # USAR CACHE SI EXISTE con nombre único por ubicación
            from .cache_manager import CacheManager
            import hashlib
            
            # Generar nombre único de archivo cache basado en la ruta
            path_hash = hashlib.md5(location['path'].encode()).hexdigest()[:8]
            cache_filename = f"cache_{path_hash}.pkl"
            
            # OPTIMIZACIÓN: auto_build_index=False para evitar indexación costosa en búsquedas rápidas
            temp_cache = CacheManager(location['path'], auto_build_index=False)
            temp_cache.cache_file = cache_filename
            
            # Cargar cache existente con el nombre correcto
            cache_loaded = temp_cache.cargar_cache()
            
            if cache_loaded and temp_cache.cache.valido and len(temp_cache.cache.directorios.get('directorios', [])) > 0:
                print(f"[DEBUG] Cache válido encontrado para {location['name']}: {temp_cache.cache.directorios['total']} directorios")
                # Usar búsqueda lineal rápida en lugar de Trie para evitar overhead de construcción
                results = temp_cache._linear_search(criterio, max_resultados=20)
                if results:
                    print(f"[DEBUG] Cache devolvió {len(results)} resultados para {location['name']}")
                    return results
                else:
                    print(f"[DEBUG] Cache no encontró resultados para '{criterio}' en {location['name']}")
                    return []
            else:
                print(f"[DEBUG] No hay cache válido para {location['name']} (archivo: {cache_filename})")
            
            # Si no hay cache, búsqueda directa MUY limitada
            return self._search_direct_limited(location['path'], criterio)
            
        except Exception as e:
            print(f"[DEBUG] Error buscando en {location['path']}: {e}")
            return []
    
    def _search_direct_limited(self, path, criterio):
        """Búsqueda directa super limitada para no bloquear"""
        results = []
        criterio_lower = criterio.lower()
        start_time = time.time()
        
        try:
            for root, dirs, files in os.walk(path):
                # Tiempo máximo por ubicación: 50ms
                if time.time() - start_time > 0.05:
                    break
                
                if self.search_cancelled:
                    break
                
                # Procesar solo los primeros 20 directorios por nivel
                for dirname in dirs[:20]:
                    if criterio_lower in dirname.lower():
                        ruta_completa = os.path.join(root, dirname)
                        ruta_relativa = os.path.relpath(ruta_completa, path)
                        results.append((dirname, ruta_relativa, ruta_completa))
                        
                        if len(results) >= 25:  # Max 25 resultados por ubicación
                            return results
                
                # Limitar profundidad
                depth = root.replace(path, '').count(os.sep)
                if depth >= 3:
                    dirs.clear()
                
        except (PermissionError, OSError):
            pass
        
        return results
    
    def _should_use_cache(self, criterio):
        """Determina si debe usar cache - MÁS ESTRICTO"""
        try:
            cache_manager = getattr(self.app, 'cache_manager', None)
            
            if not cache_manager or not cache_manager.cache.valido:
                return False
            
            if len(cache_manager.cache.directorios.get('directorios', [])) == 0:
                return False
            
            return True
            
        except Exception as e:
            print(f"Error verificando cache: {e}")
            return False
    
    def _search_from_cache(self, criterio):
        """Búsqueda desde cache - OPTIMIZADA"""
        try:
            resultados = self.app.cache_manager.buscar_en_cache(criterio)
            return resultados[:100] if resultados else []  # Limitar a 100 resultados
        except Exception as e:
            print(f"Error en búsqueda cache: {e}")
            return []
    
    def _search_traditional(self, criterio):
        """Búsqueda tradicional - MÁS RÁPIDA"""
        try:
            if not os.path.exists(self.app.search_engine.ruta_base):
                return []
            
            # Configurar límites más estrictos
            self.app.search_engine.busqueda_cancelada = False
            resultados = []
            criterio_lower = criterio.lower()
            start_time = time.time()
            processed = 0
            
            for root, dirs, files in os.walk(self.app.search_engine.ruta_base):
                # Tiempo máximo: 2 segundos
                if time.time() - start_time > 2.0 or self.search_cancelled:
                    break
                
                # Procesar directorios con límite
                for dirname in dirs[:30]:  # Solo primeros 30 por nivel
                    if criterio_lower in dirname.lower():
                        ruta_completa = os.path.join(root, dirname)
                        ruta_relativa = os.path.relpath(ruta_completa, self.app.search_engine.ruta_base)
                        resultados.append((dirname, ruta_relativa, ruta_completa))
                        
                        if len(resultados) >= 150:  # Max 150 resultados
                            return resultados
                
                processed += 1
                # Limitar profundidad más agresivamente
                depth = root.replace(self.app.search_engine.ruta_base, '').count(os.sep)
                if depth >= 4:
                    dirs.clear()
                
                # Cada 50 carpetas verificar cancelación
                if processed % 50 == 0 and self.search_cancelled:
                    break
            
            return resultados
            
        except Exception as e:
            print(f"Error en búsqueda tradicional: {e}")
            return []
    
    def _on_search_completed_async(self, resultados, criterio, metodo, tiempo, silenciosa):
        """Callback cuando se completa búsqueda"""
        if not silenciosa:
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
        
        # Mostrar resultados según el tipo
        if metodo == "Multi" and hasattr(self.app, 'mostrar_resultados_multi_ubicacion'):
            self.app.mostrar_resultados_multi_ubicacion(resultados, criterio)
        else:
            self.app.ui_callbacks.mostrar_resultados(resultados, metodo, tiempo)
        
        # Mensaje de estado
        mensaje = f"✅ {len(resultados)} carpetas encontradas ({metodo}) - {tiempo:.2f}s"
        self.app.ui_callbacks.actualizar_estado(mensaje)
        
        # Agregar al historial si no es silenciosa
        if not silenciosa and hasattr(self.app, 'historial_manager'):
            self.finalizar_busqueda_con_historial(metodo, len(resultados))
    
    def _on_search_error(self, error_msg):
        """Callback cuando hay error en búsqueda"""
        self.app.btn_buscar.configure(state='normal', text='Buscar')
        self.app.btn_cancelar.configure(state='disabled')
        self.app.ui_callbacks.actualizar_estado(f"Error en búsqueda: {error_msg}")
    
    def finalizar_busqueda_con_historial(self, metodo, num_resultados):
        """Finaliza búsqueda y actualiza historial"""
        if self.busqueda_silenciosa:
            return
            
        tiempo_total = time.time() - self.tiempo_inicio_busqueda
        self.app.historial_manager.agregar_busqueda(
            self.criterio_actual, 
            metodo, 
            num_resultados, 
            tiempo_total
        )
    
    def cancelar_busqueda(self):
        """Cancela búsqueda en curso"""
        self.search_cancelled = True
        
        if hasattr(self.app, 'search_manager'):
            self.app.search_manager.cancelar()
            
        if not self.busqueda_silenciosa:
            self.app.ui_callbacks.habilitar_busqueda()
    
    def cancel_search(self):
        """Alias para cancelar_busqueda"""
        return self.cancelar_busqueda()
    
    # ELIMINADOS los métodos construir_cache_automatico, construir_cache_manual, etc.
    # Estos ahora se manejan directamente en cache_manager y app.py
    
    def verificar_problemas_cache(self):
        """Ejecuta diagnóstico del cache - MÉTODO MANTENIDO para compatibilidad"""
        if not self.app.ruta_carpeta:
            self.app.ui_callbacks.mostrar_advertencia("No hay ruta seleccionada")
            return
        
        try:
            cache_stats = self.app.cache_manager.get_cache_stats()
            
            checks = [
                ("Ruta configurada", self.app.ruta_carpeta),
                ("Existe", os.path.exists(self.app.ruta_carpeta)),
                ("Es directorio", os.path.isdir(self.app.ruta_carpeta)),
                ("Permiso lectura", os.access(self.app.ruta_carpeta, os.R_OK)),
                ("Permiso escritura", os.access(self.app.ruta_carpeta, os.W_OK)),
                ("Cache válido", cache_stats['valido']),
                ("Total directorios", cache_stats['carpetas']),
                ("Edad del cache", cache_stats['edad'])
            ]
            
            resultado = "Diagnóstico completo:\n\n" + "\n".join([f"{k}: {v}" for k, v in checks])
            
            if not cache_stats['valido'] or cache_stats['carpetas'] == 0:
                resultado += "\n\nRecomendación: El caché se construirá automáticamente en la próxima búsqueda"
            
            self.app.ui_callbacks.mostrar_info("Resultados del diagnóstico", resultado)
            
        except Exception as e:
            self.app.ui_callbacks.mostrar_error(f"Error en diagnóstico: {str(e)}")
    
    def limpiar_cache(self):
        """Limpia el cache completamente - MÉTODO MANTENIDO para compatibilidad"""
        self.app.cache_manager.limpiar()
        self.app.actualizar_info_carpeta()
        self.app.ui_callbacks.actualizar_estado("Cache limpiado")
        self.app.ui_callbacks.mostrar_info("Información", "El caché ha sido limpiado correctamente")