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
            
            # CRÍTICO: indicatedon=True muestra checkbox visual
            menu.add_checkbutton(
                label=f"  {col_title}",
                command=lambda c=col_id: self._toggle_column_safe(c),
                variable=var,
                indicatedon=True
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

