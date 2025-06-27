# src/ui_components.py - Componentes de Interfaz
"""
Maneja la creación y configuración de todos los elementos de la interfaz
"""

import tkinter as tk
from tkinter import ttk

class UIComponents:
    def __init__(self, master, version):
        self.master = master
        self.version = version
        self.configurar_estilos()

    def configurar_estilos(self):
        """Configura estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        gris_oscuro = "#424242"
        gris_medio = "#757575"
        gris_claro = "#e0e0e0"
        gris_muy_claro = "#f5f5f5"
        blanco = "#ffffff"
        azul_barra = "#1976D2"
        
        # Estilos de botones
        style.configure('TButton', 
                      font=("Arial", 10), 
                      foreground=gris_oscuro,
                      background=gris_claro,
                      padding=8,
                      width=12)
        
        # Barra de progreso
        style.configure('Horizontal.TProgressbar',
                       thickness=20,
                       troughcolor=gris_muy_claro,
                       background=azul_barra,
                       borderwidth=0)
        
        # Treeview
        style.configure('Treeview.Heading', 
                      font=('Arial', 10, 'bold'),
                      background=gris_claro,
                      foreground=gris_oscuro)
        
        style.configure('Treeview',
                      rowheight=25,
                      background=blanco,
                      fieldbackground=blanco,
                      foreground=gris_oscuro)

    def crear_interfaz_completa(self):
        """Crea toda la interfaz y retorna referencias a elementos importantes"""
        # Frame principal
        main_frame = tk.Frame(self.master, bg="#f6f5f5")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=20)
        
        # Título
        tk.Label(
            main_frame,
            text="Búsqueda Rápida de Carpetas",
            font=("Arial", 16, "bold"),
            bg="#f6f5f5",
            fg="#424242"
        ).pack(pady=(0, 20))
        
        # Campo de búsqueda
        tk.Label(
            main_frame,
            text="Ingrese el criterio de búsqueda:",
            font=("Arial", 10),
            bg="#f6f5f5",
            fg="#757575"
        ).pack()
        
        entry = tk.Entry(
            main_frame,
            width=40,
            font=("Arial", 10),
            relief=tk.SOLID,
            borderwidth=1,
            bg="#ffffff",
            fg="#424242",
            justify="center"
        )
        entry.pack(pady=10, ipady=5)
        entry.focus_set()
        
        # Botones de búsqueda
        btn_frame = tk.Frame(main_frame, bg="#f6f5f5")
        btn_frame.pack(pady=(0, 20))
        
        btn_buscar = ttk.Button(btn_frame, text="Buscar")
        btn_buscar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(btn_frame, text="Cancelar", state=tk.DISABLED)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        # Barra de progreso
        progress = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            mode="determinate",
            style='Horizontal.TProgressbar',
            length=400
        )
        progress.pack(pady=(0, 10))
        
        # Etiqueta de porcentaje
        label_porcentaje = tk.Label(
            main_frame,
            text="0%",
            font=("Arial", 10),
            bg="#f6f5f5",
            fg="#757575"
        )
        label_porcentaje.pack(pady=(0, 15))
        
        # TreeView
        tree_frame = tk.Frame(main_frame, bg="#f6f5f5")
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 15))
        
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        tree = ttk.Treeview(
            tree_frame,
            columns=("Nombre", "Ruta"),
            show="headings",
            selectmode="browse",
            height=6,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        tree.heading("Nombre", text="Nombre", anchor=tk.CENTER)
        tree.heading("Ruta", text="Ruta", anchor=tk.CENTER)
        tree.column("Nombre", width=200, anchor=tk.CENTER)
        tree.column("Ruta", width=400, anchor=tk.CENTER)
        
        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)
        
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Botones de acciones
        action_frame = tk.Frame(main_frame, bg="#f6f5f5")
        action_frame.pack(pady=(0, 10))
        
        btn_copiar = ttk.Button(action_frame, text="Copiar Ruta (F3)", state=tk.DISABLED)
        btn_copiar.pack(side=tk.LEFT, padx=5)
        
        btn_abrir = ttk.Button(action_frame, text="Abrir Carpeta (F4)", state=tk.DISABLED)
        btn_abrir.pack(side=tk.LEFT, padx=5)
        
        # Línea de información de carpeta y cache
        label_carpeta_info = tk.Label(
            main_frame,
            text="Carpeta: No seleccionada | Cache: No disponible",
            font=("Arial", 9),
            bg="#f6f5f5",
            fg="#757575"
        )
        label_carpeta_info.pack(pady=(5, 0))
        
        # Barra de estado
        status_frame = tk.Frame(main_frame, bg="#f6f5f5", height=28)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        label_estado = tk.Label(
            status_frame,
            text="Listo para buscar. Presione F2 para enfocar el campo de búsqueda",
            font=("Arial", 9),
            anchor=tk.W,
            bg="#f6f5f5",
            fg="#424242"
        )
        label_estado.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        label_version = tk.Label(
            status_frame,
            text=self.version,
            font=("Arial", 8),
            bg="#f6f5f5",
            fg="#757575"
        )
        label_version.pack(side=tk.RIGHT)
        
        # Retornar diccionario con todos los elementos
        return {
            'entry': entry,
            'btn_buscar': btn_buscar,
            'btn_cancelar': btn_cancelar,
            'progress': progress,
            'label_porcentaje': label_porcentaje,
            'tree': tree,
            'btn_copiar': btn_copiar,
            'btn_abrir': btn_abrir,
            'label_estado': label_estado,
            'label_carpeta_info': label_carpeta_info
        }