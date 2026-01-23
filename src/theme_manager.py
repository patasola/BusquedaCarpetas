# src/theme_manager.py - V3 con callbacks y actualización dinámica
import tkinter as tk
from tkinter import ttk
import ctypes
import os
import sys

class ThemeManager:
    """Gestiona los temas (modo oscuro/claro) de la aplicación"""
    
    # Definición de paletas de colores
    TEMAS = {
        "claro": {
            # Base Colors
            "bg": "#f5f5f5",              # bg_primary - Fondo principal
            "bg_alt": "#ffffff",          # bg_secondary - Fondo secundario
            "bg_surface": "#e8e8e8",      # Superficies elevadas
            
            # Text Colors
            "fg": "#2c3e50",              # text_primary - Texto principal
            "fg_alt": "#7f8c8d",          # text_secondary - Texto secundario
            "fg_disabled": "#bdc3c7",     # text_disabled
            
            # Accent Colors
            "accent_primary": "#3498db",  # Azul principal
            "accent_hover": "#5dade2",    # Hover
            "success": "#27ae60",         # Verde - solo para éxito
            "warning": "#e67e22",         # Naranja - advertencias
            "error": "#e74c3c",           # Rojo - errores
            
            # Button Colors
            "button_bg": "#e0e0e0",       # Fondo de botones neutro
            "button_fg": "#2c3e50",       # Texto de botones
            "button_hover": "#d0d0d0",    # Hover
            "button_active_bg": "#3498db", # Activo
            "button_active_fg": "#ffffff", # Texto activo
            
            # Legacy mappings for compatibility
            "entry_bg": "#ffffff",
            "entry_fg": "#2c3e50",
            "entry_border": "#bdc3c7",
            "tree_bg": "#ffffff",
            "tree_fg": "#2c3e50",
            "tree_selected_bg": "#3498db",
            "tree_selected_fg": "#ffffff",
            "tree_field_bg": "#ffffff",
            "tree_heading_bg": "#e8e8e8",
            "frame_bg": "#f5f5f5",
            "border": "#bdc3c7",
            "status_bg": "#e8e8e8",
            "status_fg": "#2c3e50",
            "menu_bg": "#f5f5f5",
            "menu_fg": "#2c3e50",
            "menu_active_bg": "#3498db",
            "menu_active_fg": "#ffffff",
            "menu_active_fg": "#ffffff",
            
            # Method Colors (Tags)
            "tag_cache_bg": "#e8f5e8", "tag_cache_fg": "#1b5e20",
            "tag_traditional_bg": "#e3f2fd", "tag_traditional_fg": "#0d47a1",
            "tag_tree_bg": "#fff3e0", "tag_tree_fg": "#e65100",
            "tag_unknown_bg": "#f5f5f5", "tag_unknown_fg": "#424242",
        },
        "oscuro": {
            "bg": "#1e1e1e",
            "fg": "#d4d4d4",
            "bg_alt": "#252526",
            "fg_alt": "#cccccc",
            "button_bg": "#333333",
            "button_fg": "#d4d4d4",
            "button_active_bg": "#3e3e42",
            "entry_bg": "#252526",
            "entry_fg": "#d4d4d4",
            "entry_border": "#3e3e42",
            # TreeView - Colores EXACTOS según especificación
            "tree_bg": "#333333",  # Fondo contenido
            "tree_fg": "#cccccc",  # Texto items
            "tree_selected_bg": "#0974bc",
            "tree_selected_fg": "#ffffff",
            "tree_field_bg": "#333333",  # Mismo que tree_bg
            "tree_heading_bg": "#2d2f32",  # Headers columnas
            "tree_heading_fg": "#cccccc",  # Texto headers
            "frame_bg": "#1e1e1e",
            "border": "#3e3e42",
            "status_bg": "#007acc",
            "status_fg": "#ffffff",
            # Menú
            "menu_bg": "#2d2d30",
            "menu_fg": "#e0e0e0",
            "menu_active_bg": "#0974bc",
            "menu_active_fg": "#ffffff",
            "menu_active_fg": "#ffffff",
            
            # Method Colors (Tags) - DARK MODE
            "tag_cache_bg": "#0d2b10", "tag_cache_fg": "#81c784",  # Verde oscuro/claro
            "tag_traditional_bg": "#0d1b2a", "tag_traditional_fg": "#64b5f6",  # Azul oscuro/claro
            "tag_tree_bg": "#331e0d", "tag_tree_fg": "#ffb74d",  # Naranja oscuro/claro
            "tag_unknown_bg": "#2d2d30", "tag_unknown_fg": "#9e9e9e",  # Gris oscuro/claro
        }
    }
    
    def __init__(self, app, tema_inicial="claro"):
        self.app = app
        self.tema_actual = tema_inicial
        self.colores = self.TEMAS[tema_inicial].copy()
        self.theme_callbacks = []
    
    def get_color(self, key):
        return self.colores.get(key, "#FFFFFF")
    
    def apply_theme_to_item(self, tree, item_id):
        """Aplica tema a un item individual del TreeView (para items nuevos)"""
        try:
            # PRIMERO: Asegurar que tag esté configurada
            tree.tag_configure('themed',
                foreground=self.colores["tree_fg"],
                background=self.colores["tree_bg"]
            )
            
            # SEGUNDO: Obtener tags existentes y añadir 'themed'
            current_tags = list(tree.item(item_id, 'tags'))
            if 'themed' not in current_tags:
                current_tags.append('themed')
            tree.item(item_id, tags=current_tags)
        except Exception as e:
            print(f"[ThemeManager] Error aplicando tema a item: {e}")
    
    def register_callback(self, callback):
        """Registra callback para notificaciones de cambio de tema"""
        if callback not in self.theme_callbacks:
            self.theme_callbacks.append(callback)
    
    def _notify_callbacks(self):
        """Notifica a todos los callbacks"""
        for callback in self.theme_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"[ThemeManager] Error en callback: {e}")
    
    def cambiar_tema(self, nombre_tema):
        if nombre_tema not in self.TEMAS:
            return
        
        self.tema_actual = nombre_tema
        self.colores = self.TEMAS[nombre_tema].copy()
        self.aplicar_tema()
        self._notify_callbacks()
    
    def toggle_tema(self):
        nuevo_tema = "oscuro" if self.tema_actual == "claro" else "claro"
        self.cambiar_tema(nuevo_tema)
    
    def aplicar_tema(self):
        """Aplica el tema actual a todos los widgets"""
        self.app.master.configure(bg=self.colores["bg"])
        self._aplicar_tema_recursivo(self.app.master)
        self._configurar_estilos_ttk()
        self._configurar_estilos_ttk()
        self._actualizar_treeviews()
        self._aplicar_modo_oscuro_windows()
    
    def _aplicar_modo_oscuro_windows(self):
        """Intenta aplicar modo oscuro a la barra de título de Windows"""
        try:
            if sys.platform != "win32":
                return
                
            # Obtener HWND
            hwnd = ctypes.windll.user32.GetParent(self.app.master.winfo_id())
            
            # Constantes DWM
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
            
            # Determinar valor (1 = True/Oscuro, 0 = False/Claro)
            value = 1 if self.tema_actual == "oscuro" else 0
            value = ctypes.c_int(value)
            
            # Intentar aplicar (Windows 11 / 10 20H1+)
            try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(value), 
                    ctypes.sizeof(value)
                )
            except:
                # Fallback para versiones anteriores de Windows 10
                try:
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, 
                        DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
                        ctypes.byref(value), 
                        ctypes.sizeof(value)
                    )
                except:
                    pass
        except Exception as e:
            print(f"[ThemeManager] Error aplicando modo oscuro Windows: {e}")
    
    def _aplicar_tema_recursivo(self, widget):
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == "Frame":
                widget.configure(bg=self.colores["frame_bg"])
            elif widget_class == "Label":
                widget.configure(bg=self.colores["bg"], fg=self.colores["fg"])
            elif widget_class == "Button":
                widget.configure(
                    bg=self.colores["button_bg"],
                    fg=self.colores["button_fg"],
                    activebackground=self.colores["button_active_bg"],
                    activeforeground=self.colores["button_fg"]
                )
            elif widget_class == "Entry":
                widget.configure(
                    bg=self.colores["entry_bg"],
                    fg=self.colores["entry_fg"],
                    insertbackground=self.colores["entry_fg"]
                )
            elif widget_class == "Text":
                widget.configure(
                    bg=self.colores["entry_bg"],
                    fg=self.colores["entry_fg"],
                    insertbackground=self.colores["entry_fg"]
                )
            elif widget_class == "Listbox":
                widget.configure(
                    bg=self.colores["tree_bg"],
                    fg=self.colores["tree_fg"],
                    selectbackground=self.colores["tree_selected_bg"],
                    selectforeground=self.colores["tree_selected_fg"]
                )
            elif widget_class == "Menu":
                widget.configure(
                    bg=self.colores["menu_bg"],
                    fg=self.colores["menu_fg"],
                    activebackground=self.colores["menu_active_bg"],
                    activeforeground=self.colores["menu_active_fg"]
                )
            
            for child in widget.winfo_children():
                self._aplicar_tema_recursivo(child)
        except:
            pass
    
    def _actualizar_treeviews(self):
        """Actualiza TreeViews usando TAGS (funciona en Windows)"""
        print(f"[ThemeManager] Aplicando tema {self.tema_actual} a TreeViews")
        
        try:
            # Configurar tag universal para items
            tag_colors = {
                'fg': self.colores["tree_fg"],
                'bg': self.colores["tree_bg"]
            }
            
            # TreeView principal
            if hasattr(self.app, 'tree') and self.app.tree:
                self._apply_theme_to_tree(self.app.tree, "Principal", tag_colors)
            
            # TreeView historial
            if hasattr(self.app, 'historial_manager') and self.app.historial_manager:
                if hasattr(self.app.historial_manager, 'tree') and self.app.historial_manager.tree:
                    self._apply_theme_to_tree(self.app.historial_manager.tree, "Historial", tag_colors)
            
            # TreeView explorador
            if hasattr(self.app, 'file_explorer') and self.app.file_explorer:
                if hasattr(self.app.file_explorer, 'tree') and self.app.file_explorer.tree:
                    self._apply_theme_to_tree(self.app.file_explorer.tree, "Explorador", tag_colors)
                            
        except Exception as e:
            print(f"[ThemeManager] Error actualizando TreeViews: {e}")
    
    def _apply_theme_to_tree(self, tree, nombre, tag_colors):
        """Aplica tema a un TreeView específico usando tags"""
        try:
            print(f"[ThemeManager] Actualizando TreeView {nombre}")
            
            # 1. Configurar tag 'themed' con colores
            tree.tag_configure('themed',
                foreground=tag_colors['fg'],
                background=tag_colors['bg']
            )
            
            # 2. Aplicar tag a TODOS los items existentes
            def apply_to_items(parent=''):
                items = tree.get_children(parent)
                for item in items:
                    # Obtener tags existentes
                    current_tags = list(tree.item(item, 'tags'))
                    # Añadir 'themed' si no existe
                    if 'themed' not in current_tags:
                        current_tags.append('themed')
                    tree.item(item, tags=current_tags)
                    # Recursivo para hijos
                    apply_to_items(item)
            
            apply_to_items()
            
            # 3. Actualizar frame contenedor
            if tree.master:
                try:
                    tree.master.configure(bg=self.colores["tree_bg"])
                except:
                    pass
            
            # 4. Forzar refresh visual
            tree.update_idletasks()
            
            print(f"[ThemeManager] TreeView {nombre} actualizado exitosamente")
            
            # 5. Configurar tags de métodos (NUEVO)
            self._configurar_tags_metodos(tree)
            
        except Exception as e:
            print(f"[ThemeManager] Error en TreeView {nombre}: {e}")
    
    def _configurar_estilos_ttk(self):
        """Configura los estilos de ttk"""
        style = ttk.Style()
        
        try:
            style.theme_use('clam')
        except:
            pass
        
        # TreeView styles
        for style_name in ["Treeview", "Custom.Treeview"]:
            style.configure(style_name,
                background=self.colores["tree_bg"],
                foreground=self.colores["tree_fg"],
                fieldbackground=self.colores["tree_field_bg"],
                borderwidth=0 if style_name == "Treeview" else 1,
                relief="flat" if style_name == "Treeview" else "solid"
            )
            
            style.map(style_name,
                background=[("selected", self.colores["tree_selected_bg"])],
                foreground=[("selected", self.colores["tree_selected_fg"])]
            )
        
        # Headings
        heading_bg = self.colores.get("tree_heading_bg", self.colores["button_bg"])
        heading_fg = self.colores.get("tree_heading_fg", self.colores["button_fg"])  # Usar gris suave
        for heading_name in ["Treeview.Heading", "Custom.Treeview.Heading"]:
            style.configure(heading_name,
                background=heading_bg,
                foreground=heading_fg,  # GRIS SUAVE
                relief="flat",
                borderwidth=0 if heading_name == "Treeview.Heading" else 1
            )
            
            style.map(heading_name,
                background=[("active", self.colores["button_active_bg"])]
            )
    
    def get_tema_actual(self):
        return self.tema_actual
    def get_tema_actual(self):
        return self.tema_actual

    def _configurar_tags_metodos(self, tree):
        """Configura los tags de métodos con los colores del tema actual"""
        try:
            # Tags base de métodos
            method_tags = {
                'cache_method': {'foreground': self.colores["tag_cache_fg"], 'background': self.colores["tag_cache_bg"]},
                'tradicional_method': {'foreground': self.colores["tag_traditional_fg"], 'background': self.colores["tag_traditional_bg"]},
                'tree_method': {'foreground': self.colores["tag_tree_fg"], 'background': self.colores["tag_tree_bg"]},
                'unknown_method': {'foreground': self.colores["tag_unknown_fg"], 'background': self.colores["tag_unknown_bg"]}
            }
            
            for tag, config in method_tags.items():
                tree.tag_configure(tag, **config)
            
            # Tags combinados (evenrow/oddrow + método)
            # En modo oscuro, podemos querer que evenrow/oddrow sean sutilmente diferentes o iguales
            # Para simplificar y garantizar legibilidad, usaremos los mismos colores base del método
            # pero quizás con una ligera variación si fuera necesario. Por ahora, directos.
            
            combined_tags = [
                ('evenrow_cache', self.colores["tag_cache_bg"], self.colores["tag_cache_fg"]),
                ('evenrow_tradicional', self.colores["tag_traditional_bg"], self.colores["tag_traditional_fg"]),
                ('evenrow_tree', self.colores["tag_tree_bg"], self.colores["tag_tree_fg"]),
                ('evenrow_unknown', self.colores["tag_unknown_bg"], self.colores["tag_unknown_fg"]),
                ('oddrow_cache', self.colores["tag_cache_bg"], self.colores["tag_cache_fg"]),
                ('oddrow_tradicional', self.colores["tag_traditional_bg"], self.colores["tag_traditional_fg"]),
                ('oddrow_tree', self.colores["tag_tree_bg"], self.colores["tag_tree_fg"]),
                ('oddrow_unknown', self.colores["tag_unknown_bg"], self.colores["tag_unknown_fg"])
            ]
            
            for tag, bg, fg in combined_tags:
                tree.tag_configure(tag, background=bg, foreground=fg)
                
            # Configurar evenrow/oddrow genéricos
            tree.tag_configure('evenrow', background=self.colores["tree_bg"], foreground=self.colores["tree_fg"])
            tree.tag_configure('oddrow', background=self.colores["tree_bg"], foreground=self.colores["tree_fg"])
            
        except Exception as e:
            print(f"[ThemeManager] Error configurando tags de métodos: {e}")
