# src/navigation_manager.py - Gestión de Navegación V.4.2 (Refactorizado)
import tkinter as tk

class NavigationManager:
    """Maneja navegación por Tab, layout y ajuste de columnas"""
    
    def __init__(self, app):
        self.app = app
    
    def configurar_navegacion(self):
        """Configura la navegación inicial"""
        self.app.master.after_idle(self._configurar_navegacion_tab)
    
    def _configurar_navegacion_tab(self):
        """Configura navegación por Tab incluyendo historial si está visible"""
        elementos_navegacion = [
            self.app.entry,
            self.app.btn_buscar,
            self.app.btn_cancelar,
            self.app.tree,
            self.app.btn_copiar,
            self.app.btn_abrir
        ]
        
        # Agregar historial si está visible
        if self._historial_visible():
            elementos_navegacion.append(self.app.historial_manager.tree)
        
        # Configurar takefocus
        for elemento in elementos_navegacion:
            if hasattr(elemento, 'configure'):
                try:
                    elemento.configure(takefocus=True)
                except:
                    pass
        
        # Limpiar bindings anteriores
        self._limpiar_bindings(elementos_navegacion)
        
        # Configurar nuevos bindings
        for i, elemento in enumerate(elementos_navegacion):
            siguiente = elementos_navegacion[(i + 1) % len(elementos_navegacion)]
            anterior = elementos_navegacion[(i - 1) % len(elementos_navegacion)]
            
            try:
                elemento.bind("<Tab>", lambda e, sig=siguiente: self._ir_a_elemento(sig))
                elemento.bind("<Shift-Tab>", lambda e, ant=anterior: self._ir_a_elemento(ant))
            except:
                pass
    
    def _historial_visible(self):
        """Verifica si el historial está visible"""
        return (hasattr(self.app, 'historial_manager') and 
                self.app.historial_manager.visible and 
                self.app.historial_manager.tree)
    
    def _limpiar_bindings(self, elementos):
        """Limpia bindings anteriores"""
        for widget in elementos:
            try:
                widget.unbind("<Tab>")
                widget.unbind("<Shift-Tab>")
            except:
                pass
    
    def _ir_a_elemento(self, elemento):
        """Navega al elemento especificado"""
        try:
            elemento.focus_set()
            
            if hasattr(elemento, 'get_children'):  # Es un TreeView
                children = elemento.get_children()
                if children and not elemento.selection():
                    elemento.selection_set(children[0])
                    elemento.focus(children[0])
                    elemento.see(children[0])
                elemento.focus_set()
                
        except (tk.TclError, AttributeError):
            pass
        
        return "break"
    
    def actualizar_navegacion_tab(self):
        """Actualiza navegación Tab cuando cambia visibilidad del historial"""
        self._configurar_navegacion_tab()
        self.app.master.after(50, self._configurar_navegacion_tab)
        self._ajustar_columnas_tree()
    
    def ajustar_layout_para_historial(self, mostrar_historial):
        """Ajusta layout cuando se muestra/oculta historial"""
        try:
            if mostrar_historial:
                # Reducir ancho del contenedor principal
                self.app.main_container.pack_forget()
                self.app.main_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 5), pady=10)
            else:
                # Restaurar contenedor original
                self.app.main_container.pack_forget()
                self.app.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            self._ajustar_columnas_tree()
            self.app.master.update_idletasks()
            
        except Exception as e:
            print(f"Error en ajustar_layout_para_historial: {e}")
    
    def _ajustar_columnas_tree(self):
        """Ajusta columnas del TreeView según espacio disponible"""
        try:
            historial_visible = self._historial_visible()
            
            if historial_visible:
                # Modo compacto - historial visible
                configuracion = {
                    "#0": {"width": 180, "minwidth": 120},
                    "Método": {"width": 25, "minwidth": 22},
                    "Ruta": {"width": 300, "minwidth": 200}
                }
            else:
                # Modo normal - historial oculto
                configuracion = {
                    "#0": {"width": 200, "minwidth": 150},
                    "Método": {"width": 35, "minwidth": 30},
                    "Ruta": {"width": 400, "minwidth": 250}
                }
            
            for col, config in configuracion.items():
                self.app.tree.column(col, **config)
            
            self.app.tree.update_idletasks()
            
        except Exception as e:
            print(f"Error ajustando columnas: {e}")
    
    def toggle_historial(self):
        """Método de compatibilidad para alternar historial"""
        if hasattr(self.app, 'historial_manager'):
            self.app.historial_manager.toggle_visibility()
        else:
            print("ERROR: historial_manager no disponible")