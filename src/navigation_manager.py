# src/navigation_manager.py - Gestión de Navegación V.4.1
import tkinter as tk

class NavigationManager:
    """Maneja la navegación por Tab y layout de la aplicación"""
    
    def __init__(self, app):
        self.app = app
    
    def configurar_navegacion(self):
        """Configura la navegación inicial"""
        # Configurar después de que todos los elementos estén creados
        self.app.master.after_idle(self._configurar_navegacion_tab)
    
    def _configurar_navegacion_tab(self):
        """Configura la navegación por Tab incluyendo el historial si está visible"""
        
        # Orden básico de navegación
        elementos_navegacion = [
            self.app.entry,
            self.app.btn_buscar,
            self.app.btn_cancelar,
            self.app.tree,
            self.app.btn_copiar,
            self.app.btn_abrir
        ]
        
        # Agregar historial al final si está visible
        if (hasattr(self.app, 'historial_manager') and 
            self.app.historial_manager.visible and 
            self.app.historial_manager.tree):
            elementos_navegacion.append(self.app.historial_manager.tree)
        
        # Configurar takefocus para todos los elementos
        for elemento in elementos_navegacion:
            if hasattr(elemento, 'configure'):
                try:
                    elemento.configure(takefocus=True)
                except:
                    pass
        
        # Limpiar todos los bindings anteriores
        all_widgets = [self.app.entry, self.app.btn_buscar, self.app.btn_cancelar, 
                      self.app.tree, self.app.btn_copiar, self.app.btn_abrir]
        if hasattr(self.app, 'historial_manager') and self.app.historial_manager.tree:
            all_widgets.append(self.app.historial_manager.tree)
        
        for widget in all_widgets:
            try:
                widget.unbind("<Tab>")
                widget.unbind("<Shift-Tab>")
            except:
                pass
        
        # Configurar nuevos bindings
        for i, elemento in enumerate(elementos_navegacion):
            siguiente = elementos_navegacion[(i + 1) % len(elementos_navegacion)]
            anterior = elementos_navegacion[(i - 1) % len(elementos_navegacion)]
            
            try:
                elemento.bind("<Tab>", lambda e, sig=siguiente: self._ir_a_elemento(sig))
                elemento.bind("<Shift-Tab>", lambda e, ant=anterior: self._ir_a_elemento(ant))
            except:
                pass
    
    def _ir_a_elemento(self, elemento):
        """Navega al elemento especificado"""
        try:
            # Forzar el foco al elemento
            elemento.focus_set()
            
            if hasattr(elemento, 'get_children'):  # Es un TreeView
                children = elemento.get_children()
                if children:
                    # Si hay elementos en el TreeView, seleccionar el primero si no hay selección
                    if not elemento.selection():
                        elemento.selection_set(children[0])
                        elemento.focus(children[0])
                        elemento.see(children[0])
                # Asegurar que el TreeView tenga el foco
                elemento.focus_set()
            else:
                # Para botones y otros elementos
                elemento.focus_set()
                
        except (tk.TclError, AttributeError) as e:
            # El elemento ya no existe o hay un problema
            print(f"Error navegando a elemento: {e}")
            pass
        
        return "break"
    
    def actualizar_navegacion_tab(self):
        """Actualiza la navegación por Tab cuando cambia la visibilidad del historial"""
        # Llamar inmediatamente y también con delay para asegurar
        self._configurar_navegacion_tab()
        self.app.master.after(50, self._configurar_navegacion_tab)
    
    def ajustar_layout_para_historial(self, mostrar_historial):
        """Ajusta el layout cuando se muestra/oculta el historial"""
        if mostrar_historial:
            # CORREGIDO: Contraer más el contenedor principal para hacer espacio al historial
            self.app.main_container.configure(width=600)  # Reducido de 700 a 600
            self.app.main_container.pack_configure(side=tk.LEFT, fill=tk.Y, padx=(20, 0))  # Menos padding
        else:
            # Expandir el contenedor principal a todo el ancho
            self.app.main_container.configure(width=1050)  # Ancho completo
            self.app.main_container.pack_configure(side=tk.TOP, fill=tk.BOTH, expand=True, padx=30)
        
        # Forzar actualización
        self.app.master.update_idletasks()