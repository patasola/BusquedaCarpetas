# src/tooltip_helper.py - Helper para Tooltips en TreeView
import tkinter as tk
from tkinter import ttk

class TreeViewTooltip:
    """Tooltip que muestra ruta completa al pasar mouse sobre TreeView"""
    
    def __init__(self, treeview):
        self.treeview = treeview
        self.tooltip_window = None
        self.current_item = None
        self.after_id = None
        
        # Configurar eventos
        self.treeview.bind("<Motion>", self._on_motion)
        self.treeview.bind("<Leave>", self._on_leave)
        self.treeview.bind("<Button-1>", self._hide_tooltip)
        
    def _on_motion(self, event):
        """Maneja movimiento del mouse"""
        # Identificar item bajo el cursor
        item = self.treeview.identify_row(event.y)
        
        if item != self.current_item:
            self.current_item = item
            self._hide_tooltip()
            
            if item:
                # Programar mostrar tooltip después de 0.5 segundos
                self.after_id = self.treeview.after(500, 
                    lambda: self._show_tooltip(event.x_root, event.y_root, item))
        elif self.tooltip_window:
            # Actualizar posición si tooltip ya está visible
            self._update_tooltip_position(event.x_root, event.y_root)
    
    def _on_leave(self, event):
        """Mouse salió del TreeView"""
        self._hide_tooltip()
        self.current_item = None
    
    def _show_tooltip(self, x, y, item):
        """Muestra tooltip con ruta completa"""
        if self.current_item != item:  # Verificar que aún es el item correcto
            return
            
        # Obtener ruta completa del item
        ruta_completa = self._get_full_path(item)
        if not ruta_completa:
            return
            
        # Crear ventana de tooltip
        self.tooltip_window = tk.Toplevel(self.treeview)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.configure(bg="#ffffe0", relief="solid", bd=1)
        
        # Crear label con la ruta
        label = tk.Label(
            self.tooltip_window,
            text=ruta_completa,
            bg="#ffffe0",
            fg="#000000",
            font=("Segoe UI", 9),
            padx=6,
            pady=4
        )
        label.pack()
        
        # Posicionar tooltip
        self._position_tooltip(x, y)
    
    def _update_tooltip_position(self, x, y):
        """Actualiza posición del tooltip"""
        if self.tooltip_window:
            self._position_tooltip(x, y)
    
    def _position_tooltip(self, x, y):
        """Posiciona tooltip evitando bordes de pantalla"""
        if not self.tooltip_window:
            return
            
        # Obtener dimensiones del tooltip
        self.tooltip_window.update_idletasks()
        tooltip_width = self.tooltip_window.winfo_reqwidth()
        tooltip_height = self.tooltip_window.winfo_reqheight()
        
        # Obtener dimensiones de pantalla
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()
        
        # Calcular posición evitando bordes
        tooltip_x = x + 15  # Offset del cursor
        tooltip_y = y + 10
        
        # Ajustar si se sale por la derecha
        if tooltip_x + tooltip_width > screen_width:
            tooltip_x = x - tooltip_width - 15
            
        # Ajustar si se sale por abajo
        if tooltip_y + tooltip_height > screen_height:
            tooltip_y = y - tooltip_height - 10
            
        # Asegurar que no quede fuera de pantalla
        tooltip_x = max(0, min(tooltip_x, screen_width - tooltip_width))
        tooltip_y = max(0, min(tooltip_y, screen_height - tooltip_height))
        
        self.tooltip_window.geometry(f"+{tooltip_x}+{tooltip_y}")
    
    def _hide_tooltip(self):
        """Oculta tooltip"""
        if self.after_id:
            self.treeview.after_cancel(self.after_id)
            self.after_id = None
            
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def _get_full_path(self, item):
        """Obtiene ruta completa del item (debe ser sobrescrito por subclases)"""
        try:
            # Intentar obtener de la columna 'ruta_absoluta' si existe
            values = self.treeview.item(item, 'values')
            if values and len(values) > 1:
                # Asumir que la ruta está en la segunda columna
                return values[1] if values[1] else values[0]
            
            # Fallback: usar el texto del item
            return self.treeview.item(item, 'text')
        except:
            return None


class TreeResultsTooltip(TreeViewTooltip):
    """Tooltip especializado para tabla de resultados"""
    
    def _get_full_path(self, item):
        """Obtiene ruta completa de tabla de resultados"""
        try:
            values = self.treeview.item(item, 'values')
            if values and len(values) >= 2:
                # En tabla de resultados: [nombre, ruta_relativa, ...]
                # Queremos mostrar la ruta completa
                nombre = values[0]
                ruta_relativa = values[1] if len(values) > 1 else ''
                
                # Si la ruta relativa ya es completa, usarla
                if ruta_relativa.startswith(('C:', 'D:', '/', '\\\\')):
                    return ruta_relativa
                
                # Si no, construir ruta completa
                # Esto requiere acceso a la ruta base, que podemos obtener del contexto
                return ruta_relativa or nombre
            
            return self.treeview.item(item, 'text')
        except:
            return None


class TreeExplorerTooltip(TreeViewTooltip):
    """Tooltip especializado para explorador de árbol"""
    
    def __init__(self, treeview, tree_explorer_instance):
        super().__init__(treeview)
        self.tree_explorer = tree_explorer_instance
    
    def _get_full_path(self, item):
        """Obtiene ruta completa del explorador de árbol"""
        try:
            # En tree explorer, construir ruta desde la jerarquía
            path_parts = []
            current = item
            
            while current:
                text = self.treeview.item(current, 'text')
                if text and text != '':
                    path_parts.append(text)
                current = self.treeview.parent(current)
            
            if path_parts:
                path_parts.reverse()
                # Agregar ruta base si está disponible
                if hasattr(self.tree_explorer, 'ruta_base'):
                    full_path = self.tree_explorer.ruta_base
                    for part in path_parts[1:]:  # Saltar el primer elemento si es la raíz
                        full_path = full_path + '\\' + part
                    return full_path
                else:
                    return '\\'.join(path_parts)
            
            return None
        except:
            return None