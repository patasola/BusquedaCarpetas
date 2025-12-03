# src/tree_column_config.py - V2.1 - Bugs corregidos
"""
Módulo V2.1 para gestión avanzada de columnas en TreeView.
Añade columnas dinámicamente y se vincula a TreeViews existentes.
"""

import tkinter as tk
from tkinter import ttk
import json
import os

class TreeColumnConfig:
    """Configura columnas de TreeView con capacidad de añadir columnas dinámicamente"""
    
    # Definiciones de columnas disponibles para cada tipo de TreeView
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
    
    def __init__(self, tree, config_id):
        """
        Args:
            tree: TreeView instance existente (puede ser None si aún no existe)
            config_id: ID único para persistencia ('results' o 'historial')
        """
        self.tree = tree
        self.config_id = config_id
        self.config_file = "tree_column_config.json"
        
        # Obtener definiciones de columnas para este TreeView
        self.column_defs = self.COLUMN_DEFINITIONS.get(config_id, {})
        
        # Solo inicializar si el tree existe
        if self.tree:
            self._initialize_columns()
            self.load_config()
            self._reconfigure_all_headings()  # Asegurar headings visibles al inicio
            self.bind_context_menu()
        else:
            print(f"[TreeColumnConfig] Tree no existe aún para {config_id}")
    
    def initialize_when_ready(self, tree):
        """Inicializa cuando el TreeView esté listo (para historial)"""
        self.tree = tree
        if self.tree:
            self._initialize_columns()
            self.load_config()
            self.bind_context_menu()
    
    def _initialize_columns(self):
        """Inicializa todas las columnas definidas en el TreeView"""
        # Configurar heading de columna #0 (Carpeta)
        self.tree.heading("#0", text="Carpeta", anchor="center")
        
        # Obtener columnas actuales (Método, Ruta)
        current_columns = list(self.tree["columns"])
        
        # all_available: todas las definidas en COLUMN_DEFINITIONS
        all_available_columns = list(self.column_defs.keys())
        
        # CRÍTICO: Crear lista de TODAS las columnas manteniendo orden
        # Primero las que ya están, luego las adicionales
        all_columns_ordered = current_columns.copy()
        for col in all_available_columns:
            if col not in all_columns_ordered:
                all_columns_ordered.append(col)
        
        # Configurar TODAS las columnas en el tree (para que existan)
        self.tree.configure(columns=tuple(all_columns_ordered))
        
        # Configurar headings y propiedades de TODAS las columnas
        for col_id in all_columns_ordered:
            col_def = self.column_defs.get(col_id, {
                "title": col_id,
                "width": 100,
                "anchor": "w",
                "default_visible": True
            })
            
            self.tree.heading(col_id, text=col_def.get("title", col_id), anchor=col_def.get("anchor", "w"))
            self.tree.column(
                col_id,
                width=col_def.get("width", 100),
                anchor=col_def.get("anchor", "w"),
                minwidth=col_def.get("minwidth", 50),
                stretch=col_def.get("stretch", False)
            )
        
        # Guardar todas las columnas disponibles
        self.all_columns = all_columns_ordered
    
    def bind_context_menu(self):
        """Vincula menú contextual a las cabeceras del TreeView"""
        if self.tree:
            self.tree.bind("<Button-3>", self._on_right_click)
            self.configure_drag_drop()
        self.configure_doubleclick_resize()
    
    def configure_drag_drop(self):
        """Configura drag & drop para reordenar columnas"""
        if not self.tree:
            return
        
        # Variables para tracking de drag
        self._drag_data = {
            "dragging": False,
            "column": None,
            "start_x": 0
        }
        
        # Bindings para drag & drop
        self.tree.bind("<ButtonPress-1>", self._on_drag_start, add="+")
        self.tree.bind("<B1-Motion>", self._on_drag_motion, add="+")
        self.tree.bind("<ButtonRelease-1>", self._on_drag_release, add="+")
    
    def _on_drag_start(self, event):
        """Detecta inicio de arrastre en heading"""
        try:
            region = self.tree.identify_region(event.x, event.y)
            if region == "heading":
                column = self.tree.identify_column(event.x)
                self._drag_data["dragging"] = True
                self._drag_data["column"] = column
                self._drag_data["start_x"] = event.x
                self.tree.config(cursor="hand2")
                
                # Crear línea guía visual
                self._create_drop_indicator()
        except:
            pass
    
    def _create_drop_indicator(self):
        """Crea línea vertical guía para drag & drop"""
        try:
            # Frame delgado para línea vertical
            self._drop_line = tk.Frame(
                self.tree.master,
                bg="#007ACC",  # Azul
                width=3,
                height=self.tree.winfo_height()
            )
            # Inicialmente oculto
            self._drop_line.place_forget()
        except:
            self._drop_line = None
    
    def _on_drag_motion(self, event):
        """Maneja movimiento durante drag"""
        if self._drag_data["dragging"]:
            # Visual feedback: cambiar cursor
            self.tree.config(cursor="exchange")
            
            # Actualizar posición de línea guía
            try:
                region = self.tree.identify_region(event.x, event.y)
                if region == "heading":
                    target_col = self.tree.identify_column(event.x)
                    if target_col:
                        # Obtener bbox de la columna target
                        bbox = self.tree.bbox(self.tree.get_children()[0] if self.tree.get_children() else "", target_col)
                        if bbox and self._drop_line:
                            # Posicionar línea al inicio de la columna target
                            x_pos = bbox[0]
                            self._drop_line.place(
                                x=x_pos,
                                y=0,
                                height=self.tree.winfo_height()
                            )
            except:
                pass
    
    def _on_drag_release(self, event):
        """Maneja soltar columna para reordenar"""
        try:
            if not self._drag_data["dragging"]:
                return
            
            region = self.tree.identify_region(event.x, event.y)
            
            if region == "heading":
                source_col = self._drag_data["column"]
                target_col = self.tree.identify_column(event.x)
                
                if source_col and target_col and source_col != target_col:
                    self._reorder_columns(source_col, target_col)
            
        finally:
            # Reset drag state
            self._drag_data["dragging"] = False
            self._drag_data["column"] = None
            self.tree.config(cursor="")
            
            # Destruir línea guía
            if hasattr(self, '_drop_line') and self._drop_line:
                try:
                    self._drop_line.destroy()
                    self._drop_line = None
                except:
                    pass
    
    def _reorder_columns(self, source_col, target_col):
        """Reordena columnas moviendo source_col a posición de target_col"""
        try:
            # Convertir #N a índice
            source_idx = int(source_col.replace("#", "")) - 1
            target_idx = int(target_col.replace("#", "")) - 1
            
            # Obtener displaycolumns actual
            current_display = list(self.tree["displaycolumns"])
            if current_display == ['#all']:
                current_display = list(self.tree["columns"])
            
            # Reordenar
            if 0 <= source_idx < len(current_display) and 0 <= target_idx < len(current_display):
                col_to_move = current_display[source_idx]
                current_display.pop(source_idx)
                current_display.insert(target_idx, col_to_move)
                
                # Aplicar nuevo orden
                self.tree.configure(displaycolumns=tuple(current_display))
                self.save_config()
                print(f"[TreeColumnConfig] Columna '{col_to_move}' reordenada: posición {source_idx} → {target_idx}")
        except Exception as e:
            print(f"[TreeColumnConfig] Error reordenando columnas: {e}")
    
    def _on_right_click(self, event):
        """Maneja clic derecho - muestra menú si es en cabecera"""
        region = self.tree.identify_region(event.x, event.y)
        
        if region == "heading":
            self._show_column_menu(event)
            return "break"  # Prevenir propagación
    
    def _show_column_menu(self, event):
        """Muestra menú de configuración de columnas"""
        menu = tk.Menu(self.tree, tearoff=0)
        
        # Título
        menu.add_command(label="📋 Configurar Columnas", state="disabled",
                        font=('Segoe UI', 9, 'bold'))
        menu.add_separator()
        
        # Obtener columnas visibles actualmente
        current_display = list(self.tree["displaycolumns"])
        if current_display == ['#all']:
            current_display = list(self.tree["columns"])
        
        # Crear variables para cada columna (para persistir estado)
        self._menu_vars = {}
        
        # Checkbuttons para cada columna disponible
        for col_id in self.all_columns:
            is_visible = col_id in current_display
            col_def = self.column_defs.get(col_id, {})
            col_title = col_def.get("title", col_id)
            
            # Crear variable booleana para esta columna
            var = tk.BooleanVar(value=is_visible)
            self._menu_vars[col_id] = var
            
            # CRÍTICO: indicatoron=True muestra checkbox visual
            menu.add_checkbutton(
                label=f"  {col_title}",
                command=lambda c=col_id: self._toggle_column_safe(c),
                variable=var,
                indicatoron=True
            )
        
        menu.add_separator()
        menu.add_command(label="↩️ Restaurar por defecto", 
                        command=self._reset_to_defaults)
        
        # Mostrar menú
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _toggle_column_safe(self, column_id):
        """Toggle seguro de columna con verificación"""
        try:
            # CRÍTICO: Usar displaycolumns en lugar de columns
            # Esto oculta columnas sin cambiar el mapeo de datos
            all_columns = list(self.tree["columns"])
            current_display = list(self.tree["displaycolumns"])
            
            # Si displaycolumns es '#all', obtener lista real
            if current_display == ['#all']:
                current_display = all_columns.copy()
            
            if column_id in current_display:
                # Ocultar - pero mantener al menos 1 columna
                if len(current_display) > 1:
                    current_display.remove(column_id)
                    self.tree.configure(displaycolumns=tuple(current_display))
                    self.tree.update_idletasks()
                    # NO necesitamos reconfigure headings aquí
                    self.save_config()
                else:
                    print(f"[TreeColumnConfig] No se puede ocultar la última columna")
            else:
                # Mostrar - añadir en posición original
                # Encontrar posición correcta para mantener orden
                insert_pos = len(current_display)
                for col in all_columns:
                    if col == column_id:
                        break
                    if col in current_display:
                        insert_pos = current_display.index(col) + 1
                
                current_display.insert(insert_pos, column_id)
                self.tree.configure(displaycolumns=tuple(current_display))
                self.tree.update_idletasks()
                # NO necesitamos reconfigure headings aquí
                self.save_config()
                
        except Exception as e:
            print(f"[TreeColumnConfig] Error en toggle: {e}")
    
    def load_config(self):
        """Carga configuración guardada"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    all_configs = json.load(f)
                
                config = all_configs.get(self.config_id, {})
                visible_columns = config.get('visible_columns', None)
                
                if visible_columns:
                    # Filtrar solo columnas que existen
                    valid_columns = [c for c in visible_columns if c in self.all_columns]
                    if valid_columns:
                        self.tree.configure(displaycolumns=tuple(valid_columns))
                        return
            
            # Si no hay config guardada, usar defaults
            self._apply_defaults()
            
        except Exception as e:
            print(f"[TreeColumnConfig] Error cargando config: {e}")
            self._apply_defaults()
    
    def _apply_defaults(self):
        """Aplica columnas visibles por defecto"""
        try:
            default_visible = []
            for col_id in self.all_columns:
                col_def = self.column_defs.get(col_id, {})
                if col_def.get("default_visible", False):
                    default_visible.append(col_id)
            
            if default_visible:
                self.tree.configure(displaycolumns=tuple(default_visible))
            elif self.all_columns:
                # Si no hay defaults, mostrar primeras 3
                self.tree.configure(displaycolumns=tuple(self.all_columns[:3]))
            
            # NO necesitamos reconfigure headings aquí
                
        except Exception as e:
            print(f"[TreeColumnConfig] Error aplicando defaults: {e}")
    
    def save_config(self):
        """Guarda configuración actual"""
        try:
            # Leer configuraciones existentes
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    all_configs = json.load(f)
            else:
                all_configs = {}
            
            # Obtener displaycolumns actual
            current_display = list(self.tree["displaycolumns"])
            if current_display == ['#all']:
                current_display = list(self.tree["columns"])
            
            # Actualizar configuración de este TreeView
            all_configs[self.config_id] = {
                'visible_columns': current_display,
                'all_columns': self.all_columns
            }
            
            # Guardar
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[TreeColumnConfig] Error guardando config: {e}")
    
    def _reconfigure_all_headings(self):
        """Re-configura todos los headings (útil después de tree.configure)"""
        try:
            # Configurar heading #0
            self.tree.heading("#0", text="Carpeta", anchor="center")
            
            # Configurar headings de todas las columnas visibles
            current_columns = list(self.tree["columns"])
            for col_id in current_columns:
                col_def = self.column_defs.get(col_id, {})
                self.tree.heading(
                    col_id, 
                    text=col_def.get("title", col_id), 
                    anchor=col_def.get("anchor", "w")
                )
        except Exception as e:
            print(f"[TreeColumnConfig] Error reconfigurando headings: {e}")
    
    def _reset_to_defaults(self):
        """Restaura columnas a configuración por defecto"""
        try:
            self._apply_defaults()
            self.save_config()
            print(f"[TreeColumnConfig] Columnas restauradas a defaults para {self.config_id}")
        except Exception as e:
            print(f"[TreeColumnConfig] Error en reset: {e}")


    def configure_doubleclick_resize(self):
        """Configura doble click en headings para autoajustar ancho"""
        if not self.tree:
            return
        
        self.tree.bind('<Double-Button-1>', self._on_heading_doubleclick, add='+')
    
    def _on_heading_doubleclick(self, event):
        """Autoajusta ancho de columna al hacer doble click en heading"""
        try:
            region = self.tree.identify_region(event.x, event.y)
            if region == 'heading':
                column = self.tree.identify_column(event.x)
                if column:                
                # Detectar si esta cerca del borde derecho (separator)
                column_x = self.tree.bbox(self.tree.get_children()[0] if self.tree.get_children() else '', column)
                if column_x:
                    col_right = column_x[0] + column_x[2]
                    if abs(event.x - col_right) > 5:
                        return  # No esta en separator, permitir propagacion
                    self._autofit_column(column)
        except Exception as e:
            print(f'[TreeColumnConfig] Error en doble click: {e}')
    
    def _autofit_column(self, column_id):
        """Ajusta ancho de columna al contenido mas ancho"""
        try:
            items = self.tree.get_children()
            if not items:
                return
            
            max_width = 100
            
            # Ancho del heading
            heading_text = self.tree.heading(column_id, 'text')
            if heading_text:
                max_width = max(max_width, len(str(heading_text)) * 8)
            
            # Ancho del contenido
            if column_id == '#0':
                for item in items:
                    text = self.tree.item(item, 'text')
                    if text:
                        max_width = max(max_width, len(str(text)) * 7)
            else:
                col_index = list(self.tree['columns']).index(column_id)
                for item in items:
                    values = self.tree.item(item, 'values')
                    if values and col_index < len(values):
                        text = str(values[col_index])
                        max_width = max(max_width, len(text) * 7)
            
            new_width = min(max_width + 20, 600)
            self.tree.column(column_id, width=new_width)
            print(f'[TreeColumnConfig] Columna {column_id} ajustada a {new_width}px')
            
        except Exception as e:
            print(f'[TreeColumnConfig] Error autoajustando: {e}')
