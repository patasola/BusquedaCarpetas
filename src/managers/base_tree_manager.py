# src/managers/base_tree_manager.py - Clase Base para Managers con TreeView
import tkinter as tk
from tkinter import ttk

class BaseTreeManager:
    """
    Clase base para managers que usan TreeView.
    Consolida lógica común de file_explorer, historial y tree_navigator.
    """
    
    def __init__(self, app, config):
        """
        Args:
            app: Referencia a la aplicación principal
            config: Dict con configuración del manager:
                - title: Título del panel
                - columns: Lista de tuplas (nombre, ancho)
                - width_cm: Ancho del panel en cm (opcional)
                - mode: Modo del manager (opcional)
        """
        self.app = app
        self.config = config
        
        # Estado común
        self.visible = False
        self.frame = None
        self.tree = None
        self.assigned_column = None
        
        # Tooltip state
        self.tooltip_window = None
        self.current_item = None
        self.after_id = None
    
    # ==================== TreeView Creation ====================
    
    def create_tree_widget(self, parent):
        """Crea TreeView con scrollbars y configuración estándar"""
        # Frame contenedor
        tree_frame = ttk.Frame(parent)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # TreeView
        columns = [col[0] for col in self.config['columns']]
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='tree headings',
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            selectmode='browse'
        )
        
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configurar columnas
        self._configure_columns()
        
        # Bindings comunes
        self._setup_bindings()
        
        # Tooltip
        self._setup_tooltip()
        
        return tree_frame
    
    def _configure_columns(self):
        """Configura columnas del TreeView"""
        for col_name, col_width in self.config['columns']:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=col_width, minwidth=50)
        
        # Columna de ícono
        self.tree.column('#0', width=40, minwidth=40, stretch=False)
    
    def _setup_bindings(self):
        """Configura eventos comunes del TreeView"""
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Return>', self.on_enter_key)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    # ==================== Show/Hide Management ====================
    
    def show(self):
        """Muestra el panel con posicionamiento dual"""
        if self.visible:
            return
        
        self.visible = True
        
        # Crear si no existe
        if not self.frame:
            self.create_widget()
        
        # Asignar columna disponible
        column = self.app.dual_panel_manager.get_available_column()
        if column is not None:
            self.assigned_column = column
            self.app.dual_panel_manager.assign_panel(self.frame, column)
            self.frame.pack(side='left', fill='both', expand=False)
    
    def hide(self):
        """Oculta el panel y libera su posición"""
        if not self.visible:
            return
        
        self.visible = False
        
        if self.frame:
            self.frame.pack_forget()
        
        # Liberar columna
        if self.assigned_column is not None:
            self.app.dual_panel_manager.free_column(self.assigned_column)
            self.assigned_column = None
    
    def toggle_visibility(self):
        """Alterna la visibilidad del panel"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def is_visible(self):
        """Retorna True si el panel está visible"""
        return self.visible
    
    # ==================== Tooltip Management ====================
    
    def _setup_tooltip(self):
        """Configura tooltip para el TreeView"""
        self.tree.bind("<Motion>", self._on_tooltip_motion)
        self.tree.bind("<Leave>", self._on_tooltip_leave)
        self.tree.bind("<Button-1>", self._hide_tooltip)
    
    def _on_tooltip_motion(self, event):
        """Maneja movimiento del mouse para tooltip"""
        item = self.tree.identify_row(event.y)
        
        if item != self.current_item:
            self.current_item = item
            self._hide_tooltip()
            
            if item:
                self.after_id = self.tree.after(
                    500,
                    lambda: self._show_tooltip(event.x_root, event.y_root, item)
                )
    
    def _on_tooltip_leave(self, event):
        """Mouse salió del TreeView"""
        self._hide_tooltip()
        self.current_item = None
    
    def _show_tooltip(self, x, y, item):
        """Muestra tooltip - Override en subclases para contenido específico"""
        if self.current_item != item:
            return
        
        # Obtener texto del item (override en subclases)
        text = self.get_tooltip_text(item)
        if not text:
            return
        
        # Crear tooltip
        self.tooltip_window = tk.Toplevel(self.tree)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.configure(bg="#ffffe0", relief="solid", bd=1)
        
        label = tk.Label(
            self.tooltip_window,
            text=text,
            bg="#ffffe0",
            fg="#000000",
            font=("Segoe UI", 9),
            padx=6,
            pady=4,
            wraplength=300,
            justify='left'
        )
        label.pack()
        
        # Posicionar
        self._position_tooltip(x, y)
    
    def _position_tooltip(self, x, y):
        """Posiciona tooltip evitando bordes de pantalla"""
        if not self.tooltip_window:
            return
        
        self.tooltip_window.update_idletasks()
        tw_width = self.tooltip_window.winfo_width()
        tw_height = self.tooltip_window.winfo_height()
        
        screen_width = self.tree.winfo_screenwidth()
        screen_height = self.tree.winfo_screenheight()
        
        # Ajustar X
        if x + tw_width > screen_width:
            x = screen_width - tw_width - 10
        
        # Ajustar Y
        if y + tw_height > screen_height:
            y = y - tw_height - 20
        else:
            y = y + 20
        
        self.tooltip_window.geometry(f"+{x}+{y}")
    
    def _hide_tooltip(self, event=None):
        """Oculta tooltip"""
        if self.after_id:
            self.tree.after_cancel(self.after_id)
            self.after_id = None
        
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    # ==================== Métodos a Override ====================
    
    def create_widget(self):
        """Crea el widget principal - DEBE ser implementado por subclases"""
        raise NotImplementedError("Subclases deben implementar create_widget()")
    
    def get_tooltip_text(self, item):
        """Retorna texto para tooltip - Override en subclases"""
        return self.tree.item(item, 'text')
    
    def on_double_click(self, event):
        """Maneja doble click - Override en subclases"""
        pass
    
    def on_enter_key(self, event):
        """Maneja tecla Enter - Override en subclases"""
        pass
    
    def show_context_menu(self, event):
        """Muestra menú contextual - Override en subclases"""
        pass
    
    # ==================== Helpers ====================
    
    def _get_selected_item(self):
        """Retorna el item seleccionado en el TreeView"""
        selection = self.tree.selection()
        return selection[0] if selection else None
