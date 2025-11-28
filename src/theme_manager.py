# src/theme_manager.py - V2 con actualización forzada de TreeViews
import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """Gestiona los temas (modo oscuro/claro) de la aplicación"""
    
    # Definición de paletas de colores
    TEMAS = {
        "claro": {
            # Modo claro con mejor contraste
            "bg": "#F5F5F5",
            "fg": "#1e1e1e",  # Texto muy oscuro para legibilidad
            "bg_alt": "#FFFFFF",
            "fg_alt": "#333333",
            "button_bg": "#E0E0E0",
            "button_fg": "#1e1e1e",
            "button_active_bg": "#D0D0D0",
            "entry_bg": "#FFFFFF",
            "entry_fg": "#1e1e1e",
            "entry_border": "#CCCCCC",
            # TreeView con texto oscuro
            "tree_bg": "#FFFFFF",
            "tree_fg": "#1e1e1e",  # Negro suave para legibilidad
            "tree_selected_bg": "#0078D7",
            "tree_selected_fg": "#FFFFFF",
            "tree_field_bg": "#FAFAFA",
            "tree_heading_bg": "#F0F0F0",  # Heading gris claro
            "frame_bg": "#F5F5F5",
            "border": "#CCCCCC",
            "status_bg": "#007acc",
            "status_fg": "#FFFFFF",
            "menu_bg": "#F0F0F0",
            "menu_fg": "#1e1e1e",
            "menu_active_bg": "#0078D7",
            "menu_active_fg": "#FFFFFF",
        },
        "oscuro": {
            # Paleta VSCode Dark Theme
            "bg": "#1e1e1e",  # Fondo editor VSCode
            "fg": "#d4d4d4",  # Texto VSCode
            "bg_alt": "#252526",  # Sidebar VSCode
            "fg_alt": "#cccccc",
            
            # Componentes
            "button_bg": "#333333",
            "button_fg": "#d4d4d4",
            "button_active_bg": "#3e3e42",
            
            # Entry
            "entry_bg": "#252526",
            "entry_fg": "#d4d4d4",
            "entry_border": "#3e3e42",
            
            # TreeView - Colores VSCode
            "tree_bg": "#252526",  # Sidebar background
            "tree_fg": "#cccccc",  # Texto lista archivos
            "tree_selected_bg": "#0974bc",  # Azul selección VSCode
            "tree_selected_fg": "#ffffff",
            "tree_field_bg": "#252526",
            "tree_heading_bg": "#2d2d30",  # Heading gris medio (no tan negro)
            
            # Frame
            "frame_bg": "#1e1e1e",
            "border": "#3e3e42",
            
            # Barras
            "status_bg": "#007acc",  # Azul barra estado VSCode
            "status_fg": "#ffffff",
            
            # Menú
            "menu_bg": "#252526",
            "menu_fg": "#cccccc",
            "menu_active_bg": "#0974bc",
            "menu_active_fg": "#ffffff",
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
        """Actualiza DIRECTAMENTE todos los TreeViews forzando colores"""
        print(f"[ThemeManager] Actualizando TreeViews a tema {self.tema_actual}")
        try:
            # TreeView principal de resultados
            if hasattr(self.app, 'tree') and self.app.tree:
                tree = self.app.tree
                print(f"[ThemeManager] Actualizando TreeView principal")
                
                # CRÍTICO: Aplicar colores DIRECTAMENTE al widget
                tree.configure(
                    background=self.colores["tree_bg"],
                    foreground=self.colores["tree_fg"]
                )
                
                # Actualizar frame contenedor
                if tree.master:
                    try:
                        tree.master.configure(bg=self.colores["tree_bg"])
                    except Exception as e:
                        print(f"[ThemeManager] Error frame principal: {e}")
                
                # Forzar refresh
                tree.update_idletasks()
            
            # TreeView de historial
            if hasattr(self.app, 'historial_manager') and self.app.historial_manager:
                if hasattr(self.app.historial_manager, 'tree') and self.app.historial_manager.tree:
                    htree = self.app.historial_manager.tree
                    print(f"[ThemeManager] Actualizando TreeView historial")
                    
                    htree.configure(
                        background=self.colores["tree_bg"],
                        foreground=self.colores["tree_fg"]
                    )
                    
                    if htree.master:
                        try:
                            htree.master.configure(bg=self.colores["tree_bg"])
                        except Exception as e:
                            print(f"[ThemeManager] Error frame historial: {e}")
                    
                    htree.update_idletasks()
            
            # TreeView del explorador
            if hasattr(self.app, 'file_explorer') and self.app.file_explorer:
                if hasattr(self.app.file_explorer, 'tree') and self.app.file_explorer.tree:
                    etree = self.app.file_explorer.tree
                    print(f"[ThemeManager] Actualizando TreeView explorador")
                    
                    etree.configure(
                        background=self.colores["tree_bg"],
                        foreground=self.colores["tree_fg"]
                    )
                    
                    if etree.master:
                        try:
                            etree.master.configure(bg=self.colores["tree_bg"])
                        except Exception as e:
                            print(f"[ThemeManager] Error frame explorador: {e}")
                    
                    etree.update_idletasks()
                            
        except Exception as e:
            print(f"[ThemeManager] Error actualizando TreeViews: {e}")
    
    def _configurar_estilos_ttk(self):
        """Configura los estilos de ttk"""
        style = ttk.Style()
        
        # Forzar tema base
        try:
            style.theme_use('clam')  # Tema base que permite personalización
        except:
            pass
        
        # TreeView y Custom.Treeview
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
        
        # Headings - usar color específico si existe
        heading_bg = self.colores.get("tree_heading_bg", self.colores["button_bg"])
        for heading_name in ["Treeview.Heading", "Custom.Treeview.Heading"]:
            style.configure(heading_name,
                background=heading_bg,
                foreground=self.colores["button_fg"],
                relief="flat",
                borderwidth=0 if heading_name == "Treeview.Heading" else 1
            )
            
            style.map(heading_name,
                background=[("active", self.colores["button_active_bg"])]
            )
    
    def toggle_tema(self):
        nuevo_tema = "oscuro" if self.tema_actual == "claro" else "claro"
        self.cambiar_tema(nuevo_tema)
    
    def get_tema_actual(self):
        return self.tema_actual
