# src/about_dialog.py - Diálogo Acerca de V.4.5 Simple con Scroll Automático
import tkinter as tk
from tkinter import ttk
from .constants import Colors, Fonts

class AboutDialog:
    def __init__(self, parent, version):
        self.parent = parent
        self.version = version
        self.dialog = None
        self.scroll_frame = None
        self.content_frame = None
        self.scroll_speed = 1  # píxeles por frame
        self.scroll_delay = 50  # milisegundos entre frames
        self.is_scrolling = False
        self.scroll_after_id = None
        self.current_y = 0
    
    def mostrar_acerca_de(self):
        """Muestra el diálogo 'Acerca de'"""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.lift()
            self.dialog.focus()
            return
            
        self._crear_ventana()
        self._crear_contenido()
        self._configurar_eventos()
        # Iniciar scroll automático después de un breve delay
        self.dialog.after(2000, self._iniciar_scroll_automatico)
    
    def _crear_ventana(self):
        """Crea y configura la ventana"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Acerca de Búsqueda Rápida de Carpetas")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=Colors.BACKGROUND)
        
        # Centrar ventana
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar ventana manualmente
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        
        x = parent_x + (parent_w - 600) // 2
        y = parent_y + (parent_h - 500) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _crear_contenido(self):
        """Crea el contenido con scroll automático"""
        # Frame principal con canvas para scroll
        self.scroll_frame = tk.Frame(self.dialog, bg=Colors.BACKGROUND)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas para el scroll
        self.canvas = tk.Canvas(
            self.scroll_frame, 
            bg=Colors.BACKGROUND, 
            highlightthickness=0,
            width=580,
            height=480
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Frame de contenido que se moverá
        self.content_frame = tk.Frame(self.canvas, bg=Colors.BACKGROUND)
        
        # Crear el contenido
        self._crear_contenido_estatico()
        
        # Colocar el frame de contenido en el canvas
        self.canvas_window = self.canvas.create_window(
            300, 480,  # Comenzar desde abajo de la ventana
            window=self.content_frame,
            anchor='center'
        )
        
        # Actualizar el scroll region después de que se renderice
        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _crear_contenido_estatico(self):
        """Crea el contenido usando el diseño original"""
        # Espaciado inicial
        self._add_space(50)
        
        # Título principal
        title_label = tk.Label(self.content_frame,
                             text="🔍 Búsqueda Rápida de Carpetas",
                             font=("Segoe UI", 18, "bold"),
                             fg=Colors.BLUE_BAR,
                             bg=Colors.BACKGROUND)
        title_label.pack(pady=(0, 5))
        
        # Versión
        version_label = tk.Label(self.content_frame,
                               text=f"Versión {self.version}",
                               font=Fonts.TITLE,
                               fg=Colors.TREE_SELECT_FG,
                               bg=Colors.BACKGROUND)
        version_label.pack(pady=(0, 15))
        
        # Descripción principal
        desc_text = ("Herramienta profesional de búsqueda de carpetas diseñada para encontrar "
                    "directorios en tu sistema de manera ultrarrápida y eficiente.\n\n"
                    "Desarrollado con Python 3.12+ usando arquitectura modular y "
                    "patrones de diseño modernos.")
        
        desc_label = tk.Label(self.content_frame,
                            text=desc_text,
                            font=Fonts.NORMAL,
                            fg=Colors.DARK_GRAY,
                            bg=Colors.BACKGROUND,
                            wraplength=540,
                            justify='center')
        desc_label.pack(pady=(0, 20))
        
        # Información técnica
        tech_frame = tk.Frame(self.content_frame, bg=Colors.BACKGROUND)
        tech_frame.pack(pady=(10, 20))
        
        # Crear dos columnas para la información técnica
        left_column = tk.Frame(tech_frame, bg=Colors.BACKGROUND)
        left_column.pack(side='left', padx=(0, 30))
        
        right_column = tk.Frame(tech_frame, bg=Colors.BACKGROUND)
        right_column.pack(side='right')
        
        # Características V.4.5
        features_label = tk.Label(left_column,
                                text="✨ Nuevas características V.4.5:",
                                font=("Segoe UI", 11, "bold"),
                                fg=Colors.BLUE_BAR,
                                bg=Colors.BACKGROUND,
                                anchor='w')
        features_label.pack(anchor='w')
        
        features_text = ("• Paneles duales sin solapamiento\n"
                        "• Redimensionamiento dinámico automático\n"
                        "• Sistema de 3 columnas inteligente\n"
                        "• Navegación Tab mejorada\n"
                        "• Arquitectura refactorizada modular")
        
        features_detail = tk.Label(left_column,
                                 text=features_text,
                                 font=("Segoe UI", 9),
                                 fg=Colors.DARK_GRAY,
                                 bg=Colors.BACKGROUND,
                                 justify='left',
                                 anchor='w')
        features_detail.pack(anchor='w', pady=(5, 0))
        
        # Información técnica
        tech_label = tk.Label(right_column,
                            text="🛠️ Información técnica:",
                            font=("Segoe UI", 11, "bold"),
                            fg=Colors.TREE_SELECT_FG,
                            bg=Colors.BACKGROUND,
                            anchor='w')
        tech_label.pack(anchor='w')
        
        tech_text = ("• Python 3.12+ con Tkinter\n"
                    "• Arquitectura MVC modular\n"
                    "• Watchdog para monitoreo\n"
                    "• Threading para asíncronia\n"
                    "• Pathlib para rutas modernas")
        
        tech_detail = tk.Label(right_column,
                             text=tech_text,
                             font=("Segoe UI", 9),
                             fg=Colors.DARK_GRAY,
                             bg=Colors.BACKGROUND,
                             justify='left',
                             anchor='w')
        tech_detail.pack(anchor='w', pady=(5, 0))
        
        self._add_space(30)
        
        # Sección adicional - Evolución
        evolution_label = tk.Label(self.content_frame,
                                 text="📈 Evolución de Versiones:",
                                 font=("Segoe UI", 12, "bold"),
                                 fg=Colors.BLUE_BAR,
                                 bg=Colors.BACKGROUND)
        evolution_label.pack(pady=(10, 5))
        
        evolution_text = ("V.4.0 → Purgatorio: historial + modularización\n"
                         "V.4.1 → Explorador integrado + tree navigation\n"
                         "V.4.2 → Refactorización completa: código optimizado\n"
                         "V.4.3 → Transición: tooltips + navegación inicial\n"
                         "V.4.4 → Explorador de archivos refactorizado completo\n"
                         "V.4.5 → Paneles duales con redimensión dinámica")
        
        evolution_detail = tk.Label(self.content_frame,
                                   text=evolution_text,
                                   font=("Segoe UI", 9),
                                   fg=Colors.DARK_GRAY,
                                   bg=Colors.BACKGROUND,
                                   justify='left')
        evolution_detail.pack(pady=(5, 20))
        
        self._add_space(40)
        
        # Cita de Dante
        dante_label1 = tk.Label(self.content_frame,
                              text="\"Nel mezzo del cammin di nostra vita",
                              font=("Segoe UI", 11, "italic"),
                              fg=Colors.TREE_SELECT_FG,
                              bg=Colors.BACKGROUND)
        dante_label1.pack(pady=2)
        
        dante_label2 = tk.Label(self.content_frame,
                              text="mi ritrovai per una selva oscura,",
                              font=("Segoe UI", 11, "italic"),
                              fg=Colors.TREE_SELECT_FG,
                              bg=Colors.BACKGROUND)
        dante_label2.pack(pady=2)
        
        dante_label3 = tk.Label(self.content_frame,
                              text="ché la diritta via era smarrita.\"",
                              font=("Segoe UI", 11, "italic"),
                              fg=Colors.TREE_SELECT_FG,
                              bg=Colors.BACKGROUND)
        dante_label3.pack(pady=2)
        
        dante_author = tk.Label(self.content_frame,
                              text="— Dante Alighieri, Divina Comedia",
                              font=("Segoe UI", 9),
                              fg=Colors.MEDIUM_GRAY,
                              bg=Colors.BACKGROUND)
        dante_author.pack(pady=(5, 20))
        
        # Créditos finales
        credits_title = tk.Label(self.content_frame,
                               text="CO-CREADO POR",
                               font=("Segoe UI", 12, "bold"),
                               fg=Colors.BLUE_BAR,
                               bg=Colors.BACKGROUND)
        credits_title.pack(pady=(20, 10))
        
        creator1 = tk.Label(self.content_frame,
                          text="Elkin Darío Pérez Puyana",
                          font=("Segoe UI", 11),
                          fg=Colors.DARK_GRAY,
                          bg=Colors.BACKGROUND)
        creator1.pack(pady=2)
        
        and_label = tk.Label(self.content_frame,
                           text="&",
                           font=("Segoe UI", 11),
                           fg=Colors.DARK_GRAY,
                           bg=Colors.BACKGROUND)
        and_label.pack(pady=2)
        
        creator2 = tk.Label(self.content_frame,
                          text="Claude Sonnet 4",
                          font=("Segoe UI", 11),
                          fg=Colors.DARK_GRAY,
                          bg=Colors.BACKGROUND)
        creator2.pack(pady=2)
        
        collab_label1 = tk.Label(self.content_frame,
                               text="Desarrollado con colaboración humano-IA",
                               font=("Segoe UI", 9),
                               fg=Colors.MEDIUM_GRAY,
                               bg=Colors.BACKGROUND)
        collab_label1.pack(pady=(10, 2))
        
        collab_label2 = tk.Label(self.content_frame,
                               text="para optimizar la gestión de archivos",
                               font=("Segoe UI", 9),
                               fg=Colors.MEDIUM_GRAY,
                               bg=Colors.BACKGROUND)
        collab_label2.pack(pady=2)
        
        self._add_space(30)
        
        # Copyright
        copyright_label = tk.Label(self.content_frame,
                                 text="© 2024 - Búsqueda Rápida de Carpetas V.4.5\n"
                                      "Desarrollado con ❤️ para mejorar tu productividad",
                                 font=("Segoe UI", 9),
                                 fg=Colors.MEDIUM_GRAY,
                                 bg=Colors.BACKGROUND,
                                 justify='center')
        copyright_label.pack(pady=(20, 10))
        
        # Mensaje final
        final_label = tk.Label(self.content_frame,
                             text="¡Gracias por usar Búsqueda Rápida de Carpetas!",
                             font=("Segoe UI", 11, "bold"),
                             fg=Colors.BLUE_BAR,
                             bg=Colors.BACKGROUND)
        final_label.pack(pady=(20, 10))
        
        # Botón de cierre
        close_button = tk.Button(self.content_frame,
                               text="Cerrar",
                               font=("Segoe UI", 10, "bold"),
                               fg=Colors.WHITE,
                               bg=Colors.BLUE_BAR,
                               activeforeground=Colors.WHITE,
                               activebackground=Colors.TREE_SELECT_FG,
                               relief='flat',
                               padx=25,
                               pady=8,
                               cursor='hand2',
                               command=self._cerrar_dialog)
        close_button.pack(pady=(20, 50))
        
        # Espaciado final para que termine el scroll
        self._add_space(100)
    
    def _add_space(self, height):
        """Añade espacio vertical"""
        spacer = tk.Frame(self.content_frame, bg=Colors.BACKGROUND, height=height)
        spacer.pack(fill=tk.X)
        return spacer
    
    def _iniciar_scroll_automatico(self):
        """Inicia el scroll automático"""
        if not self.is_scrolling:
            self.is_scrolling = True
            self.current_y = 480  # Comenzar desde abajo
            self._scroll_step()
    
    def _scroll_step(self):
        """Realiza un paso del scroll automático"""
        if not self.is_scrolling or not self.dialog.winfo_exists():
            return
        
        try:
            # Mover el contenido hacia arriba
            self.current_y -= self.scroll_speed
            self.canvas.coords(self.canvas_window, 300, self.current_y)
            
            # Obtener la altura total del contenido
            self.content_frame.update_idletasks()
            content_height = self.content_frame.winfo_reqheight()
            
            # Si el contenido ha salido completamente por arriba, reiniciar
            if self.current_y < -content_height - 100:
                self.current_y = 480
            
            # Programar el siguiente paso
            if self.is_scrolling:
                self.scroll_after_id = self.dialog.after(self.scroll_delay, self._scroll_step)
                
        except tk.TclError:
            # La ventana fue cerrada
            self.is_scrolling = False
    
    def _pausar_scroll(self):
        """Pausa o reanuda el scroll"""
        self.is_scrolling = not self.is_scrolling
        if self.is_scrolling:
            self._scroll_step()
    
    def _configurar_eventos(self):
        """Configura eventos de la ventana"""
        def on_close():
            self.is_scrolling = False
            if self.scroll_after_id:
                self.dialog.after_cancel(self.scroll_after_id)
            self.dialog.destroy()
        
        self.dialog.protocol("WM_DELETE_WINDOW", on_close)
        self.dialog.bind("<Escape>", lambda e: on_close())
        
        # Click para pausar/reanudar scroll
        self.canvas.bind("<Button-1>", lambda e: self._pausar_scroll())
        self.dialog.bind("<space>", lambda e: self._pausar_scroll())
        
        # Scroll con rueda del ratón para cambiar velocidad
        def on_mousewheel(event):
            if event.delta > 0:
                self.scroll_speed = max(0.5, self.scroll_speed - 0.5)
            else:
                self.scroll_speed = min(3, self.scroll_speed + 0.5)
        
        self.canvas.bind("<MouseWheel>", on_mousewheel)

    def _cerrar_dialog(self):
        """Cierra el diálogo"""
        if self.dialog:
            self.is_scrolling = False
            if self.scroll_after_id:
                self.dialog.after_cancel(self.scroll_after_id)
            self.dialog.destroy()
            self.dialog = None