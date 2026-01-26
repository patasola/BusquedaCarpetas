# src/results_display.py - Visualización OPTIMIZADA para 1-20 resultados típicos
import tkinter as tk
import os

class ResultsDisplay:
    """Maneja la visualización de resultados en el TreeView"""
    
    def __init__(self, app):
        self.app = app
    
    def mostrar_instantaneos(self, resultados, criterio, metodo):
        """Muestra resultados instantáneos"""
        try:
            self._agregar_resultados(resultados, metodo)
            self.app.ui_callbacks.actualizar_estado(f"✅ {len(resultados)} resultados ({metodo})")
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
            
            if hasattr(self.app, 'historial_manager'):
                self.app.master.after(50, lambda: self.app.historial_manager.agregar_busqueda(
                    criterio, metodo, len(resultados), 0.05))
            
            # Actualizar scrollbars
            if hasattr(self.app, 'configurar_scrollbars'):
                self.app.configurar_scrollbars()

        except Exception as e:
            self.app.ui_callbacks.habilitar_busqueda()
    
    def mostrar_multi(self, resultados, criterio):
        """Muestra resultados multi-ubicaciones"""
        if not resultados:
            from .search_methods import SearchMethods
            SearchMethods(self.app).buscar_tradicional_fallback(criterio)
            return
        
        try:
            # Optimizado para 1-20 resultados típicos
            self._agregar_resultados_multi(resultados)
            self._finalizar_multi(resultados, criterio)
        except Exception as e:
            self.app.ui_callbacks.habilitar_busqueda()
    
    def mostrar_tradicionales(self, resultados, criterio):
        """Muestra resultados búsqueda tradicional"""
        if not resultados:
            self.app.ui_callbacks.actualizar_estado("No se encontraron resultados")
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
            return
        
        try:
            self._agregar_resultados(resultados, "Tradicional")
            self.app.ui_callbacks.actualizar_estado(f"✅ {len(resultados)} resultados (Búsqueda tradicional)")
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
            
            if hasattr(self.app, 'historial_manager'):
                self.app.master.after(50, lambda: self.app.historial_manager.agregar_busqueda(
                    criterio, "Tradicional", len(resultados), 0.1))
            
            # Actualizar scrollbars
            if hasattr(self.app, 'configurar_scrollbars'):
                self.app.configurar_scrollbars()

        except Exception as e:
            self.app.ui_callbacks.habilitar_busqueda()
    
    def _agregar_resultados(self, resultados, metodo):
        """Agrega resultados con Lote Crítico para percepción instantánea"""
        # LOTE CRÍTICO: Primeros 30 resultados (caben en pantalla) se muestran síncronos
        lote_critico = resultados[:30]
        self._agregar_batch(lote_critico, 0, metodo)
        self.app.master.update_idletasks() # Forzar dibujado inmediato
        
        # RESTO: El resto se carga en batches asíncronos para no bloquear
        if len(resultados) > 30:
            resto = resultados[30:]
            batch_size = 100
            for i in range(0, len(resto), batch_size):
                batch = resto[i:i+batch_size]
                delay = (i // batch_size) * 1  # Delay mínimo (1ms)
                self.app.master.after(delay, lambda b=batch, idx=30+i, m=metodo: 
                    self._agregar_batch(b, idx, m))
    
    def _agregar_resultados_multi(self, resultados):
        """Agrega resultados multi con Lote Crítico"""
        # LOTE CRÍTICO: Primeros 30 síncronos
        lote_critico = resultados[:30]
        self._agregar_batch_multi(lote_critico, 0)
        self.app.master.update_idletasks() # Forzar dibujado
        
        if len(resultados) > 30:
            resto = resultados[30:]
            batch_size = 100
            for i in range(0, len(resto), batch_size):
                batch = resto[i:i+batch_size]
                delay = (i // batch_size) * 1
                self.app.master.after(delay, lambda b=batch, idx=30+i: 
                    self._agregar_batch_multi(b, idx))
    
    def _agregar_batch(self, batch, start_index, metodo):
        """Agrega un batch al TreeView - SIN verificación I/O"""
        try:
            letra_metodo = metodo[0].upper() if metodo else 'C'
            
            for i, resultado in enumerate(batch):
                try:
                    actual_index = start_index + i
                    tag = 'evenrow' if actual_index % 2 == 0 else 'oddrow'
                    
                    if isinstance(resultado, tuple) and len(resultado) >= 3:
                        nombre, ruta_rel, ruta_abs = resultado[:3]
                        
                        # Usar ruta absoluta si existe, sino relativa
                        ruta_completa = ruta_abs if ruta_abs else ruta_rel
                        
                        # Insertar item principal
                        item_id = self.app.tree.insert("", "end",
                            text=f"📂 {nombre}",
                            values=(letra_metodo, ruta_completa),
                            tags=(tag,))
                        
                        # Agregar dummy para triángulo de expansión
                        self.app.tree.insert(item_id, "end", text="Cargando...", values=("", ""))
                            
                except Exception as e:
                    print(f"[ERROR] Error agregando item: {e}")
                    continue
        except Exception as e:
            print(f"[ERROR] Error en _agregar_batch: {e}")
    
    def _agregar_batch_multi(self, batch, start_index):
        """Agrega batch multi-ubicaciones - SIN verificación I/O"""
        try:
            for i, resultado in enumerate(batch):
                try:
                    actual_index = start_index + i
                    tag = 'evenrow' if actual_index % 2 == 0 else 'oddrow'
                    
                    # Tuplas de 4 (sin BD) o 6 elementos (con BD enriquecido)
                    if isinstance(resultado, tuple) and len(resultado) >= 4:
                        nombre = resultado[0]
                        ruta_rel = resultado[1]
                        ruta_abs = resultado[2]
                        ubicacion = resultado[3]
                        demandante = resultado[4] if len(resultado) > 4 else ""
                        demandado = resultado[5] if len(resultado) > 5 else ""
                        
                        # Insertar item principal
                        item_id = self.app.tree.insert("", "end",
                            text=f"📂 {nombre}",
                            values=(ubicacion, ruta_abs, demandante, demandado),
                            tags=(tag,))
                        
                        # Agregar dummy para triángulo de expansión
                        self.app.tree.insert(item_id, "end", text="Cargando...", values=("", "", "", ""))
                            
                except Exception as e:
                    print(f"[ERROR] Error agregando item multi: {e}")
                    continue
        except Exception as e:
            print(f"[ERROR] Error en _agregar_batch_multi: {e}")
    
    def _finalizar_multi(self, resultados, criterio):
        """Finaliza búsqueda multi"""
        try:
            self.app.ui_callbacks.actualizar_estado(f"✅ {len(resultados)} resultados en múltiples ubicaciones")
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
            
            if hasattr(self.app, 'historial_manager'):
                self.app.historial_manager.agregar_busqueda(criterio, "Multi", len(resultados), 0.2)
            
            # Actualizar scrollbars
            if hasattr(self.app, 'configurar_scrollbars'):
                self.app.configurar_scrollbars()

        except:
            self.app.ui_callbacks.habilitar_busqueda()