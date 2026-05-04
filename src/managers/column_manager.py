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
            "Fecha_C": {"title": "Fecha Completa", "width": 120, "anchor": "center", "default_visible": False},
            "Demandante": {"title": "Demandante", "width": 150, "anchor": "w", "default_visible": False},
            "Demandado": {"title": "Demandado", "width": 150, "anchor": "w", "default_visible": False},
            "Ruta": {"title": "Ruta", "width": 200, "anchor": "w", "default_visible": False}
        },
        "index_config": {
            "path": {"title": "Carpeta", "width": 350, "anchor": "w", "default_visible": True},
            "status": {"title": "Estado", "width": 100, "anchor": "center", "default_visible": True},
            "last": {"title": "Última Indexación", "width": 150, "anchor": "center", "default_visible": True},
            "duration": {"title": "⏳ Duración", "width": 100, "anchor": "center", "default_visible": True}
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
            "historial": "history_column_widths",
            "index_config": "index_config_column_widths"
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
            
            # Prioridad: 1. Guardado en disco, 2. Default definicion
            w = saved_widths.get(col_id, col_def.get("width", 100))
            if w < 10: w = col_def.get("width", 100) # Evitar 1px bug
            
            self.tree.heading(col_id, text=col_def.get("title", col_id))
            self.tree.column(col_id, width=w, minwidth=50, anchor=col_def.get("anchor", "w"), 
                            stretch=False) # Forzar stretch=False para persistencia exacta
        
        # Cargar visibilidad de columnas si está guardada
        if self.app and hasattr(self.app, 'config'):
            key = self.config_keys.get(self.config_id)
            if key:
                conf = self.app.config.get(key, {})
                visible = conf.get('visible_columns')
                if visible:
                    valid_visible = [c for c in visible if c in all_columns_ordered]
                    if valid_visible:
                        self.tree.configure(displaycolumns=tuple(valid_visible))
        
        self.all_columns = all_columns_ordered

    def bind_events(self):
        """Vincula clics y drag&drop de forma aditiva"""
        self.tree.bind("<Button-3>", self._on_right_click, add="+")
        self.tree.bind("<Button-2>", self._on_right_click, add="+")
        self.tree.bind("<Double-Button-1>", self._handle_doubleclick_autofit, add="+")
        self.tree.bind("<ButtonRelease-1>", self._on_button_release, add="+")
        self._setup_drag_drop()

    def _on_button_release(self, event):
        """Al soltar el click, guardamos el estado si algo cambió"""
        # Siempre intentamos guardar después de una interacción de ratón en cabeceras/separadores
        # o simplemente en cualquier release para ser robustos.
        self.save_config()

    def load_config(self):
        """Carga visibilidad y anchos desde el ConfigManager central"""
        if self.app and hasattr(self.app, 'config'):
            key = self.config_keys.get(self.config_id)
            config = self.app.config.get(key, {})
            
            if config and isinstance(config, dict):
                # Cargar anchos de forma robusta
                widths = config.get('widths', {})
                if widths:
                    for cid, w in widths.items():
                        try:
                            # Asegurarse de que el ancho sea un entero válido
                            if isinstance(w, (int, float)) and w > 0:
                                self.tree.column(cid, width=int(w))
                        except Exception as e:
                            print(f"[ColumnManager] Error cargando ancho para {cid}: {e}")
                
                # Cargar visibilidad
                display = config.get('visible_columns', [])
                if display:
                    self._apply_visibility(display)
                
                # Forzar actualización visual
                self.tree.update_idletasks()
                
                # Notificar éxito
                if self.app and hasattr(self.app, 'actualizar_estado'):
                    self.app.actualizar_estado("✓ Columnas cargadas")
                    self.app.master.after(2000, lambda: self.app.actualizar_estado("Listo"))

    def save_config(self):
        """Envía el estado actual al ConfigManager central"""
        if not self.app or not hasattr(self.app, 'config'): return
        
        display = list(self.tree["displaycolumns"])
        # Normalizar displaycolumns (puede contener nombres o índices)
        all_cols = list(self.tree["columns"])
        if not display or display == ["#all"] or display == ("#all",):
             display = all_cols
        else:
             # Convertir índices a nombres si es necesario
             norm_display = []
             for col in display:
                 if isinstance(col, int):
                     if 0 <= col < len(all_cols): 
                         norm_display.append(all_cols[col])
                 else:
                     norm_display.append(col)
             display = norm_display if norm_display else all_cols
             
        widths = {str(c): self.tree.column(c, 'width') for c in ["#0"] + list(self.tree["columns"])}
        
        # Guardar en configuración
        self.app.config.set(self.config_keys.get(self.config_id), {
            'visible_columns': display,
            'widths': widths
        })
        
        # Opcional: Notificar al usuario de forma sutil
        if hasattr(self.app, 'actualizar_estado'):
            # Solo si no está en medio de una búsqueda
            pass

    def _on_right_click(self, event):
        """Muestra menú de columnas"""
        if self.tree.identify_region(event.x, event.y) == "heading":
            self._show_column_menu(event)
            return "break"

    def _show_column_menu(self, event):
        """Muestra menú de columnas con checkmarks correctos"""
        menu = tk.Menu(self.tree, tearoff=0)
        
        # Obtener columnas visibles DIRECTAMENTE del TreeView
        display_raw = self.tree["displaycolumns"]
        all_cols = list(self.tree["columns"])
        
        # DEBUG COMPLETO
        print(f"\n[DEBUG] === COLUMN MENU DEBUG ===")
        print(f"[DEBUG] displaycolumns RAW: {display_raw}")
        print(f"[DEBUG] displaycolumns TYPE: {type(display_raw)}")
        print(f"[DEBUG] all_columns from tree: {all_cols}")
        print(f"[DEBUG] self.all_columns: {self.all_columns}")
        
        # Determinar qué columnas están visibles
        if display_raw == "" or display_raw == "#all" or display_raw == ("#all",) or display_raw == ["#all"]:
            visible_cols = all_cols
            print(f"[DEBUG] Using ALL columns as visible")
        else:
            # displaycolumns puede ser una tupla de strings o una string separada por espacios
            if isinstance(display_raw, str):
                visible_cols = display_raw.split()
            elif isinstance(display_raw, (list, tuple)):
                visible_cols = list(display_raw)
            else:
                visible_cols = all_cols
            print(f"[DEBUG] visible_cols parsed: {visible_cols}")
        
        # Crear menú con checkmarks
        self._check_vars = []  # IMPORTANTE: Guardar referencias para evitar GC
        for col_id in self.all_columns:
            is_visible = col_id in visible_cols
            print(f"[DEBUG] Column '{col_id}' -> visible: {is_visible}")
            
            var = tk.BooleanVar(value=is_visible)
            self._check_vars.append(var)
            
            title = self.column_defs.get(col_id, {}).get('title', col_id)
            menu.add_checkbutton(
                label=f"  {title}",
                command=lambda c=col_id: self._toggle_column(c),
                variable=var
            )
        
        print(f"[DEBUG] === END DEBUG ===\n")
        
        menu.add_separator()
        menu.add_command(label="↩️ Restaurar", command=self._reset_defaults)
        menu.tk_popup(event.x_root, event.y_root)

    def _toggle_column(self, col_id):
        curr = list(self.tree["displaycolumns"])
        
        # Normalizar displaycolumns (puede contener nombres o índices)
        all_cols = list(self.tree["columns"])
        if not curr or curr == ["#all"] or curr == ("#all",):
             curr = all_cols
        else:
             # Convertir índices a nombres si es necesario
             norm_curr = []
             for col in curr:
                 if isinstance(col, int):
                     if 0 <= col < len(all_cols): 
                         norm_curr.append(all_cols[col])
                 else:
                     norm_curr.append(col)
             curr = norm_curr if norm_curr else all_cols
        
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

    def _apply_visibility(self, visible_cols):
        """Aplica la lista de columnas visibles de forma segura"""
        if not visible_cols: return
        
        # Las columnas disponibles reales en el widget
        all_available = list(self.tree["columns"])
        
        # Filtrar solo las que existen
        to_show = [c for c in visible_cols if c in all_available]
        
        if to_show:
            try:
                self.tree.configure(displaycolumns=tuple(to_show))
            except Exception as e:
                print(f"[ColumnManager] Error aplicando visibilidad: {e}")

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
        if not self.app or not hasattr(self.app, 'config'): return {}
        key = self.config_keys.get(self.config_id)
        if not key: return {}
        conf = self.app.config.get(key, {})
        if not isinstance(conf, dict): return {}
        # Si la config es del formato nuevo {visible_columns: [], widths: {}}
        if 'widths' in conf:
            return conf.get('widths', {})
        # Si la config es del formato viejo {col: width}
        return conf

    def _reconfigure_all_headings(self):
        for cid in list(self.tree["columns"]):
            d = self.column_defs.get(cid, {})
            self.tree.heading(cid, text=d.get("title", cid))
