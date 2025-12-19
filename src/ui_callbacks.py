# src/ui_callbacks.py - Callbacks de UI V.4.2 (Refactorizado)
import tkinter as tk
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
        try:
            # Borrado masivo es mucho más rápido que uno por uno
            if hasattr(self.app, 'tree') and self.app.tree:
                children = self.app.tree.get_children()
                if children:
                    self.app.tree.delete(*children)
        except Exception as e:
            print(f"Error limpiando resultados: {e}")

    def mostrar_resultados(self, resultados, metodo, tiempo_total):
        """Muestra resultados en TreeView con Lazy Loading OPTIMIZADO"""
        self.limpiar_resultados()
        
        if not resultados:
            # Restaurar botón de búsqueda cuando no hay resultados
            self.app.btn_buscar.configure(state='normal', text='Buscar')
            self.app.btn_cancelar.configure(state='disabled')
            self.actualizar_estado(f"No se encontraron resultados ({metodo}, {tiempo_total:.3f}s)")
            return
        
        # Agregar al historial si NO es búsqueda silenciosa
        if not getattr(self.app.search_coordinator, 'busqueda_silenciosa', False):
            num_resultados = len(resultados) if resultados else 0
            if hasattr(self.app, '_finalizar_busqueda_con_historial'):
                self.app._finalizar_busqueda_con_historial(metodo, num_resultados)
            elif hasattr(self.app.search_coordinator, 'finalizar_busqueda_con_historial'):
                self.app.search_coordinator.finalizar_busqueda_con_historial(metodo, num_resultados)
        
        try:
            # Usar tree explorer si está disponible y activo
            if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer and \
               hasattr(self.app, 'mostrar_explorador') and self.app.mostrar_explorador.get():
                
                formatted_results = []
                for resultado in resultados:
                    if isinstance(resultado, tuple) and len(resultado) >= 3:
                        nombre, ruta_rel, ruta_abs = resultado[:3]
                        formatted_results.append({
                            'name': nombre,
                            'path': ruta_abs,
                            'files': 0,
                            'size': '0 B'
                        })
                    elif isinstance(resultado, dict):
                        formatted_results.append(resultado)
                
                self.app.tree_explorer.populate_search_results(formatted_results)
                self.actualizar_estado(f"✅ {len(resultados)} resultados en {tiempo_total:.3f}s ({metodo})")
                return

            # Fallback: TreeView normal con LAZY LOADING
            letra_metodo, tags_color = self._metodo_a_config(metodo)
            items_to_insert = []
            
            for i, resultado in enumerate(resultados):
                base_tags = ['evenrow' if i % 2 == 0 else 'oddrow']
                
                if isinstance(resultado, tuple) and len(resultado) >= 3:
                    nombre, ruta_rel, ruta_abs = resultado[:3]
                elif isinstance(resultado, dict):
                    nombre = resultado.get('name', 'Sin nombre')
                    ruta_rel = resultado.get('path', '')
                else:
                    continue
                
                items_to_insert.append({
                    'text': f"📁 {nombre}",
                    'values': (letra_metodo, ruta_rel),
                    'tags': tuple(base_tags + [tags_color])
                })
            
            # OPTIMIZACIÓN: Insertar primer lote INMEDIATAMENTE para feedback instantáneo
            BATCH_SIZE = 100
            first_batch_end = min(BATCH_SIZE, len(items_to_insert))
            
            for i in range(first_batch_end):
                item = items_to_insert[i]
                self.app.tree.insert("", "end", 
                                   text=item['text'],
                                   values=item['values'],
                                   tags=item['tags'])
            
            # Si hay más, programar el resto
            if len(items_to_insert) > BATCH_SIZE:
                self.actualizar_estado(f"Renderizando {len(items_to_insert)} resultados...")
                # Usar after(1) para que sea casi inmediato pero permita refrescar UI
                self.app.master.after(1, lambda: self._insertar_lote(items_to_insert, BATCH_SIZE, metodo, tiempo_total))
            else:
                # Si son pocos, finalizar ya
                self.actualizar_estado(f"✅ {len(items_to_insert)} resultados en {tiempo_total:.3f}s ({metodo})")
                self.app.configurar_scrollbars()
                self._ajustar_columnas_inmediato()
                
                # Restaurar botones
                self.app.btn_buscar.configure(state='normal', text='Buscar')
                self.app.btn_cancelar.configure(state='disabled')
            
        except Exception as e:
            self.actualizar_estado(f"Error mostrando resultados: {str(e)}")
            print(f"Error detallado: {e}")

    def _insertar_lote(self, items, start_index, metodo, tiempo_total):
        """Inserta un lote de items en el TreeView"""
        try:
            BATCH_SIZE = 100
            end_index = min(start_index + BATCH_SIZE, len(items))
            
            for i in range(start_index, end_index):
                item = items[i]
                self.app.tree.insert("", "end", 
                                   text=item['text'],
                                   values=item['values'],
                                   tags=item['tags'])
            
            if end_index < len(items):
                # Programar siguiente lote (1ms delay para máxima velocidad)
                progress = int((end_index / len(items)) * 100)
                if start_index % 500 == 0: # Actualizar texto menos frecuentemente
                    self.actualizar_estado(f"Renderizando... {progress}%")
                
                self.app.master.after(1, lambda: self._insertar_lote(items, end_index, metodo, tiempo_total))
            else:
                # Finalizado
                self.actualizar_estado(f"✅ {len(items)} resultados en {tiempo_total:.3f}s ({metodo})")
                self.app.configurar_scrollbars()
                # self._ajustar_columnas_inmediato() # OPTIMIZACIÓN: No ajustar en cada lote
                
                # Restaurar botones
                self.app.btn_buscar.configure(state='normal', text='Buscar')
                self.app.btn_cancelar.configure(state='disabled')
                
        except Exception as e:
            print(f"Error en carga por lotes: {e}")
            
    def _metodo_a_config(self, metodo):
        """Helper para obtener configuración según método"""
        metodo_lower = metodo.lower() if metodo else ""
        if 'cache' in metodo_lower:
            return "C", 'cache'
        elif 'tradicional' in metodo_lower:
            return "T", 'tradicional'
        elif 'tree' in metodo_lower:
            return "E", 'tree'
        else:
            return "?", 'unknown'

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

    def actualizar_estado(self, mensaje, color="black"):
        """Actualiza la barra de estado"""
        try:
            if hasattr(self.app, 'label_estado') and self.app.label_estado:
                self.app.label_estado.config(text=mensaje, fg=color)
                self.app.label_estado.update_idletasks()
        except Exception as e:
            print(f"Error actualizando estado: {e}")

    def mostrar_advertencia(self, mensaje):
        messagebox.showwarning("Advertencia", mensaje)

    def mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)

    def mostrar_info(self, mensaje):
        messagebox.showinfo("Información", mensaje)

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