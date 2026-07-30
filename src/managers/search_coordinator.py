# src/search_coordinator.py - Coordinador de Búsquedas V.4.5 - OPTIMIZADO
import time
import threading
import os
from ..core.cache_manager import CacheManager

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
    
    def ejecutar_busqueda(self, criterio, silenciosa=False, incluir_contenido=False):
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
        
        if not silenciosa:
            self.app.ui_manager.deshabilitar_busqueda()
            self.app.ui_manager.actualizar_estado("Iniciando búsqueda...")
        
        self.current_search_thread = threading.Thread(
            target=self._perform_search_async,
            args=(criterio, silenciosa, my_search_id, incluir_contenido),
            daemon=True
        )
        self.current_search_thread.start()
    
    def _perform_search_async(self, criterio, silenciosa, search_id, incluir_contenido=False):
        """Búsqueda por STREAMING: Muestra resultados instantáneos y sigue buscando en el fondo"""
        try:
            if search_id != self.current_search_id: return
            
            # 1. PREPARACIÓN E INICIO
            self.app.master.after(0, self.app.ui_manager.limpiar_resultados)
            start_time = time.time()
            
            # Forzar inclusión si el checkbox global está encendido
            if hasattr(self.app, 'incluir_archivos') and self.app.incluir_archivos.get():
                incluir_contenido = True

            # --- FASE 1: CACHÉ (INSTANTÁNEO) ---
            if not silenciosa:
                self.app.master.after(0, lambda: self.app.ui_manager.actualizar_estado("Consultando memoria rápida..."))
            
            resultados_cache_totales = []
            
            # A. Caché Principal
            if hasattr(self.app, 'cache_manager') and self.app.cache_manager.cache.valido:
                res_p = self.app.cache_manager.buscar_en_cache(criterio)
                for r in res_p:
                    # (nombre, rel, abs, hijos, origin, d1, d2)
                    resultados_cache_totales.append((r[0], r[1], r[2], r[3], "Caché-Principal", "", ""))

            # B. Cachés Adicionales
            if hasattr(self.app, 'multi_location_search'):
                for loc in self.app.multi_location_search.get_enabled_locations():
                    path = loc['path']
                    if path not in self._multi_cache_managers:
                        from ..core.cache_manager import CacheManager
                        self._multi_cache_managers[path] = CacheManager(path, self._get_cache_filename(path))
                    
                    mgr = self._multi_cache_managers[path]
                    if mgr.cache.valido:
                        for r in mgr.buscar_en_cache(criterio):
                            resultados_cache_totales.append((r[0], r[1], r[2], r[3], loc['name'], "", ""))

            # MOSTRAR CACHÉ INMEDIATAMENTE
            if resultados_cache_totales:
                self.app.master.after(0, lambda: self.app.ui_manager.mostrar_resultados_incrementales(
                    resultados_cache_totales, "C", time.time() - start_time
                ))
            
            if self.search_cancelled or search_id != self.current_search_id: return

            # --- FASE 2: BÚSQUEDA NITRO (Siempre activa para nombres/rutas) ---
            if not hasattr(self.app, 'content_indexer'):
                from ..core.content_indexer import ContentIndexer
                self.app.content_indexer = ContentIndexer(self.app)
            try:
                # Buscamos siempre en el índice por nombres de carpeta y archivo
                res_nitro = self.app.content_indexer.search(criterio, search_field="path")
                if res_nitro:
                    res_ui_nitro = []
                    stale_paths = []
                    for r in res_nitro:
                        ruta = r.get('abs_path', r.get('path', ''))
                        if os.path.exists(ruta):
                            # Identificar si es una carpeta (icono expandible)
                            es_carpeta = r.get('is_folder', False)
                            res_ui_nitro.append((r['name'], r['path'], r['abs_path'], es_carpeta, "Nitro", "", ""))
                        else:
                            stale_paths.append(ruta)
                    
                    if res_ui_nitro:
                        self.app.master.after(0, lambda: self.app.ui_manager.mostrar_resultados_incrementales(
                            res_ui_nitro, "N", time.time() - start_time
                        ))
                        
                    # Purgar obsoletos si los hay
                    if stale_paths and hasattr(self, '_cleanup_stale_nitro'):
                        threading.Thread(target=self._cleanup_stale_nitro, args=(stale_paths,), daemon=True).start()
            except Exception as e:
                print(f"[SEARCH COORDINATOR] Error en Fase Nitro: {e}")

            # --- FASE 3: BÚSQUEDA DE CONTENIDO (Solo si se marca la casilla) ---
            if incluir_contenido:
                try:
                    res_cont = self.app.content_indexer.search(criterio, search_field="content")
                    if res_cont:
                        res_ui_cont = []
                        for r in res_cont:
                            # Los resultados de contenido puro no suelen ser carpetas
                            res_ui_cont.append((r['name'], r['path'], r['abs_path'], False, "Contenido", "", ""))
                        
                        self.app.master.after(0, lambda: self.app.ui_manager.mostrar_resultados_incrementales(
                            res_ui_cont, "C", time.time() - start_time
                        ))
                except Exception as e:
                    print(f"[SEARCH COORDINATOR] Error en Fase Contenido: {e}")

            if self.search_cancelled or search_id != self.current_search_id: return

            # --- FASE 3: DISCO (COMPLEMENTARIO) ---
            # Si después de caché y contenido no hay mucho, o si el usuario quiere profundidad, buscamos en disco
            # Pero sobre todo, buscamos en disco las ubicaciones ADICIONALES para asegurar que no falte nada.
            
            if not silenciosa:
                self.app.master.after(0, lambda: self.app.ui_manager.actualizar_estado("Buscando duplicados en fondo..."))
            
            # A. Disco Principal
            if hasattr(self.app, 'search_engine') and self.app.search_engine:
                res_disco_p = self.app.search_engine.buscar_tradicional(criterio)
                if res_disco_p:
                    res_ui_p = [(r[0], r[1], r[2], True, "Principal", "", "") for r in res_disco_p]
                    self.app.master.after(0, lambda: self.app.ui_manager.mostrar_resultados_incrementales(
                        res_ui_p, "D", time.time() - start_time
                    ))

            # B. Disco Adicionales (donde no hay caché o es necesaria búsqueda profunda)
            if hasattr(self.app, 'multi_location_search'):
                for loc in self.app.multi_location_search.get_enabled_locations():
                    if self.search_cancelled or search_id != self.current_search_id: break
                    
                    # Para ubicaciones adicionales, siempre hacemos un barrido de disco si se solicita
                    # o si no hay caché cargada para esa ubicación
                    mgr = self._multi_cache_managers.get(loc['path'])
                    if not mgr or not mgr.cache.valido:
                        res_disco_m = self.app.multi_location_search._search_in_location(loc, criterio)
                        if res_disco_m:
                            res_ui_m = [(r[0], r[1], r[2], True, loc['name'], "", "") for r in res_disco_m]
                            self.app.master.after(0, lambda: self.app.ui_manager.mostrar_resultados_incrementales(
                                res_ui_m, "D", time.time() - start_time
                            ))

            # --- FINALIZACIÓN ---
            tiempo_total = time.time() - start_time
            self.app.master.after(0, self.app.ui_manager.habilitar_busqueda)
            
            # Enriquecimiento final de metadatos (el que ya teníamos funcionando)
            # Como usamos mostrar_resultados_incrementales, los items ya están en el árbol con iid=ruta_abs
            # No necesitamos pasar todos los resultados, el worker buscará radicado del criterio
            self._trigger_background_enrichment([], criterio, search_id)
            
            if not silenciosa:
                self.app.master.after(0, lambda: self.app.ui_manager.actualizar_estado(
                    f"✅ Búsqueda completa ({tiempo_total:.2f}s)"
                ))

            self.app.master.after(0, self.app.ui_manager.habilitar_busqueda)
            
        except Exception as e:
            print(f"[ERROR] Búsqueda falló: {e}")
            self.app.master.after(0, lambda: self.app.ui_manager.actualizar_estado(f"Error: {str(e)}"))
            self.app.master.after(0, self.app.ui_manager.habilitar_busqueda)

    def _trigger_background_enrichment(self, resultados, criterio, search_id):
        """Inicia el enriquecimiento de metadatos en segundo plano asociado a un ID de búsqueda"""
        import threading
        threading.Thread(target=self._enrich_worker, args=(resultados, criterio, search_id), daemon=True).start()

    def _enrich_worker(self, resultados, criterio, search_id):
        """Worker que consulta BD y actualiza UI por cada resultado"""
        try:
            if search_id != self.current_search_id: return
            
            if not hasattr(self.app, 'database_manager') or not self.app.database_manager:
                return
            
            # Esperar un momento para que la UI se pueble en búsquedas instantáneas
            import time
            time.sleep(1.0)
            
            # Recolectar nombres de carpeta actuales del TreeView en el hilo principal
            items_to_check = []
            def _get_items():
                if hasattr(self.app, 'tree'):
                    for item_id in self.app.tree.get_children():
                        text = str(self.app.tree.item(item_id, 'text'))
                        items_to_check.append((item_id, text))
            
            self.app.master.after(0, _get_items)
            
            # Dar tiempo a que main thread llene la lista
            time.sleep(0.5)
            
            if not items_to_check: return
            
            # Extraer radicados únicos
            radicados_a_consultar = {} # radicado: [item_ids]
            
            for item_id, text in items_to_check:
                rad = self._convertir_a_radicado(text)
                if rad:
                    if rad not in radicados_a_consultar:
                        radicados_a_consultar[rad] = []
                    radicados_a_consultar[rad].append(item_id)
            
            # Consultar BD en bloque (Batch) para velocidad máxima
            resultados_batch = self.app.database_manager.obtener_info_procesos_batch(list(radicados_a_consultar.keys()))
            
            # Actualizar UI agrupando por radicado
            for radicado, item_ids in radicados_a_consultar.items():
                if search_id != self.current_search_id: return
                
                if radicado in resultados_batch:
                    demandante, demandado = resultados_batch[radicado]
                    if demandante or demandado:
                        self.app.master.after(0, lambda ids=item_ids, d1=demandante, d2=demandado: 
                            self.app.ui_manager.actualizar_metadata_por_ids(ids, d1, d2))
                        
            # Si el criterio en sí mismo era un radicado, actualizar historial
            rad_criterio = self._convertir_a_radicado(criterio)
            if rad_criterio:
                if rad_criterio in resultados_batch:
                    dem1, dem2 = resultados_batch[rad_criterio]
                else:
                    dem1, dem2 = self.app.database_manager.obtener_info_proceso(rad_criterio)
                    
                if hasattr(self.app, 'historial_manager') and self.app.historial_manager and (dem1 or dem2):
                     self.app.master.after(0, lambda d1=dem1, d2=dem2: 
                        self.app.historial_manager.actualizar_ultima_busqueda(d1, d2))

        except Exception as e:
            print(f"[BG ENRICH] Error: {e}")

    def _cleanup_stale_nitro(self, stale_paths):
        """Elimina del índice los resultados Nitro que ya no existen en disco"""
        if not stale_paths or not hasattr(self.app, 'content_indexer'): return
        try:
            import sqlite3
            db_path = self.app.content_indexer.db_path
            with self.app.content_indexer.db_lock:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                for p in stale_paths:
                    cursor.execute("DELETE FROM file_metadata WHERE path = ?", (p,))
                    cursor.execute("DELETE FROM content_fts WHERE path = ?", (p,))
                conn.commit()
                conn.close()
            print(f"[SEARCH COORDINATOR] Purgados {len(stale_paths)} resultados fantasma Nitro de forma diferida.")
        except Exception as e:
            print(f"[SEARCH COORDINATOR] Error limpiando resultados fantasma diferidos: {e}")

    
    def _append_results_batch(self, resultados, criterio, loc_name, start_time, silenciosa, search_id):
        """Añade un lote de resultados a la UI sin limpiar los anteriores"""
        if self.search_cancelled or search_id != self.current_search_id: return
        tiempo_parcial = time.time() - start_time
        if hasattr(self.app, 'ui_manager'):
            self.app.ui_manager.mostrar_resultados_incrementales(resultados, loc_name, tiempo_parcial)
            self.app.ui_manager.actualizar_estado(f"Streaming... {loc_name} listo ({len(resultados)} encontrados)")
    
    def _convertir_a_radicado(self, texto):
        """Helper para extraer radicado de 23 dígitos de cualquier texto"""
        if not texto: return None
        import re
        
        # 1. Buscar si hay exactamente 23 dígitos seguidos (o que al limpiar lo sean)
        digitos = ''.join(filter(str.isdigit, texto))
        if len(digitos) >= 23:
            match_23 = re.search(r'\b(\d{23})\b', texto)
            if match_23: return match_23.group(1)
            
        # 2. Buscar formato AAAA-XXXXX en cualquier parte del texto
        match = re.search(r'\b(\d{4})-(\d{1,5})\b', texto)
        if match:
            año = match.group(1)
            exp = match.group(2).zfill(5)
            return f"110013105017{año}{exp}00"
            
        return None
    
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

    def pre_cargar_ubicaciones_adicionales(self):
        """Inicia carga paralela de caches para ubicaciones externas durante el arranque"""
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
        """Worker individual para cargar caché de una ubicación sin bloquear"""
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
