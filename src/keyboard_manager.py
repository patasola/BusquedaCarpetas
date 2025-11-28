# src/keyboard_manager.py - Gestión de Teclado y Navegación V.4.5 (Remapeado)
import tkinter as tk

class KeyboardManager:
    """Centraliza el manejo de atajos de teclado y navegación"""
    
    def __init__(self, app):
        self.app = app
    
    def configure_all_shortcuts(self):
        """Configura todos los atajos de teclado"""
        # Búsqueda
        self.app.entry.bind('<Return>', lambda e: self.app.buscar_carpeta())
        self.app.entry.bind('<KeyRelease>', self.app.ui_state_manager.on_entry_change)
        self.app.entry.bind('<Button-1>', lambda e: self.app.on_entry_click())
        
        # TreeView eventos
        self.app.tree.bind('<<TreeviewSelect>>', self.app.on_tree_select)
        self.app.tree.bind("<Double-1>", lambda e: self.app.event_manager.abrir_carpeta_seleccionada())
        
        # Atajos principales REMAPEADOS
        shortcuts = {
            '<F1>': lambda e: self.app.mostrar_manual(),  # Ayuda/Manual
            '<F4>': lambda e: self.app.ui_state_manager.cambiar_modo_entrada(),  # Cambiar modo numérico/alfanumérico
            '<F5>': lambda e: self.app.ui_state_manager.enfocar_y_seleccionar_campo(),  # Enfocar búsqueda
            '<F6>': self._handle_f6,  # Copiar ruta
            '<F7>': self._handle_f7,  # Abrir carpeta
            '<Control-u>': self._show_locations_config,
            '<Control-U>': self._show_locations_config,
        }
        
        for key, handler in shortcuts.items():
            self.app.master.bind(key, handler)
        
        # Atajos especiales para paneles - USANDO CTRL+SHIFT (más confiable en Windows)
        # Historial - Ctrl+Shift+H
        self.app.master.bind('<Control-Shift-h>', lambda e: self.toggle_historial())
        self.app.master.bind('<Control-Shift-H>', lambda e: self.toggle_historial())
        self.app.master.bind('<Control-Shift-Key-h>', lambda e: self.toggle_historial())

        # Explorador - Ctrl+Shift+E  
        self.app.master.bind('<Control-Shift-e>', lambda e: self.toggle_explorador())
        self.app.master.bind('<Control-Shift-E>', lambda e: self.toggle_explorador())
        self.app.master.bind('<Control-Shift-Key-e>', lambda e: self.toggle_explorador())

        # F12: Toggle tema
        self.app.master.bind('<F12>', lambda e: self._toggle_tema())

        print("[DEBUG] Atajos de paneles configurados:")
        print("  - Ctrl+Shift+H: Historial")
        print("  - Ctrl+Shift+E: Explorador")
        
        # Configurar navegación Tab
        self.configurar_navegacion_completa()
    
    def _show_locations_config(self, event=None):
        """Muestra configuración de ubicaciones con Ctrl+U"""
        try:
            if hasattr(self.app, 'menu_manager'):
                self.app.menu_manager._show_locations_config()
        except Exception as e:
            print(f"Error abriendo configuración de ubicaciones: {e}")
    
    def _handle_f2_global(self, event):
        """Maneja F2 - Renombrar inline SOLO en explorador de archivos"""
        focused_widget = self.app.master.focus_get()
        
        # F2 es SOLO para renombrar en el explorador de archivos
        if (hasattr(self.app, 'file_explorer_manager') and 
            self.app.file_explorer_manager and
            hasattr(self.app.file_explorer_manager, 'tree') and
            self.app.file_explorer_manager.tree and 
            focused_widget == self.app.file_explorer_manager.tree):
            # Dejar que el explorador maneje F2 para renombrar
            return
        else:
            # Si no está en el explorador, no hacer nada o mostrar mensaje
            if hasattr(self.app, 'ui_callbacks'):
                self.app.ui_callbacks.actualizar_estado("F2: Renombrar (solo en explorador de archivos)")
    
    def _handle_f6(self, event):
        """Maneja F6 - Copiar ruta según el componente que tenga el foco"""
        widget_with_focus = self.app.master.focus_get()
        
        # Verificar si el foco está en el explorador de archivos
        if (hasattr(self.app, 'file_explorer_manager') and 
            self.app.file_explorer_manager and
            hasattr(self.app.file_explorer_manager, 'is_visible') and
            self.app.file_explorer_manager.is_visible()):
            if (hasattr(self.app.file_explorer_manager, 'tree') and 
                widget_with_focus == self.app.file_explorer_manager.tree):
                self.app.file_explorer_manager.copy_selected_path()
                return
        
        # Por defecto, copiar del TreeView principal
        self.app.event_manager.copiar_ruta_seleccionada()
    
    def _handle_f7(self, event):
        """Maneja F7 - Abrir carpeta según el componente que tenga el foco"""
        widget_with_focus = self.app.master.focus_get()
        
        # Verificar si el foco está en el explorador de archivos
        if (hasattr(self.app, 'file_explorer_manager') and 
            self.app.file_explorer_manager and
            hasattr(self.app.file_explorer_manager, 'is_visible') and
            self.app.file_explorer_manager.is_visible()):
            if (hasattr(self.app.file_explorer_manager, 'tree') and 
                widget_with_focus == self.app.file_explorer_manager.tree):
                self.app.file_explorer_manager.open_selected_item()
                return
        
        # Por defecto, abrir del TreeView principal
        self.app.event_manager.abrir_carpeta_seleccionada()
    
    def toggle_historial(self):
        """Toggle para historial con posicionamiento dual"""
        print("[DEBUG] toggle_historial() llamado")
        try:
            if hasattr(self.app, 'historial_manager') and self.app.historial_manager:
                self.app.historial_manager.toggle_visibility()
                self.app.mostrar_historial.set(self.app.historial_manager.visible)
                self.app.master.after(50, self.configurar_navegacion_completa)
            else:
                print("[ERROR] historial_manager no disponible")
        except Exception as e:
            print(f"[ERROR] toggle_historial: {e}")
    
    def toggle_explorador(self):
        """Toggle para explorador de archivos con posicionamiento dual"""
        print("[DEBUG] toggle_explorador() llamado")
        try:
            if hasattr(self.app, 'file_explorer_manager') and self.app.file_explorer_manager:
                self.app.file_explorer_manager.toggle_visibility()
                self.app.master.after(50, self.configurar_navegacion_completa)
            else:
                print("[ERROR] file_explorer_manager no disponible")
        except Exception as e:
            print(f"[ERROR] toggle_explorador: {e}")
    
    def configurar_navegacion_completa(self):
        """Configura la navegación Tab usando el sistema nativo de Tkinter para paneles duales"""
        try:
            widgets_principales = []
            
            main_widgets = [self.app.entry, self.app.btn_buscar, self.app.btn_cancelar, 
                           self.app.tree, self.app.btn_copiar, self.app.btn_abrir]
            
            for widget in main_widgets:
                if widget and widget.winfo_exists():
                    widgets_principales.append(widget)
            
            panels_by_position = {}
            
            if (hasattr(self.app, 'file_explorer_manager') and 
                self.app.file_explorer_manager and
                hasattr(self.app.file_explorer_manager, 'is_visible') and
                self.app.file_explorer_manager.is_visible() and 
                hasattr(self.app.file_explorer_manager, 'tree') and
                self.app.file_explorer_manager.tree and
                self.app.file_explorer_manager.tree.winfo_exists()):
                
                if hasattr(self.app, 'dual_panel_manager'):
                    position = self.app.dual_panel_manager.panel_positions.get('explorador')
                    if position is not None:
                        panels_by_position[position] = self.app.file_explorer_manager.tree
                    
            if (hasattr(self.app, 'historial_manager') and 
                self.app.historial_manager and
                hasattr(self.app.historial_manager, 'visible') and 
                self.app.historial_manager.visible and
                hasattr(self.app.historial_manager, 'tree') and 
                self.app.historial_manager.tree and
                self.app.historial_manager.tree.winfo_exists()):
                
                if hasattr(self.app, 'dual_panel_manager'):
                    position = self.app.dual_panel_manager.panel_positions.get('historial')
                    if position is not None:
                        panels_by_position[position] = self.app.historial_manager.tree
            
            for pos in sorted(panels_by_position.keys()):
                widgets_principales.append(panels_by_position[pos])
            
            for i, widget in enumerate(widgets_principales):
                if widget and widget.winfo_exists():
                    widget.configure(takefocus=True)
                    
                    if i < len(widgets_principales) - 1:
                        next_widget = widgets_principales[i + 1]
                        widget.bind('<Tab>', lambda e, nw=next_widget: self.focus_widget_and_break(nw))
                    else:
                        first_widget = widgets_principales[0]
                        widget.bind('<Tab>', lambda e, fw=first_widget: self.focus_widget_and_break(fw))
                    
                    if i > 0:
                        prev_widget = widgets_principales[i - 1]
                        widget.bind('<Shift-Tab>', lambda e, pw=prev_widget: self.focus_widget_and_break(pw))
                    else:
                        last_widget = widgets_principales[-1]
                        widget.bind('<Shift-Tab>', lambda e, lw=last_widget: self.focus_widget_and_break(lw))
            
            print(f"[DEBUG] Navegación configurada para {len(widgets_principales)} widgets")
            
        except Exception as e:
            print(f"[DEBUG] Error configurando navegación: {e}")
    
    def focus_widget_and_break(self, widget):
        """Enfoca un widget y detiene la propagación del evento Tab"""
        try:
            if widget and widget.winfo_exists():
                widget.focus_set()
                
                if hasattr(widget, 'selection'):
                    if not widget.selection():
                        children = widget.get_children()
                        if children:
                            widget.selection_set(children[0])
                            widget.focus(children[0])
                            
                print(f"[DEBUG] Foco establecido en: {widget.winfo_class()}")
        except Exception as e:
            print(f"[DEBUG] Error enfocando widget: {e}")
        
        return "break"
    
    def get_shortcuts_help(self):
        """Obtiene ayuda de atajos de teclado ACTUALIZADA"""
        return {
            'busqueda': {
                'F4': 'Cambiar modo numérico/alfanumérico',
                'F5': 'Enfocar campo de búsqueda',
                'Enter': 'Ejecutar búsqueda'
            },
            'navegacion': {
                'Tab': 'Navegar entre elementos',
                'Shift+Tab': 'Navegar hacia atrás',
                'F6': 'Copiar ruta seleccionada',
                'F7': 'Abrir carpeta seleccionada'
            },
            'explorador': {
                'F2': 'Renombrar archivo/carpeta (solo en explorador)'
            },
            'paneles': {
                'Ctrl+Shift+H': 'Alternar historial',
                'Ctrl+Shift+E': 'Alternar explorador'
            },
            'ayuda': {
                'F1': 'Mostrar ayuda',
                'Ctrl+U': 'Configurar ubicaciones de búsqueda'
            }
        }
    
    def reset_all_bindings(self):
        """Resetea todos los bindings de teclado"""
        try:
            shortcuts_to_unbind = [
                '<F1>', '<F4>', '<F5>', '<F6>', '<F7>',
                '<Control-u>', '<Control-U>',
                '<Control-Shift-h>', '<Control-Shift-H>',
                '<Control-Shift-e>', '<Control-Shift-E>',
            ]
            
            for shortcut in shortcuts_to_unbind:
                try:
                    self.app.master.unbind(shortcut)
                except:
                    pass
            
            print("[DEBUG] Todos los atajos de teclado han sido reseteados")
            
        except Exception as e:
            print(f"[DEBUG] Error reseteando bindings: {e}")
    
    def validate_keyboard_state(self):
        """Valida el estado actual del teclado"""
        validation_result = {
            'shortcuts_configured': False,
            'navigation_working': False,
            'panels_responsive': False
        }
        
        try:
            main_widgets_exist = all([
                hasattr(self.app, 'entry') and self.app.entry,
                hasattr(self.app, 'tree') and self.app.tree,
                hasattr(self.app, 'btn_buscar') and self.app.btn_buscar
            ])
            
            validation_result['shortcuts_configured'] = main_widgets_exist
            validation_result['navigation_working'] = main_widgets_exist
            
            historial_ok = (hasattr(self.app, 'historial_manager') and 
                           self.app.historial_manager is not None)
            explorador_ok = (hasattr(self.app, 'file_explorer_manager') and 
                            self.app.file_explorer_manager is not None)
            
            validation_result['panels_responsive'] = historial_ok and explorador_ok
            
        except Exception as e:
            print(f"[DEBUG] Error validando estado del teclado: {e}")
        
        return validation_result

    def _toggle_tema(self):
        """Toggle entre modo claro y oscuro"""
        if hasattr(self.app, 'theme_manager'):
            self.app.theme_manager.toggle_tema()
            return "break"