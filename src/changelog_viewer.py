# src/changelog_viewer.py - Visor de Changelog V.4.2 (Refactorizado)
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
            
        self._crear_ventana()
        self._crear_contenido()
        self._cargar_changelog()
        self._aplicar_formato()
        
    def _crear_ventana(self):
        """Crea y configura la ventana"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Historial de Cambios - La Divina Comedia del Código")
        self.window.geometry("700x750")
        self.window.configure(bg=Colors.BACKGROUND)
        self.window.resizable(True, True)
        self.window.transient(self.parent)
        self.window.grab_set()
        
    def _crear_contenido(self):
        """Crea la interfaz del changelog"""
        main_frame = tk.Frame(self.window, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Título
        title_frame = tk.Frame(main_frame, bg=Colors.BACKGROUND)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            title_frame,
            text="HISTORIAL DE CAMBIOS",
            font=("Segoe UI", 16, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG
        ).pack()
        
        tk.Label(
            title_frame,
            text="La Divina Comedia del Código - Co-creado por Elkin Darío Pérez Puyana y Claude Sonnet 4",
            font=("Segoe UI", 10, "italic"),
            bg=Colors.BACKGROUND,
            fg="#666666"
        ).pack(pady=(5, 0))
        
        # Área de texto
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
            padx=15, pady=15,
            relief=tk.FLAT,
            borderwidth=1
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Botón cerrar
        tk.Button(
            main_frame,
            text="Cerrar",
            font=Fonts.BUTTONS,
            bg=Colors.BUTTON_BG,
            fg=Colors.BUTTON_FG,
            relief=tk.FLAT,
            borderwidth=1,
            padx=20, pady=8,
            command=self.window.destroy,
            cursor="hand2"
        ).pack()
        
        # Eventos
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.window.bind("<Escape>", lambda e: self.window.destroy())
    
    def _cargar_changelog(self):
        changelog_content = """V. 4.2 - Purgatorio (Refactorización Completa) - VERSIÓN ACTUAL
========================================

REFACTORIZACIÓN MASIVA COMPLETADA:
• Reducción promedio del 30% en líneas de código por archivo
• 20 archivos completamente refactorizados y optimizados
• Eliminación de redundancias y código duplicado
• Mantenimiento 100% de funcionalidad existente
• Arquitectura más limpia y mantenible

ARCHIVOS REFACTORIZADOS (Líneas reducidas):
• app.py: De ~400 → 200 líneas (-50%)
• cache_manager.py: De ~270 → 200 líneas (-26%)
• event_manager.py: De ~280 → 200 líneas (-29%)  
• historial_manager.py: De ~480 → 330 líneas (-31%)
• search_coordinator.py: De ~470 → 320 líneas (-32%)
• tree_explorer.py: De ~520 → 380 líneas (-27%)
• ui_callbacks.py: De ~600 → 280 líneas (-53%)
• +13 archivos más completamente optimizados

OPTIMIZACIONES TÉCNICAS:
• Consolidación de métodos similares usando diccionarios
• Eliminación de comentarios excesivos y debug innecesario
• Manejo de errores unificado y consistente
• Loops y comprensiones para reducir código repetitivo
• Configuraciones por diccionario en lugar de múltiples if-elif

MEJORAS EN LEGIBILIDAD:
• Nombres de métodos más descriptivos y concisos
• Estructura modular más clara y enfocada
• Separación mejorada de responsabilidades
• Código más pythónico y eficiente

========================================

V. 4.1 - Purgatorio (Explorador Integrado)
========================================

TREE EXPLORER V.4.1 INTEGRADO:
• Explorador de árbol completamente funcional
• Expansión/colapso de nodos con subdirectorios
• Cache temporal para navegación rápida
• Navegación con flechas (←→↑↓, Enter, F-keys)
• Ajuste automático de columnas bidireccional

FUNCIONALIDADES TREE EXPLORER:
• F6: Limpiar cache temporal del explorador
• Doble-click: Abrir carpeta en explorador del sistema
• Threading asíncrono para carga de subdirectorios
• Indicadores visuales de carga y estado
• Integración perfecta con búsquedas existentes

========================================

V. 4.0 - Purgatorio (Purificación) 
========================================

MENÚ "VER" - CONTROL TOTAL DE INTERFAZ:
• Barra de Estado: Control independiente de barra inferior
• Barra de Cache: Toggle de barra de información azul
• Historial de Búsquedas: Panel lateral integrado
• Sincronización perfecta entre menú y estado real

HISTORIAL DE BÚSQUEDAS INTEGRADO:
• Panel lateral integrado (no ventana separada)
• Historial de sesión únicamente (máximo 50 entradas)
• Búsqueda rápida desde cache al seleccionar
• Ordenamiento por columnas con indicadores
• Botón Limpiar con confirmación

