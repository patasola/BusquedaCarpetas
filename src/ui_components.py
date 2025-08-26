# src/ui_components.py - Componentes de Interfaz V.4.1 (Corregido)
import tkinter as tk
from tkinter import ttk

class Colors:
    BACKGROUND = "#f6f5f5"
    TITLE_FG = "#424242"
    INFO_FG = "#424242"
    TREE_FG = "#424242"
    TREE_BG = "#ffffff"
    TREE_SELECT_BG = "#e3f2fd"
    TREE_SELECT_FG = "#0d47a1"
    BUTTON_BG = "#e0e0e0"
    BUTTON_FG = "#424242"
    BUTTON_ACTIVE_BG = "#d0d0d0"
    PROGRESS_BG = "#1976D2"
    CACHE_BAR_BG = "#F0F8FF"  # Azul MUCHO más claro (Alice Blue)
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
        self.configurar_estilos()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TButton', 
                      font=("Segoe UI", 9), 
                      foreground="#424242",
                      background="#e0e0e0",
                      padding=6,
                      width=10)
        
        style.configure('Horizontal.TProgressbar',
                       thickness=15,
                       troughcolor="#f5f5f5",
                       background="#1976D2",
                       borderwidth=0)
        
        # Estilo mejorado para encabezados de tabla
        style.configure('Custom.Treeview.Heading', 
                      font=('Segoe UI', 10, 'bold'),
                      background="#f8f9fa",
                      foreground="#2c3e50",
                      relief="flat",
                      borderwidth=1)
        
        # Estilo mejorado para la tabla
        style.configure('Custom.Treeview',
                      rowheight=28,
                      background="#ffffff",
                      fieldbackground="#ffffff",
                      foreground="#2c3e50",
                      selectbackground="#e8f4fd",
                      selectforeground="#1976d2",
                      borderwidth=1,
                      relief="solid")
        
        # Configurar colores alternados para filas
        style.map('Custom.Treeview',
                 background=[('selected', '#e8f4fd')],
                 foreground=[('selected', '#1976d2')])

    def crear_interfaz_completa(self):
        # Frame principal con menos padding para el historial
        main_frame = tk.Frame(self.master, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)  # Reducido padding
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Búsqueda Rápida de Carpetas",
            font=Fonts.TITLE,
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG
        )
        title_label.pack(pady=(0, 20))
        
        # Criterio de búsqueda - MISMO COLOR QUE EL TÍTULO
        search_label = tk.Label(
            main_frame,
            text="Criterio de búsqueda:",
            font=Fonts.NORMAL,
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG
        )
        search_label.pack()
        
        # Campo de entrada (centrado) - más compacto
        entry = tk.Entry(
            main_frame,
            width=30,  # Reducido de 35 a 30
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            borderwidth=1,
            bg="#ffffff",
            fg=Colors.TREE_FG,
            justify="center"
        )
        entry.pack(pady=8, ipady=4)
        entry.focus_set()
        
        # Indicador de modo DEBAJO del campo (centrado)
        modo_label = tk.Label(
            main_frame,
            text="[123] Numérico",
            font=("Segoe UI", 9),
            bg=Colors.BACKGROUND,
            fg="#006600"
        )
        modo_label.pack(pady=(2, 15))
        
        # Frame de botones
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
            padx=15,
            pady=8,
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
            padx=15,
            pady=8,
            state=tk.DISABLED,
            cursor="hand2"
        )
        btn_cancelar.pack(side=tk.LEFT)
        
        # Tabla de resultados con marco estético
        table_container = tk.Frame(main_frame, bg="#e9ecef", relief=tk.SOLID, borderwidth=1)
        table_container.pack(fill=tk.BOTH, expand=True, pady=(10, 15))
        
        tree_frame = tk.Frame(table_container, bg="#ffffff")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Scrollbars estáticas
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # CORREGIDO: Solo 2 columnas (sin "Nombre") + título para columna del árbol
        tree = ttk.Treeview(
            tree_frame,
            columns=("Método", "Ruta"),
            show="tree headings",  # Mostrar árbol + encabezados
            selectmode="browse",
            height=5,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
            style="Custom.Treeview"
        )
        
        # CORREGIDO: Configurar encabezados (columna del árbol + 2 columnas)
        tree.heading("#0", text="Carpeta", anchor=tk.CENTER)  # Título para columna del árbol
        tree.heading("Método", text="Método", anchor=tk.CENTER)
        tree.heading("Ruta", text="Ruta Relativa", anchor=tk.W)
        
        # CORREGIDO: Configurar columnas con mejor espaciado para historial visible
        tree.column("#0", width=200, anchor=tk.W, minwidth=150)  # Columna del árbol (reducida)
        tree.column("Método", width=70, anchor=tk.CENTER, minwidth=60)  # Reducida
        tree.column("Ruta", width=280, anchor=tk.W, minwidth=200)  # Reducida para hacer espacio
        
        # Configurar scrollbars automáticas mejoradas
        def configurar_scrollbars():
            tree.update_idletasks()
            
            # Scrollbar vertical
            total_items = len(tree.get_children())
            if total_items > tree['height']:
                if not y_scroll.winfo_viewable():
                    y_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(1, 0))
            else:
                if y_scroll.winfo_viewable():
                    y_scroll.pack_forget()
            
            # Scrollbar horizontal
            if tree.bbox(""):
                tree_width = tree.winfo_width()
                content_width = sum(tree.column(col, "width") for col in tree["columns"])
                if content_width > tree_width - 20:  # Margen para scrollbar vertical
                    if not x_scroll.winfo_viewable():
                        x_scroll.pack(side=tk.BOTTOM, fill=tk.X, pady=(1, 0))
                else:
                    if x_scroll.winfo_viewable():
                        x_scroll.pack_forget()
        
        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)
        
        # Eventos para scrollbars y efectos visuales
        tree.bind('<Configure>', lambda e: tree.after_idle(configurar_scrollbars))
        tree.bind('<<TreeviewSelect>>', lambda e: tree.after_idle(configurar_scrollbars))
        
        tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Configurar tags para filas alternadas
        tree.tag_configure('oddrow', background='#f8f9fa')
        tree.tag_configure('evenrow', background='#ffffff')
        
        # Botones de acción más compactos
        action_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND)
        action_frame.pack(pady=(10, 15))  # Menos padding
        
        btn_copiar = tk.Button(
            action_frame,
            text="📋 Copiar",  # Texto más corto
            font=Fonts.BUTTONS,
            bg="#e8f5e8",
            fg="#2e7d32",
            relief=tk.FLAT,
            borderwidth=1,
            padx=12,  # Menos padding
            pady=6,   # Menos padding
            state=tk.DISABLED,
            cursor="hand2",
            activebackground="#c8e6c9"
        )
        btn_copiar.pack(side=tk.LEFT, padx=(0, 8))  # Menos espaciado
        
        btn_abrir = tk.Button(
            action_frame,
            text="📂 Abrir",  # Texto más corto
            font=Fonts.BUTTONS,
            bg="#e3f2fd",
            fg="#1565c0",
            relief=tk.FLAT,
            borderwidth=1,
            padx=12,  # Menos padding
            pady=6,   # Menos padding
            state=tk.DISABLED,
            cursor="hand2",
            activebackground="#bbdefb"
        )
        btn_abrir.pack(side=tk.LEFT)
        
        # Barra de información (caché) - AZUL MUY CLARO
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
        
        # Barra de estado - TRANSPARENTE
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
            'configurar_scrollbars': configurar_scrollbars
        }