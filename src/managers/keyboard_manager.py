# src/keyboard_manager.py - Gestión de Teclado y Navegación V.11.4 (Alt+V)
import tkinter as tk
import threading
import time
import ctypes
from typing import Optional

class KeyboardManager:
    """Centraliza el manejo de atajos de teclado y navegación"""
    
    def __init__(self, app):
        self.app = app
    
    def configure_all_shortcuts(self):
        """Configura todos los atajos de teclado"""
        # Búsqueda
        self.app.entry.bind('<Return>', lambda e: self.app.buscar_carpeta())
        self.app.entry.bind('<KeyRelease>', self.app.ui_manager.on_entry_change)
        self.app.entry.bind('<Button-1>', lambda e: self.app.on_entry_click())
        
        # TreeView eventos
        self.app.tree.bind('<<TreeviewSelect>>', self.app.on_tree_select)
        self.app.tree.bind("<Double-1>", lambda e: self.app.event_manager.abrir_carpeta_seleccionada(), add="+")
        
        # Atajos principales
        shortcuts = {
            '<F1>': lambda e: self.app.mostrar_manual(),
            '<F4>': lambda e: self.app.ui_manager.cambiar_modo_entrada(),
            '<F5>': lambda e: self.app.ui_manager.enfocar_y_seleccionar_campo(),
            '<F6>': self._handle_f6,
            '<F7>': self._handle_f7,
            '<Control-u>': self._show_locations_config,
            '<Control-U>': self._show_locations_config,
        }
        
        for key, handler in shortcuts.items():
            self.app.master.bind(key, handler)
        
        # Atajos de paneles
        self.app.master.bind('<Control-Shift-h>', lambda e: self.toggle_historial())
        self.app.master.bind('<Control-Shift-H>', lambda e: self.toggle_historial())
        self.app.master.bind('<Control-Shift-e>', lambda e: self.toggle_explorador())
        self.app.master.bind('<Control-Shift-E>', lambda e: self.toggle_explorador())

        # F12: Toggle tema
        self.app.master.bind('<F12>', lambda e: self._toggle_tema())
        
        # Alt: Toggle menú
        self.app.master.bind('<Alt_L>', lambda e: self._toggle_menu())
        self.app.master.bind('<Alt_R>', lambda e: self._toggle_menu())

        self.setup_global_hotkey()
        self.configurar_navegacion_completa()
    
    def _show_locations_config(self, event=None):
        try:
            if hasattr(self.app, 'menu_manager'):
                self.app.menu_manager._show_locations_config()
        except Exception as e:
            print(f"Error abriendo configuración de ubicaciones: {e}")
    
    def _handle_f6(self, event):
        widget_with_focus = self.app.master.focus_get()
        if (hasattr(self.app, 'file_explorer_manager') and 
            self.app.file_explorer_manager and
            self.app.file_explorer_manager.is_visible()):
            if (hasattr(self.app.file_explorer_manager, 'tree') and 
                widget_with_focus == self.app.file_explorer_manager.tree):
                self.app.file_explorer_manager.copy_selected_path()
                return
        self.app.event_manager.copiar_ruta_seleccionada()
    
    def _handle_f7(self, event):
        widget_with_focus = self.app.master.focus_get()
        if (hasattr(self.app, 'file_explorer_manager') and 
            self.app.file_explorer_manager and
            self.app.file_explorer_manager.is_visible()):
            if (hasattr(self.app.file_explorer_manager, 'tree') and 
                widget_with_focus == self.app.file_explorer_manager.tree):
                self.app.file_explorer_manager.open_selected_item()
                return
        self.app.event_manager.abrir_carpeta_seleccionada()
    
    def toggle_historial(self):
        try:
            if hasattr(self.app, 'historial_manager') and self.app.historial_manager:
                self.app.historial_manager.toggle_visibility()
                self.app.mostrar_historial.set(self.app.historial_manager.visible)
                self.app.master.after(50, self.configurar_navegacion_completa)
        except Exception as e:
            print(f"[ERROR] toggle_historial: {e}")
    
    def toggle_explorador(self):
        try:
            if hasattr(self.app, 'file_explorer_manager') and self.app.file_explorer_manager:
                self.app.file_explorer_manager.toggle_visibility()
                self.app.master.after(50, self.configurar_navegacion_completa)
        except Exception as e:
            print(f"[ERROR] toggle_explorador: {e}")
    
    def configurar_navegacion_completa(self):
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
                self.app.file_explorer_manager.is_visible() and 
                self.app.file_explorer_manager.tree.winfo_exists()):
                
                if hasattr(self.app, 'dual_panel_manager'):
                    pos = self.app.dual_panel_manager.panel_positions.get('explorador')
                    if pos is not None: panels_by_position[pos] = self.app.file_explorer_manager.tree
                    
            if (hasattr(self.app, 'historial_manager') and 
                self.app.historial_manager and
                self.app.historial_manager.visible and
                self.app.historial_manager.tree.winfo_exists()):
                
                if hasattr(self.app, 'dual_panel_manager'):
                    pos = self.app.dual_panel_manager.panel_positions.get('historial')
                    if pos is not None: panels_by_position[pos] = self.app.historial_manager.tree
            
            for pos in sorted(panels_by_position.keys()):
                widgets_principales.append(panels_by_position[pos])
            
            for i, widget in enumerate(widgets_principales):
                if widget and widget.winfo_exists():
                    widget.configure(takefocus=True)
                    is_treeview = (hasattr(widget, 'winfo_class') and widget.winfo_class() == 'Treeview')
                    
                    if not is_treeview:
                        if i < len(widgets_principales) - 1:
                            nw = widgets_principales[i + 1]
                            widget.bind('<Tab>', lambda e, nw=nw: self.focus_widget_and_break(nw, e.widget))
                        else:
                            fw = widgets_principales[0]
                            widget.bind('<Tab>', lambda e, fw=fw: self.focus_widget_and_break(fw, e.widget))
                        
                        if i > 0:
                            pw = widgets_principales[i - 1]
                            widget.bind('<Shift-Tab>', lambda e, pw=pw: self.focus_widget_and_break(pw, e.widget))
                        else:
                            last_widget = widgets_principales[-1]
                            widget.bind('<Shift-Tab>', lambda e, lw=last_widget: self.focus_widget_and_break(lw, e.widget))
        except Exception as e:
            print(f"[DEBUG] Error configurando navegación: {e}")
    
    def focus_widget_and_break(self, widget, source_widget=None):
        try:
            if widget and widget.winfo_exists():
                widget.focus_set()
                if hasattr(widget, 'selection') and not widget.selection():
                    children = widget.get_children()
                    if children:
                        widget.selection_set(children[0])
                        widget.focus(children[0])
        except Exception as e:
            print(f"[DEBUG] Error enfocando widget: {e}")
        
        if source_widget and hasattr(source_widget, 'winfo_class'):
            if source_widget.winfo_class() == 'Treeview':
                return None
        return "break"
    
    def _toggle_tema(self):
        if hasattr(self.app, 'theme_manager'):
            self.app.theme_manager.toggle_tema()
            return "break"

    def _toggle_menu(self):
        if hasattr(self.app, 'menu_manager'):
            self.app.menu_manager.toggle_menu_visibility()

    def setup_global_hotkey(self):
        """Configura el atajo global Alt+V para traer la app al frente (V.11.4)"""
        try:
            from pynput import keyboard
            def on_activate():
                self.app.master.after(0, self._bring_to_front_and_focus)

            self.hotkey_listener = keyboard.GlobalHotKeys({
                '<alt>+v': on_activate
            })
            self.hotkey_listener.daemon = True
            self.hotkey_listener.start()
        except Exception as e:
            print(f"[ERROR] No se pudo iniciar el atajo global: {e}")

    def _bring_to_front_and_focus(self):
        """Trae la app al frente y OBLIGA a Windows a darle el foco del teclado (V.10.8)"""
        try:
            user32 = ctypes.windll.user32
            hwnd = self.app.master.winfo_id()
            foreground_hwnd = user32.GetForegroundWindow()
            foreground_thread_id = user32.GetWindowThreadProcessId(foreground_hwnd, None)
            current_thread_id = user32.GetCurrentThreadId()
            
            if foreground_thread_id != current_thread_id:
                user32.AttachThreadInput(foreground_thread_id, current_thread_id, True)
                user32.ShowWindow(hwnd, 9)
                user32.SetForegroundWindow(hwnd)
                user32.SetFocus(hwnd)
                user32.AttachThreadInput(foreground_thread_id, current_thread_id, False)
            else:
                user32.SetForegroundWindow(hwnd)
            
            self.app.master.deiconify()
            self.app.master.lift()
            self.app.master.attributes("-topmost", True)
            self.app.master.after(10, lambda: self.app.master.attributes("-topmost", False))
            self.app.master.focus_force()
            
            modal_active = (hasattr(self.app, 'content_search_modal') and 
                          self.app.content_search_modal and 
                          self.app.content_search_modal.modal and 
                          self.app.content_search_modal.modal.winfo_exists())
            
            if modal_active:
                modal = self.app.content_search_modal.modal
                m_hwnd = modal.winfo_id()
                if foreground_thread_id != current_thread_id:
                    user32.AttachThreadInput(foreground_thread_id, current_thread_id, True)
                    user32.ShowWindow(m_hwnd, 5)
                    user32.SetForegroundWindow(m_hwnd)
                    user32.SetFocus(m_hwnd)
                    user32.AttachThreadInput(foreground_thread_id, current_thread_id, False)
                
                modal.deiconify()
                modal.lift()
                modal.focus_force()
                
                notebook = self.app.content_search_modal.notebook
                tab_index = notebook.index(notebook.select())
                target_entry = None
                if tab_index == 0: target_entry = getattr(self.app.content_search_modal, 'search_entry_content', None)
                elif tab_index == 1: target_entry = getattr(self.app.content_search_modal, 'search_entry_files', None)

                if target_entry and target_entry.winfo_exists():
                    self.app.master.after(50, lambda: [
                        target_entry.focus_force(),
                        target_entry.selection_range(0, tk.END),
                        target_entry.icursor(tk.END)
                    ])
            else:
                search_entry = None
                if hasattr(self.app, 'ui') and hasattr(self.app.ui, 'search_entry'):
                    search_entry = self.app.ui.search_entry
                elif hasattr(self.app, 'entry'):
                    search_entry = self.app.entry
                
                if search_entry and search_entry.winfo_exists():
                    self.app.master.after(50, lambda: [
                        search_entry.focus_force(),
                        search_entry.selection_range(0, tk.END),
                        search_entry.icursor(tk.END)
                    ])
        except Exception as e:
            print(f"[ERROR] Error en Súper Enfoque: {e}")
