# src/manual_viewer.py - Manual de Usuario V.4.5 Real
import tkinter as tk
from .constants import Colors, Fonts

class ManualViewer:
    def __init__(self, parent):
        self.parent = parent
        self.manual_window = None

    def mostrar_manual(self, seccion="inicio"):
        """Muestra el manual"""
        if self.manual_window:
            self.manual_window.lift()
            return

        # Crear ventana simple
        self.manual_window = tk.Toplevel(self.parent)
        self.manual_window.title("Manual de Usuario - Búsqueda Rápida de Carpetas V.4.5")
        self.manual_window.geometry("900x600")
        self.manual_window.configure(bg=Colors.BACKGROUND)
        
        # Protocolo de cierre
        self.manual_window.protocol("WM_DELETE_WINDOW", self._cerrar_manual)
        
        # Crear contenido
        self._crear_manual_real()

    def _crear_manual_real(self):
        """Crea el manual real de uso"""
        # Frame principal
        main_frame = tk.Frame(self.manual_window, bg=Colors.BACKGROUND)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title = tk.Label(main_frame,
                        text="📚 MANUAL DE USUARIO - CÓMO USAR LA APLICACIÓN",
                        font=("Segoe UI", 14, "bold"),
                        fg=Colors.BLUE_BAR,
                        bg=Colors.BACKGROUND)
        title.pack(pady=(0, 20))
        
        # Frame para texto con scrollbar
        text_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND)
        text_frame.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Widget de texto
        self.text_widget = tk.Text(text_frame,
                                 wrap='word',
                                 font=Fonts.NORMAL,
                                 bg=Colors.BACKGROUND,
                                 fg=Colors.DARK_GRAY,
                                 relief='flat',
                                 padx=20,
                                 pady=20,
                                 yscrollcommand=scrollbar.set)
        self.text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.text_widget.yview)
        
        # Insertar contenido del manual
        contenido = self._get_manual_real_content()
        self.text_widget.insert('1.0', contenido)
        self.text_widget.config(state='disabled')
        
        # Botón cerrar
        close_btn = tk.Button(main_frame,
                            text="Cerrar",
                            font=("Segoe UI", 10, "bold"),
                            fg=Colors.WHITE,
                            bg=Colors.BLUE_BAR,
                            command=self._cerrar_manual,
                            relief='flat',
                            padx=20,
                            pady=5)
        close_btn.pack(pady=(10, 0))

    def _get_manual_real_content(self):
        """Manual de uso práctico paso a paso"""
        return r"""===============================================================================
CÓMO USAR BÚSQUEDA RÁPIDA DE CARPETAS V.6.0 - EMPÍREO
===============================================================================

PASO 1: CONFIGURACIÓN INICIAL
===============================================

1. Al abrir la aplicación por primera vez:
   - Ve al menú "Archivo" → "Seleccionar carpeta"
   - Elige la carpeta raíz donde quieres buscar
   - La aplicación escaneará automáticamente y creará un índice

2. Espera a que aparezca el mensaje "Caché construido exitosamente"


PASO 2: REALIZAR TU PRIMERA BÚSQUEDA
====================================

1. En el campo de búsqueda (arriba), escribe el nombre de la carpeta
2. Presiona ENTER o haz clic en "Buscar"
3. Los resultados aparecerán en la tabla principal


PASO 3: ABRIR UNA CARPETA
=========================

- DOBLE CLIC sobre el resultado
- ENTER sobre el resultado
- Botón "Abrir" del menú principal


PASO 13: BÚSQUEDA POR CONTENIDO (¡NUEVO EN V.6.0!)
===================================================

Esta es la funcionalidad estrella de la versión EMPÍREO:

1. Presiona CTRL + I para abrir el Buscador de Contenido.
2. Agrega las carpetas que quieres indexar (pueden ser distintas a la principal).
3. Haz clic en "⚡ Iniciar Indexación".
4. Una vez terminado, escribe cualquier palabra que esté DENTRO de tus archivos (PDF, Word, Excel, TXT).
5. CLIC DERECHO en los resultados para ver el CONTEXTO (Snippets) donde aparece la palabra.
6. DOBLE CLIC o ENTER para abrir el archivo directamente.


NUEVOS ATAJOS V.6.0:
====================
• Ctrl + I : Abrir Buscador de Contenido
• Ctrl + U : Configurar Ubicaciones de Contenido
• Ctrl + O : Abrir archivo/carpeta seleccionado
• ESC      : Cerrar ventana actual (Buscador/Ubicaciones)


===============================================================================
© 2026 - Búsqueda Rápida de Carpetas V.6.0 - EMPÍREO
¡El paraíso de la búsqueda de archivos!"""

    def _cerrar_manual(self):
        """Cierra la ventana del manual"""
        if self.manual_window:
            self.manual_window.destroy()
            self.manual_window = None