# src/results_display.py - Visualización de resultados con soporte de subcarpetas
import tkinter as tk
import os

class ResultsDisplay:
    """Maneja la visualización de resultados en el TreeView"""
    
    def __init__(self, app):
        self.app = app
    
    def mostrar_instantaneos(self, resultados, criterio, metodo):
        """Muestra resultados instantáneos"""
        try:
            self._agregar_por_lotes(resultados, metodo)
            self.app.ui_callbacks.actualizar_estado(f"✅ {len(resultados)} resultados ({metodo})")
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
            
            if hasattr(self.app, 'historial_manager'):
                self.app.master.after(50, lambda: self.app.historial_manager.agregar_busqueda(
                    criterio, metodo, len(resultados), 0.05))
        except Exception as e:
            self.app.ui_callbacks.habilitar_busqueda()
    
    def mostrar_multi(self, resultados, criterio):
        """Muestra resultados multi-ubicaciones"""
        if not resultados:
            from .search_methods import SearchMethods
            SearchMethods(self.app).buscar_tradicional_fallback(criterio)
            return
        
        try:
            batch_size = 3
            for i in range(0, len(resultados), batch_size):
                batch = resultados[i:i+batch_size]
                delay = (i // batch_size) * 3
                self.app.master.after(delay, lambda b=batch, idx=i: 
                    self._agregar_batch_multi(b, idx))
            
            total_delay = ((len(resultados) // batch_size) + 1) * 3
            self.app.master.after(total_delay + 10, lambda: 
                self._finalizar_multi(resultados, criterio))
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
            self._agregar_por_lotes(resultados, "Tradicional")
            self.app.ui_callbacks.actualizar_estado(f"✅ {len(resultados)} resultados (Búsqueda tradicional)")
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
            
            if hasattr(self.app, 'historial_manager'):
                self.app.master.after(50, lambda: self.app.historial_manager.agregar_busqueda(
                    criterio, "Tradicional", len(resultados), 0.1))
        except Exception as e:
            self.app.ui_callbacks.habilitar_busqueda()
    
    def _agregar_por_lotes(self, resultados, metodo):
        """Agrega resultados por lotes"""
        batch_size = 5
        for i in range(0, len(resultados), batch_size):
            batch = resultados[i:i+batch_size]
            delay = (i // batch_size) * 2
            self.app.master.after(delay, lambda b=batch, idx=i, m=metodo: 
                self._agregar_batch(b, idx, m))
    
    def _agregar_batch(self, batch, start_index, metodo):
        """Agrega un batch al TreeView CON soporte de subcarpetas"""
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
                        
                        # NUEVO: Agregar dummy si tiene subcarpetas
                        if os.path.isdir(ruta_completa) and self._tiene_subcarpetas(ruta_completa):
                            # Agregar nodo dummy para mostrar flecha de expansión
                            self.app.tree.insert(item_id, "end", text="Cargando...", values=("", ""))
                            
                except Exception as e:
                    print(f"[ERROR] Error agregando item: {e}")
                    continue
        except Exception as e:
            print(f"[ERROR] Error en _agregar_batch: {e}")
    
    def _agregar_batch_multi(self, batch, start_index):
        """Agrega batch multi-ubicaciones CON soporte de subcarpetas"""
        try:
            for i, resultado in enumerate(batch):
                try:
                    actual_index = start_index + i
                    tag = 'evenrow' if actual_index % 2 == 0 else 'oddrow'
                    
                    if isinstance(resultado, tuple) and len(resultado) >= 4:
                        nombre, ruta_rel, ruta_abs, ubicacion = resultado[:4]
                        
                        # Insertar item principal
                        item_id = self.app.tree.insert("", "end",
                            text=f"📂 {nombre} [{ubicacion}]",
                            values=("M", ruta_abs),
                            tags=(tag,))
                        
                        # NUEVO: Agregar dummy si tiene subcarpetas
                        if os.path.isdir(ruta_abs) and self._tiene_subcarpetas(ruta_abs):
                            self.app.tree.insert(item_id, "end", text="Cargando...", values=("", ""))
                            
                except Exception as e:
                    print(f"[ERROR] Error agregando item multi: {e}")
                    continue
        except Exception as e:
            print(f"[ERROR] Error en _agregar_batch_multi: {e}")
    
    def _tiene_subcarpetas(self, ruta):
        """Verifica si una carpeta tiene subcarpetas"""
        try:
            if not os.path.exists(ruta) or not os.path.isdir(ruta):
                return False
            
            for entry in os.scandir(ruta):
                if entry.is_dir():
                    return True
            return False
        except:
            return False
    
    def _finalizar_multi(self, resultados, criterio):
        """Finaliza búsqueda multi"""
        try:
            self.app.ui_callbacks.actualizar_estado(f"✅ {len(resultados)} resultados en múltiples ubicaciones")
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
            
            if hasattr(self.app, 'historial_manager'):
                self.app.historial_manager.agregar_busqueda(criterio, "Multi", len(resultados), 0.2)
        except:
            self.app.ui_callbacks.habilitar_busqueda()