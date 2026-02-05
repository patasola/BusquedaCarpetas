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
        self.current_search_id = 0 # ID único para cada sesión de búsqueda
        self._multi_cache_managers = {} # Persistencia en memoria de caches por ruta
    
    def _get_cache_filename(self, path):
        """Genera un nombre de archivo de caché consistente basado en el hash de la ruta"""
        import hashlib
        path_norm = os.path.normpath(path).lower()
        path_hash = hashlib.md5(path_norm.encode()).hexdigest()[:8]
        return f"cache_{path_hash}.pkl"
    
    def ejecutar_busqueda(self, criterio, silenciosa=False):
        """Ejecuta búsqueda completamente asíncrona"""
        if not criterio:
            if not silenciosa:
                self.app.ui_manager.mostrar_advertencia("Ingrese un criterio de búsqueda")
            return
        
        self.busqueda_silenciosa = silenciosa
        self.criterio_actual = criterio
        self.tiempo_inicio_busqueda = time.time()
        
        # Cancelar búsqueda anterior e incrementar ID
        self.search_cancelled = True
        self.current_search_id += 1
        my_search_id = self.current_search_id
            
        self.search_cancelled = False
        
        # Limpiar resultados siempre para evitar acumulación (Feedback del usuario)
        self.app.ui_manager.limpiar_resultados()
        
        if not silenciosa:
            self.app.ui_manager.deshabilitar_busqueda()
            self.app.ui_manager.actualizar_estado("Iniciando búsqueda...")
        
        self.current_search_thread = threading.Thread(
            target=self._perform_search_async,
            args=(criterio, silenciosa, my_search_id),
            daemon=True
        )
        self.current_search_thread.start()
    
    def _perform_search_async(self, criterio, silenciosa, search_id):
        """Realiza búsqueda asíncrona optimizada con paralelismo total"""
        try:
            # Verificar si esta búsqueda sigue siendo la actual
            if search_id != self.current_search_id: return
            
            # Limpiar UI antes de empezar el streaming (Siempre para evitar acumulación)
            self.app.master.after(0, self.app.ui_manager.limpiar_resultados)
            start_time = time.time()
            if not silenciosa:
                self.app.master.after(0, lambda: self.app.ui_manager.actualizar_estado("Buscando..."))
            
            # 1. REUNIR TODAS LAS UBICACIONES A BUSCAR
            locations_to_search = []
            
            # Ubicaciones adicionales
            if hasattr(self.app, 'multi_location_search'):
                locations_to_search.extend(self.app.multi_location_search.get_enabled_locations())
            
            # Carpeta principal
            if hasattr(self.app, 'ruta_carpeta') and self.app.ruta_carpeta:
                principal_path = os.path.normpath(self.app.ruta_carpeta).lower()
                ya_incluida = any(os.path.normpath(l['path']).lower() == principal_path for l in locations_to_search)
                if not ya_incluida:
                    locations_to_search.append({'name': 'Principal', 'path': self.app.ruta_carpeta, 'enabled': True})
            
            if not locations_to_search:
                self.app.master.after(0, self._on_search_error, "No hay carpetas configuradas para buscar")
                return

            # --- FASE 1: BÚSQUEDA INSTANTÁNEA EN CACHÉ ---
            seen_paths = set()
            total_resultados_contados = 0
            
            for loc in locations_to_search:
                if self.search_cancelled or search_id != self.current_search_id: return
                
                # Obtener solo de caché (muy rápido)
                path = loc['path']
                cache_filename = self._get_cache_filename(path)
                
                # Reutilizar o crear manager temporal
                mgr = self._multi_cache_managers.get(path)
                if not mgr:
                    mgr = CacheManager(path, cache_file=cache_filename)
                
                if mgr.cache.valido:
                    resultados_cache = mgr.buscar_en_cache(criterio)
                    if resultados_cache:
                        batch_cache = []
                        for r in resultados_cache:
                            p_key = os.path.normpath(r[2]).lower()
                            if p_key not in seen_paths:
                                seen_paths.add(p_key)
                                batch_cache.append((r[0], r[1], r[2], r[3], loc['name']))
                        
                        if batch_cache:
                            total_resultados_contados += len(batch_cache)
                            enriched = self._enriquecer_resultados_con_bd(batch_cache, criterio)
                            self.app.master.after(0, self._append_results_batch, 
                                                enriched, criterio, loc['name'], start_time, silenciosa, search_id)

            # --- FASE 2: BÚSQUEDA COMPLEMENTARIA EN DISCO (PARALELA) ---
            from concurrent.futures import ThreadPoolExecutor, as_completed
            max_workers = min(len(locations_to_search), 10)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Solo buscar en disco (depth 1 o 5) para lo que no está en caché o carpetas nuevas
                future_to_loc = {
                    executor.submit(self._search_complementary_disk_only, loc, criterio): loc 
                    for loc in locations_to_search
                }
                
                num_completados = 0
                for future in as_completed(future_to_loc):
                    if self.search_cancelled or search_id != self.current_search_id: break
                    num_completados += 1
                    loc = future_to_loc[future]
                    try:
                        loc_results = future.result()
                        if not loc_results: continue
                        
                        # Filtrar duplicados GLOBALMENTE (vs lo que ya se mostró del caché)
                        batch_to_show = []
                        for r in loc_results:
                            if self.search_cancelled or search_id != self.current_search_id: break
                            path_key = os.path.normpath(r[2]).lower()
                            if path_key not in seen_paths:
                                seen_paths.add(path_key)
                                batch_to_show.append((r[0], r[1], r[2], r[3], loc['name']))
                        
                        if batch_to_show and not self.search_cancelled and search_id == self.current_search_id:
                            total_resultados_contados += len(batch_to_show)
                            enriched_batch = self._enriquecer_resultados_con_bd(batch_to_show, criterio)
                            self.app.master.after(0, self._append_results_batch, 
                                                enriched_batch, criterio, loc['name'], start_time, silenciosa, search_id)
                        
                        # Callback final si es la última ubicación
                        if num_completados == len(locations_to_search) and not self.search_cancelled and search_id == self.current_search_id:
                            search_time = time.time() - start_time
                            self.app.master.after(100, self._on_search_completed_async, 
                                               total_resultados_contados, criterio, "Streaming", search_time, silenciosa, search_id)
                                                
                    except Exception as e:
                        print(f"[ERROR] Ubicación {loc['name']} falló: {e}")

        except Exception as e:
            print(f"Error crítico en búsqueda: {e}")
            if not self.search_cancelled:
                self.app.master.after(0, self._on_search_error, str(e))
    
    def _append_results_batch(self, resultados, criterio, loc_name, start_time, silenciosa, search_id):
        """Añade un lote de resultados a la UI sin limpiar los anteriores"""
        if self.search_cancelled or search_id != self.current_search_id: return
        tiempo_parcial = time.time() - start_time
        if hasattr(self.app, 'ui_manager'):
            self.app.ui_manager.mostrar_resultados_incrementales(resultados, loc_name, tiempo_parcial)
            self.app.ui_manager.actualizar_estado(f"Streaming... {loc_name} listo ({len(resultados)} encontrados)")
    
    def _search_complementary_disk_only(self, loc, criterio):
        """Busca solo en disco para complementar lo que falte en el caché"""
        try:
            path = loc['path']
            mgr = self._multi_cache_managers.get(path)
            
            # Profundidad: 1 si hay caché (solo carpetas nuevas), 5 si no hay caché
            depth_fallback = 1 if (mgr and mgr.cache.valido) else 5
            return self._search_direct_recursive(path, criterio, max_depth=depth_fallback)
        except Exception as e:
            print(f"[ERROR] Complementary disk search failed for {loc['name']}: {e}")
            return []

    def _search_single_location_unified(self, location, criterio):
        """Mantenemos por retrocompatibilidad pero preferimos usar la lógica de fases en _perform_search_async"""
        return self._search_complementary_disk_only(location, criterio)
    
    def _search_direct_recursive(self, path, criterio, max_depth=3):
        """Búsqueda directa usando BFS con scandir (Más rápido que os.walk)"""
        results = []
        criterio_lower = criterio.lower()
        
        # BFS para control preciso de profundidad y velocidad
        queue = [(path, 0)]
        
        try:
            while queue:
                if self.search_cancelled or len(results) >= 1000:
                    break
                    
                curr_path, depth = queue.pop(0)
                if depth > max_depth:
                    continue
                
                try:
                    with os.scandir(curr_path) as it:
                        for entry in it:
                            if self.search_cancelled: break
                            if not entry.is_dir(): continue
                            
                            if criterio_lower in entry.name.lower():
                                # Unificación de formato. 
                                # OPTIMIZACIÓN: En búsqueda directa, asumimos True para hijos por velocidad.
                                # El explorador/expansión lo verificará al hacer clic.
                                # Esto evita miles de hits extra a disco.
                                try:
                                    ruta_rel = os.path.relpath(entry.path, path)
                                except:
                                    ruta_rel = entry.name
                                    
                                results.append((entry.name, ruta_rel, entry.path, True))
                            
                            # Añadir a la cola para profundizar
                            if depth < max_depth:
                                queue.append((entry.path, depth + 1))
                except (PermissionError, OSError):
                    continue
                            
        except Exception as e:
            print(f"[DEBUG] Error en escaneo directo para {path}: {e}")
            
        return results

    def _enriquecer_resultados_con_bd(self, resultados, criterio):
        """Añade info de Demandante/Demandado si existe el DatabaseManager"""
        if not hasattr(self.app, 'database_manager') or not self.app.database_manager:
            return resultados
            
        # Intentar convertir criterio a radicado
        radicado = self._convertir_a_radicado(criterio)
        if not radicado:
            return resultados
            
        demandante, demandado = self.app.database_manager.obtener_info_proceso(radicado)
        if not demandante and not demandado:
            return resultados
            
        enriquecidos = []
        for r in resultados:
            # r puede ser:
            # (nombre, rel, abs, tiene_hijos) -> len 4
            # (nombre, rel, abs, tiene_hijos, loc) -> len 5
            
            base = list(r)
            # Asegurar que tiene al menos loc_name (índice 4)
            if len(base) == 4:
                base.append("") # loc_name vacío
            
            # Agregar demandante/demandado
            base.extend([demandante, demandado])
            enriquecidos.append(tuple(base))
        return enriquecidos

    def _tiene_hijos_rapido(self, path):
        """Verifica si una carpeta tiene subcarpetas de forma muy rápida"""
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_dir():
                        return True
            return False
        except:
            return False

    def _convertir_a_radicado(self, criterio):
        """Helper para extraer radicado de 23 dígitos"""
        import re
        # Formato AAAA-XXXXX -> 23 dígitos
        match = re.match(r'(\d{4})-(\d+)$', criterio)
        if match:
            año = match.group(1)
            exp = match.group(2).zfill(5)
            return f"110013105017{año}{exp}00"
        return None
    
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
            
            # Búsqueda en dos fases para velocidad instantánea
            # Fase 1: Niveles superficiales (0-2)
            for root, dirs, files in os.walk(self.app.ruta_carpeta):
                if time.time() - start_time > 1.5 or self.search_cancelled: break
                
                depth = root.replace(self.app.ruta_carpeta, '').count(os.sep)
                if depth > 2:
                    continue # Dejar niveles profundos para la fase 2 si sobra tiempo
                
                for dirname in dirs:
                    if criterio_lower in dirname.lower():
                        ruta_completa = os.path.join(root, dirname)
                        ruta_relativa = os.path.relpath(ruta_completa, self.app.ruta_carpeta)
                        # Detección precisa
                        tiene_hijos = self._tiene_hijos_rapido(ruta_completa)
                        resultados.append((dirname, ruta_relativa, ruta_completa, tiene_hijos))
                        if len(resultados) >= 500: return resultados

            # Fase 2: Niveles profundos (si queda tiempo)
            if not self.search_cancelled and time.time() - start_time < 0.8:
                for root, dirs, files in os.walk(self.app.ruta_carpeta):
                    if time.time() - start_time > 2.0 or self.search_cancelled: break
                    
                    depth = root.replace(self.app.ruta_carpeta, '').count(os.sep)
                    if depth <= 2: continue # Ya cubiertos
                    if depth > 5: 
                        dirs.clear()
                        continue
                        
                    for dirname in dirs:
                        if criterio_lower in dirname.lower():
                            ruta_completa = os.path.join(root, dirname)
                            ruta_relativa = os.path.relpath(ruta_completa, self.app.ruta_carpeta)
                            tiene_hijos = self._tiene_hijos_rapido(ruta_completa)
                            resultados.append((dirname, ruta_relativa, ruta_completa, tiene_hijos))
                            if len(resultados) >= 500: return resultados
            return resultados
        except:
            return []
    
    def _on_search_completed_async(self, resultados_o_conteo, criterio, metodo, tiempo, silenciosa, search_id):
        """Callback cuando se completa búsqueda"""
        if self.search_cancelled or search_id != self.current_search_id: return
        
        # Obtener número total de resultados
        if isinstance(resultados_o_conteo, list):
            num_resultados = len(resultados_o_conteo)
        else:
            num_resultados = resultados_o_conteo

        if not silenciosa:
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
        
        # SI ES MODO STREAMING, actualización de estado y registro en historial
        if metodo == "Streaming":
             mensaje = f"✅ Búsqueda finalizada ({metodo}) - {num_resultados} resultados - {tiempo:.2f}s"
             self.app.ui_manager.actualizar_estado(mensaje)
             
             # REGISTRAR SIEMPRE EN HISTORIAL
             if hasattr(self.app, 'historial_manager'):
                 self.app.historial_manager.agregar_busqueda(criterio, "Híbrida", num_resultados, tiempo)
             return
             
        if metodo == "Multi" and hasattr(self.app, 'results_display'):
            self.app.results_display.mostrar_multi(resultados, criterio)
        else:
            self.app.ui_manager.mostrar_resultados(resultados, metodo, tiempo)
        
        mensaje = f"✅ {len(resultados)} carpetas encontradas ({metodo}) - {tiempo:.2f}s"
        self.app.ui_manager.actualizar_estado(mensaje)
        
        if not silenciosa and hasattr(self.app, 'historial_manager'):
            self.finalizar_busqueda_con_historial(metodo, len(resultados))
    
    def _on_search_error(self, error_msg):
        self.app.btn_buscar.configure(state='normal', text='Buscar')
        self.app.btn_cancelar.configure(state='disabled')
        self.app.ui_manager.actualizar_estado(f"Error en búsqueda: {error_msg}")
    
    def finalizar_busqueda_con_historial(self, metodo, num_resultados):
        if self.busqueda_silenciosa:
            return
        tiempo_total = time.time() - self.tiempo_inicio_busqueda
        self.app.historial_manager.agregar_busqueda(self.criterio_actual, metodo, num_resultados, tiempo_total)
    
    def cancelar_busqueda(self):
        self.search_cancelled = True
        if not self.busqueda_silenciosa:
            self.app.ui_manager.habilitar_busqueda()
    
    def cancel_search(self):
        return self.cancelar_busqueda()
    
    def limpiar_cache(self):
        self.app.cache_manager.limpiar()
        self.app.ui_manager.actualizar_estado("Cache limpiado")

    def construir_cache_automatico(self):
        """Wrapper para compatibilidad"""
        import threading
        threading.Thread(target=self.app.cache_manager.construir_cache, daemon=True).start()

    def construir_cache_manual(self):
        """Wrapper para compatibilidad"""
        return self.construir_cache_automatico()

    def verificar_problemas_cache(self):
        """Verifica y limpia problemas comunes del caché, incluyendo 'mugre' (obsoletos)"""
        try:
            from tkinter import messagebox
            
            # 1. Obtener lista de archivos activos
            archivos_activos = []
            
            # Cache principal
            if hasattr(self.app, 'cache_manager'):
                archivos_activos.append(self.app.cache_manager.cache_file)
            
            # Caches de ubicaciones adicionales
            if hasattr(self.app, 'multi_location_search'):
                for loc in self.app.multi_location_search.get_enabled_locations():
                    import hashlib
                    path_hash = hashlib.md5(loc['path'].encode()).hexdigest()[:8]
                    archivos_activos.append(f"cache_{path_hash}.pkl")
            
            # 2. Ejecutar limpieza
            num_eliminados = 0
            if hasattr(self.app, 'cache_manager'):
                num_eliminados = self.app.cache_manager.limpiar_obsoletos(archivos_activos)
            
            # 3. Notificar
            if num_eliminados > 0:
                messagebox.showinfo("Limpieza de Caché", 
                    f"Se han eliminado {num_eliminados} archivos de caché obsoletos ('mugre').\n\n"
                    f"El sistema ahora está optimizado.")
            else:
                messagebox.showinfo("Verificación", 
                    "No se encontraron archivos de caché obsoletos.\n"
                    "El sistema de archivos está limpio.")
                    
        except Exception as e:
            print(f"[SEARCH_COORD] Error en verificación: {e}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error verificando caché: {e}")
            
    def verificar_problemas_cache_silencioso(self):
        """Versión silenciosa para limpieza automática en background"""
        try:
            archivos_activos = []
            if hasattr(self.app, 'cache_manager'):
                archivos_activos.append(self.app.cache_manager.cache_file)
            if hasattr(self.app, 'multi_location_search'):
                for loc in self.app.multi_location_search.get_enabled_locations():
                    archivos_activos.append(self._get_cache_filename(loc['path']))
            
            if hasattr(self.app, 'cache_manager'):
                self.app.cache_manager.limpiar_obsoletos(archivos_activos)
        except:
            pass # Silencioso, no queremos interrumpir al usuario si falla
        # FINALIZAR AQUÍ la versión silenciosa para que no siga al diagnóstico
        return

    def _ejecutar_diagnostico_completo(self):
        """Muestra el informe detallado de diagnóstico (Ventana)"""
        try:
            cache_stats = self.app.cache_manager.get_cache_stats()
            # 1. Diagnóstico de Carpeta Principal
            cache_stats = self.app.cache_manager.get_cache_stats()
            
            checks = [
                ("--- CARPETA PRINCIPAL ---", ""),
                ("Ruta", self.app.ruta_carpeta),
                ("Existe", "SÍ" if os.path.exists(self.app.ruta_carpeta) else "NO"),
                ("Caché válido", "SÍ" if cache_stats['valido'] else "NO"),
                ("Total carpetas", f"{cache_stats['carpetas']:,}"),
                ("Edad caché", cache_stats['edad']),
                ("", "")
            ]
            
            # 2. Diagnóstico de Ubicaciones Adicionales
            if hasattr(self.app, 'multi_location_search'):
                enabled = self.app.multi_location_search.get_enabled_locations()
                if enabled:
                    checks.append(("--- UBICACIONES ADICIONALES ---", ""))
                    for loc in enabled:
                        path_norm = os.path.normpath(loc['path'])
                        # Buscar en los managers persistentes
                        mgr = self._multi_cache_managers.get(path_norm)
                        
                        if mgr:
                            s = mgr.get_cache_stats()
                            status = "LISTO" if s['valido'] else ("CONSTRUYENDO..." if mgr.construyendo else "PENDIENTE")
                            checks.append((f"[{loc['name']}] Estado", status))
                            checks.append((f"[{loc['name']}] Carpetas", f"{s['carpetas']:,}"))
                        else:
                            # Intentar cargar localmente para el reporte si no se ha usado aún
                            c_file = self._get_cache_filename(path_norm)
                            if os.path.exists(c_file):
                                checks.append((f"[{loc['name']}]", "Caché en disco (Pendiente de carga)"))
                            else:
                                checks.append((f"[{loc['name']}]", "Sin caché (Se creará al buscar)"))
                        checks.append(("", ""))
            
            resultado = "Informe de Diagnóstico de Sistemas:\n\n" + "\n".join([f"{k}: {v}" if v != "" else k for k, v in checks])
            
            if not cache_stats['valido']:
                resultado += "\nNota: El caché principal se está construyendo en segundo plano o requiere una búsqueda inicial."
            
            self.app.ui_manager.mostrar_info("Diagnóstico de Cache", resultado)
            
        except Exception as e:
            self.app.ui_manager.mostrar_error(f"Error en diagnóstico: {str(e)}")

    def verificar_problemas_cache(self):
        """Versión MANUAL (con ventana) - Limpia y diagnostica"""
        try:
            # 1. Limpieza activa
            archivos_activos = []
            if hasattr(self.app, 'cache_manager'):
                archivos_activos.append(self.app.cache_manager.cache_file)
            if hasattr(self.app, 'multi_location_search'):
                for loc in self.app.multi_location_search.get_enabled_locations():
                    archivos_activos.append(self._get_cache_filename(loc['path']))
            
            if hasattr(self.app, 'cache_manager'):
                self.app.cache_manager.limpiar_obsoletos(archivos_activos)
            
            # 2. Ejecutar diagnóstico visual
            self._ejecutar_diagnostico_completo()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error en verificación: {e}")