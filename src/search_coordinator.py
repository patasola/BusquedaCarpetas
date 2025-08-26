# src/search_coordinator.py - Coordinador de Búsquedas V.4.1 (Búsqueda Tradicional Corregida)
import time
import threading
import os

class SearchCoordinator:
    """Coordina las búsquedas con soporte V.4.0 + Tree Explorer V.4.1"""
    
    def __init__(self, app):
        self.app = app
        self.criterio_actual = ""
        self.tiempo_inicio_busqueda = 0
        self.busqueda_silenciosa = False
        
        # V.4.1 - Threading
        self.current_search_thread = None
        self.search_cancelled = False
    
    # ===== MÉTODOS V.4.0 (ESPAÑOL) - COMPATIBILIDAD =====
    
    def ejecutar_busqueda(self, criterio, silenciosa=False):
        """Ejecuta una búsqueda normal o silenciosa (V.4.0 + V.4.1)"""
        if not criterio:
            if not silenciosa:
                self.app.ui_callbacks.mostrar_advertencia("Ingrese un criterio de búsqueda")
            return
        
        # DEBUG para historial
        print(f"🔍 EJECUTAR_BUSQUEDA: criterio='{criterio}', silenciosa={silenciosa}")
        
        self.busqueda_silenciosa = silenciosa
        self.criterio_actual = criterio
        self.tiempo_inicio_busqueda = time.time()
        
        # V.4.1 - Cancelar búsqueda anterior si existe
        if self.current_search_thread and self.current_search_thread.is_alive():
            self.cancel_search()
            
        self.search_cancelled = False
        
        if not silenciosa:
            self.app.ui_callbacks.deshabilitar_busqueda()
        
        # V.4.1 - Threading para búsqueda
        self.current_search_thread = threading.Thread(
            target=self._perform_search_v41,
            args=(criterio, silenciosa),
            daemon=True
        )
        self.current_search_thread.start()
    
    def finalizar_busqueda_con_historial(self, metodo, num_resultados):
        """Finaliza búsqueda y agrega entrada al historial (V.4.0)"""
        if self.busqueda_silenciosa:
            return  # No agregar búsquedas silenciosas al historial
            
        tiempo_total = time.time() - self.tiempo_inicio_busqueda
        
        # Agregar al historial
        self.app.historial_manager.agregar_busqueda(
            self.criterio_actual, 
            metodo, 
            num_resultados, 
            tiempo_total
        )
    
    def cancelar_busqueda(self):
        """Cancela la búsqueda en curso (V.4.0)"""
        self.search_cancelled = True
        
        if hasattr(self.app, 'search_manager'):
            self.app.search_manager.cancelar()
            
        if not self.busqueda_silenciosa:
            self.app.ui_callbacks.habilitar_busqueda()
    
    def construir_cache_automatico(self):
        """Inicia construcción automática de cache (V.4.0)"""
        if (not self.app.ruta_carpeta or 
            self.app.cache_manager.construyendo or 
            (hasattr(self.app, 'search_manager') and self.app.search_manager.busqueda_activa)):
            return
        
        self.app.btn_buscar.config(state='disabled')
        self.app.ui_callbacks.actualizar_estado("Construyendo cache de directorios... 0%")
        
        threading.Thread(
            target=self._ejecutar_construccion_cache,
            daemon=True
        ).start()
    
    def construir_cache_manual(self):
        """Inicia construcción manual de cache (V.4.0)"""
        if not self.app.ruta_carpeta:
            self.app.ui_callbacks.mostrar_advertencia("Seleccione una ruta primero")
            return
        
        if self.app.cache_manager.construyendo:
            self.app.ui_callbacks.actualizar_estado("Ya se está construyendo el cache")
            return
        
        self.app.btn_buscar.config(state='disabled')
        self.app.ui_callbacks.actualizar_estado("Iniciando construcción manual de cache... 0%")
        
        threading.Thread(
            target=self._ejecutar_construccion_cache,
            daemon=True
        ).start()
    
    def verificar_problemas_cache(self):
        """Ejecuta diagnóstico del cache (V.4.0)"""
        if not self.app.ruta_carpeta:
            self.app.ui_callbacks.mostrar_advertencia("No hay ruta seleccionada")
            return
        
        try:
            checks = [
                ("Ruta configurada", self.app.ruta_carpeta),
                ("Existe", os.path.exists(self.app.ruta_carpeta)),
                ("Es directorio", os.path.isdir(self.app.ruta_carpeta)),
                ("Permiso lectura", os.access(self.app.ruta_carpeta, os.R_OK)),
                ("Permiso escritura", os.access(self.app.ruta_carpeta, os.W_OK)),
                ("Permiso ejecución", os.access(self.app.ruta_carpeta, os.X_OK)),
                ("Ruta absoluta", os.path.abspath(self.app.ruta_carpeta)),
                ("Cache válido", self.app.cache_manager.cache.valido),
                ("Total directorios", len(self.app.cache_manager.cache.directorios.get('directorios', [])) 
                 if self.app.cache_manager.cache.valido else 0)
            ]
            
            resultado = "Diagnóstico completo:\n\n" + \
                       "\n".join([f"{k}: {v}" for k, v in checks])
            
            self.app.ui_callbacks.mostrar_info("Resultados del diagnóstico", resultado)
            
        except Exception as e:
            self.app.ui_callbacks.mostrar_error(f"Error en diagnóstico: {str(e)}")
    
    def limpiar_cache(self):
        """Limpia el cache completamente (V.4.0)"""
        self.app.cache_manager.limpiar()
        self.app.actualizar_info_carpeta()
        self.app.ui_callbacks.actualizar_estado("Cache limpiado")
        self.app.ui_callbacks.mostrar_info("Información", "El caché ha sido limpiado correctamente")
    
    # ===== MÉTODOS V.4.1 (INGLÉS) - COMPATIBILIDAD =====
    
    def execute_search(self, criterio, silenciosa=False):
        """Alias en inglés para ejecutar_busqueda (V.4.1)"""
        return self.ejecutar_busqueda(criterio, silenciosa)
    
    def cancel_search(self):
        """Alias en inglés para cancelar_busqueda (V.4.1)"""
        return self.cancelar_busqueda()
    
    def get_search_status(self):
        """Obtiene el estado actual de la búsqueda (V.4.1)"""
        if self.current_search_thread and self.current_search_thread.is_alive():
            return "searching"
        elif self.search_cancelled:
            return "cancelled"
        else:
            return "idle"
    
    def cleanup(self):
        """Limpia recursos del coordinador (V.4.1)"""
        self.cancel_search()
        if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
            self.app.tree_explorer.clear_temp_cache()
    
    # ===== MÉTODOS INTERNOS CORREGIDOS =====
    
    def _perform_search_v41(self, criterio, silenciosa):
        """Realiza la búsqueda en thread separado (V.4.1) - CORREGIDO"""
        try:
            print(f"🔍 _PERFORM_SEARCH_V41: criterio='{criterio}', silenciosa={silenciosa}")
            
            start_time = time.time()
            
            # Actualizar UI - inicio de búsqueda (solo si no es silenciosa)
            if not silenciosa:
                self.app.master.after(0, self._on_search_started, criterio)
            
            # PASO 1: Intentar cache primero
            resultados = []
            metodo = "Cache"
            
            if self._should_use_cache(criterio):
                print(f"🔍 Intentando búsqueda en cache...")
                resultados = self._search_from_cache(criterio)
                print(f"🔍 Cache devolvió {len(resultados) if resultados else 0} resultados")
            else:
                print(f"🔍 Cache no disponible o criterio excluido, usando búsqueda tradicional directamente")
            
            # PASO 2: Si cache no tiene resultados O no está disponible, usar búsqueda tradicional
            if not resultados or resultados is None:
                print(f"🔍 Ejecutando búsqueda tradicional...")
                metodo = "Tradicional"
                
                # CORREGIDO: Asegurar que search_engine tenga la ruta correcta
                if not self.app.search_engine.ruta_base or self.app.search_engine.ruta_base != self.app.ruta_carpeta:
                    self.app.search_engine.actualizar_ruta_base(self.app.ruta_carpeta)
                    print(f"🔍 Actualizada ruta base en search_engine: {self.app.ruta_carpeta}")
                
                # Ejecutar búsqueda tradicional
                resultados = self._search_traditional(criterio)
                print(f"🔍 Búsqueda tradicional devolvió {len(resultados) if resultados else 0} resultados")
                
            end_time = time.time()
            search_time = end_time - start_time
            
            print(f"🔍 Búsqueda completada: {len(resultados) if resultados else 0} resultados en {search_time:.2f}s usando {metodo}")
            
            if not self.search_cancelled:
                # Formatear resultados para tree explorer si está disponible
                if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
                    print(f"🔍 Formateando resultados para tree explorer...")
                    formatted_results = self._format_results_for_tree(resultados)
                    print(f"🔍 Resultados formateados: {len(formatted_results)}")
                else:
                    print(f"🔍 Tree explorer no disponible, usando resultados originales")
                    formatted_results = resultados
                
                # Actualizar UI - búsqueda completada
                self.app.master.after(0, self._on_search_completed, 
                                    formatted_results, criterio, metodo, search_time, silenciosa)
                
        except Exception as e:
            print(f"🔍 ERROR en _perform_search_v41: {e}")
            import traceback
            traceback.print_exc()
            if not self.search_cancelled:
                self.app.master.after(0, self._on_search_error, str(e))
    
    def _should_use_cache(self, criterio):
        """Determina si debe usar cache o búsqueda tradicional - MEJORADO"""
        try:
            cache_manager = getattr(self.app, 'cache_manager', None)
            
            if not cache_manager:
                print("🔍 No hay cache_manager disponible")
                return False
            
            if not hasattr(cache_manager, 'cache') or not cache_manager.cache.valido:
                print("🔍 Cache no válido o no disponible")
                return False
            
            # Búsquedas por tamaño con unidades van directo a tradicional
            if any(unit in criterio.upper() for unit in ['MB', 'GB', 'TB', 'KB']):
                print("🔍 Criterio con unidades de tamaño, usando búsqueda tradicional")
                return False
            
            print("🔍 Cache disponible y criterio válido para cache")
            return True
            
        except Exception as e:
            print(f"⚠️ Error verificando cache: {e}")
            return False
    
    def _search_from_cache(self, criterio):
        """Realiza búsqueda desde cache"""
        resultados = self.app.cache_manager.buscar_en_cache(criterio)
        
        # Si cache no tiene resultados, devolver lista vacía para intentar búsqueda tradicional
        if not resultados:
            return []
            
        return resultados
    
    def _search_traditional(self, criterio):
        """Realiza búsqueda tradicional - CORREGIDO"""
        try:
            print(f"🔍 _SEARCH_TRADITIONAL: Iniciando búsqueda para '{criterio}'")
            print(f"🔍 Ruta base configurada: {self.app.search_engine.ruta_base}")
            print(f"🔍 Ruta carpeta app: {self.app.ruta_carpeta}")
            
            # Verificar que el search_engine esté correctamente configurado
            if not self.app.search_engine.ruta_base and self.app.ruta_carpeta:
                self.app.search_engine.actualizar_ruta_base(self.app.ruta_carpeta)
                print(f"🔍 Ruta base actualizada a: {self.app.search_engine.ruta_base}")
            
            # Verificar que la ruta existe
            if not os.path.exists(self.app.search_engine.ruta_base):
                print(f"❌ La ruta base no existe: {self.app.search_engine.ruta_base}")
                return []
            
            # Ejecutar búsqueda tradicional
            resultados = self.app.search_engine.buscar_tradicional(criterio)
            print(f"🔍 Búsqueda tradicional retornó: {len(resultados) if resultados else 0} resultados")
            
            return resultados if resultados else []
            
        except Exception as e:
            print(f"❌ Error en búsqueda tradicional: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _format_results_for_tree(self, resultados):
        """Convierte resultados al formato esperado por tree explorer"""
        if not resultados:
            return []
            
        formatted = []
        
        print(f"🔍 Formateando {len(resultados)} resultados para tree explorer")
        
        for resultado in resultados:
            if isinstance(resultado, tuple) and len(resultado) >= 3:
                # Formato V.4.0: (nombre, ruta_rel, ruta_abs)
                nombre, ruta_rel, ruta_abs = resultado[:3]
                print(f"🔍 Resultado V.4.0: {nombre} -> {ruta_abs}")
                formatted_item = {
                    'name': nombre,
                    'path': ruta_abs,
                    'files': self._get_file_count_quick(ruta_abs),
                    'size': self._get_folder_size_quick(ruta_abs)
                }
            elif isinstance(resultado, dict):
                # Ya está en formato correcto
                print(f"🔍 Resultado V.4.1: {resultado.get('name', 'Sin nombre')}")
                formatted_item = resultado
            else:
                # Formato desconocido
                path = str(resultado)
                print(f"🔍 Resultado desconocido: {path}")
                formatted_item = {
                    'name': os.path.basename(path),
                    'path': path,
                    'files': self._get_file_count_quick(path),
                    'size': self._get_folder_size_quick(path)
                }
                    
            formatted.append(formatted_item)
            
        print(f"🔍 Formateados {len(formatted)} resultados para tree explorer")
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
                if count >= 20:  # Límite para velocidad
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
        """Callback cuando inicia la búsqueda"""
        print(f"🔍 _ON_SEARCH_STARTED: criterio='{criterio}'")
        
        # Limpiar resultados anteriores
        if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
            print(f"🔍 Limpiando tree con tree_explorer")
            self.app.tree.delete(*self.app.tree.get_children())
        else:
            print(f"🔍 Limpiando tree con ui_callbacks")
            self.app.ui_callbacks.limpiar_resultados()
            
        # Actualizar UI
        self.app.ui_callbacks.actualizar_estado("🔍 Buscando...")
        self.app.btn_buscar.configure(state='disabled', text='Buscando...')
        self.app.btn_cancelar.configure(state='normal')
    
    def _on_search_completed(self, resultados, criterio, metodo, tiempo, silenciosa):
        """Callback cuando se completa la búsqueda"""
        # Restaurar UI solo si no es silenciosa
        if not silenciosa:
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
        
        # DEBUG: Mostrar información de la búsqueda
        print(f"🔍 Búsqueda completada: {len(resultados)} resultados, silenciosa: {silenciosa}")
        print(f"🔍 Tree explorer disponible: {hasattr(self.app, 'tree_explorer') and self.app.tree_explorer}")
        
        # CORREGIDO: Siempre usar tree_explorer si está disponible
        if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
            print("🔍 Usando tree_explorer para mostrar resultados")
            # Asegurar que el formato es correcto para tree_explorer
            formatted_results = self._format_results_for_tree(resultados)
            self.app.tree_explorer.populate_search_results(formatted_results)
        else:
            print("🔍 Usando ui_callbacks como fallback")
            # Usar ui_callbacks como fallback
            self.app.ui_callbacks.mostrar_resultados(resultados, metodo, tiempo)
            
        # Actualizar mensaje de estado
        mensaje = f"✅ {len(resultados)} carpetas encontradas ({metodo}) - {tiempo:.2f}s"
        self.app.ui_callbacks.actualizar_estado(mensaje)
        
        # Agregar al historial si no es silenciosa
        if not silenciosa and hasattr(self.app, 'historial_manager'):
            self.finalizar_busqueda_con_historial(metodo, len(resultados))
    
    def _on_search_error(self, error_msg):
        """Callback cuando hay error en la búsqueda"""
        # Restaurar UI
        self.app.btn_buscar.configure(state='normal', text='Buscar')
        self.app.btn_cancelar.configure(state='disabled')
        
        # Mostrar error
        self.app.ui_callbacks.actualizar_estado(f"❌ Error en búsqueda: {error_msg}")
    
    def _ejecutar_construccion_cache(self):
        """Ejecuta la construcción de cache en thread separado (V.4.0) - CORREGIDO"""
        try:
            inicio = time.time()
            
            def callback_progreso_cache(procesados, total, mensaje=""):
                """Callback de progreso mejorado con mensaje opcional"""
                porcentaje = int(procesados) if total == 100 else int((procesados / total) * 100)
                
                # Crear mensaje de estado completo
                if mensaje:
                    mensaje_completo = f"{mensaje} - {porcentaje}%"
                else:
                    mensaje_completo = f"Construyendo cache de directorios... {porcentaje}%"
                
                # Actualizar en el hilo principal
                self.app.master.after(0, lambda: self.app.ui_callbacks.actualizar_estado(mensaje_completo))
            
            # Asignar callback mejorado
            self.app.cache_manager.callback_progreso = callback_progreso_cache
            
            # Iniciar construcción
            if self.app.cache_manager.construir_cache():
                tiempo_total = time.time() - inicio
                self.app.master.after(0, lambda: [
                    self.app.ui_callbacks.actualizar_estado(f"✅ Cache construido en {tiempo_total:.1f}s"),
                    self.app.actualizar_info_carpeta()
                ])
            else:
                self.app.master.after(0, lambda: [
                    self.app.ui_callbacks.actualizar_estado("❌ Error al construir cache")
                ])
        except Exception as e:
            self.app.master.after(0, lambda: [
                self.app.ui_callbacks.actualizar_estado(f"❌ Error crítico: {str(e)}")
            ])
        finally:
            self.app.cache_manager.callback_progreso = None
            self.app.master.after(0, lambda: self.app.btn_buscar.config(state='normal'))