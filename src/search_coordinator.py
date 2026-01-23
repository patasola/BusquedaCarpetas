# src/search_coordinator.py - Coordinador de Búsquedas V.4.5 - OPTIMIZADO
import time
import threading
import os

class SearchCoordinator:
    """Coordina las búsquedas sin bloquear la UI - OPTIMIZADO"""
    
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
            self.app.ui_callbacks.deshabilitar_busqueda()
            self.app.ui_callbacks.limpiar_resultados()
            self.app.ui_callbacks.actualizar_estado("Iniciando búsqueda...")
        
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
            
            if not silenciosa:
                self.app.master.after(0, lambda: self.app.ui_callbacks.actualizar_estado("Buscando..."))
            
            # 1. INTENTAR BÚSQUEDA EN MÚLTIPLES UBICACIONES PRIMERO
            multi_results = None
            metodo = "Multi"
            
            try:
                if hasattr(self.app, 'multi_location_search'):
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
                
                location_results = self._search_single_location_fast(location, criterio)
                for result in location_results:
                    if isinstance(result, tuple) and len(result) >= 3:
                        nombre, ruta_rel, ruta_abs = result[:3]
                        enhanced_result = (nombre, ruta_rel, ruta_abs, location['name'])
                        all_results.append(enhanced_result)
                
                if len(all_results) >= 1000:
                    break
        except Exception as e:
            print(f"[DEBUG] Error en búsqueda multi-ubicaciones: {e}")
        return all_results
    
    def _search_single_location_fast(self, location, criterio):
        """Búsqueda ultra-rápida en una sola ubicación"""
        try:
            from .cache_manager import CacheManager
            import hashlib
            
            path_hash = hashlib.md5(location['path'].encode()).hexdigest()[:8]
            cache_filename = f"cache_{path_hash}.pkl"
            
            # Usar el nuevo constructor optimizado
            temp_cache = CacheManager(location['path'], cache_file=cache_filename)
            
            if temp_cache.cache.valido and len(temp_cache.cache.directorios.get('directorios', [])) > 0:
                results = temp_cache.buscar_en_cache(criterio)
                return results[:1000] if results else []
            
            return self._search_direct_limited(location['path'], criterio)
        except Exception as e:
            print(f"[DEBUG] Error buscando en {location['path']}: {e}")
            return []
    
    def _search_direct_limited(self, path, criterio):
        """Búsqueda directa super limitada usando os.scandir"""
        results = []
        criterio_lower = criterio.lower()
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if self.search_cancelled:
                        break
                    if entry.is_dir() and criterio_lower in entry.name.lower():
                        results.append((entry.name, entry.name, entry.path))
                        if len(results) >= 100:
                            break
        except:
            pass
        return results
    
    def _should_use_cache(self, criterio):
        """Determina si debe usar cache"""
        try:
            cache_manager = getattr(self.app, 'cache_manager', None)
            return cache_manager and cache_manager.cache.valido and len(cache_manager.cache.directorios.get('directorios', [])) > 0
        except:
            return False
    
    def _search_from_cache(self, criterio):
        """Búsqueda desde cache"""
        try:
            resultados = self.app.cache_manager.buscar_en_cache(criterio)
            return resultados[:1000] if resultados else []
        except:
            return []
    
    def _search_traditional(self, criterio):
        """Búsqueda tradicional optimizada"""
        try:
            if not os.path.exists(self.app.ruta_carpeta):
                return []
            
            resultados = []
            criterio_lower = criterio.lower()
            start_time = time.time()
            
            for root, dirs, files in os.walk(self.app.ruta_carpeta):
                if time.time() - start_time > 2.0 or self.search_cancelled:
                    break
                
                for dirname in dirs[:30]:
                    if criterio_lower in dirname.lower():
                        ruta_completa = os.path.join(root, dirname)
                        ruta_relativa = os.path.relpath(ruta_completa, self.app.ruta_carpeta)
                        resultados.append((dirname, ruta_relativa, ruta_completa))
                        if len(resultados) >= 500:
                            return resultados
                
                depth = root.replace(self.app.ruta_carpeta, '').count(os.sep)
                if depth >= 4:
                    dirs.clear()
            return resultados
        except:
            return []
    
    def _on_search_completed_async(self, resultados, criterio, metodo, tiempo, silenciosa):
        """Callback cuando se completa búsqueda"""
        if not silenciosa:
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
        
        if metodo == "Multi" and hasattr(self.app, 'results_display'):
            self.app.results_display.mostrar_multi(resultados, criterio)
        else:
            self.app.ui_callbacks.mostrar_resultados(resultados, metodo, tiempo)
        
        mensaje = f"✅ {len(resultados)} carpetas encontradas ({metodo}) - {tiempo:.2f}s"
        self.app.ui_callbacks.actualizar_estado(mensaje)
        
        if not silenciosa and hasattr(self.app, 'historial_manager'):
            self.finalizar_busqueda_con_historial(metodo, len(resultados))
    
    def _on_search_error(self, error_msg):
        self.app.btn_buscar.configure(state='normal', text='Buscar')
        self.app.btn_cancelar.configure(state='disabled')
        self.app.ui_callbacks.actualizar_estado(f"Error en búsqueda: {error_msg}")
    
    def finalizar_busqueda_con_historial(self, metodo, num_resultados):
        if self.busqueda_silenciosa:
            return
        tiempo_total = time.time() - self.tiempo_inicio_busqueda
        self.app.historial_manager.agregar_busqueda(self.criterio_actual, metodo, num_resultados, tiempo_total)
    
    def cancelar_busqueda(self):
        self.search_cancelled = True
        if not self.busqueda_silenciosa:
            self.app.ui_callbacks.habilitar_busqueda()
    
    def cancel_search(self):
        return self.cancelar_busqueda()
    
    def limpiar_cache(self):
        self.app.cache_manager.limpiar()
        self.app.ui_callbacks.actualizar_estado("Cache limpiado")

    def construir_cache_automatico(self):
        """Wrapper para compatibilidad"""
        import threading
        threading.Thread(target=self.app.cache_manager.construir_cache, daemon=True).start()

    def construir_cache_manual(self):
        """Wrapper para compatibilidad"""
        return self.construir_cache_automatico()

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