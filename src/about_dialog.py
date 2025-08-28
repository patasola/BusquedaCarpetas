# src/about_dialog.py - Diálogo Acerca de V.4.2 (Refactorizado)
import tkinter as tk
from tkinter import ttk
from .constants import Colors, Fonts

class AboutDialog:
    def __init__(self, parent, version):
        self.parent = parent
        self.version = version
        self.dialog = None
    
    def mostrar_acerca_de(self):
        """Muestra el diálogo 'Acerca de'"""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.lift()
            self.dialog.focus()
            return
            
        self._crear_ventana()
        self._crear_contenido()
        self._configurar_eventos()
    
    def _crear_ventana(self):
        """Crea y configura la ventana"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Acerca de - Búsqueda Rápida de Carpetas")
        self.dialog.geometry("480x520")  # Aumentado a 520px
        self.dialog.configure(bg=Colors.BACKGROUND)
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        
        x = parent_x + (parent_w - 480) // 2
        y = parent_y + (parent_h - 520) // 2  # Ajustado para nueva altura
        self.dialog.geometry(f"+{x}+{y}")
    
    def _crear_contenido(self):
        """Crea el contenido del diálogo"""
        main_frame = tk.Frame(self.dialog, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título principal
        tk.Label(
            main_frame,
            text="Búsqueda Rápida de Carpetas",
            font=("Segoe UI", 16, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG
        ).pack(pady=(0, 10))
        
        # Versión
        tk.Label(
            main_frame,
            text=self.version,
            font=("Segoe UI", 12),
            bg=Colors.BACKGROUND,
            fg="#666666"
        ).pack(pady=(0, 20))
        
        # Información principal - texto más compacto
        info_text = """Sistema híbrido de cache y exploración de árbol integrada.

V.4.2 - Características principales:
• Búsqueda híbrida (Cache + Tradicional)
• Explorador de árbol expandible
• Historial con panel lateral integrado
• Navegación completa por teclado
• Código refactorizado (50% menos líneas)

Tecnologías:
• Python 3.8+ con Tkinter nativo
• Threading asíncrono + Pickle cache
• Arquitectura modular optimizada

Inspirado en "La Divina Comedia":
V.4.2 Purgatorio - Refactorización completa"""
        
        tk.Label(
            main_frame,
            text=info_text,
            font=("Segoe UI", 9),
            bg=Colors.BACKGROUND,
            fg=Colors.INFO_FG,
            justify=tk.LEFT,
            wraplength=440
        ).pack(pady=(0, 20))
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=(0, 15))
        
        # Información del desarrollador
        tk.Label(
            main_frame,
            text="Co-creado por Elkin Darío Pérez Puyana y Claude Sonnet 4",
            font=("Segoe UI", 9, "italic"),
            bg=Colors.BACKGROUND,
            fg="#666666"
        ).pack(pady=(5, 0))
        
        tk.Label(
            main_frame,
            text="Desarrollado con colaboración humano-IA para optimizar la gestión de archivos",
            font=("Segoe UI", 8),
            bg=Colors.BACKGROUND,
            fg="#888888"
        ).pack(pady=(0, 15))
        
        # Botón cerrar
        tk.Button(
            main_frame,
            text="Cerrar",
            font=Fonts.BUTTONS,
            bg=Colors.BUTTON_BG,
            fg=Colors.BUTTON_FG,
            relief=tk.FLAT,
            borderwidth=1,
            padx=30, pady=8,
            command=self.dialog.destroy,
            cursor="hand2"
        ).pack()
    
    def _configurar_eventos(self):
        """Configura eventos de la ventana"""
        self.dialog.protocol("WM_DELETE_WINDOW", self.dialog.destroy)
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())