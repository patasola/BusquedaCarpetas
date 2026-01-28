# src/changelog_viewer.py - Visualizador de Registro de Cambios V.4.5 (Paneles Duales con Redimensión)
import tkinter as tk
from tkinter import ttk
from .constants import Colors, Fonts

class ChangelogViewer:
    def __init__(self, parent):
        self.parent = parent
        self.changelog_window = None

    def mostrar_changelog(self):
        """Muestra la ventana del changelog"""
        if self.changelog_window:
            self.changelog_window.lift()
            return

        self.changelog_window = tk.Toplevel(self.parent)
        self.changelog_window.title("Registro de Cambios")
        self.changelog_window.geometry("800x600")
        self.changelog_window.resizable(True, True)
        
        # Protocolo de cierre
        self.changelog_window.protocol("WM_DELETE_WINDOW", self._cerrar_changelog)
        
        # Frame principal con scrollbar
        main_frame = ttk.Frame(self.changelog_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear el texto con scrollbar
        self.text_widget = tk.Text(main_frame, 
                                 wrap='word',
                                 font=Fonts.NORMAL,
                                 background=Colors.BACKGROUND,
                                 foreground=Colors.DARK_GRAY,
                                 insertbackground=Colors.DARK_GRAY,
                                 selectbackground=Colors.TREE_SELECT_BG,
                                 selectforeground=Colors.TREE_SELECT_FG,
                                 relief='flat',
                                 borderwidth=0,
                                 padx=15,
                                 pady=15)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.text_widget.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Cargar contenido
        self._cargar_changelog()
        
        # Configurar tags para estilo
        self._configurar_tags()
        
        # Aplicar colores después de cargar
        self._aplicar_colores_automaticos()
        
        # Deshabilitar edición
        self.text_widget.config(state='disabled')
        
        # Enfocar
        self.changelog_window.focus_set()

    def _cargar_changelog(self):
        changelog_content = """V. 4.5 - Purgatorio Perfeccionado (Paneles Duales con Redimensión) - VERSIÓN ACTUAL
========================================

🚀 NUEVA FUNCIONALIDAD PRINCIPAL: PANELES DUALES SIN SOLAPAMIENTO
✅ Sistema de 3 columnas: Principal + Panel 1 + Panel 2
✅ SIN solapamiento: Los paneles aparecen lado a lado, no uno encima del otro
✅ Posicionamiento inteligente: El primer panel que se abra va pegado a la app principal
✅ Segundo panel automático: Se posiciona a la derecha del primero

🎛️ REDIMENSIONAMIENTO DINÁMICO AUTOMÁTICO
✅ App sola: 15cm de ancho (tamaño optimizado)
✅ App + 1 panel: Se expande automáticamente a 23cm
✅ App + 2 paneles: Se expande automáticamente a 31cm
✅ Cierre inteligente: La ventana se reduce progresivamente al cerrar paneles
✅ Centrado automático: La ventana se reposiciona al centro al cambiar de tamaño

🔧 MEJORAS DE USABILIDAD
✅ Contenido principal preservado: NUNCA se comprime, mantiene su espacio completo
✅ Paneles de ancho completo: Cada panel mantiene sus 8cm de ancho sin compresión
✅ Navegación Tab mejorada: Incluye ambos paneles en orden de posición
✅ Transiciones suaves: Sin saltos bruscos al redimensionar

📊 IMPACTO EN RENDIMIENTO
✅ Carga mínima adicional: <0.05 segundos de tiempo inicial
✅ Uso de memoria optimizado: +10-50KB por panel adicional
✅ Velocidad preservada: Sin impacto perceptible en operaciones

🛠️ ARQUITECTURA MEJORADA
✅ Sistema de posiciones: Gestión inteligente de columnas disponibles
✅ WindowManager expandido: Métodos de redimensionamiento dinámico
✅ Debug completo: Trazabilidad total del posicionamiento de paneles

════════════════════════════════════════════════════════════════════════

V. 4.4 - Purgatorio Perfeccionado (Refactorización Masiva) 
========================================

🔧 REFACTORIZACIÓN DEL EXPLORADOR DE ARCHIVOS
✅ Reducción masiva: De 1098 líneas a 465 líneas (57% menos código)
✅ Arquitectura modular: Separado en 3 componentes especializados
   - explorer_ui.py: Interfaz gráfica completa
   - file_monitor.py: Monitoreo automático con watchdog
   - file_operations.py: Operaciones de archivos especializadas

🚀 MEJORAS DE MANTENIBILIDAD
✅ Código organizado por responsabilidades
✅ Debugging simplificado con errores aislados
✅ Testing granular por módulos
✅ Reutilización de componentes

📈 ARQUITECTURA OPTIMIZADA
✅ Separación de responsabilidades clara
✅ Interfaces públicas preservadas al 100%
✅ Compatibilidad total con versiones anteriores
✅ Base sólida para futuras expansiones

════════════════════════════════════════════════════════════════════════

V. 4.3 - Purgatorio Perfeccionado
========================================

🎨 NUEVA IDENTIDAD VISUAL COMPLETA
✅ Tema oscuro profesional con paleta de colores cohesiva
✅ Tipografías optimizadas: Segoe UI para claridad, Consolas para código
✅ Iconos SVG vectoriales de alta calidad integrados
✅ Espaciado y márgenes consistentes en toda la aplicación

🖥️ INTERFAZ REDISEÑADA COMPLETAMENTE
✅ Explorador de archivos lateral con navegación por teclado
✅ Panel de historial lateral con búsqueda y filtros
✅ Menú contextual avanzado con acciones rápidas
✅ Tooltips informativos con ayuda contextual

⚡ RENDIMIENTO Y VELOCIDAD OPTIMIZADOS
✅ Sistema de caché inteligente con estadísticas en tiempo real
✅ Búsquedas 5-10x más rápidas con índices optimizados
✅ Interfaz responsiva sin congelamientos
✅ Monitoreo automático de cambios en archivos con watchdog

🔧 FUNCIONALIDADES AVANZADAS
✅ Múltiples métodos de búsqueda (Caché, Directo, Windows Search)
✅ Filtros por tipo de archivo y fecha de modificación
✅ Exportación de resultados en múltiples formatos
✅ Navegación por teclado completa con Tab y flechas

📊 SISTEMA DE ESTADÍSTICAS
✅ Métricas de rendimiento en tiempo real
✅ Estadísticas de caché y hit ratio
✅ Tiempos de respuesta detallados
✅ Información del sistema y recursos

🎯 MEJORAS DE USABILIDAD
✅ Atajos de teclado intuitivos (F1-F12)
✅ Drag & drop para carpetas
✅ Copiar rutas y nombres con un clic
✅ Vista previa de archivos y propiedades

════════════════════════════════════════════════════════════════════════

V. 4.2 - Herramientas Auxiliares
========================================

📚 SISTEMA DE DOCUMENTACIÓN INTEGRADA
✅ Manual de usuario completo con ejemplos
✅ Registro de cambios versionado
✅ Diálogo "Acerca de" con información del sistema

🎨 MEJORAS VISUALES
✅ Iconos SVG personalizados
✅ Tema de colores consistente
✅ Mejores tooltips y ayudas contextuales

🔧 ESTABILIDAD Y RENDIMIENTO
✅ Corrección de bugs menores
✅ Optimizaciones de memoria
✅ Mejor manejo de errores

════════════════════════════════════════════════════════════════════════

V. 4.1 - Optimizaciones Core
========================================

⚡ BÚSQUEDAS MÁS RÁPIDAS
✅ Algoritmos de búsqueda optimizados
✅ Mejor manejo de memoria durante búsquedas
✅ Caché más eficiente y menos fragmentado

🔧 MEJORAS DE ESTABILIDAD
✅ Manejo robusto de errores de sistema
✅ Mejor gestión de hilos y procesos
✅ Menos uso de recursos del sistema

🛠️ CORRECCIONES DE BUGS
✅ Fixes en navegación por teclado
✅ Corrección de memory leaks menores
✅ Mejoras en compatibilidad con Windows 11

════════════════════════════════════════════════════════════════════════

V. 4.0 - Reescritura Completa
========================================

🏗️ ARQUITECTURA COMPLETAMENTE NUEVA
✅ Código modular y mantenible con separación clara
✅ Patrón MVC (Modelo-Vista-Controlador) implementado
✅ Estructura de archivos organizada por funcionalidad
✅ Sistema de plugins preparado para futuras expansiones

🚀 NUEVAS CARACTERÍSTICAS PRINCIPALES
✅ Interfaz gráfica moderna con Tkinter optimizado
✅ Sistema de caché inteligente con indexación rápida
✅ Múltiples métodos de búsqueda intercambiables
✅ Navegación completa por teclado sin dependencia del mouse

📈 RENDIMIENTO DRAMÁTICAMENTE MEJORADO
✅ Búsquedas hasta 10x más rápidas que versiones anteriores
✅ Uso de memoria optimizado (50% menos que V.3.x)
✅ Interfaz más responsiva sin congelamientos
✅ Startup time reducido a menos de 1 segundo

🎨 NUEVA EXPERIENCIA DE USUARIO
✅ Tema oscuro profesional como estándar
✅ Iconos vectoriales SVG de alta calidad
✅ Tooltips informativos en cada elemento
✅ Feedback visual inmediato en todas las acciones

🔍 SISTEMA DE BÚSQUEDA AVANZADO
✅ Búsqueda por patrones y expresiones regulares
✅ Filtros por fecha, tamaño y atributos
✅ Historial inteligente con sugerencias
✅ Exportación de resultados en múltiples formatos

⌨️ ACCESIBILIDAD Y PRODUCTIVIDAD
✅ Atajos de teclado para todas las funciones
✅ Navegación Tab completa y lógica
✅ Soporte para lectores de pantalla
✅ Modo alto contraste disponible

🛠️ HERRAMIENTAS DE DESARROLLO
✅ Modo debug con logging detallado
✅ Profiler de rendimiento integrado
✅ Estadísticas de uso en tiempo real
✅ API para integraciones futuras

════════════════════════════════════════════════════════════════════════

VERSIONES ANTERIORES (3.x y menores)
====================================

V. 3.2 - Última versión del prototipo anterior
✅ Búsqueda básica por línea de comandos
✅ Soporte limitado para filtros
✅ Interfaz de texto simple

V. 3.1 - Mejoras de estabilidad
✅ Corrección de crashes en Windows 10
✅ Mejor manejo de caracteres especiales
✅ Optimizaciones menores de velocidad

V. 3.0 - Primer prototipo funcional
✅ Concepto inicial de búsqueda de carpetas
✅ Algoritmo básico de indexación
✅ Interfaz por línea de comandos

V. 2.x y anteriores - Versiones de desarrollo
✅ Pruebas de concepto
✅ Experimentación con diferentes algoritmos
✅ Prototipos no públicos

════════════════════════════════════════════════════════════════════════

NOTAS DE DESARROLLO
==================

La evolución de Búsqueda Rápida de Carpetas representa un viaje de 
optimización constante. Desde los primeros prototipos de línea de 
comandos hasta la actual interfaz gráfica profesional, cada versión 
ha incorporado feedback de usuarios y lecciones aprendidas.

La versión 4.0 marcó un punto de inflexión con la reescritura completa
usando patrones de diseño modernos. Las versiones 4.1-4.3 refinaron
esta base con optimizaciones y nuevas características.

La versión 4.4 introdujo la refactorización masiva para mejorar 
mantenibilidad, y la versión 4.5 presenta el sistema de paneles duales
que revoluciona la experiencia de usuario.

Cada actualización mantiene compatibilidad hacia atrás mientras
introduce mejoras significativas en usabilidad y rendimiento.

Para sugerencias y reportes de bugs, consulte la documentación
de desarrollo en el repositorio del proyecto.

════════════════════════════════════════════════════════════════════════

CRÉDITOS Y AGRADECIMIENTOS
==========================

Desarrollado con Python 3.12+ y las siguientes tecnologías:
• Tkinter para la interfaz gráfica
• Watchdog para monitoreo de archivos
• Threading para operaciones asíncronas
• Pathlib para manejo moderno de rutas
• JSON para configuración y cache

Agradecimientos especiales a la comunidad Python por las 
librerías que hacen posible esta aplicación.

════════════════════════════════════════════════════════════════════════"""

        self.text_widget.insert('1.0', changelog_content)

    def _configurar_tags(self):
        """Configura los tags para el formato del changelog"""
        # Título principal
        self.text_widget.tag_configure("title", 
                                     font=Fonts.TITLE,
                                     foreground=Colors.TREE_SELECT_FG)
        
        # Separadores
        self.text_widget.tag_configure("separator", 
                                     foreground=Colors.MEDIUM_GRAY)
        
        # Categorías (🚀, 🔧, etc.)
        self.text_widget.tag_configure("category", 
                                     font=("Segoe UI", 10, "bold"),
                                     foreground=Colors.BLUE_BAR)
        
        # Items de lista (✅)
        self.text_widget.tag_configure("item", 
                                     foreground=Colors.DARK_GRAY)

    def _aplicar_colores_automaticos(self):
        """Aplica colores automáticamente basado en el contenido"""
        content = self.text_widget.get('1.0', 'end')
        lines = content.split('\n')
        
        self.text_widget.config(state='normal')
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            
            if line.startswith("V.") and "====" not in line:
                self.text_widget.tag_add("title", line_start, line_end)
            elif line.startswith("🚀") or line.startswith("🔧") or line.startswith("📊") or line.startswith("🎛️") or line.startswith("🛠️") or line.startswith("📈") or line.startswith("🎨") or line.startswith("🖥️") or line.startswith("⚡") or line.startswith("🏗️") or line.startswith("🔍") or line.startswith("⌨️") or line.startswith("📚"):
                self.text_widget.tag_add("category", line_start, line_end)
            elif line.startswith("✅"):
                self.text_widget.tag_add("item", line_start, line_end)
            elif "====" in line:
                self.text_widget.tag_add("separator", line_start, line_end)
        
        self.text_widget.config(state='disabled')

    def _cerrar_changelog(self):
        """Cierra la ventana del changelog"""
        if self.changelog_window:
            self.changelog_window.destroy()
            self.changelog_window = None