NAVEGACIÓN POR TAB COMPLETA:
• Orden: Campo → Buscar → Cancelar → Tabla → Copiar → Abrir → Historial
• Navegación circular automática
• Inclusión dinámica del historial según visibilidad
• Flechas funcionales en todas las secciones

LAYOUT ADAPTATIVO:
• Ventana expandida de 650px → 1200px
• Contracción automática con historial visible
• Barras pegadas al borde izquierdo perfectamente

ARQUITECTURA MODULAR:
• app.py: Coordinación principal optimizada
• historial_manager.py: Gestión completa del historial
• ui_manager.py: Control de elementos de interfaz  
• search_coordinator.py: Coordinación de búsquedas
• window_manager.py: Gestión de ventana y centrado

========================================

V. 3.6 - Inferno (Estable)
========================================

CÓDIGO PROFESIONALIZADO:
• Eliminación completa de OneDrive
• Comentarios reducidos a lo esencial
• Funcionalidad limpia sin código experimental
• Arquitectura estabilizada

PROGRESO SIMPLIFICADO:
• Solo porcentaje visible en barra de estado
• Comportamiento unificado cache/tradicional
• Ocultación automática tras completar

INTERFAZ ULTRA-COMPACTA:
• Ventana optimizada 660px
• Barras pegadas sin espacios
• Elementos de altura fija
• Fuentes legibles 9pts

========================================

EVOLUCIÓN DE LA DIVINA COMEDIA DEL CÓDIGO:

V. 2.1 → Estructura inicial básica
V. 3.0B → Búsqueda híbrida + interfaz moderna  
V. 3.2 → Sistema dual de entrada + optimizaciones
V. 3.4 → Refactorización arquitectónica
V. 3.6 → Estabilización profesional
V. 4.0 → Purificación: historial + modularización
V. 4.1 → Explorador integrado + tree navigation
V. 4.2 → Refactorización completa: código optimizado

PRÓXIMAS VERSIONES:
V. 4.3 → Filtros avanzados y wildcards
V. 4.4 → Favoritos y búsquedas guardadas
V. 5.0 (Paradiso) → Integración con explorador + API RESTful

========================================

"Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura, 
ché la diritta via era smarrita."
- Dante Alighieri, Divina Comedia

V. 4.2 - Purgatorio representa la refactorización y optimización completa:
código limpio, eficiente, y mantenible sin perder funcionalidad.

Co-creado por la colaboración humano-IA entre 
Elkin Darío Pérez Puyana y Claude Sonnet 4

¡El Purgatorio está perfeccionado y optimizado! 
Próximo destino: Paradiso - La perfección absoluta"""
        
        self.text_area.insert("1.0", changelog_content)
        self.text_area.configure(state="disabled")
        
    def _aplicar_formato(self):
        """Aplica formato de colores al texto"""
        # Configurar tags
        tags = {
            "version": {"font": ("Segoe UI", 12, "bold"), "foreground": "#d32f2f"},
            "section": {"font": ("Segoe UI", 10, "bold"), "foreground": "#1976d2"},
            "bullet": {"foreground": "#4caf50"},
            "quote": {"font": ("Segoe UI", 9, "italic"), "foreground": "#666666"},
            "separator": {"foreground": "#cccccc"},
            "highlight": {"font": ("Segoe UI", 9, "bold"), "foreground": "#ff5722"},
            "new": {"font": ("Segoe UI", 10, "bold"), "foreground": "#e91e63"}
        }
        
        for tag, config in tags.items():
            self.text_area.tag_configure(tag, **config)
        
        # Aplicar formato por líneas
        content = self.text_area.get("1.0", tk.END)
        lines = content.split('\n')
        
        self.text_area.configure(state="normal")
        
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            
            if "V. 4.2 - Purgatorio (Refactorización Completa)" in line:
                self.text_area.tag_add("new", line_start, line_end)
            elif "V. 4.0 - Purgatorio (Purificación)" in line or "V. 4.1" in line:
                self.text_area.tag_add("version", line_start, line_end)
            elif "V. 3.6" in line:
                self.text_area.tag_add("highlight", line_start, line_end)
            elif line.startswith("•"):
                self.text_area.tag_add("bullet", line_start, line_end)
            elif "Nel mezzo del cammin" in line or "Dante Alighieri" in line:
                self.text_area.tag_add("quote", line_start, line_end)
            elif "=" in line and len(line) > 20:
                self.text_area.tag_add("separator", line_start, line_end)
            elif line.isupper() and len(line) > 10:
                self.text_area.tag_add("section", line_start, line_end)
        
        self.text_area.configure(state="disabled")