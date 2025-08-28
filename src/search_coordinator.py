# src/search_coordinator.py - Coordinador de Búsquedas V.4.2 (Refactorizado)
import time
import threading
import os

class SearchCoordinator:
    """Coordina las búsquedas con construcción inteligente de cache"""
    
    def __init__(self, app):
        self.app = app
        self.criterio_actual = ""
        self.tiempo_inicio_busqueda = 0
        self.busqueda_silenciosa = False
        self.current_search_thread = None
        self.search_cancelled = False
    
    def ejecutar_busqueda(self, criterio, silenciosa=False):
        """Ejecuta búsqueda normal o silenciosa"""
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
        
        # Ejecutar búsqueda en thread
        self.current_search_thread = threading.Thread(
            target=self._perform_search,
            args=(criterio, silenciosa),
            daemon=True
        )
        self.current_search_thread.start()
    
    def _perform_search(self, criterio, silenciosa):
        """Realiza búsqueda en thread separado"""
        try:
            start_time = time.time()
            
            if not silenciosa:
                self.app.master.after(0, self._on_search_started, criterio)
            
            # Intentar cache primero
            resultados = []
            metodo = "Cache"
            
            if self._should_use_cache(criterio):
                resultados = self._search_from_cache(criterio)
            
            # Si cache no tiene resultados, usar búsqueda tradicional
            if not resultados:
                metodo = "Tradicional"
                
                if not self.app.search_engine.ruta_base or self.app.search_engine.ruta_base != self.app.ruta_carpeta:
                    self.app.search_engine.actualizar_ruta_base(self.app.ruta_carpeta)
                
                resultados = self._search_traditional(criterio)
            
            search_time = time.time() - start_time
            
            if not self.search_cancelled:
                # Formatear resultados para tree explorer
                if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
                    formatted_results = self._format_results_for_tree(resultados)
                else:
                    formatted_results = resultados
                
                self.app.master.after(0, self._on_search_completed, 
                                    formatted_results, criterio, metodo, search_time, silenciosa)
                
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            if not self.search_cancelled:
                self.app.master.after(0, self._on_search_error, str(e))
    
    def _should_use_cache(self, criterio):
        """Determina si debe usar cache o búsqueda tradicional"""
        try:
            cache_manager = getattr(self.app, 'cache_manager', None)
            
            if not cache_manager or not cache_manager.cache.valido:
                return False
            
            if len(cache_manager.cache.directorios.get('directorios', [])) == 0:
                return False
            
            # Búsquedas por tamaño con unidades van directo a tradicional
            if any(unit in criterio.upper() for unit in ['MB', 'GB', 'TB', 'KB']):
                return False
            
            return True
            
        except Exception as e:
            print(f"Error verificando cache: {e}")
            return False
    
    def _search_from_cache(self, criterio):
        """Realiza búsqueda desde cache"""
        resultados = self.app.cache_manager.buscar_en_cache(criterio)
        return resultados if resultados else []
    
    def _search_traditional(self, criterio):
        """Realiza búsqueda tradicional"""
        try:
            if not os.path.exists(self.app.search_engine.ruta_base):
                return []
            
            resultados = self.app.search_engine.buscar_tradicional(criterio)
            return resultados if resultados else []
            
        except Exception as e:
            print(f"Error en búsqueda tradicional: {e}")
            return []
    
    def _format_results_for_tree(self, resultados):
        """Convierte resultados al formato esperado por tree explorer"""
        if not resultados:
            return []
            
        formatted = []
        
        for resultado in resultados:
            if isinstance(resultado, tuple) and len(resultado) >= 3:
                nombre, ruta_rel, ruta_abs = resultado[:3]
                formatted_item = {
                    'name': nombre,
                    'path': ruta_abs,
                    'files': self._get_file_count_quick(ruta_abs),
                    'size': self._get_folder_size_quick(ruta_abs)
                }
            elif isinstance(resultado, dict):
                formatted_item = resultado
            else:
                path = str(resultado)
                formatted_item = {
                    'name': os.path.basename(path),
                    'path': path,
                    'files': self._get_file_count_quick(path),
                    'size': self._get_folder_size_quick(path)
                }
                    
            formatted.append(formatted_item)
            
        return formatted
    
    def _get_file_count_quick(self, path):
        """Obtiene conteo rápido de archivos"""
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return 0
            return len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        except (PermissionError, OSError):
            return 0
            
    def _get_folder_size_quick(self, path):
        """Obtiene tamaño rápido de carpeta"""
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return "0 B"
                
            total_size = 0
            count = 0
            
            for item in os.listdir(path):
                if count >= 20:
                    break
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    total_size += os.path.getsize(item_path)
                    count += 1
                    
            return self._format_size(total_size)
        except (PermissionError, OSError):
            return "N/A"
    
    def _format_size(self, size_bytes):
        """Formatea tamaño en bytes"""
        if size_bytes == 0:
            return "0 B"
            
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
            
        return f"{size_bytes:.1f} TB"
    
    def _on_search_started(self, criterio):
        """Callback cuando inicia búsqueda"""
        if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
            self.app.tree.delete(*self.app.tree.get_children())
        else:
            self.app.ui_callbacks.limpiar_resultados()
            
        self.app.ui_callbacks.actualizar_estado("Buscando...")
        self.app.btn_buscar.configure(state='disabled', text='Buscando...')
        self.app.btn_cancelar.configure(state='normal')
    
    def _on_search_completed(self, resultados, criterio, metodo, tiempo, silenciosa):
        """Callback cuando se completa búsqueda"""
        if not silenciosa:
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
        
        # Mostrar resultados
        if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
            formatted_results = self._format_results_for_tree(resultados)
            self.app.tree_explorer.populate_search_results(formatted_results)
        else:
            self.app.ui_callbacks.mostrar_resultados(resultados, metodo, tiempo)
        
        # Actualizar estado
        mensaje = f"Encontradas {len(resultados)} carpetas ({metodo}) - {tiempo:.2f}s"
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
    
    def construir_cache_automatico(self):
        """Construcción inteligente de cache automático"""
        if not self._should_build_cache_automatically():
            return
        
        if (self.app.cache_manager.construyendo or 
            (hasattr(self.app, 'search_manager') and self.app.search_manager.busqueda_activa)):
            return
        
        self.app.btn_buscar.config(state='disabled')
        self.app.ui_callbacks.actualizar_estado("Construyendo cache automáticamente... 0%")
        
        threading.Thread(target=self._ejecutar_construccion_cache_visual, daemon=True).start()
    
    def _should_build_cache_automatically(self):
        """Determina si debería construir cache automáticamente"""
        try:
            if not self.app.ruta_carpeta or not os.path.exists(self.app.ruta_carpeta):
                return False
            
            cache_manager = self.app.cache_manager
            
            if (cache_manager.cache.valido and 
                len(cache_manager.cache.directorios.get('directorios', [])) > 0):
                return False
            
            return True
            
        except Exception as e:
            print(f"Error verificando necesidad de cache: {e}")
            return False
    
    def construir_cache_manual(self):
        """Inicia construcción manual de cache"""
        if not self.app.ruta_carpeta:
            self.app.ui_callbacks.mostrar_advertencia("Seleccione una ruta primero")
            return
        
        if self.app.cache_manager.construyendo:
            self.app.ui_callbacks.actualizar_estado("Ya se está construyendo el cache")
            return
        
        self.app.btn_buscar.config(state='disabled')
        self.app.ui_callbacks.actualizar_estado("Iniciando construcción manual de cache... 0%")
        
        threading.Thread(target=self._ejecutar_construccion_cache_visual, daemon=True).start()
    
    def _ejecutar_construccion_cache_visual(self):
        """Ejecuta construcción de cache con progreso visual"""
        try:
            inicio = time.time()
            
            def callback_progreso_cache(procesados, total, mensaje=""):
                porcentaje = int(procesados) if total == 100 else int((procesados / total) * 100)
                mensaje_completo = f"{mensaje} - {porcentaje}%" if mensaje else f"Construyendo cache... {porcentaje}%"
                
                if porcentaje % 5 == 0 or porcentaje >= 95:
                    self.app.master.after(0, lambda: self.app.ui_callbacks.actualizar_estado(mensaje_completo))
            
            self.app.cache_manager.callback_progreso = callback_progreso_cache
            
            if self.app.cache_manager.construir_cache():
                tiempo_total = time.time() - inicio
                self.app.master.after(0, lambda: [
                    self.app.ui_callbacks.actualizar_estado(f"Cache construido en {tiempo_total:.1f}s"),
                    self.app.actualizar_info_carpeta()
                ])
            else:
                self.app.master.after(0, lambda: [
                    self.app.ui_callbacks.actualizar_estado("Error al construir cache")
                ])
        except Exception as e:
            self.app.master.after(0, lambda: [
                self.app.ui_callbacks.actualizar_estado(f"Error crítico: {str(e)}")
            ])
        finally:
            self.app.cache_manager.callback_progreso = None
            self.app.master.after(0, lambda: self.app.btn_buscar.config(state='normal'))
    
    def verificar_problemas_cache(self):
        """Ejecuta diagnóstico del cache"""
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
                resultado += "\n\nRecomendación: Construir cache de directorios"
            
            self.app.ui_callbacks.mostrar_info("Resultados del diagnóstico", resultado)
            
        except Exception as e:
            self.app.ui_callbacks.mostrar_error(f"Error en diagnóstico: {str(e)}")
    
    def limpiar_cache(self):
        """Limpia el cache completamente"""
        self.app.cache_manager.limpiar()
        self.app.actualizar_info_carpeta()
        self.app.ui_callbacks.actualizar_estado("Cache limpiado")
        self.app.ui_callbacks.mostrar_info("Información", "El caché ha sido limpiado correctamente")