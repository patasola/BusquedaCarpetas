# src/about_dialog.py - Diálogo Acerca de V.4.1
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
            
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Acerca de - Búsqueda Rápida de Carpetas")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg=Colors.BACKGROUND)
        self.dialog.resizable(False, False)
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self._centrar_ventana()
        
        # Crear contenido
        self._crear_contenido()
        
        # Configurar eventos
        self.dialog.protocol("WM_DELETE_WINDOW", self.dialog.destroy)
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())
    
    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.dialog.update_idletasks()
        
        # Obtener dimensiones
        window_width = self.dialog.winfo_reqwidth()
        window_height = self.dialog.winfo_reqheight()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calcular posición centrada respecto al padre
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _crear_contenido(self):
        """Crea el contenido del diálogo"""
        main_frame = tk.Frame(self.dialog, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título principal
        title_label = tk.Label(
            main_frame,
            text="🔍 Búsqueda Rápida de Carpetas",
            font=("Segoe UI", 16, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG
        )
        title_label.pack(pady=(0, 10))
        
        # Versión
        version_label = tk.Label(
            main_frame,
            text=self.version,
            font=("Segoe UI", 12),
            bg=Colors.BACKGROUND,
            fg="#666666"
        )
        version_label.pack(pady=(0, 20))
        
        # Información
        info_text = """Herramienta profesional para búsqueda rápida de directorios
con sistema híbrido de cache y exploración de árbol integrada.

🌟 Características principales:
• Búsqueda híbrida (Cache + Tradicional)
• Explorador de árbol expandible (V.4.1)
• Historial de búsquedas integrado
• Navegación completa por teclado
• Interfaz moderna y responsiva

⚡ Tecnologías:
• Python 3.8+
• Tkinter (GUI nativa)
• Threading (búsquedas asíncronas)
• Pickle (persistencia de cache)

📋 Inspirado en "La Divina Comedia" de Dante:
V.4.0 Purgatorio - Purificación del código
V.4.1 Purgatorio - Explorador integrado"""
        
        info_label = tk.Label(
            main_frame,
            text=info_text,
            font=("Segoe UI", 9),
            bg=Colors.BACKGROUND,
            fg=Colors.INFO_FG,
            justify=tk.LEFT,
            wraplength=450
        )
        info_label.pack(pady=(0, 20))
        
        # Separador
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # Información del desarrollador
        dev_label = tk.Label(
            main_frame,
            text="Desarrollado con ❤️ para optimizar la gestión de archivos",
            font=("Segoe UI", 9, "italic"),
            bg=Colors.BACKGROUND,
            fg="#666666"
        )
        dev_label.pack(pady=(0, 15))
        
        # Botón cerrar
        btn_cerrar = tk.Button(
            main_frame,
            text="Cerrar",
            font=Fonts.BUTTONS,
            bg=Colors.BUTTON_BG,
            fg=Colors.BUTTON_FG,
            relief=tk.FLAT,
            borderwidth=1,
            padx=30,
            pady=8,
            command=self.dialog.destroy,
            cursor="hand2"
        )
        btn_cerrar.pack()