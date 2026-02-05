# src/results_renderer.py - Renderizador centralizado de resultados
"""
Módulo centralizado para renderizar resultados en el TreeView.
Elimina duplicación de código entre ui_callbacks.py y dynamic_column_manager.py.
"""

class ResultsRenderer:
    """Renderiza resultados de búsqueda en TreeView de forma optimizada"""
    
    @staticmethod
    def _tiene_subcarpetas_rapido(ruta):
        """Verificación ultra-rápida de subcarpetas usando os.scandir
        Solo busca el PRIMER subdirectorio, no escanea toda la carpeta"""
        import os as _os
        try:
            with _os.scandir(ruta) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        return True
            return False
        except (PermissionError, OSError, FileNotFoundError):
            return False
    
    @staticmethod
    def render_results(app, resultados, metodo, tiempo_total, actualizar_estado_callback=None):
        """
        Renderiza resultados en TreeView con batch processing optimizado.
        
        Args:
            app: Instancia de la aplicación con acceso al TreeView
            resultados: Lista de resultados a mostrar
            metodo: Método de búsqueda utilizado
            tiempo_total: Tiempo que tomó la búsqueda
            actualizar_estado_callback: Función opcional para actualizar status bar
        
        Returns:
            bool: True si se renderizó exitosamente, False en caso de error
        """
        import time as _time
        from datetime import datetime as _datetime
        _t0 = _time.perf_counter()
        current_time = _datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{current_time}] [RESULTS_RENDERER] Iniciando render de {len(resultados) if resultados else 0} resultados")
        
        if not resultados:
            print(f"[{current_time}] [RESULTS_RENDERER] Sin resultados")
            if actualizar_estado_callback:
                actualizar_estado_callback(
                    f"No se encontraron resultados ({metodo}, {tiempo_total:.3f}s)"
                )
            return False
        
        try:
            # Determinar configuración según método de búsqueda
            letra_metodo = metodo[0].upper() if metodo else 'C'
            
            # OPTIMIZACIÓN: Batch processing para evitar lag en UI
            batch_size = 500
            total = len(resultados)
            
            for batch_start in range(0, total, batch_size):
                batch_end = min(batch_start + batch_size, total)
                batch = resultados[batch_start:batch_end]
                
                # Insertar batch en TreeView
                for i, resultado in enumerate(batch, start=batch_start):
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    
                    # Extraer datos del resultado unificado: (nom, rel, abs, hijos, loc, dem1, dem2)
                    if isinstance(resultado, tuple) and len(resultado) >= 3:
                        nombre, ruta_rel, ruta_abs = resultado[:3]
                        # En formato unificado: index 3 = hijos, index 4 = loc_name
                        tiene_hijos = resultado[3] if len(resultado) >= 4 else False
                        
                        # Si hay un nombre de ubicación (index 4), usarlo en vez de la letra del método
                        metodo_display = letra_metodo
                        if len(resultado) >= 5 and resultado[4]:
                            metodo_display = resultado[4]
                        
                        # Info de base de datos (si existe)
                        extra_values = []
                        if len(resultado) >= 7:
                            extra_values = [resultado[5], resultado[6]]
                    elif isinstance(resultado, dict):
                        nombre = resultado.get('name', 'Sin nombre')
                        ruta_rel = resultado.get('path', '')
                        ruta_abs = resultado.get('abs_path', ruta_rel)
                        tiene_hijos = resultado.get('has_children', False)
                        metodo_display = letra_metodo
                        extra_values = []
                    else:
                        continue
                    
                    # Insertar en TreeView: 
                    # values[0]=Método/Loc, values[1]=RutaRel, values[2]=MetadataAbs, ...
                    tree_values = [metodo_display, ruta_rel, ruta_abs] + extra_values
                    
                    item_id = app.tree.insert("", "end",
                                   text=f"📂 {nombre}",
                                   values=tuple(tree_values),
                                   tags=(tag,))
                    
                    # RECUPERAR INFO DE HIJOS PRE-CALCULADA
                    if tiene_hijos:
                        # Insertar dummy con la misma cantidad de columnas para evitar errores de índice
                        dummy_values = [""] * len(tree_values)
                        app.tree.insert(item_id, "end", text="Cargando...", values=tuple(dummy_values))
                
                # Actualizar UI solo cada batch (no cada item)
                if batch_end < total:
                    if actualizar_estado_callback:
                        actualizar_estado_callback(f"Cargando {batch_end}/{total}...")
                    app.tree.update_idletasks()
            
            # Actualización final
            # NOTA: NO llamamos _ajustar_columnas porque recorre TODOS los items (muy lento)
            # Las columnas se ajustan automáticamente con el contenido
            if actualizar_estado_callback:
                actualizar_estado_callback(
                    f"✅ {len(resultados):,} resultados en {tiempo_total:.3f}s ({metodo})"
                )
            
            # Configurar scrollbars si está disponible
            if callable(getattr(app, 'configurar_scrollbars', None)):
                app.configurar_scrollbars()
            
            _t1 = _time.perf_counter()
            current_time_end = _datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{current_time_end}] [RESULTS_RENDERER] Render completado en {(_t1-_t0)*1000:.2f} ms")
            return True
            
        except Exception as e:
            if actualizar_estado_callback:
                actualizar_estado_callback(f"Error mostrando resultados: {str(e)}")
            return False
