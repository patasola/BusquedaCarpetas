# src/ui_components.py - Componentes de Interfaz V.4.2 (Tooltip Simple)
import tkinter as tk
from tkinter import ttk
from .components.tree_tooltip import TreeViewTooltip


class Colors:
    BACKGROUND = "#f6f5f5"
    TITLE_FG = "#424242"
    TREE_BG = "#ffffff"
    TREE_SELECT_BG = "#e3f2fd"
    TREE_SELECT_FG = "#0d47a1"
    BUTTON_BG = "#e0e0e0"
    BUTTON_FG = "#424242"
    BUTTON_ACTIVE_BG = "#d0d0d0"
    CACHE_BAR_BG = "#F0F8FF"
    STATUS_BAR_BG = "SystemButtonFace"

class Fonts:
    BUTTONS = ("Segoe UI", 9)
    NORMAL = ("Segoe UI", 9)
    TITLE = ("Segoe UI", 14, "bold")
    VERSION = ("Segoe UI", 8)

class UIComponents:
    def __init__(self, master, version):
        self.master = master
        self.version = version
        self.tooltip = None  # Referencia al tooltip
        self.configurar_estilos()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilos principales
        style.configure('TButton', 
                      font=Fonts.BUTTONS, 
                      foreground=Colors.BUTTON_FG,
                      background=Colors.BUTTON_BG,
                      padding=6, width=10)
        
        style.configure('Horizontal.TProgressbar',
                       thickness=15, troughcolor="#f5f5f5",
                       background="#1976D2", borderwidth=0)
        
        style.configure('Custom.Treeview.Heading', 
                      font=('Segoe UI', 10, 'bold'),
                      background="#f8f9fa", foreground="#2c3e50",
                      relief="flat", borderwidth=1)
        
        style.configure('Custom.Treeview',
                      rowheight=28, background=Colors.TREE_BG,
                      fieldbackground=Colors.TREE_BG, foreground="#2c3e50",
                      selectbackground=Colors.TREE_SELECT_BG,
                      selectforeground=Colors.TREE_SELECT_FG,
                      borderwidth=1, relief="solid")
        
        style.map('Custom.Treeview',
                 background=[('selected', Colors.TREE_SELECT_BG)],
                 foreground=[('selected', Colors.TREE_SELECT_FG)])

    def crear_interfaz_completa(self):
        # Frame principal
        main_frame = tk.Frame(self.master, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Título
        tk.Label(
            main_frame,
            text="Búsqueda Rápida de Carpetas",
            font=Fonts.TITLE,
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG
        ).pack(pady=(0, 20))
        
        # Campo de búsqueda
        tk.Label(
            main_frame,
            text="Criterio de búsqueda:",
            font=Fonts.NORMAL,
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG
        ).pack()
        
        entry = tk.Entry(
            main_frame,
            width=30,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            borderwidth=1,
            bg="#ffffff",
            fg=Colors.TITLE_FG,
            justify="center"
        )
        entry.pack(pady=8, ipady=4)
        entry.focus_set()
        
        # Indicador de modo
        modo_label = tk.Label(
            main_frame,
            text="[123] Numérico",
            font=("Segoe UI", 9),
            bg=Colors.BACKGROUND,
            fg="#006600"
        )
        modo_label.pack(pady=(2, 15))
        
        # Botones de búsqueda
        button_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND)
        button_frame.pack(pady=(0, 10))
        
        btn_buscar = tk.Button(
            button_frame,
            text="Buscar",
            font=Fonts.BUTTONS,
            bg=Colors.BUTTON_BG,
            fg=Colors.BUTTON_FG,
            relief=tk.FLAT,
            borderwidth=1,
            padx=15, pady=8,
            state=tk.DISABLED,
            cursor="hand2"
        )
        btn_buscar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_cancelar = tk.Button(
            button_frame,
            text="Cancelar",
            font=Fonts.BUTTONS,
            bg=Colors.BUTTON_BG,
            fg=Colors.BUTTON_FG,
            relief=tk.FLAT,
            borderwidth=1,
            padx=15, pady=8,
            state=tk.DISABLED,
            cursor="hand2"
        )
        btn_cancelar.pack(side=tk.LEFT)
        
        # Tabla de resultados
        table_container = tk.Frame(main_frame, bg="#e9ecef", relief=tk.SOLID, borderwidth=1)
        table_container.pack(fill=tk.BOTH, expand=True, pady=(10, 15))
        
        tree_frame = tk.Frame(table_container, bg=Colors.TREE_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # TreeView
        tree = ttk.Treeview(
            tree_frame,
            columns=("Método", "Ruta"),
            show="tree headings",
            selectmode="browse",
            height=5,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            style="Custom.Treeview"
        )
        
        # Configurar encabezados y columnas
        tree.heading("#0", text="Carpeta", anchor=tk.CENTER)
        tree.heading("Método", text="M", anchor=tk.CENTER)
        tree.heading("Ruta", text="Ruta Relativa", anchor=tk.W)
        
        tree.column("#0", width=200, anchor=tk.W, minwidth=120, stretch=False)
        tree.column("Método", width=35, anchor=tk.CENTER, minwidth=30, stretch=False)
        tree.column("Ruta", width=300, anchor=tk.W, minwidth=150, stretch=True)
        
        # AGREGAR TOOLTIP AL TREEVIEW
        self.tooltip = TreeViewTooltip(tree)
        
        # Configurar Grid Layout
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # TreeView en Grid
        tree.grid(row=0, column=0, sticky='nsew')
        
        # Configurar scrollbars
        def configurar_scrollbars():
            # Scrollbar vertical
            if len(tree.get_children()) > tree['height']:
                y_scroll.grid(row=0, column=1, sticky='ns')
            else:
                y_scroll.grid_remove()
            
            # Scrollbar horizontal - Solo si hay items Y se necesita
            if not tree.get_children():
                x_scroll.grid_remove()
                return

            # Usar after_idle para asegurar que la geometría esté actualizada
            def check_xview():
                xview = tree.xview()
                if xview[0] > 0.0 or xview[1] < 1.0:
                    x_scroll.grid(row=1, column=0, sticky='ew')
                else:
                    x_scroll.grid_remove()
            
            tree.after_idle(check_xview)
        
        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)
        
        # Bind para auto-hide scrollbars
        tree.bind('<Configure>', lambda e: configurar_scrollbars())
        
        # Inicializar
        tree.after(100, configurar_scrollbars)
        tree.tag_configure('evenrow', background='#ffffff')
        
        # Tags para métodos con colores
        method_tags = {
            'cache_method': {'foreground': '#1b5e20', 'background': '#e8f5e8', 'font': ('Segoe UI', 10, 'bold')},
            'tradicional_method': {'foreground': '#0d47a1', 'background': '#e3f2fd', 'font': ('Segoe UI', 10, 'bold')},
            'tree_method': {'foreground': '#e65100', 'background': '#fff3e0', 'font': ('Segoe UI', 10, 'bold')},
            'unknown_method': {'foreground': '#424242', 'background': '#f5f5f5', 'font': ('Segoe UI', 10, 'bold')}
        }
        
        for tag, config in method_tags.items():
            tree.tag_configure(tag, **config)
        
        # Tags combinados para filas alternadas con colores
        combined_tags = [
            ('evenrow_cache', '#f1f8e9', '#1b5e20'),
            ('evenrow_tradicional', '#e8f4fd', '#0d47a1'),
            ('evenrow_tree', '#fff8f0', '#e65100'),
            ('evenrow_unknown', '#fafafa', '#424242'),
            ('oddrow_cache', '#e8f5e8', '#1b5e20'),
            ('oddrow_tradicional', '#e3f2fd', '#0d47a1'),
            ('oddrow_tree', '#fff3e0', '#e65100'),
            ('oddrow_unknown', '#f5f5f5', '#424242')
        ]
        
        for tag, bg, fg in combined_tags:
            tree.tag_configure(tag, background=bg, foreground=fg, font=('Segoe UI', 10, 'bold'))
        
        # Botones de acción
        action_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND)
        action_frame.pack(pady=(10, 15))
        
        btn_copiar = tk.Button(
            action_frame,
            text="Copiar",
            font=Fonts.BUTTONS,
            bg="#e8f5e8", fg="#2e7d32",
            relief=tk.FLAT, borderwidth=1,
            padx=12, pady=6,
            state=tk.DISABLED, cursor="hand2",
            activebackground="#c8e6c9"
        )
        btn_copiar.pack(side=tk.LEFT, padx=(0, 8))
        
        btn_abrir = tk.Button(
            action_frame,
            text="Abrir",
            font=Fonts.BUTTONS,
            bg="#e3f2fd", fg="#1565c0",
            relief=tk.FLAT, borderwidth=1,
            padx=12, pady=6,
            state=tk.DISABLED, cursor="hand2",
            activebackground="#bbdefb"
        )
        btn_abrir.pack(side=tk.LEFT)
        
        # Barra de información de caché
        info_frame = tk.Frame(self.master, bg=Colors.CACHE_BAR_BG, height=22)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X)
        info_frame.pack_propagate(False)
        
        label_carpeta_info = tk.Label(
            info_frame,
            text="Sin carpeta seleccionada",
            font=Fonts.NORMAL,
            anchor=tk.W,
            bg=Colors.CACHE_BAR_BG,
            fg="#2c3e50",
            padx=10
        )
        label_carpeta_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Barra de estado
        status_frame = tk.Frame(self.master, bg=Colors.STATUS_BAR_BG, height=22)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        label_estado = tk.Label(
            status_frame,
            text="F2: Enfocar búsqueda • F3: Copiar • F4: Abrir • F5: Modo • Tab: Navegar",
            font=Fonts.NORMAL,
            anchor=tk.W,
            bg=Colors.STATUS_BAR_BG,
            fg="#2c3e50",
            padx=10
        )
        label_estado.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        label_version = tk.Label(
            status_frame,
            text=self.version,
            font=Fonts.VERSION,
            bg=Colors.STATUS_BAR_BG,
            fg="#666666",
            padx=10
        )
        label_version.pack(side=tk.RIGHT)
        
        return {
            'entry': entry,
            'modo_label': modo_label,
            'btn_buscar': btn_buscar,
            'btn_cancelar': btn_cancelar,
            'tree': tree,
            'btn_copiar': btn_copiar,
            'btn_abrir': btn_abrir,
            'label_estado': label_estado,
            'label_carpeta_info': label_carpeta_info,
            'configurar_scrollbars': configurar_scrollbars,
            'tooltip': self.tooltip
        }
