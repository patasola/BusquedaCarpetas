# src/ui_components.py - Componentes de Interfaz V.3.6 - Ultra-compacta
"""
Maneja la creación y configuración de todos los elementos de la interfaz
Versión ultra-compacta con barras pegadas y layout estabilizado
"""

import tkinter as tk
from tkinter import ttk

class UIComponents:
    def __init__(self, master, version):
        self.master = master
        self.version = version
        self.configurar_estilos()

    def configurar_estilos(self):
        """Configura estilos personalizados para V.3.6"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores V.3.6
        gris_oscuro = "#424242"
        gris_medio = "#757575"
        gris_claro = "#e0e0e0"
        gris_muy_claro = "#f5f5f5"
        blanco = "#ffffff"
        azul_barra = "#1976D2"
        
        # Estilos de botones compactos
        style.configure('TButton', 
                      font=("Segoe UI", 9), 
                      foreground=gris_oscuro,
                      background=gris_claro,
                      padding=6,
                      width=10)
        
        # Barra de progreso compacta
        style.configure('Horizontal.TProgressbar',
                       thickness=15,
                       troughcolor=gris_muy_claro,
                       background=azul_barra,
                       borderwidth=0)
        
        # Treeview compacto
        style.configure('Treeview.Heading', 
                      font=('Segoe UI', 9, 'bold'),
                      background=gris_claro,
                      foreground=gris_oscuro)
        
        style.configure('Treeview',
                      rowheight=22,
                      background=blanco,
                      fieldbackground=blanco,
                      foreground=gris_oscuro)

    def crear_interfaz_completa(self):
        """Crea toda la interfaz ultra-compacta y retorna referencias a elementos importantes"""
        # Frame principal ultra-compacto
        main_frame = tk.Frame(self.master, bg="#f6f5f5")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=15)
        
        # Título compacto
        tk.Label(
            main_frame,
            text="🔍 Búsqueda Rápida de Carpetas",
            font=("Segoe UI", 14, "bold"),
            bg="#f6f5f5",
            fg="#424242"
        ).pack(pady=(0, 10))
        
        # Campo de búsqueda compacto
        tk.Label(
            main_frame,
            text="Criterio de búsqueda:",
            font=("Segoe UI", 9),
            bg="#f6f5f5",
            fg="#757575"
        ).pack()
        
        entry = tk.Entry(
            main_frame,
            width=35,
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            borderwidth=1,
            bg="#ffffff",
            fg="#424242",
            justify="center"
        )
        entry.pack(pady=8, ipady=4)
        entry.focus_set()
        
        # Botones de búsqueda compactos
        btn_frame = tk.Frame(main_frame, bg="#f6f5f5")
        btn_frame.pack(pady=(0, 10))
        
        btn_buscar = ttk.Button(btn_frame, text="Buscar")
        btn_buscar.pack(side=tk.LEFT, padx=3)
        
        btn_cancelar = ttk.Button(btn_frame, text="Cancelar", state=tk.DISABLED)
        btn_cancelar.pack(side=tk.LEFT, padx=3)
        
        # Barra de progreso compacta (solo cuando sea necesario)
        progress = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            mode="determinate",
            style='Horizontal.TProgressbar',
            length=350
        )
        
        # Etiqueta de porcentaje compacta
        label_porcentaje = tk.Label(
            main_frame,
            text="0%",
            font=("Segoe UI", 9),
            bg="#f6f5f5",
            fg="#757575"
        )
        
        # TreeView ultra-compacto
        tree_frame = tk.Frame(main_frame, bg="#f6f5f5")
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=(5, 10))
        
        # Scrollbars inteligentes
        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        tree = ttk.Treeview(
            tree_frame,
            columns=("Nombre", "Ruta"),
            show="headings",
            selectmode="browse",
            height=4,  # Más compacto
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        # Configuración de columnas optimizada
        tree.heading("Nombre", text="Nombre", anchor=tk.W)
        tree.heading("Ruta", text="Ruta Relativa", anchor=tk.W)
        tree.column("Nombre", width=150, anchor=tk.W, minwidth=100)
        tree.column("Ruta", width=350, anchor=tk.W, minwidth=200)
        
        y_scroll.config(command=tree.yview)
        x_scroll.config(command=tree.xview)
        
        # Posicionamiento de scrollbars
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Botones de acciones compactos
        action_frame = tk.Frame(main_frame, bg="#f6f5f5")
        action_frame.pack(pady=(0, 5))
        
        btn_copiar = ttk.Button(action_frame, text="Copiar (F3)", state=tk.DISABLED)
        btn_copiar.pack(side=tk.LEFT, padx=3)
        
        btn_abrir = ttk.Button(action_frame, text="Abrir (F4)", state=tk.DISABLED)
        btn_abrir.pack(side=tk.LEFT, padx=3)
        
        # BARRAS PEGADAS - Ultra-compacta sin espacios
        info_cache_frame = tk.Frame(main_frame, bg="#1976D2", height=20)
        info_cache_frame.pack(fill=tk.X, side=tk.BOTTOM)
        info_cache_frame.pack_propagate(False)
        
        label_carpeta_info = tk.Label(
            info_cache_frame,
            text="Sin carpeta seleccionada",
            font=("Segoe UI", 9),
            anchor=tk.W,
            bg="#1976D2",
            fg="white",
            padx=10
        )
        label_carpeta_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Barra de estado pegada DEBAJO
        status_frame = tk.Frame(main_frame, bg="#424242", height=20)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        label_estado = tk.Label(
            status_frame,
            text="Listo. Presione F2 para enfocar búsqueda",
            font=("Segoe UI", 9),
            anchor=tk.W,
            bg="#424242",
            fg="white",
            padx=10
        )
        label_estado.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        label_version = tk.Label(
            status_frame,
            text=self.version,
            font=("Segoe UI", 8),
            bg="#424242",
            fg="#cccccc",
            padx=10
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

    @staticmethod
    def create_progress_bar(parent):
        """Crea componentes de barra de progreso para uso externo"""
        # Frame contenedor para la barra de progreso
        progress_frame = tk.Frame(parent, bg="#f6f5f5")
        
        # Contenedor interno
        progress_container = tk.Frame(progress_frame, bg="#f6f5f5")
        
        # Barra de progreso
        progress = ttk.Progressbar(
            progress_container,
            orient="horizontal",
            mode="determinate",
            style='Horizontal.TProgressbar',
            length=350
        )
        
        # Etiqueta de porcentaje
        label_porcentaje = tk.Label(
            progress_frame,
            text="0%",
            font=("Segoe UI", 9),
            bg="#f6f5f5",
            fg="#757575"
        )
        
        return progress_frame, progress, label_porcentaje, progress_container

# Clase para mantener compatibilidad con versiones anteriores
class Colors:
    BACKGROUND = "#f6f5f5"
    TITLE_FG = "#424242"
    INFO_FG = "#757575" 
    TREE_FG = "#424242"
    BUTTON_BG = "#e0e0e0"
    BUTTON_FG = "#424242"

class Fonts:
    BUTTONS = ("Segoe UI", 9)
    NORMAL = ("Segoe UI", 9)
    TITLE = ("Segoe UI", 14, "bold")