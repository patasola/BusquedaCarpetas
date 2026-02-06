# src/managers/ui_manager.py - Gestor Unificado de UI V.5.0
import tkinter as tk
from tkinter import messagebox
import os
import time
from ..ui.results_renderer import ResultsRenderer

class UIManager:
    """Gestor centralizado de todos los elementos, estados y callbacks de la interfaz"""
    
    def __init__(self, app):
        self.app = app
        
        # Referencias a frames de barras
        self.status_frame = None
        self.cache_frame = None
        
        # Estado de UI
        self.modo_entrada = "normal"
        self._updating_vars = False
        self._last_adjust_time = 0
        self._ajuste_en_progreso = False
        self._search_timer = None # Timer para búsqueda automática (debounce)

    # --- CONFIGURACIÓN E INICIALIZACIÓN ---

    def configurar_referencias(self, status_frame, cache_frame):
        """Configura las referencias a los frames de las barras"""
        self.status_frame = status_frame
        self.cache_frame = cache_frame
        self._asegurar_barras_visibles()
    
    def configurar_validacion(self):
        """Configura la validación del campo de entrada"""
        try:
            vcmd = (self.app.master.register(self._validar_entrada), '%P')
            self.app.entry.configure(validate="key", validatecommand=vcmd)
            self.app.entry.bind('<KeyRelease>', self.on_entry_change)
        except Exception as e:
            print(f"[UIManager] Error configurando validación: {e}")

    # --- GESTIÓN DE VISIBILIDAD (Antes en ui_manager.py) ---

    def _asegurar_barras_visibles(self):
        """Asegura que las barras estén visibles al inicio según las variables guardadas"""
        try:
            if self.cache_frame and hasattr(self.app, 'mostrar_barra_cache') and self.app.mostrar_barra_cache.get():
                if self.status_frame and hasattr(self.app, 'mostrar_barra_estado') and self.app.mostrar_barra_estado.get():
                    self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame)
                else:
                    self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X)
            
            if self.status_frame and hasattr(self.app, 'mostrar_barra_estado') and self.app.mostrar_barra_estado.get():
                self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        except Exception as e:
            print(f"[UIManager] Error asegurando barras visibles: {e}")

    def toggle_barra_estado(self):
        """Alterna visibilidad de la barra de estado"""
        if self._updating_vars or not self.status_frame: return
        mostrar = self.app.mostrar_barra_estado.get()
        if mostrar:
            self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
            if self.cache_frame and self.app.mostrar_barra_cache.get():
                self.cache_frame.pack_forget()
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame)
        else:
            self.status_frame.pack_forget()
            if self.cache_frame and self.app.mostrar_barra_cache.get():
                self.cache_frame.pack_forget()
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X)

    def toggle_barra_cache(self):
        """Alterna visibilidad de la barra de cache"""
        if self._updating_vars or not self.cache_frame: return
        mostrar = self.app.mostrar_barra_cache.get()
        if mostrar:
            if self.status_frame and self.app.mostrar_barra_estado.get():
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame)
            else:
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.cache_frame.pack_forget()

    def toggle_historial(self):
        """Alterna visibilidad del historial"""
        if hasattr(self.app, 'historial_manager') and self.app.historial_manager:
            self.app.historial_manager.toggle_visibility()
            if hasattr(self.app, 'mostrar_historial'):
                self._updating_vars = True
                self.app.mostrar_historial.set(self.app.historial_manager.visible)
                self._updating_vars = False

    # --- GESTIÓN DE ESTADO Y VALIDACIÓN (Antes en ui_state_manager.py) ---

    def _validar_entrada(self, nuevo_texto):
        """Valida el texto de entrada en tiempo real"""
        if not nuevo_texto:
            self._actualizar_boton_buscar(False)
            return True
        
        if self.app.modo_numerico:
            if not all(c.isdigit() or c == '-' for c in nuevo_texto):
                return False
        
        self._actualizar_boton_buscar(len(nuevo_texto.strip()) >= 1)
        return True

    def _actualizar_boton_buscar(self, habilitar):
        """Actualiza estado del botón buscar según criterios"""
        try:
            if habilitar and getattr(self.app, 'ruta_carpeta', None):
                self.app.btn_buscar.configure(state='normal')
            else:
                self.app.btn_buscar.configure(state='disabled')
        except: pass

    def on_entry_change(self, event):
        """Callback al cambiar texto en entry para activar búsqueda automática (DEBOUNCE)"""
        texto = self.app.entry.get().strip()
        
        # 1. Habilitar/Deshabilitar botón de búsqueda
        habilitada = bool(texto) and bool(getattr(self.app, 'ruta_carpeta', None))
        self._actualizar_boton_buscar(habilitada)
        
        # 2. Programar búsqueda automática si hay texto y no es numérico estricto
        # No queremos disparar accidentalmente si está pegando un radicado largo de golpe
        if len(texto) >= 3:
            if self._search_timer:
                self.app.master.after_cancel(self._search_timer)
            
            # Solo disparar automático si el cache está listo para que sea INSTANTANEO
            if hasattr(self.app, 'cache_manager') and self.app.cache_manager.cache.valido:
                self._search_timer = self.app.master.after(1200, self._trigger_auto_search)

    def _trigger_auto_search(self):
        """Dispara la búsqueda automática tras el debounce (Modo Silencioso)"""
        if not self.app.entry.get().strip(): return
        if self.app.btn_buscar['state'] == 'disabled': return
        
        print("[DEBUG] Disparando búsqueda automática (Silenciosa para no robar foco)")
        self.app.buscar_carpeta(silenciosa=True)

    def cambiar_modo_entrada(self):
        """Alterna entre modo Numérico y Alfanumérico"""
        self.app.modo_numerico = not self.app.modo_numerico
        self.actualizar_indicador_modo()
        self.app.entry.delete(0, tk.END)
        self.app.entry.focus_set()

    def actualizar_indicador_modo(self):
        """Actualiza el label visual del modo"""
        if self.app.modo_numerico:
            self.app.modo_label.config(text="[123] Numérico", fg="#006600")
        else:
            self.app.modo_label.config(text="[ABC] Alfanumérico", fg="#0066cc")

    def actualizar_estado_botones(self, hay_seleccion=False):
        """Habilita o deshabilita botones de acción según selección"""
        estado = 'normal' if hay_seleccion else 'disabled'
        for attr in ['btn_copiar', 'btn_abrir']:
            if hasattr(self.app, attr):
                getattr(self.app, attr).configure(state=estado)

    def enfocar_y_seleccionar_campo(self):
        """F2: Enfoca y selecciona todo el texto de búsqueda"""
        try:
            self.app.entry.configure(state='normal')
            self.app.entry.focus_force()
            self.app.entry.select_range(0, tk.END)
            self.app.entry.icursor(tk.END)
            if self.app.entry.get().strip() and getattr(self.app, 'ruta_carpeta', None):
                self.app.btn_buscar.configure(state='normal')
        except: pass

    # --- CALLBACKS Y LOGICA DE NEGOCIO (Antes en ui_callbacks.py) ---

    def limpiar_resultados(self):
        """Limpia el TreeView de resultados de forma eficiente"""
        try:
            children = self.app.tree.get_children()
            if children:
                self.app.tree.delete(*children)
            
            # Limpiar cache de expansión para evitar problemas con IDs reciclados
            if hasattr(self.app, 'tree_expansion_handler'):
                self.app.tree_expansion_handler.clear_cache()
        except Exception as e:
            print(f"[UIManager] Error limpiando resultados: {e}")

    def mostrar_resultados(self, resultados, metodo, tiempo_total):
        """Renderiza resultados limpiando previos (Legacy/Full)"""
        self.limpiar_resultados()
        return self.mostrar_resultados_incrementales(resultados, metodo, tiempo_total)

    def mostrar_resultados_incrementales(self, resultados, metodo, tiempo_total):
        """Añade resultados al TreeView sin limpiar los anteriores (Para Streaming)"""
        return ResultsRenderer.render_results(
            self.app, resultados, metodo, tiempo_total,
            actualizar_estado_callback=self.actualizar_estado
        )

    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje en la barra de estado"""
        try:
            if hasattr(self.app, 'label_estado') and self.app.label_estado:
                self.app.label_estado.config(text=mensaje)
                self.app.master.update_idletasks()
        except: pass

    def deshabilitar_busqueda(self, incluir_entry=True):
        """Bloquea controles durante búsqueda activa"""
        self.app.btn_buscar.config(state='disabled')
        if hasattr(self.app, 'btn_cancelar'):
            self.app.btn_cancelar.config(state='normal')
        
        # SIEMPRE mantener el entry habilitado si se solicita (ej: búsqueda automática)
        # para evitar pérdida de foco mientras el usuario escribe.
        if incluir_entry:
            self.app.entry.config(state='disabled')

    def habilitar_busqueda(self):
        """Libera controles tras finalizar búsqueda"""
        self.app.btn_buscar.config(state='normal', text="Buscar")
        if hasattr(self.app, 'btn_cancelar'):
            self.app.btn_cancelar.config(state='disabled')
        self.app.entry.config(state='normal')

    def actualizar_metadata_resultados(self, demandante, demandado):
        """Actualiza los resultados visibles con info de BD (Lazy Loading)"""
        try:
            if not hasattr(self.app, 'tree'): return
            
            # PRESERVAR FOCO: Evitar que la actualización robe el foco
            foco_actual = self.app.master.focus_get()
            
            items = self.app.tree.get_children()
            for item_id in items:
                values = list(self.app.tree.item(item_id, 'values'))
                if len(values) >= 5:
                    # Actualizar columnas de Demandante/Demandado
                    # values: [Metodo, RutaRel, Dem1, Dem2, RutaAbs]
                    # Dem1 -> idx 2, Dem2 -> idx 3
                    values[2] = demandante or ""
                    values[3] = demandado or ""
                    
                    self.app.tree.item(item_id, values=tuple(values))
            
            # RESTAURAR FOCO si se perdió
            if foco_actual:
                try:
                    foco_actual.focus_set()
                except: pass
                    
            print(f"[UI] Metadata actualizada: {demandante} / {demandado}")
        except Exception as e:
            print(f"[UI ERROR] Falló actualizar metadata: {e}")

    def copiar_ruta(self):
        """Copia la ruta de la carpeta seleccionada al portapapeles"""
        try:
            datos = self.obtener_seleccion_tabla()
            if not datos: return
            
            ruta = datos['ruta_abs']
            if ruta:
                self.app.master.clipboard_clear()
                self.app.master.clipboard_append(ruta)
                self.actualizar_estado(f"Ruta copiada: {datos['nombre']}")
        except Exception as e:
            self.mostrar_error(f"Error al copiar ruta: {e}")

    def abrir_carpeta(self):
        """Abre la carpeta seleccionada en el explorador de Windows"""
        try:
            selection = self.app.tree.selection()
            if not selection: return
            
            # Obtener datos usando el nuevo método centralizado
            datos = self.obtener_seleccion_tabla()
            if not datos: return
            
            ruta = datos['ruta_abs']
            
            if ruta and os.path.exists(ruta):
                import subprocess
                os.startfile(ruta) if hasattr(os, 'startfile') else subprocess.Popen(['explorer', ruta])
                self.actualizar_estado(f"Abierta: {os.path.basename(ruta)}")
            else:
                self.mostrar_advertencia("La carpeta no existe o la ruta no es válida.")
        except Exception as e:
            self.mostrar_error(f"Error al abrir carpeta: {e}")

    def obtener_seleccion_tabla(self):
        """Retorna un diccionario con los datos del elemento seleccionado en el TreeView principal"""
        try:
            selection = self.app.tree.selection()
            if not selection:
                return None
            
            item_id = selection[0]
            item_data = self.app.tree.item(item_id)
            values = item_data.get('values', [])
            texto = item_data.get('text', "")
            
            if not values:
                return None
            
            # Limpiar nombre (quitar emoji si existe)
            nombre = texto.replace("📁 ", "").replace("📂 ", "").strip()
            
            # Según ResultsRenderer, values[0] es método, values[1] es ruta_rel
            metodo = values[0]
            ruta_info = values[1]
            
            # Determinar ruta absoluta
            if os.path.isabs(ruta_info):
                ruta_abs = ruta_info
                ruta_rel = os.path.relpath(ruta_info, self.app.ruta_carpeta) if hasattr(self.app, 'ruta_carpeta') else ruta_info
            else:
                ruta_rel = ruta_info
                ruta_abs = os.path.join(self.app.ruta_carpeta, ruta_info) if hasattr(self.app, 'ruta_carpeta') else ruta_info
            
            return {
                'id': item_id,
                'nombre': nombre,
                'metodo': metodo,
                'ruta_rel': ruta_rel,
                'ruta_abs': os.path.normpath(ruta_abs)
            }
        except Exception as e:
            print(f"[UIManager] Error obteniendo selección: {e}")
            return None

    # --- UTILIDADES DE COLUMNAS ---

    def _ajustar_columnas_inmediato(self):
        """Dispara el redimensionamiento inteligente de columnas"""
        if hasattr(self.app, 'results_column_config'):
            # El ColumnManager unificado maneja la carga y guardado, 
            # pero podemos forzar un ajuste aquí si es necesario.
            # Por ahora, simplemente actualizamos las columnas base si no hay config
            pass
        
        # Lógica de fallback para ajuste rápido
        try:
            self.app.tree.update_idletasks()
            if callable(getattr(self.app, 'configurar_scrollbars', None)):
                self.app.configurar_scrollbars()
        except: pass

    # --- DIÁLOGOS Y MENÚS ---

    def mostrar_advertencia(self, mensaje):
        messagebox.showwarning("Advertencia", mensaje)

    def mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)

    def mostrar_info(self, titulo, mensaje):
        messagebox.showinfo(titulo, mensaje)

    def mostrar_acerca_de(self):
        info = f"Búsqueda de Carpetas V.{self.app.version}\n© 2025 - Elkin Pérez Puyana"
        messagebox.showinfo("Acerca de", info)

    def buscar(self):
        """Shortcut para disparar búsqueda desde UI"""
        criterio = self.app.entry.get().strip()
        if criterio:
            self.app.search_coordinator.ejecutar_busqueda(criterio)
        else:
            self.mostrar_advertencia("Ingrese un criterio de búsqueda")

    def limpiar(self):
        """Reset completo de la vista de búsqueda"""
        self.limpiar_resultados()
        self.app.entry.delete(0, tk.END)
        self.actualizar_estado("Esperando búsqueda...")

    def salir(self):
        if messagebox.askokcancel("Salir", "¿Deseas cerrar la aplicación?"):
            self.app.master.quit()

    # --- ALIAS DE COMPATIBILIDAD ASYNC ---
    def actualizar_estado_async(self, mensaje):
        self.app.master.after(0, lambda: self.actualizar_estado(mensaje))
    
    def mostrar_resultados_async(self, resultados, metodo, tiempo_total):
        self.app.master.after(0, lambda: self.mostrar_resultados(resultados, metodo, tiempo_total))
    
    def finalizar_busqueda_async(self):
        self.app.master.after(0, self.habilitar_busqueda)
    
    def finalizar_busqueda_inmediata(self):
        self.habilitar_busqueda()