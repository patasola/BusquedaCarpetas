# src/components/tree_view.py - TreeView configurable y reutilizable
import tkinter as tk
from tkinter import ttk
from .tree_tooltip import TreeViewTooltip

class ConfigurableTreeView:
    """TreeView unificado con temas dinámicos y columnas configurables"""
    
    def __init__(self, parent, config_id, columns_def, **treeview_kwargs):
        """
        Args:
            parent: Widget padre
            config_id: ID único para este TreeView (results/historial/explorer)
            columns_def: Lista de tuplas (nombre_columna, ancho, anchor)
            **treeview_kwargs: Argumentos adicionales para ttk.Treeview
        """
        self.parent = parent
        self.config_id = config_id
        self.columns_def = columns_def
        
        # Frame contenedor
        self.frame = tk.Frame(parent)
        
        # Crear scrollbars
        self.vsb = ttk.Scrollbar(self.frame, orient="vertical")
        self.hsb = ttk.Scrollbar(self.frame, orient="horizontal")
        
        # Extraer columnas
        column_names = tuple(col[0] for col in columns_def)
        
        # Crear TreeView
        self.tree = ttk.Treeview(
            self.frame,
            columns=column_names,
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.hsb.set,
            style="Custom.Treeview",
            **treeview_kwargs
        )
        
        # Configurar scrollbars
        self.vsb.configure(command=self.tree.yview)
        self.hsb.configure(command=self.tree.xview)
        
        # Aplicar configuración de columnas
        self._setup_columns()
        
        # Aplicar tema actual
        self.update_theme()
        
        # Añadir tooltip
        self.tooltip = TreeViewTooltip(self.tree)
        
        # Empaquetar
        self.tree.pack(side='left', fill='both', expand=True)
    
    def _setup_columns(self):
        """Configura columnas según definición"""
        for col_name, width, anchor in self.columns_def:
            self.tree.column(col_name, width=width, anchor=anchor)
            self.tree.heading(col_name, text=col_name, anchor=tk.CENTER)
    
    def update_theme(self):
        """Actualiza colores según tema actual"""
        try:
            # Intentar obtener colores desde theme_manager
            from ..theme_manager import ThemeManager
            # Si existe app con theme_manager, usar sus colores
            # Por ahora, usar colores por defecto
            pass
        except:
            pass
        
        # Aplicar colores directamente al widget
        # Esto se actualizará cuando theme_manager llame a update_theme()
        pass
    
    def pack(self, **kwargs):
        """Empaqueta el frame contenedor"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grilla el frame contenedor"""
        self.frame.grid(**kwargs)
    
    def get_tree(self):
        """Retorna el widget TreeView interno"""
        return self.tree
