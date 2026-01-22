# src/results_display.py - Visualización de resultados OPTIMIZADO
import tkinter as tk
import os
import time

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
            print(f"[PROFILE] Inicio renderizado multi: {time.time()}")
            batch_size = 50
            for i in range(0, len(resultados), batch_size):
                batch = resultados[i:i+batch_size]
                delay = (i // batch_size) * 5
                self.app.master.after(delay, lambda b=batch, idx=i: 
                    self._agregar_batch_multi(b, idx))
            
            total_delay = ((len(resultados) // batch_size) + 1) * 5
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
            print(f"[PROFILE] Inicio renderizado tradicional: {time.time()}")
            self._agregar_por_lotes(resultados, "Tradicional")
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
    
    def _agregar_por_lotes(self, resultados, metodo):
        """Agrega resultados por lotes"""
        batch_size = 50
        for i in range(0, len(resultados), batch_size):
            batch = resultados[i:i+batch_size]
            delay = (i // batch_size) * 5
            self.app.master.after(delay, lambda b=batch, idx=i, m=metodo: 
                self._agregar_batch(b, idx, m))
        print(f"[PROFILE] Fin programación lotes: {time.time()}")
    
    def _tiene_subcarpetas_rapido(self, ruta):
        """Verificación ultra-rápida de subcarpetas usando os.scandir
        Solo busca el PRIMER subdirectorio, no escanea toda la carpeta"""
        try:
            with os.scandir(ruta) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        return True  # Encontramos al menos una subcarpeta
            return False
        except (PermissionError, OSError, FileNotFoundError):
            return False
    
    def _agregar_batch(self, batch, start_index, metodo):
        """Agrega un batch al TreeView con verificación optimizada"""
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
                        
                        # ⚡ OPTIMIZACIÓN: Verificación rápida solo del primer item
                        # Mucho más eficiente que os.path.isdir() completo
                        if self._tiene_subcarpetas_rapido(ruta_completa):
                            self.app.tree.insert(item_id, "end", text="", values=("", ""))
                            
                except Exception as e:
                    print(f"[ERROR] Error agregando item: {e}")
                    continue
        except Exception as e:
            print(f"[ERROR] Error en _agregar_batch: {e}")
    
    def _agregar_batch_multi(self, batch, start_index):
        """Agrega batch multi-ubicaciones con verificación optimizada"""
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
                        
                        item_id = self.app.tree.insert("", "end",
                            text=f"📂 {nombre}",
                            values=(ubicacion, ruta_abs, demandante, demandado),
                            tags=(tag,))
                        
                        # ⚡ OPTIMIZACIÓN: Verificación rápida solo del primer item
                        if self._tiene_subcarpetas_rapido(ruta_abs):
                            self.app.tree.insert(item_id, "end", text="", values=("", "", "", ""))
                            
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
            
            print(f"[PROFILE] Fin renderizado multi: {time.time()}")

        except:
            self.app.ui_callbacks.habilitar_busqueda()