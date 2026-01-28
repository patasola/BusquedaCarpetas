# src/managers/column_manager.py - Gestor Unificado de Columnas V.5.0
import tkinter as tk
from tkinter import ttk
import json
import os

class ColumnManager:
    """Gestiona configuración, persistencia, visibilidad y reordenamiento de columnas TreeView"""
    
    COLUMN_DEFINITIONS = {
        "results": {
            "Método": {"title": "M", "width": 35, "anchor": "center", "default_visible": True},
            "Ruta": {"title": "Ruta Relativa", "width": 300, "anchor": "w", "default_visible": True},
            "Demandante": {"title": "Demandante", "width": 200, "anchor": "w", "default_visible": False},
            "Demandado": {"title": "Demandado", "width": 200, "anchor": "w", "default_visible": False},
            "Resultados": {"title": "Res.", "width": 60, "anchor": "center", "default_visible": False},
            "Hora": {"title": "Hora", "width": 80, "anchor": "center", "default_visible": False},
            "Tiempo": {"title": "Tiempo", "width": 70, "anchor": "center", "default_visible": False}
        },
        "historial": {
            "Criterio": {"title": "Criterio", "width": 100, "anchor": "w", "default_visible": True},
            "Metodo": {"title": "M", "width": 30, "anchor": "center", "default_visible": True},
            "Resultados": {"title": "Res.", "width": 50, "anchor": "center", "default_visible": True},
            "Tiempo": {"title": "Tiempo", "width": 55, "anchor": "center", "default_visible": True},
            "Fecha": {"title": "Hora", "width": 55, "anchor": "center", "default_visible": True},
            "Demandante": {"title": "Demandante", "width": 150, "anchor": "w", "default_visible": False},
            "Demandado": {"title": "Demandado", "width": 150, "anchor": "w", "default_visible": False},
            "Ruta": {"title": "Ruta", "width": 200, "anchor": "w", "default_visible": False}
        }
    }
    
    def __init__(self, tree, config_id, app=None):
        self.tree = tree
        self.app = app
        self.config_id = config_id
        self._original_widths = {}
        self.column_defs = self.COLUMN_DEFINITIONS.get(config_id, {})
        
        self.config_keys = {
            "results": "main_column_widths",
            "historial": "history_column_widths"
        }
        
        if self.tree:
            self._initialize_columns()
            self.load_config()
            self._reconfigure_all_headings()
            self.bind_events()

    def _initialize_columns(self):
        """Define e inicializa las columnas en el widget"""
        self.tree.heading("#0", text="Carpeta", anchor="center")
        current_columns = list(self.tree["columns"])
        all_available_columns = list(self.column_defs.keys())
        
        all_columns_ordered = current_columns.copy()
        for col in all_available_columns:
            if col not in all_columns_ordered:
                all_columns_ordered.append(col)
        
        self.tree.configure(columns=tuple(all_columns_ordered))
        saved_widths = self._get_saved_widths()
        
        for col_id in all_columns_ordered:
            col_def = self.column_defs.get(col_id, {"title": col_id, "width": 100})
            w = saved_widths.get(col_id, col_def.get("width", 100))
            self.tree.heading(col_id, text=col_def.get("title", col_id))
            self.tree.column(col_id, width=w, anchor=col_def.get("anchor", "w"), 
                            stretch=(col_id == "Ruta"))
        
        self.all_columns = all_columns_ordered

    def bind_events(self):
        """Vincula clics y drag&drop"""
        self.tree.bind("<Button-3>", self._on_right_click)
        self.tree.bind("<Double-Button-1>", self._handle_doubleclick_autofit)
        self._setup_drag_drop()

    def load_config(self):
        """Carga visibilidad y anchos desde el ConfigManager central"""
        if self.app and hasattr(self.app, 'config'):
            key = self.config_keys.get(self.config_id)
            if key:
                config = self.app.config.get(key, {})
                visible = config.get('visible_columns')
                if visible:
                    self.tree.configure(displaycolumns=tuple([c for c in visible if c in self.all_columns]))
                widths = config.get('widths', {})
                for cid, w in widths.items():
                    try: self.tree.column(cid, width=w)
                    except: pass

    def save_config(self):
        """Envía el estado actual al ConfigManager central"""
        if not self.app: return
        display = list(self.tree["displaycolumns"])
        if display == ['#all']: display = list(self.tree["columns"])
        widths = {str(c): self.tree.column(c, 'width') for c in ["#0"] + list(self.tree["columns"])}
        
        self.app.config.set(self.config_keys.get(self.config_id), {
            'visible_columns': display,
            'widths': widths
        })

    def _on_right_click(self, event):
        """Muestra menú de columnas"""
        if self.tree.identify_region(event.x, event.y) == "heading":
            self._show_column_menu(event)
            return "break"

    def _show_column_menu(self, event):
        menu = tk.Menu(self.tree, tearoff=0)
        current_display = list(self.tree["displaycolumns"])
        if current_display == ['#all']: current_display = list(self.tree["columns"])
        
        for col_id in self.all_columns:
            var = tk.BooleanVar(value=col_id in current_display)
            menu.add_checkbutton(label=f"  {self.column_defs.get(col_id, {}).get('title', col_id)}",
                                command=lambda c=col_id: self._toggle_column(c), variable=var)
        
        menu.add_separator()
        menu.add_command(label="↩️ Restaurar", command=self._reset_defaults)
        menu.tk_popup(event.x_root, event.y_root)

    def _toggle_column(self, col_id):
        curr = list(self.tree["displaycolumns"])
        if curr == ['#all']: curr = list(self.tree["columns"])
        
        if col_id in curr:
            if len(curr) > 1: curr.remove(col_id)
        else:
            curr.append(col_id) # Orden simplificado
            
        self.tree.configure(displaycolumns=tuple(curr))
        self.save_config()

    def _reset_defaults(self):
        visible = [cid for cid, d in self.column_defs.items() if d.get('default_visible')]
        self.tree.configure(displaycolumns=tuple(visible))
        self.save_config()

    def _handle_doubleclick_autofit(self, event):
        if self.tree.identify_region(event.x, event.y) == 'separator':
            cid = self.tree.identify_column(event.x)
            if cid: self._autofit(cid)

    def _autofit(self, cid):
        # Lógica de autofit simplificada
        items = self.tree.get_children()
        max_w = 100
        for item in items:
            txt = self.tree.item(item, 'text') if cid == '#0' else str(self.tree.item(item, 'values')[int(cid[1:])-1])
            max_w = max(max_w, len(txt) * 8 + 40)
        self.tree.column(cid, width=min(max_w, 800))

    def _setup_drag_drop(self):
        # Placeholder para drag & drop de columnas si se requiere portar la lógica V2.1 completa
        pass

    def _get_saved_widths(self):
        if not self.app: return {}
        conf = self.app.config.get(self.config_keys.get(self.config_id), {})
        return conf.get('widths', {})

    def _reconfigure_all_headings(self):
        for cid in list(self.tree["columns"]):
            d = self.column_defs.get(cid, {})
            self.tree.heading(cid, text=d.get("title", cid))
