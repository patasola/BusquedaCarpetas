# src/explorer_ui.py - Interfaz Gráfica del Explorador V.4.5 (Con columnas optimizadas)
import tkinter as tk
from tkinter import ttk

class ExplorerUI:
    """Maneja la interfaz gráfica del explorador"""
    
    def __init__(self, parent_frame, explorer_manager):
        self.parent_frame = parent_frame
        self.explorer_manager = explorer_manager
        self.frame = None
        self.content_frame = None
        self.grip_frame = None
        self.tree = None
        self.path_label = None
    
    def create(self, panel_width=300):
        """Crea la interfaz del explorador con ancho específico"""
        try:
            # Frame principal con grip - USAR ANCHO CALCULADO
            self.frame = tk.Frame(self.parent_frame, width=panel_width, relief=tk.RIDGE, borderwidth=1)
            self.frame.pack_propagate(False)
            
            # Grip de redimensionamiento
            self._create_grip()
            
            # Frame de contenido
            self.content_frame = tk.Frame(self.frame)
            self.content_frame.pack(side='right', fill='both', expand=True)
            
            # Crear componentes
            self._create_title()
            self._create_navigation_bar()
            self._create_path_display()
            self._create_treeview()
            self._create_shortcuts_bar()
            
            return True
        except Exception as e:
            print(f"Error creando explorador: {e}")
            return False
    
    def _create_grip(self):
        """Crea el grip de redimensionamiento"""
        self.grip_frame = tk.Frame(self.frame, width=5, bg='#d0d0d0', cursor='sb_h_double_arrow')
        self.grip_frame.pack(side='left', fill='y')
        self.grip_frame.pack_propagate(False)
        
        # Eventos del grip
        self.grip_frame.bind('<Button-1>', self.explorer_manager.start_resize)
        self.grip_frame.bind('<B1-Motion>', self.explorer_manager.do_resize)
        self.grip_frame.bind('<Enter>', lambda e: self.grip_frame.config(bg='#b0b0b0'))
        self.grip_frame.bind('<Leave>', lambda e: self.grip_frame.config(bg='#d0d0d0'))
    
    def _create_title(self):
        """Crea la barra de título"""
        title_frame = tk.Frame(self.content_frame, bg='#2c3e50')
        title_frame.pack(fill='x')
        
        tk.Label(title_frame, text="Explorador de Archivos", bg='#2c3e50', fg='white',
                font=('Segoe UI', 10, 'bold'), pady=8).pack(side='left', expand=True)
        
        tk.Button(title_frame, text="✕", command=self.explorer_manager.hide, bg='#2c3e50',
                 fg='white', font=('Segoe UI', 10, 'bold'), bd=0, padx=8, pady=4).pack(side='right')
    
    def _create_navigation_bar(self):
        """Crea barra de navegación con botones"""
        nav_frame = tk.Frame(self.content_frame, bg='#f0f0f0')
        nav_frame.pack(fill='x', padx=2, pady=2)
        
        # Configuración común para todos los botones
        btn_config = {
            'font': ('Segoe UI', 10),
            'bd': 1,
            'padx': 8,
            'pady': 4,
            'cursor': 'hand2',
            'relief': 'raised'
        }
        
        # Botón home
        self.btn_home = tk.Button(
            nav_frame, 
            text="🏠", 
            bg='#e3f2fd', 
            fg='#1565c0',
            command=self.explorer_manager.go_home,
            **btn_config
        )
        self.btn_home.pack(side='left', padx=2)
        
        # Botón refresh
        self.btn_refresh = tk.Button(
            nav_frame, 
            text="🔄", 
            bg='#fff3e0', 
            fg='#e65100',
            command=self.explorer_manager.refresh_tree,
            **btn_config
        )
        self.btn_refresh.pack(side='left', padx=2)
        
        # Botón nueva carpeta
        self.btn_new_folder = tk.Button(
            nav_frame, 
            text="📁", 
            bg='#e8f5e9', 
            fg='#2e7d32',
            command=self.explorer_manager.create_new_folder_inline,
            **btn_config
        )
        self.btn_new_folder.pack(side='left', padx=2)
        
        # Botón eliminar
        self.btn_delete = tk.Button(
            nav_frame, 
            text="🗑", 
            bg='#ffebee', 
            fg='#c62828',
            command=self.explorer_manager.delete_selected_item,
            **btn_config
        )
        self.btn_delete.pack(side='left', padx=2)
        
        # Tooltips
        self._create_tooltip(self.btn_home, "Ir a carpeta personal")
        self._create_tooltip(self.btn_refresh, "Actualizar árbol")
        self._create_tooltip(self.btn_new_folder, "Nueva carpeta (Ctrl+N)")
        self._create_tooltip(self.btn_delete, "Eliminar selección (Supr)")
    
    def _create_tooltip(self, widget, text):
        """Crea un tooltip simple para un widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="#ffffe0", 
                           relief='solid', borderwidth=1, font=('Segoe UI', 8))
            label.pack()
            
            widget.tooltip_window = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip_window'):
                widget.tooltip_window.destroy()
                del widget.tooltip_window
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def _create_path_display(self):
        """Crea la visualización de la ruta actual"""
        path_frame = tk.Frame(self.content_frame)
        path_frame.pack(fill='x', padx=5, pady=5)
        
        self.path_label = tk.Label(path_frame, text="", font=('Segoe UI', 8), anchor='w',
                                  bg='#f5f5f5', relief='sunken', bd=1, padx=5, pady=2)
        self.path_label.pack(fill='x')
    
    def _create_treeview(self):
        """Crea el TreeView con columnas OPTIMIZADAS"""
        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # TreeView con el MISMO estilo que el TreeView principal
        self.tree = ttk.Treeview(tree_frame, columns=("Fecha",), show="tree headings", 
                         style="Custom.Treeview", selectmode="extended")
        
        # Asegurar que use exactamente el mismo estilo
        style = ttk.Style()
        style.configure('Custom.Treeview',
                       rowheight=28,
                       background="#ffffff",
                       fieldbackground="#ffffff",
                       foreground="#2c3e50",
                       selectbackground="#e3f2fd",
                       selectforeground="#0d47a1",
                       borderwidth=1,
                       relief="solid",
                       font=('Segoe UI', 10))
        
        style.configure('Custom.Treeview.Heading',
                       font=('Segoe UI', 10, 'bold'),
                       background="#f8f9fa",
                       foreground="#2c3e50",
                       relief="flat",
                       borderwidth=1)
        
        # Tags IDÉNTICOS al TreeView principal
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('oddrow', background='#f8f9fa')
        
        # Configurar encabezados
        self.tree.heading("#0", text="Carpeta", anchor=tk.CENTER)
        self.tree.heading("Fecha", text="Modificación", anchor=tk.CENTER)
        
        # ANCHOS OPTIMIZADOS - Más compactos
        self.tree.column("#0", width=180, anchor=tk.W, minwidth=100)
        self.tree.column("Fecha", width=90, anchor=tk.CENTER, minwidth=85, stretch=False)
        
        # Configurar scrollbars
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.configure(command=self.tree.yview)
        hsb.configure(command=self.tree.xview)
        
        # Auto-hide scrollbars
        self.update_scrollbars = lambda: self._update_scrollbars(vsb, hsb)
        
        # Eventos (incluyendo navegación por flechas)
        self._bind_treeview_events()
        
        # Empaquetar TreeView
        self.tree.pack(side='left', fill='both', expand=True)
    
    def _create_shortcuts_bar(self):
        """Crea la barra de atajos de teclado en la parte inferior"""
        # Frame de la barra de atajos
        self.shortcuts_frame = tk.Frame(self.content_frame, bg='#f8f9fa', 
                                       relief='flat', borderwidth=1)
        self.shortcuts_frame.pack(side='bottom', fill='x', padx=0, pady=0)
        
        # Label para mostrar los atajos (con padding interno)
        self.shortcuts_label = tk.Label(
            self.shortcuts_frame,
            text="F2: Renombrar  |  Supr: Eliminar  |  Ctrl+N: Nueva carpeta  |  Enter: Abrir/Expandir",
            font=('Segoe UI', 8),
            bg='#f8f9fa',
            fg='#546e7a',
            anchor='w',
            padx=8,
            pady=4
        )
        self.shortcuts_label.pack(fill='x')
    
    def update_shortcuts_bar(self, context='none'):
        """Actualiza la barra de atajos según el contexto
        
        Args:
            context: 'none', 'folder', 'file'
        """
        if not hasattr(self, 'shortcuts_label'):
            return
        
        if context == 'folder':
            text = "F2: Renombrar carpeta  |  Supr: Eliminar  |  Enter: Expandir  |  Ctrl+N: Nueva carpeta"
            self.shortcuts_label.config(fg='#1565c0')  # Azul para carpetas
        elif context == 'file':
            text = "F2: Renombrar archivo  |  Supr: Eliminar  |  Enter: Abrir archivo"
            self.shortcuts_label.config(fg='#2e7d32')  # Verde para archivos
        else:
            text = "F2: Renombrar  |  Supr: Eliminar  |  Ctrl+N: Nueva carpeta  |  Enter: Abrir/Expandir"
            self.shortcuts_label.config(fg='#546e7a')  # Gris neutral
        
        self.shortcuts_label.config(text=text)
    
    def _bind_treeview_events(self):
        """Configura los eventos del TreeView incluyendo navegación por flechas"""
        # Eventos básicos
        self.tree.bind('<Double-1>', self.explorer_manager.on_double_click)
        self.tree.bind('<Return>', self.explorer_manager.on_enter_key)
        self.tree.bind('<Button-3>', self.explorer_manager.show_context_menu)
        self.tree.bind('<F2>', self.explorer_manager.on_f2_key)
        self.tree.bind('<Configure>', lambda e: self.tree.after_idle(self.update_scrollbars))
        
        # Tecla Delete/Supr para eliminar
        self.tree.bind('<Delete>', lambda e: self.explorer_manager.delete_selected_item())
        
        # Actualizar barra de atajos al cambiar selección
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.explorer_manager.update_shortcuts_context())
        
        # NAVEGACIÓN POR FLECHAS
        self.tree.bind('<Up>', self._on_arrow_up)
        self.tree.bind('<Down>', self._on_arrow_down)
        self.tree.bind('<Left>', self._on_arrow_left_custom)
        self.tree.bind('<Right>', self._on_arrow_right_custom)
        self.tree.bind('<Home>', self._on_home_key)
        self.tree.bind('<End>', self._on_end_key)
        self.tree.bind('<Prior>', self._on_page_up)
        self.tree.bind('<Next>', self._on_page_down)
        
        # Foco en el TreeView para recibir eventos de teclado
        self.tree.configure(takefocus=True)
    
    def _on_arrow_left_custom(self, event):
        """Maneja flecha izquierda - colapsar o ir al padre"""
        selection = self.tree.selection()
        if not selection:
            return "break"
        
        item = selection[0]
        
        if self.tree.item(item, 'open'):
            self.tree.item(item, open=False)
        else:
            parent = self.tree.parent(item)
            if parent:
                self.tree.selection_set(parent)
                self.tree.focus(parent)
                self.tree.see(parent)
        return "break"
    
    def _on_arrow_right_custom(self, event):
        """Maneja flecha derecha - expandir o ir al primer hijo"""
        selection = self.tree.selection()
        if not selection:
            return "break"
        
        item = selection[0]
        
        if self.tree.get_children(item) and not self.tree.item(item, 'open'):
            self.tree.item(item, open=True)
            self.explorer_manager.handle_node_expansion_immediate(item)
        elif self.tree.item(item, 'open'):
            children = self.tree.get_children(item)
            if children:
                self.tree.selection_set(children[0])
                self.tree.focus(children[0])
                self.tree.see(children[0])
        return "break"
    
    def _on_arrow_up(self, event):
        """Maneja flecha arriba"""
        items = self._get_visible_items()
        if not items:
            return "break"
        
        selection = self.tree.selection()
        if not selection:
            self.tree.selection_set(items[-1])
            self.tree.focus(items[-1])
            self.tree.see(items[-1])
        else:
            current = selection[0]
            try:
                current_index = items.index(current)
                if current_index > 0:
                    prev_item = items[current_index - 1]
                    self.tree.selection_set(prev_item)
                    self.tree.focus(prev_item)
                    self.tree.see(prev_item)
            except ValueError:
                pass
        return "break"
    
    def _on_arrow_down(self, event):
        """Maneja flecha abajo"""
        items = self._get_visible_items()
        if not items:
            return "break"
        
        selection = self.tree.selection()
        if not selection:
            self.tree.selection_set(items[0])
            self.tree.focus(items[0])
            self.tree.see(items[0])
        else:
            current = selection[0]
            try:
                current_index = items.index(current)
                if current_index < len(items) - 1:
                    next_item = items[current_index + 1]
                    self.tree.selection_set(next_item)
                    self.tree.focus(next_item)
                    self.tree.see(next_item)
            except ValueError:
                pass
        return "break"
    
    def _on_home_key(self, event):
        """Maneja Home"""
        items = self._get_visible_items()
        if items:
            self.tree.selection_set(items[0])
            self.tree.focus(items[0])
            self.tree.see(items[0])
        return "break"
    
    def _on_end_key(self, event):
        """Maneja End"""
        items = self._get_visible_items()
        if items:
            self.tree.selection_set(items[-1])
            self.tree.focus(items[-1])
            self.tree.see(items[-1])
        return "break"
    
    def _on_page_up(self, event):
        """Maneja Page Up"""
        items = self._get_visible_items()
        if not items:
            return "break"
        
        selection = self.tree.selection()
        if selection:
            current = selection[0]
            try:
                current_index = items.index(current)
                new_index = max(0, current_index - 5)
                new_item = items[new_index]
                self.tree.selection_set(new_item)
                self.tree.focus(new_item)
                self.tree.see(new_item)
            except ValueError:
                pass
        return "break"
    
    def _on_page_down(self, event):
        """Maneja Page Down"""
        items = self._get_visible_items()
        if not items:
            return "break"
        
        selection = self.tree.selection()
        if selection:
            current = selection[0]
            try:
                current_index = items.index(current)
                new_index = min(len(items) - 1, current_index + 5)
                new_item = items[new_index]
                self.tree.selection_set(new_item)
                self.tree.focus(new_item)
                self.tree.see(new_item)
            except ValueError:
                pass
        return "break"
    
    def _get_visible_items(self):
        """Obtiene todos los elementos visibles en el árbol"""
        def get_visible_recursive(parent=''):
            items = []
            for child in self.tree.get_children(parent):
                items.append(child)
                if self.tree.item(child, 'open'):
                    items.extend(get_visible_recursive(child))
            return items
        
        return get_visible_recursive()
    
    def _update_scrollbars(self, vsb, hsb):
        """Actualiza la visibilidad de las scrollbars"""
        try:
            self.tree.update_idletasks()
            
            tree_height = self.tree.winfo_height()
            tree_width = self.tree.winfo_width()
            
            if tree_height <= 1 or tree_width <= 1:
                self.tree.after(100, lambda: self._update_scrollbars(vsb, hsb))
                return
            
            children = self.tree.get_children()
            
            # Scrollbar vertical
            if children:
                total_items = len(self._get_visible_items())
                visible_items = max(1, tree_height // 28)
                
                needs_vertical = total_items > visible_items
                is_vertical_visible = vsb.winfo_viewable()
                
                if needs_vertical and not is_vertical_visible:
                    vsb.pack(side='right', fill='y')
                elif not needs_vertical and is_vertical_visible:
                    vsb.pack_forget()
            else:
                if vsb.winfo_viewable():
                    vsb.pack_forget()
            
            # Scrollbar horizontal
            if children:
                max_width = 0
                for item in self._get_visible_items():
                    bbox = self.tree.bbox(item, column='#0')
                    if bbox:
                        item_width = bbox[0] + bbox[2]
                        max_width = max(max_width, item_width)
                
                needs_horizontal = max_width > tree_width
                is_horizontal_visible = hsb.winfo_viewable()
                
                if needs_horizontal and not is_horizontal_visible:
                    hsb.pack(side='bottom', fill='x')
                elif not needs_horizontal and is_horizontal_visible:
                    hsb.pack_forget()
            else:
                if hsb.winfo_viewable():
                    hsb.pack_forget()
                    
        except Exception as e:
            print(f"Error actualizando scrollbars: {e}")
            self.tree.after(200, lambda: self._update_scrollbars(vsb, hsb))