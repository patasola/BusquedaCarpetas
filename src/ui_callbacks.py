# src/ui_callbacks.py - Callbacks de UI V.4.2 (Refactorizado)
import tkinter as tk
from .results_renderer import ResultsRenderer
from tkinter import messagebox
import os
import time

class UICallbacks:
    def __init__(self, app_instance):
        self.app = app_instance
        self._last_adjust_time = 0
        self._ajuste_en_progreso = False

    def _ajustar_columnas_inmediato(self):
        """Ajuste de columnas automático optimizado"""
        if self._ajuste_en_progreso or time.time() - self._last_adjust_time < 0.05:
            return
            
        self._ajuste_en_progreso = True
        
        try:
            tree = self.app.tree
            if not tree or len(tree.get_children()) == 0:
                return
            
            max_length = 0
            max_depth = 0
            
            def analizar_visibles(parent='', depth=0):
                nonlocal max_length, max_depth
                for item in tree.get_children(parent):
                    texto = tree.item(item, 'text')
                    if texto:
                        texto_limpio = texto.replace('📁', '').replace('📂', '').strip()
                        length_with_depth = len(texto_limpio) + (depth * 2)
                        
                        max_length = max(max_length, length_with_depth)
                        max_depth = max(max_depth, depth)
                    
                    if tree.item(item, 'open'):
                        analizar_visibles(item, depth + 1)
            
            analizar_visibles()
            
            if max_length == 0:
                return
            
            # Calcular ancho óptimo
            if max_length <= 12:
                nuevo_ancho = 200
            elif max_length <= 20:
                nuevo_ancho = 200 + (max_length - 12) * 10
            elif max_length <= 35:
                nuevo_ancho = 280 + (max_length - 20) * 8
            elif max_length <= 50:
                nuevo_ancho = 400 + (max_length - 35) * 6
            else:
                nuevo_ancho = min(490 + (max_length - 50) * 4, 600)
            
            nuevo_ancho += max_depth * 12
            
            # Aplicar si hay diferencia significativa
            ancho_actual = tree.column('#0', 'width')
            if abs(nuevo_ancho - ancho_actual) > 5:
                tree.column('#0', width=nuevo_ancho)
                self._last_adjust_time = time.time()
                tree.update_idletasks()
                
        except Exception:
            pass
        finally:
            self._ajuste_en_progreso = False

    def limpiar_resultados(self):
        """Limpia resultados del TreeView - OPTIMIZADO"""
        import time as _time
        from datetime import datetime as _datetime
        _t0 = _time.perf_counter()
        try:
            # CRÍTICO: Borrado masivo en una sola operación (mucho más rápido)
            children = self.app.tree.get_children()
            if children:
                self.app.tree.delete(*children)  # Desempaquetar todos los items
            _t1 = _time.perf_counter()
            current_time = _datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{current_time}] [LIMPIAR] Completado en {(_t1-_t0)*1000:.2f} ms")
        except Exception as e:
            _t1 = _time.perf_counter()
            current_time = _datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{current_time}] [LIMPIAR] Error en {(_t1-_t0)*1000:.2f} ms: {e}")

    def mostrar_resultados(self, resultados, metodo, tiempo_total):
        """Muestra resultados - DELEGADO A ResultsRenderer"""
        self.limpiar_resultados()
        return ResultsRenderer.render_results(
            self.app, resultados, metodo, tiempo_total,
            actualizar_estado_callback=self.actualizar_estado
        )
    def actualizar_estado(self, mensaje):
        """Actualiza la barra de estado"""
        try:
            if hasattr(self.app, 'label_estado') and self.app.label_estado:
                self.app.label_estado.config(text=mensaje)
                self.app.master.update_idletasks()
                
                # Debug timestamp
                from datetime import datetime as _datetime
                current_time = _datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"[{current_time}] [DEBUG] Estado actualizado: {mensaje}")
        except Exception as e:
            print(f"Error actualizando estado: {e}")

    def deshabilitar_busqueda(self):
        """Deshabilita botones de búsqueda"""
        try:
            if hasattr(self.app, 'btn_buscar'):
                self.app.btn_buscar.config(state='disabled')
            if hasattr(self.app, 'entry'):
                self.app.entry.config(state='disabled')
        except Exception as e:
            print(f"Error deshabilitando búsqueda: {e}")

    def habilitar_busqueda(self):
        """Habilita botones de búsqueda"""
        try:
            if hasattr(self.app, 'btn_buscar'):
                self.app.btn_buscar.config(state='normal')
            if hasattr(self.app, 'entry'):
                self.app.entry.config(state='normal')
        except Exception as e:
            print(f"Error habilitando búsqueda: {e}")

    def mostrar_advertencia(self, mensaje):
        """Muestra diálogo de advertencia"""
        try:
            messagebox.showwarning("Advertencia", mensaje)
        except Exception as e:
            print(f"Error mostrando advertencia: {e}")

    def mostrar_error(self, mensaje):
        """Muestra diálogo de error"""
        try:
            messagebox.showerror("Error", mensaje)
        except Exception as e:
            print(f"Error mostrando error: {e}")

    def mostrar_info(self, titulo, mensaje):
        """Muestra diálogo informativo"""
        try:
            messagebox.showinfo(titulo, mensaje)
        except Exception as e:
            print(f"Error mostrando info: {e}")

    def obtener_seleccion_tabla(self):
        """Obtiene información del elemento seleccionado"""
        try:
            selection = self.app.tree.selection()
            if not selection:
                return None
            
            item = self.app.tree.item(selection[0])
            values = item['values']
            text = item['text']
            
            nombre = text.replace("📁 ", "").replace("📂 ", "")
            
            if len(values) >= 2:
                letra = values[0]
                ruta_rel = values[1]
                
                metodo_map = {"C": "Cache", "T": "Tradicional", "E": "Tree"}
                metodo_original = metodo_map.get(letra, "Desconocido")
                
                return {
                    'metodo': metodo_original,
                    'nombre': nombre,
                    'ruta_rel': ruta_rel
                }
            return None
            
        except Exception as e:
            print(f"Error obteniendo selección: {e}")
            return None

    def hay_seleccion(self):
        """Verifica si hay algún elemento seleccionado"""
        try:
            return len(self.app.tree.selection()) > 0
        except:
            return False

    def copiar_ruta(self):
        """Copia ruta seleccionada al portapapeles"""
        try:
            if not hasattr(self.app, 'tree') or not self.app.tree.selection():
                return
            
            item = self.app.tree.selection()[0]
            
            # Obtener ruta desde tree_explorer si está disponible
            if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
                ruta = getattr(self.app.tree_explorer, 'get_selected_path', lambda: None)()
            else:
                values = self.app.tree.item(item, 'values')
                ruta = values[1] if values and len(values) > 1 else None
            
            if ruta:
                self.app.master.clipboard_clear()
                self.app.master.clipboard_append(ruta)
                self.actualizar_estado(f"Ruta copiada: {os.path.basename(ruta)}")
            else:
                messagebox.showwarning("Advertencia", "No se pudo obtener la ruta")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al copiar ruta: {e}")

    def abrir_carpeta(self):
        """Abre carpeta seleccionada en el explorador"""
        try:
            if not hasattr(self.app, 'tree') or not self.app.tree.selection():
                return
            
            item = self.app.tree.selection()[0]
            
            # Obtener ruta desde tree_explorer si está disponible
            if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
                ruta = getattr(self.app.tree_explorer, 'get_selected_path', lambda: None)()
            else:
                values = self.app.tree.item(item, 'values')
                ruta = values[1] if values and len(values) > 1 else None
            
            if ruta and os.path.exists(ruta):
                import subprocess
                import sys
                
                if sys.platform == "win32":
                    subprocess.Popen(['explorer', ruta])
                elif sys.platform == "darwin":
                    subprocess.Popen(['open', ruta])
                else:
                    subprocess.Popen(['xdg-open', ruta])
                    
                self.actualizar_estado(f"Carpeta abierta: {os.path.basename(ruta)}")
            else:
                messagebox.showwarning("Advertencia", "La carpeta no existe o no se pudo obtener la ruta")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir carpeta: {e}")

    def toggle_historial(self):
        """Alterna visibilidad del historial"""
        try:
            if hasattr(self.app, 'ui_manager') and hasattr(self.app.ui_manager, 'toggle_historial'):
                self.app.ui_manager.toggle_historial()
            elif hasattr(self.app, 'historial_manager'):
                self.app.historial_manager.toggle_visibility()
        except Exception as e:
            print(f"Error al alternar historial: {e}")

    def construir_cache(self):
        """Inicia construcción de cache"""
        try:
            self.app.search_coordinator.construir_cache_automatico()
        except Exception as e:
            print(f"Error iniciando construcción cache: {e}")

    def mostrar_acerca_de(self):
        """Muestra información sobre la aplicación"""
        info = """Búsqueda de Carpetas V.4.2
Explorador Integrado

Funcionalidades principales:
• Búsqueda rápida en cache
• Explorador de árbol integrado
• Historial de búsquedas
• Ajuste automático de columnas
• Copiar rutas y abrir carpetas

Métodos de búsqueda:
• C = Cache (rápido)
• T = Tradicional (completo)
• E = Explorer (expandible)

© 2025 - Sistema de Búsqueda de Carpetas"""
        messagebox.showinfo("Acerca de", info.strip())

    # Métodos de compatibilidad simplificados
    def buscar(self):
        """Ejecuta búsqueda"""
        criterio = self.app.entry.get().strip()
        if criterio:
            self.app.search_coordinator.ejecutar_busqueda(criterio)
        else:
            messagebox.showwarning("Advertencia", "Ingresa un criterio de búsqueda")

    def limpiar(self):
        """Limpia resultados y criterio"""
        self.limpiar_resultados()
        if hasattr(self.app, 'entry'):
            self.app.entry.delete(0, tk.END)
        self.actualizar_estado("Listo para búsqueda")

    def salir(self):
        """Cierra la aplicación"""
        if messagebox.askokcancel("Salir", "¿Deseas cerrar la aplicación?"):
            self.app.master.quit()
            self.app.master.destroy()

    # Alias para compatibilidad
    def mostrar_resultados_async(self, resultados, metodo, tiempo_total):
        self.app.master.after(0, lambda: self.mostrar_resultados(resultados, metodo, tiempo_total))
    
    def actualizar_estado_async(self, mensaje):
        self.app.master.after(0, lambda: self.actualizar_estado(mensaje))
    
    def finalizar_busqueda_inmediata(self):
        self.habilitar_busqueda()
    
    def finalizar_busqueda_async(self):
        self.app.master.after(0, self.habilitar_busqueda)
