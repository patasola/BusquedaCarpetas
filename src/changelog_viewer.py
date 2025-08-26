# src/changelog_viewer.py - Visor de Changelog V.4.0
import tkinter as tk
from tkinter import ttk, scrolledtext
from .constants import Colors, Fonts

class ChangelogViewer:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
    
    def mostrar_changelog(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("Historial de Cambios - La Divina Comedia del Código")
        self.window.geometry("650x700")
        self.window.configure(bg=Colors.BACKGROUND)
        self.window.resizable(True, True)
        
        self.window.transient(self.parent)
        self.window.grab_set()
        
        main_frame = tk.Frame(self.window, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        title_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(
            title_frame,
            text="📋 HISTORIAL DE CAMBIOS",
            font=("Segoe UI", 16, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="La Divina Comedia del Código - Inspirada en Dante Alighieri",
            font=("Segoe UI", 10, "italic"),
            bg=Colors.BACKGROUND,
            fg="#666666"
        )
        subtitle_label.pack(pady=(5, 0))
        
        text_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#2c3e50",
            selectbackground="#e3f2fd",
            selectforeground="#0d47a1",
            padx=15,
            pady=15,
            relief=tk.FLAT,
            borderwidth=1
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        button_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND)
        button_frame.pack(fill=tk.X)
        
        close_button = tk.Button(
            button_frame,
            text="Cerrar",
            font=Fonts.BUTTONS,
            bg=Colors.BUTTON_BG,
            fg=Colors.BUTTON_FG,
            relief=tk.FLAT,
            borderwidth=1,
            padx=20,
            pady=8,
            command=self.window.destroy,
            cursor="hand2"
        )
        close_button.pack(anchor=tk.CENTER)
        
        self.cargar_changelog()
        
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.window.bind("<Escape>", lambda e: self.window.destroy())
    
    def cargar_changelog(self):
        changelog_content = """
🌟 V. 4.0 - Purgatorio (Purificación) - VERSIÓN ACTUAL
========================================

📊 MENÚ "VER" - CONTROL TOTAL DE INTERFAZ:
• Barra de Estado: Mostrar/ocultar barra inferior independientemente
• Barra de Cache: Control independiente de la barra de información azul
• Historial de Búsquedas: Panel lateral integrado con historial de sesión
• Ticks correctos: ✓ cuando están activas, ☐ cuando están inactivas
• Sincronización perfecta: Menú actualizado automáticamente con estado real

📋 HISTORIAL DE BÚSQUEDAS INTEGRADO:
• Panel lateral: Integrado en ventana principal, no como ventana separada
• Historial de sesión: Solo mantiene búsquedas de la sesión actual (máx 50)
• Búsquedas silenciosas: Al seleccionar del historial no se duplica entrada
• Formato consistente: Mismo estilo visual que la tabla principal
• Sin bordes: Se mezcla perfectamente con la aplicación principal
• Pegado al borde: Posicionamiento perfecto en el borde derecho

⌨️ NAVEGACIÓN POR TAB COMPLETA:
• Orden perfecto: Campo → Buscar → Cancelar → Tabla → Copiar → Abrir → Historial
• Navegación circular: Del último elemento regresa al primero automáticamente
• Inclusión dinámica: Historial se incluye/excluye según visibilidad
• Flechas en historial: ↑↓ para navegar, Page Up/Down, Home/End funcionales
• Selección automática: Al llegar con Tab se selecciona primer elemento

🎨 LAYOUT ADAPTATIVO:
• Ventana expandida: De 650px a 1050px para acomodar historial
• Contracción automática: Componentes se mueven a la izquierda con historial visible
• Expansión automática: Vuelve a tamaño completo al ocultar historial
• Barras pegadas: Estado y cache perfectamente pegadas al borde izquierdo

🏗️ ARQUITECTURA MODULAR REVOLUCIONARIA:
• app.py: De ~900 líneas → 330 líneas (reducción del 63%)
• historial_manager.py: Gestión completa del historial (200 líneas)
• ui_manager.py: Control de elementos de interfaz (80 líneas) 
• search_coordinator.py: Coordinación de búsquedas (120 líneas)
• Responsabilidades separadas: Cada módulo con función específica

⚡ FUNCIONALIDADES DEL HISTORIAL:
• Click en entrada: Muestra resultados automáticamente en tabla principal
• Ordenamiento: Headers clickeables por Hora y Criterio con indicadores ↑↓
• Búsqueda automática: Ejecuta cache o tradicional según disponibilidad
• Botón Limpiar: Elimina todo el historial de la sesión con confirmación
• F3/F4 funcionales: Repetir búsqueda y abrir carpeta desde historial
• Delete: Eliminar entrada individual seleccionada

🎯 MEJORAS TÉCNICAS:
• Threading seguro: Búsquedas silenciosas en background sin bloqueo
• Sincronización UI: Variables BooleanVar con callbacks automáticos
• Layout dinámico: Ajuste automático de componentes sin parpadeos
• Manejo de errores: Try/catch robusto en navegación y eventos
• Actualización forzada: update_idletasks() para renderizado inmediato

========================================

V. 3.6 - Estable (Inferno) - VERSIÓN ANTERIOR
========================================

CÓDIGO PROFESIONALIZADO:
• Comentarios reducidos: Solo los estrictamente necesarios
• Eliminación de OneDrive: Toda implementación removida
• Funcionalidad limpia: Sin código redundante o experimental
• Arquitectura estabilizada: Cada módulo con responsabilidad específica

PROGRESO SIMPLIFICADO:
• Solo porcentaje visible: Sin barra visual que cause movimientos
• Comportamiento unificado: Idéntico en cache y búsqueda tradicional
• Ocultación automática: 2s cache, 1.5s búsqueda tradicional
• Layout estable: Sin elementos que aparezcan/desaparezcan

INTERFAZ ULTRA-COMPACTA:
• Barras pegadas: Cache y estado sin espacios
• Ventana 660px: Tamaño optimizado sin desperdicios
• Fuentes legibles: 9pts en todas las barras
• Altura fija: Elementos que no cambian durante operaciones

========================================

🎯 EVOLUCIÓN DE LA DIVINA COMEDIA DEL CÓDIGO:

V. 2.1 (AllInOne) → Estructura inicial básica
V. 3.0B (Dante) → Búsqueda híbrida + interfaz moderna  
V. 3.2 (Inferno) → Sistema dual de entrada + optimizaciones
V. 3.4 (Inferno) → Refactorización arquitectónica completa
V. 3.6 (Inferno) → Estabilización y profesionalización
V. 4.0 (Purgatorio) → Purificación total: historial + modularización

🚀 PRÓXIMAS VERSIONES PLANEADAS:

V. 4.1 (Purgatorio) → Filtros avanzados y wildcards
V. 4.2 (Purgatorio) → Favoritos y búsquedas guardadas
V. 5.0 (Paradiso) → Integración con explorador + API RESTful

========================================

"Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura, 
ché la diritta via era smarrita."
- Dante Alighieri, Divina Comedia

V. 4.0 - Purgatorio representa la purificación completa del código: 
arquitectura modular, historial integrado, y navegación perfecta.

¡El Purgatorio está completo y perfeccionado! 🌟✨

Próximo destino: Paradiso - La perfección absoluta 🏔️
"""
        
        self.text_area.insert("1.0", changelog_content)
        self.text_area.configure(state="disabled")
        
        self.aplicar_formato()
    
    def aplicar_formato(self):
        self.text_area.tag_configure("version", font=("Segoe UI", 12, "bold"), foreground="#d32f2f")
        self.text_area.tag_configure("section", font=("Segoe UI", 10, "bold"), foreground="#1976d2")
        self.text_area.tag_configure("bullet", foreground="#4caf50")
        self.text_area.tag_configure("quote", font=("Segoe UI", 9, "italic"), foreground="#666666")
        self.text_area.tag_configure("separator", foreground="#cccccc")
        self.text_area.tag_configure("highlight", font=("Segoe UI", 9, "bold"), foreground="#ff5722")
        
        content = self.text_area.get("1.0", tk.END)
        lines = content.split('\n')
        
        self.text_area.configure(state="normal")
        
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            
            if "V. 4.0 - Purgatorio (Purificación) - VERSIÓN ACTUAL" in line:
                self.text_area.tag_add("version", line_start, line_end)
            elif "V. 3.6 - Estable (Inferno) - VERSIÓN ANTERIOR" in line:
                self.text_area.tag_add("highlight", line_start, line_end)
            elif line.startswith("•"):
                self.text_area.tag_add("bullet", line_start, line_end)
            elif "Nel mezzo del cammin" in line or "- Dante Alighieri" in line:
                self.text_area.tag_add("quote", line_start, line_end)
            elif "=" in line and len(line) > 20:
                self.text_area.tag_add("separator", line_start, line_end)
            elif line.isupper() and len(line) > 10:
                self.text_area.tag_add("section", line_start, line_end)
        
        self.text_area.configure(state="disabled")