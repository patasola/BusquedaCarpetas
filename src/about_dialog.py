import tkinter as tk
from tkinter import messagebox
from .constants import Colors, Fonts

class AboutDialog:
    def __init__(self, parent, version):
        self.parent = parent
        self.version = version
    
    def mostrar_acerca_de(self):
        """Muestra el diálogo 'Acerca de' con información de la aplicación"""
        mensaje = f"""🔍 Búsqueda Rápida de Carpetas
        
Versión: {self.version}
Inspirada en: La Divina Comedia de Dante Alighieri

👨‍💻 Desarrollado por:
Elkin Darío Pérez Puyana

🤖 En co-creación con los modelos IA:
Claude (Claude-3.5-Sonnet)
DeepSeek Chat (DeepSeek-V3)

🎯 Características V. 3.6:
• Progreso simplificado: Solo porcentaje visible
• Interfaz ultra-compacta: Barras perfectamente pegadas
• Layout estabilizado: Cero movimientos durante operaciones
• Búsqueda híbrida ultra-rápida
• Cache inteligente automático
• Sistema de entrada dual (numérico/alfanumérico)
• Arquitectura modular refactorizada

⌨️ Atajos de teclado:
• F2: Enfocar búsqueda
• F3: Copiar ruta
• F4: Abrir carpeta  
• F5: Cambiar modo entrada

🏗️ Tecnología:
• Python 3.12+
• Tkinter (Interfaz)
• Threading (Rendimiento)
• Cache en memoria

"Nel mezzo del cammin di nostra vita..."
- Dante Alighieri

V. 3.6 - Estable: ¡El Inferno completado! 🌟"""
        
        messagebox.showinfo("Acerca de", mensaje)
    
    def mostrar_acerca_de_avanzado(self):
        """Muestra una ventana 'Acerca de' más detallada"""
        if hasattr(self, 'about_window') and self.about_window.winfo_exists():
            self.about_window.lift()
            self.about_window.focus()
            return
            
        self.about_window = tk.Toplevel(self.parent)
        self.about_window.title("Acerca de - Búsqueda Rápida de Carpetas")
        self.about_window.geometry("600x520")
        self.about_window.configure(bg=Colors.BACKGROUND)
        self.about_window.resizable(False, False)
        
        # Centrar ventana
        self.about_window.transient(self.parent)
        self.about_window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(self.about_window, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
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
            text=f"Versión: {self.version}",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.BACKGROUND,
            fg="#d32f2f"
        )
        version_label.pack(pady=(0, 5))
        
        # Inspiración
        inspiration_label = tk.Label(
            main_frame,
            text="Inspirada en: La Divina Comedia de Dante Alighieri",
            font=("Segoe UI", 10, "italic"),
            bg=Colors.BACKGROUND,
            fg="#666666"
        )
        inspiration_label.pack(pady=(0, 15))
        
        # Desarrollador
        developer_frame = tk.LabelFrame(
            main_frame,
            text="👨‍💻 Desarrollado por",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG,
            padx=10,
            pady=5
        )
        developer_frame.pack(fill=tk.X, pady=(0, 10))
        
        developer_label = tk.Label(
            developer_frame,
            text="Elkin Darío Pérez Puyana",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.INFO_FG
        )
        developer_label.pack()
        
        # Co-creación IA
        ia_frame = tk.LabelFrame(
            main_frame,
            text="🤖 En co-creación con los modelos IA",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG,
            padx=10,
            pady=5
        )
        ia_frame.pack(fill=tk.X, pady=(0, 15))
        
        ia_label = tk.Label(
            ia_frame,
            text="Claude (Claude-3.5-Sonnet)\nDeepSeek Chat (DeepSeek-V3)",
            font=("Segoe UI", 9),
            bg=Colors.BACKGROUND,
            fg="#666666",
            justify=tk.LEFT
        )
        ia_label.pack()
        
        # Características V. 3.6
        features_frame = tk.LabelFrame(
            main_frame,
            text="🎯 Características V. 3.6 - Estable",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG,
            padx=10,
            pady=10
        )
        features_frame.pack(fill=tk.X, pady=(0, 10))
        
        features_text = """• Progreso simplificado: Solo porcentaje visible
• Interfaz ultra-compacta: Barras perfectamente pegadas
• Layout estabilizado: Cero movimientos durante operaciones
• Búsqueda híbrida ultra-rápida
• Cache inteligente automático
• Sistema de entrada dual (numérico/alfanumérico)
• Arquitectura modular refactorizada"""
        
        features_label = tk.Label(
            features_frame,
            text=features_text,
            font=("Segoe UI", 9),
            bg=Colors.BACKGROUND,
            fg=Colors.TREE_FG,
            justify=tk.LEFT
        )
        features_label.pack(anchor=tk.W)
        
        # Atajos de teclado
        shortcuts_frame = tk.LabelFrame(
            main_frame,
            text="⌨️ Atajos de teclado",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG,
            padx=10,
            pady=10
        )
        shortcuts_frame.pack(fill=tk.X, pady=(0, 10))
        
        shortcuts_text = """• F2: Enfocar búsqueda
• F3: Copiar ruta
• F4: Abrir carpeta
• F5: Cambiar modo entrada"""
        
        shortcuts_label = tk.Label(
            shortcuts_frame,
            text=shortcuts_text,
            font=("Segoe UI", 9),
            bg=Colors.BACKGROUND,
            fg=Colors.TREE_FG,
            justify=tk.LEFT
        )
        shortcuts_label.pack(anchor=tk.W)
        
        # Tecnología
        tech_frame = tk.LabelFrame(
            main_frame,
            text="🏗️ Tecnología",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG,
            padx=10,
            pady=10
        )
        tech_frame.pack(fill=tk.X, pady=(0, 15))
        
        tech_text = """• Python 3.12+
• Tkinter (Interfaz)
• Threading (Rendimiento)
• Cache en memoria"""
        
        tech_label = tk.Label(
            tech_frame,
            text=tech_text,
            font=("Segoe UI", 9),
            bg=Colors.BACKGROUND,
            fg=Colors.TREE_FG,
            justify=tk.LEFT
        )
        tech_label.pack(anchor=tk.W)
        
        # Cita de Dante
        quote_label = tk.Label(
            main_frame,
            text='"Nel mezzo del cammin di nostra vita..."\n- Dante Alighieri',
            font=("Segoe UI", 9, "italic"),
            bg=Colors.BACKGROUND,
            fg="#666666",
            justify=tk.CENTER
        )
        quote_label.pack(pady=(10, 15))
        
        # Mensaje final V. 3.6
        final_label = tk.Label(
            main_frame,
            text="V. 3.6 - Estable: ¡El Inferno completado! 🌟",
            font=("Segoe UI", 9, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.INFO_FG
        )
        final_label.pack(pady=(0, 15))
        
        # Botón cerrar
        close_button = tk.Button(
            main_frame,
            text="Cerrar",
            font=Fonts.BUTTONS,
            bg=Colors.BUTTON_BG,
            fg=Colors.BUTTON_FG,
            relief=tk.FLAT,
            borderwidth=1,
            padx=20,
            pady=8,
            command=self.about_window.destroy,
            cursor="hand2"
        )
        close_button.pack(anchor=tk.CENTER)
        
        # Configurar eventos
        self.about_window.protocol("WM_DELETE_WINDOW", self.about_window.destroy)
        self.about_window.bind("<Escape>", lambda e: self.about_window.destroy())
    
    @staticmethod
    def get_app_info():
        """Retorna información básica de la aplicación como diccionario"""
        return {
            "nombre": "Búsqueda Rápida de Carpetas",
            "version": "V. 3.6 - Estable (Inferno)",
            "tema": "La Divina Comedia de Dante Alighieri",
            "desarrollador": "Elkin Darío Pérez Puyana",
            "co_creacion_ia": ["Claude (Claude-3.5-Sonnet)", "DeepSeek Chat (DeepSeek-V3)"],
            "tecnologias": ["Python 3.12+", "Tkinter", "Threading", "Cache en memoria"],
            "caracteristicas": [
                "Progreso simplificado: Solo porcentaje visible",
                "Interfaz ultra-compacta: Barras perfectamente pegadas", 
                "Layout estabilizado: Cero movimientos durante operaciones",
                "Búsqueda híbrida ultra-rápida",
                "Cache inteligente automático",
                "Sistema de entrada dual (numérico/alfanumérico)"
            ],
            "atajos": {
                "F2": "Enfocar búsqueda",
                "F3": "Copiar ruta", 
                "F4": "Abrir carpeta",
                "F5": "Cambiar modo entrada"
            },
            "cita": "Nel mezzo del cammin di nostra vita...",
            "mensaje": "V. 3.6 - Estable: ¡El Inferno completado! 🌟"
        }