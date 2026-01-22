# src/results_renderer.py - Renderizador centralizado de resultados
"""
Módulo centralizado para renderizar resultados en el TreeView.
Elimina duplicación de código entre ui_callbacks.py y dynamic_column_manager.py.
"""

class ResultsRenderer:
    """Renderiza resultados de búsqueda en TreeView de forma optimizada"""
    
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
                    
                    # Extraer datos del resultado
                    if isinstance(resultado, tuple) and len(resultado) >= 3:
                        nombre, ruta_rel, ruta_abs = resultado[:3]
                    elif isinstance(resultado, dict):
                        nombre = resultado.get('name', 'Sin nombre')
                        ruta_rel = resultado.get('path', '')
                    else:
                        continue
                    
                    # Insertar en TreeView
                    app.tree.insert("", "end",
                                   text=f"📁 {nombre}",
                                   values=(letra_metodo, ruta_rel),
                                   tags=(tag,))
                
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
