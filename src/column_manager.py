# src/column_manager.py - Gestor de columnas configurables

import tkinter as tk
from tkinter import ttk
import json
import os

class ColumnManager:
    """Gestiona columnas configurables con menú contextual, reordenamiento y persistencia"""
    
    def __init__(self, tree, config_key, column_definitions):
        """
        Args:
            tree: TreeView instance
            config_key: Clave única para guardar preferencias ('results_tree' o 'historial_tree')
            column_definitions: Dict con definiciones de columnas
        """
        self.tree = tree
        self.config_key = config_key
        self.column_definitions = column_definitions
        self.config_file = "column_preferences.json"
        
        # Estado actual
        self.visible_columns = []
        self.column_order = []
        self.column_widths = {}
        
        # Cargar preferencias guardadas
        self.load_preferences()
        
        # Aplicar configuración al TreeView
        self.apply_configuration()
        
        # Vincular eventos
        self.bind_events()
    
    def bind_events(self):
        """Vincula eventos para menú contextual y reordenamiento"""
        # Menú contextual en cabeceras
        self.tree.bind("<Button-3>", self.show_column_menu)
        
        # Opcional: Guardar anchos al redimensionar
        self.tree.bind("<ButtonRelease-1>", self.save_column_widths_delayed)
    
    def show_column_menu(self, event):
        """Muestra menú contextual para configurar columnas"""
        # Detectar si click fue en cabecera
        region = self.tree.identify_region(event.x, event.y)
        if region != "heading":
            return
        
        # Crear menú
        menu = tk.Menu(self.tree, tearoff=0)
        menu.add_command(label="📋 Configurar Columnas", state="disabled", 
                        font=('Segoe UI', 9, 'bold'))
        menu.add_separator()
        
        # Añadir checkbuttons para cada columna
        all_columns = self.get_all_columns()
        for col_id in all_columns:
            col_def = self.column_definitions.get(col_id, {})
            col_title = col_def.get('title', col_id)
            is_visible = col_id in self.visible_columns
            
            menu.add_checkbutton(
                label=col_title,
                command=lambda c=col_id: self.toggle_column(c),
                variable=tk.BooleanVar(value=is_visible),
                onvalue=True,
                offvalue=False
            )
        
        menu.add_separator()
        menu.add_command(label="↩️ Restaurar por defecto", 
                        command=self.reset_to_defaults)
        
        # Mostrar menú
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def get_all_columns(self):
        """Retorna lista de todas las columnas disponibles"""
        return list(self.column_definitions.keys())
    
    def toggle_column(self, column_id):
        """Muestra u oculta una columna"""
        if column_id in self.visible_columns:
            self.hide_column(column_id)
        else:
            self.show_column(column_id)
    
    def show_column(self, column_id):
        """Muestra una columna"""
        if column_id not in self.visible_columns:
            self.visible_columns.append(column_id)
            self.apply_configuration()
            self.save_preferences()
    
    def hide_column(self, column_id):
        """Oculta una columna"""
        if column_id in self.visible_columns:
            self.visible_columns.remove(column_id)
            self.apply_configuration()
            self.save_preferences()
    
    def apply_configuration(self):
        """Aplica configuración actual al TreeView"""
        # Configurar columnas visibles
        self.tree.configure(columns=tuple(self.visible_columns))
        
        # Configurar cada columna visible
        for col_id in self.visible_columns:
            col_def = self.column_definitions.get(col_id, {})
            
            # Configurar heading
            self.tree.heading(
                col_id,
                text=col_def.get('title', col_id),
                anchor=col_def.get('anchor', tk.W)
            )
            
            # Configurar column
            width = self.column_widths.get(col_id, col_def.get('width', 100))
            self.tree.column(
                col_id,
                width=width,
                anchor=col_def.get('anchor', tk.W),
                minwidth=col_def.get('minwidth', 50),
                stretch=col_def.get('stretch', False)
            )
    
    def save_column_widths_delayed(self, event=None):
        """Guarda anchos de columnas con delay para evitar múltiples guardados"""
        if hasattr(self, '_save_timer'):
            self.tree.after_cancel(self._save_timer)
        self._save_timer = self.tree.after(500, self.save_column_widths)
    
    def save_column_widths(self):
        """Captura anchos actuales de columnas"""
        try:
            # Capturar ancho de tree column (#0)
            self.column_widths['#0'] = self.tree.column('#0', 'width')
            
            # Capturar anchos de otras columnas
            for col_id in self.visible_columns:
                self.column_widths[col_id] = self.tree.column(col_id, 'width')
            
            self.save_preferences()
        except:
            pass
    
    def load_preferences(self):
        """Carga preferencias desde archivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    all_prefs = json.load(f)
                
                prefs = all_prefs.get(self.config_key, {})
                
                self.visible_columns = prefs.get('visible_columns', self.get_default_visible())
                self.column_order = prefs.get('column_order', self.visible_columns.copy())
                self.column_widths = prefs.get('column_widths', {})
            else:
                self.reset_to_defaults()
        except Exception as e:
            print(f"[ColumnManager] Error cargando preferencias: {e}")
            self.reset_to_defaults()
    
    def save_preferences(self):
        """Guarda preferencias a archivo JSON"""
        try:
            # Leer archivo existente
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    all_prefs = json.load(f)
            else:
                all_prefs = {}
            
            # Actualizar preferencias de este TreeView
            all_prefs[self.config_key] = {
                'visible_columns': self.visible_columns,
                'column_order': self.column_order,
                'column_widths': self.column_widths
            }
            
            # Guardar
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(all_prefs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[ColumnManager] Error guardando preferencias: {e}")
    
    def get_default_visible(self):
        """Retorna columnas visibles por defecto"""
        return [col_id for col_id, col_def in self.column_definitions.items() 
                if col_def.get('default_visible', True)]
    
    def reset_to_defaults(self):
        """Restaura configuración por defecto"""
        self.visible_columns = self.get_default_visible()
        self.column_order = self.visible_columns.copy()
        self.column_widths = {col_id: col_def.get('width', 100) 
                             for col_id, col_def in self.column_definitions.items()}
        self.column_widths['#0'] = 200  # Ancho por defecto de tree column
        
        self.apply_configuration()
        self.save_preferences()
