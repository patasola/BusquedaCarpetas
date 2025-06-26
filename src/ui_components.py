# src/ui_components.py - Componentes de Interfaz
"""
Maneja la creación y configuración de todos los elementos de la interfaz
"""

import tkinter as tk
from tkinter import ttk
from .constants import *

class UIComponents:
    def __init__(self, master):
        self.master = master
        self.configurar_estilos()

    def configurar_estilos(self):
        """Configura estilos personalizados en escala de grises con barra azul sin borde"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores base
        gris_oscuro = COLORS['dark_gray']
        gris_medio = COLORS['medium_gray']
        gris_claro = COLORS['light_gray']
        gris_muy_claro = COLORS['very_light_gray']
        blanco = COLORS['white']
        azul_barra = COLORS['blue_bar']
        
        # Botón primario (en gris)
        style.configure('TButton', 
                      font=FONT_NORMAL, 
                      foreground=gris_oscuro,
                      background=gris_claro,
                      padding=8,
                      width=12,
                      relief=tk.RAISED,
                      borderwidth=1)
        
        style.map('TButton',
                 background=[('active', gris_medio), ('disabled', gris_muy_claro)],
                 foreground=[('active', blanco), ('disabled', gris_medio)])
        
        # Barra de progreso (AZUL sin borde)
        style.configure('Horizontal.TProgressbar',
                       thickness=20,
                       troughcolor=gris_muy_claro,
                       background=azul_barra,
                       borderwidth=0,
                       troughrelief='flat',
                       relief='flat')
                       
        # Treeview
        style.configure('Treeview.Heading', 
                      font=('Arial', 10, 'bold'),
                      background=gris_claro,
                      foreground=gris_oscuro,
                      relief=tk.FLAT)
        
        style.configure('Treeview',
                      rowheight=25,
                      background=blanco,
                      fieldbackground=blanco,
                      foreground=gris_oscuro)
        
        style.map('Treeview',
                 background=[('selected', gris_medio)],
                 foreground=[('selected', blanco)])

    def crear_frame_principal(self):
        """Crea el frame principal con padding"""
        main_frame = tk.Frame(self.master, bg=COLORS['very_light_gray'])
        main_frame.pack(expand=True, fill=tk.BOTH, 
                       padx=MAIN_PADDING['x'], pady=MAIN_PADDING['y'])
        return main_frame

    def crear_titulo(self, parent):
        """Crea el título centrado"""
        title_frame = tk.Frame(parent, bg=COLORS['very_light_gray'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame,
            text=APP_TITLE,
            font=FONT_TITLE,
            bg=COLORS['very_light_gray'],
            fg=COLORS['dark_gray']
        ).pack()
        
        return title_frame

    def crear_campo_busqueda(self, parent, callback_enter=None):
        """Crea el panel de búsqueda"""
        search_frame = tk.Frame(parent, bg=COLORS['very_light_gray'])
        search_frame.pack(fill=tk.X, pady=(0, 15))

        # Etiqueta centrada
        tk.Label(
            search_frame,
            text="Ingrese el criterio de búsqueda:",
            font=FONT_NORMAL,
            bg=COLORS['very_light_gray'],
            fg=COLORS['medium_gray']
        ).pack()

        # Frame para centrar el Entry
        entry_frame = tk.Frame(search_frame, bg=COLORS['very_light_gray'])
        entry_frame.pack()

        # Campo de entrada
        entry = tk.Entry(
            entry_frame,
            width=ENTRY_WIDTH,
            font=FONT_NORMAL,
            relief=tk.SOLID,
            borderwidth=1,
            bg=COLORS['white'],
            fg=COLORS['dark_gray'],
            justify="center"
        )
        entry.pack(pady=10, ipady=5)
        entry.focus_set()
        
        if callback_enter:
            entry.bind("<Return>", callback_enter)

        return entry

    def crear_botones_busqueda(self, parent, callback_buscar, callback_cancelar):
        """Crea los botones de búsqueda (sin botón cache)"""
        btn_frame = tk.Frame(parent, bg=COLORS['very_light_gray'])
        btn_frame.pack(fill=tk.X, pady=(0, 20))

        # Frame interno para centrar los botones
        btn_inner_frame = tk.Frame(btn_frame, bg=COLORS['very_light_gray'])
        btn_inner_frame.pack()

        # Botón Buscar
        btn_buscar = ttk.Button(
            btn_inner_frame,
            text="Buscar",
            command=callback_buscar
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        # Botón Cancelar
        btn_cancelar = ttk.Button(
            btn_inner_frame,
            text="Cancelar",
            command=callback_cancelar,
            state=tk.DISABLED
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)

        return btn_buscar, btn_cancelar

    def crear_barra_progreso(self, parent):
        """Crea la barra de progreso y etiqueta de porcentaje"""
        progress_frame = tk.Frame(parent, bg=COLORS['very_light_gray'])
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            style='Horizontal.TProgressbar',
            length=PROGRESS_LENGTH
        )
        progress.pack()

        # Etiqueta de porcentaje centrada
        label_porcentaje = tk.Label(
            progress_frame,
            text="0%",
            font=FONT_NORMAL,
            bg=COLORS['very_light_gray'],
            fg=COLORS['medium_gray']
        )
        label_porcentaje.pack(pady=(5, 15))

        return progress, label_porcentaje

    def crear_treeview_resultados(self, parent, callback_select=None):
        """Crea el treeview para mostrar resultados"""
        tree_frame = tk.Frame(parent, bg=COLORS['very_light_gray'])
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 15))

        # Scrollbars
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")

        tree = ttk.Treeview(
            tree_frame,
            columns=("Nombre", "Ruta"),
            show="headings",
            selectmode="browse",
            height=TREE_HEIGHT,
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        # Columnas centradas
        tree.heading("Nombre", text="Nombre", anchor=tk.CENTER)
        tree.heading("Ruta", text="Ruta", anchor=tk.CENTER)
        tree.column("Nombre", width=200, anchor=tk.CENTER)
        tree.column("Ruta", width=400, anchor=tk.CENTER)

        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)

        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        if callback_select:
            tree.bind("<<TreeviewSelect>>", callback_select)

        return tree

    def crear_botones_acciones(self, parent, callback_copiar, callback_abrir):
        """Crea los botones de acciones inferiores"""
        action_frame = tk.Frame(parent, bg=COLORS['very_light_gray'])
        action_frame.pack(fill=tk.X, pady=(0, 10))

        # Frame interno para centrar los botones
        action_inner_frame = tk.Frame(action_frame, bg=COLORS['very_light_gray'])
        action_inner_frame.pack()

        btn_copiar = ttk.Button(
            action_inner_frame,
            text="Copiar Ruta (F3)",
            command=callback_copiar,
            state=tk.DISABLED
        )
        btn_copiar.pack(side=tk.LEFT, padx=5)

        btn_abrir = ttk.Button(
            action_inner_frame,
            text="Abrir Carpeta (F4)",
            command=callback_abrir,
            state=tk.DISABLED
        )
        btn_abrir.pack(side=tk.LEFT, padx=5)

        return btn_copiar, btn_abrir

    def crear_barra_estado(self, parent):
        """Crea la barra de estado con versión"""
        status_frame = tk.Frame(parent, bg=COLORS['very_light_gray'], height=28)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Contenedor para los elementos de la barra de estado
        status_content = tk.Frame(status_frame, bg=COLORS['very_light_gray'])
        status_content.pack(fill=tk.X, padx=10)
        
        # Mensaje de estado (izquierda)
        label_estado = tk.Label(
            status_content,
            text=MESSAGES['ready'],
            font=("Arial", 9),
            anchor=tk.W,
            bg=COLORS['very_light_gray'],
            fg=COLORS['dark_gray']
        )
        label_estado.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Versión (derecha)
        label_version = tk.Label(
            status_content,
            text=APP_VERSION,
            font=FONT_VERSION,
            bg=COLORS['very_light_gray'],
            fg=COLORS['medium_gray']
        )
        label_version.pack(side=tk.RIGHT)

        return label_estado, label_version

    def crear_info_cache(self, parent):
        """Crea la línea de información de caché"""
        cache_frame = tk.Frame(parent, bg=COLORS['very_light_gray'], height=25)
        cache_frame.pack(fill=tk.X, pady=(5, 0))
        cache_frame.pack_propagate(False)  # Mantener altura fija
        
        # Separador visual
        separator = tk.Frame(cache_frame, height=1, bg=COLORS['light_gray'])
        separator.pack(fill=tk.X, pady=(0, 5))
        
        # Contenedor para la info del caché
        cache_content = tk.Frame(cache_frame, bg=COLORS['very_light_gray'])
        cache_content.pack(fill=tk.X, padx=10)
        
        # Información del caché
        label_cache_info = tk.Label(
            cache_content,
            text="Sin carpeta seleccionada",
            font=("Arial", 8),
            anchor=tk.CENTER,
            bg=COLORS['very_light_gray'],
            fg=COLORS['medium_gray']
        )
        label_cache_info.pack(expand=True)

        return label_cache_info