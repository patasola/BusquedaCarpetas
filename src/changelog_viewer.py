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
        
        # Centrar ventana
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Título con estilo
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
        
        # Área de texto con scroll
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
        
        # Botón cerrar
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
        
        # Cargar contenido del changelog
        self.cargar_changelog()
        
        # Configurar eventos
        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)
        self.window.bind("<Escape>", lambda e: self.window.destroy())
    
    def cargar_changelog(self):
        changelog_content = """
V. 3.6 - Estable (Inferno) - VERSION ACTUAL
========================================

PROGRESO SIMPLIFICADO Y ESTABILIZADO:
• Solo porcentaje visible: Eliminada barra visual, solo se muestra el porcentaje (0%, 25%, 50%, 100%)
• Comportamiento unificado: Idéntico progreso en construcción de cache y búsqueda tradicional
• Ocultación automática: Progreso se oculta automáticamente después de completar (2s cache, 1.5s búsqueda)
• Sin movimientos: Layout completamente estable durante todas las operaciones
• Progreso funcional: Restaurado a versión completamente operativa

INTERFAZ ULTRA-COMPACTA:
• Barras pegadas: Barra de cache y estado completamente pegadas sin espacios
• Orden correcto: Cache arriba, estado abajo, sin huecos visuales
• Altura optimizada: Barras de 20px cada una para máxima compacidad
• Ventana 660px: Tamaño perfecto sin espacios blancos sobrantes
• Fuentes legibles: 9pts en barras de estado manteniendo legibilidad

CORRECCIONES TÉCNICAS:
• Progreso restaurado: Vuelta a versión funcional que mostraba porcentajes correctamente
• Layout estabilizado: Sin elementos que aparezcan/desaparezcan causando movimiento
• Posicionamiento perfecto: `side=tk.BOTTOM` con orden correcto de empaquetado
• Threading optimizado: Callbacks de progreso con throttling del 5% para rendimiento
• Debug controlado: Logs informativos sin saturar la consola

ARQUITECTURA MANTENIDA:
• ProgressManager: Gestión simplificada solo de porcentaje (sin barra visual)
• SearchManager: Lógica de búsqueda híbrida intacta
• FileManager: Operaciones de archivos optimizadas
• UICallbacks: Interface limpia entre managers y UI
• Separación de responsabilidades: Cada módulo con función específica

========================================

V. 3.5 (Inferno) - OPTIMIZACION COMPLETA
========================================

OPTIMIZACION DE INTERFAZ:
• Columnas autoajustables: Ancho dinámico basado en contenido real
• Alineación mejorada: Método centrado, Nombre y Ruta alineados a la izquierda
• Anchos iniciales compactos: Mejor aprovechamiento del espacio disponible
• Límites inteligentes: Máximos por columna para evitar expansión excesiva

MENSAJES MEJORADOS:
• Sin resultados en cache: Mensaje específico con tiempo + continúa tradicional
• Sin resultados tradicional: Mensaje claro de finalización sin resultados
• Tiempos precisos: Duración exacta mostrada para cada tipo de búsqueda
• Estados informativos: Usuario siempre sabe qué está pasando en cada fase

CORRECCIONES TÉCNICAS:
• Manejo completo de búsquedas vacías: Todos los escenarios cubiertos
• Barra de progreso inteligente: Se oculta automáticamente en búsquedas sin resultados
• Autoajuste automático: Columnas se redimensionan al cambiar contenido
• Debug granular: Logs específicos para cada escenario de búsqueda

RENDIMIENTO DE TABLA:
• Cálculo dinámico de anchos: ~8px por carácter + padding optimizado
• Actualización automática: Redimensionamiento tras cada búsqueda
• Límites por columna: Método (100px), Nombre (250px), Ruta (400px)
• Eficiencia visual: Sin desperdicio de espacio horizontal

========================================

V. 3.4 (Inferno) - REFACTORIZACION COMPLETA
========================================

REFACTORIZACION ARQUITECTONICA:
• Arquitectura modular: Separación de responsabilidades en 5 archivos especializados
• ProgressManager: Gestión centralizada de barras de progreso
• SearchManager: Lógica de búsqueda centralizada y optimizada
• FileManager: Operaciones de archivos y rutas unificadas
• UICallbacks: Interface limpia entre managers y UI

PROGRESO EN TIEMPO REAL:
• Construcción de cache con progreso visual: Actualización cada 100 directorios
• Búsquedas tradicionales con progreso: Actualización cada 50 directorios  
• Callbacks optimizados: Threading sin bloqueo de interfaz
• Indicadores precisos: Porcentajes exactos de progreso

MEJORAS TÉCNICAS:
• Código reducido: app.py de 500+ líneas a ~300 líneas
• Mantenibilidad: Cada archivo tiene responsabilidad única
• Testing facilitado: Componentes independientes y testeable
• Debug mejorado: Mensajes específicos por manager

NUEVA ESTRUCTURA:
• progress_manager.py - Gestión de barras de progreso
• search_manager.py - Lógica de búsqueda 
• file_manager.py - Operaciones de archivos
• ui_callbacks.py - Interface UI ↔ Managers
• app.py - Coordinación principal (simplificado)

========================================

V. 3.3 (Inferno) - OPTIMIZACION COMPLETA
========================================

OPTIMIZACION DE INTERFAZ:
• Barra de progreso inteligente: Solo aparece durante búsquedas tradicionales
• Progreso en tiempo real: Actualización cada 100 directorios procesados
• Interfaz más limpia: Sin elementos innecesarios durante búsquedas en cache
• Ocultación automática: La barra desaparece 1-2 segundos después de completar

MEJORAS DE RENDIMIENTO:
• Búsquedas en cache sin barra de progreso: Máxima velocidad (< 50ms)
• Callback de progreso optimizado: Actualización eficiente durante búsquedas tradicionales
• Cancelación mejorada: Limpieza automática de elementos de interfaz
• Threading optimizado: Solo para operaciones que realmente lo requieren

CORRECCIONES TÉCNICAS:
• Scrollbar horizontal corregida: Ocultación inteligente y automática
• Detección mejorada de viewport: Solo muestra cuando es verdaderamente necesario
• Gestión de eventos mejorada: Múltiples bindings para capturar todos los cambios
• Inicialización limpia: Sin scrollbars visibles al arrancar la aplicación

========================================

V. 3.2 (Inferno) - VERSION FUNDACIONAL
========================================

NUEVAS CARACTERÍSTICAS:
• Sistema de entrada dual: Modo numérico (por defecto) y alfanumérico
• Alternancia inteligente: Tecla F5 o botón visual para cambiar modos
• Indicadores visuales: Color de fondo cambia según el modo de entrada
• Búsqueda híbrida mejorada: Cache como prioridad, tradicional como fallback
• Scrollbars inteligentes: Solo aparecen cuando son necesarias

MEJORAS DE INTERFAZ:
• Colores de selección optimizados: Texto azul oscuro sobre fondo azul claro
• Tamaño compacto: Ventana reducida a 750x480 para mayor eficiencia
• Tabla optimizada: Solo 4 líneas visibles con scroll automático
• Sin bordes: Elementos más limpios y modernos
• Espaciado optimizado: Márgenes reducidos para aprovechar mejor el espacio

CORRECCIONES TÉCNICAS:
• Fallback automático: Si cache no encuentra resultados, busca tradicionalmente
• Eventos F5 corregidos: Múltiples bindings para asegurar funcionamiento
• Legibilidad mejorada: Contraste perfecto en elementos seleccionados
• Scrollbars automáticas: Detección inteligente de necesidad de scroll

========================================

V. 3.0B (Dante) - VERSION BASE MEJORADA
========================================

CARACTERÍSTICAS PRINCIPALES:
• Búsqueda híbrida: Cache instantáneo + búsqueda tradicional como respaldo
• Interfaz moderna: Diseño completamente renovado con Segoe UI
• Columna de método: Indica si el resultado proviene de "Cache" o "Tradicional"
• Cache optimizado: Construcción automática y búsquedas en milisegundos
• Botones centrados: Diseño más equilibrado y profesional

RENOVACION VISUAL:
• Paleta de colores moderna: Grises suaves con acentos azules
• Fuentes Segoe UI: Tipografía más moderna y legible
• Título sin fondo: Integración natural con el fondo principal
• Campo centrado: Texto de entrada alineado al centro
• Barras informativas: Estado y caché claramente visibles

OPTIMIZACION DE RENDIMIENTO:
• Cache en memoria: Búsquedas instantáneas después de la construcción inicial
• Threading optimizado: Solo para búsquedas tradicionales
• Validación de rutas: Verificación automática de acceso
• Manejo de errores: Diagnósticos completos y recuperación automática

========================================

V. 2.1 (AllInOne) - VERSION ORIGINAL
========================================

ESTRUCTURA INICIAL:
• Arquitectura modular: Separación clara de responsabilidades
• Búsqueda básica: Recorrido de directorios en tiempo real
• Selección de ruta: Diálogo para elegir carpeta base
• Tabla de resultados: Mostrar nombre y ruta de carpetas encontradas
• Acciones básicas: Abrir carpeta y copiar ruta al portapapeles

ATAJOS DE TECLADO:
• F2: Enfocar campo de búsqueda
• F3: Copiar ruta seleccionada
• F4: Abrir carpeta seleccionada
• Enter: Ejecutar búsqueda

========================================

EVOLUCION DE INTERFAZ DE USUARIO
========================================

PROGRESO VISUAL:
V. 2.1 → Sin indicadores de progreso
V. 3.0B → Progreso básico en construcción
V. 3.2 → Barra de progreso mejorada
V. 3.3 → Progreso inteligente según tipo de búsqueda
V. 3.4 → Progreso centralizado con managers
V. 3.5 → Progreso sincronizado y estable
V. 3.6 → Solo porcentaje, máxima estabilidad

COMPACIDAD DE INTERFAZ:
V. 2.1 → Interfaz básica con espacios estándar
V. 3.0B → Mejoras visuales moderadas
V. 3.2 → Reducción de tamaño a 750x480
V. 3.3 → Optimización de elementos
V. 3.4 → Arquitectura modular sin cambios visuales
V. 3.5 → Ajustes de espaciado
V. 3.6 → Ultra-compacta 660px, barras pegadas

ESTABILIDAD VISUAL:
V. 2.1 → Elementos básicos estáticos
V. 3.0B → Algunos elementos dinámicos
V. 3.2 → Scrollbars inteligentes
V. 3.3 → Reducción de movimientos
V. 3.4 → Espacios reservados
V. 3.5 → Layout más estable
V. 3.6 → Cero movimientos, máxima estabilidad

========================================

RENDIMIENTO ACTUAL (V. 3.6)
========================================

INDICADORES DE PROGRESO:
• Cache: Solo porcentaje 0% → 100% (sin barra visual)
• Búsqueda tradicional: Solo porcentaje 0% → 100% (sin barra visual)
• Ocultación: Automática después de 2 segundos (cache) / 1.5 segundos (búsqueda)
• Layout: Completamente estable, sin movimientos durante operaciones

TIEMPOS DE BÚSQUEDA:
• Cache (método preferido): < 50ms (prácticamente instantáneo)
• Construcción cache: ~1-2 segundos por cada 10,000 directorios
• Búsqueda tradicional: Variable según tamaño (solo como fallback)

INTERFAZ OPTIMIZADA V. 3.6:
• Ventana 660px: Tamaño perfecto sin desperdicios
• Barras pegadas: Cache y estado sin espacios entre ellas
• Solo porcentaje: Progreso visual sin elementos que causen movimiento
• Fuentes legibles: 9pts en barras de estado para óptima lectura

ARQUITECTURA ESTABILIZADA:
• ProgressManager: Gestión simplificada solo de porcentaje
• SearchManager: Coordinación de búsquedas híbridas optimizada
• FileManager: Operaciones de archivos unificadas y confiables
• UICallbacks: Interface limpia y estable managers ↔ UI
• App: Coordinación principal sin complejidad innecesaria

========================================

PROXIMAS VERSIONES PLANIFICADAS
========================================

V. 4.0 (Purgatorio) - Purificación y refinamiento:
• Filtros avanzados de búsqueda con wildcards (* ? [])
• Historial de búsquedas recientes con persistencia
• Favoritos de carpetas más utilizadas
• Búsqueda por fecha/tamaño de carpetas
• Testing automatizado de todos los managers
• Temas visuales personalizables

V. 5.0 (Paradiso) - Perfección y funcionalidades avanzadas:
• Integración con el explorador de Windows
• Búsqueda de contenido dentro de archivos
• Sincronización con servicios en la nube
• Tema oscuro/claro automático según el sistema
• Plugin system para extensiones personalizadas
• API RESTful para integración externa

========================================

NOTAS TÉCNICAS V. 3.6
========================================

DEPENDENCIAS:
• Python 3.12+
• tkinter: Interfaz gráfica
• pyperclip: Gestión del portapapeles
• threading: Procesamiento en segundo plano

OPTIMIZACIONES V. 3.6:
• Progreso simplificado: Solo porcentaje visible, sin barra que cause movimientos
• Interface ultra-compacta: 660px altura, barras pegadas sin espacios
• Layout estabilizado: Elementos con tamaño fijo que no cambian durante operaciones
• Threading optimizado: Callbacks con throttling del 5% para máximo rendimiento

NUEVA FUNCIONALIDAD:
• Progreso unificado: Comportamiento idéntico en cache y búsqueda tradicional
• Ocultación inteligente: Temporal automática sin intervención del usuario
• Barras pegadas: Cache y estado completamente unidas sin espacios
• Máxima estabilidad: Cero movimientos de elementos durante cualquier operación

RENDIMIENTO MEJORADO:
• Callbacks optimizados: Solo actualizaciones cada 5% para evitar saturación
• Layout fijo: Todos los elementos mantienen posición y tamaño constante
• Memory footprint: Reducido al eliminar elementos visuales innecesarios
• Response time: Interfaz más responsiva al eliminar redimensionamientos

========================================

"Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura, 
ché la diritta via era smarrita."
- Dante Alighieri, Divina Comedia

En el medio del camino de nuestra aplicación, nos encontramos en un 
bosque oscuro de código monolítico, donde el camino recto hacia la 
perfección se había perdido... 

V. 3.6 - Estable representa la culminación del Inferno: una interfaz 
completamente estabilizada donde cada elemento tiene su lugar perfecto 
y ningún movimiento molesta la experiencia del usuario. El progreso 
se muestra de forma elegante y minimalista, las barras están 
perfectamente alineadas, y la funcionalidad es completamente confiable.

La arquitectura modular establecida en V. 3.4 ahora opera con máxima 
eficiencia, cada manager cumple su función específica, y la experiencia 
del usuario es fluida, predecible y profesional.

¡El Inferno está completo y perfeccionado! Próximo destino: Purgatorio.

Cada versión nos acerca más a la perfección. 🌟
"""
        
        self.text_area.insert("1.0", changelog_content)
        self.text_area.configure(state="disabled")  # Solo lectura
        
        # Aplicar formato con tags
        self.aplicar_formato()
    
    def aplicar_formato(self):
        # Configurar tags para formato
        self.text_area.tag_configure("version", font=("Segoe UI", 12, "bold"), foreground="#d32f2f")
        self.text_area.tag_configure("section", font=("Segoe UI", 10, "bold"), foreground="#1976d2")
        self.text_area.tag_configure("bullet", foreground="#4caf50")
        self.text_area.tag_configure("quote", font=("Segoe UI", 9, "italic"), foreground="#666666")
        self.text_area.tag_configure("separator", foreground="#cccccc")
        self.text_area.tag_configure("big_title", font=("Segoe UI", 14, "bold"), foreground="#000000")  # Títulos grandes negros
        self.text_area.tag_configure("version_evolution", font=("Segoe UI", 8), foreground="#4caf50")  # Verde pequeño para evolución
        
        # Buscar y aplicar formato
        content = self.text_area.get("1.0", tk.END)
        lines = content.split('\n')
        
        self.text_area.configure(state="normal")
        
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            
            # TÍTULOS GRANDES EN NEGRO NEGRITA
            if any(big_title in line for big_title in [
                "EVOLUCION DE INTERFAZ DE USUARIO",
                "RENDIMIENTO ACTUAL (V. 3.6)",
                "PROXIMAS VERSIONES PLANIFICADAS", 
                "NOTAS TÉCNICAS V. 3.6"
            ]):
                self.text_area.tag_add("big_title", line_start, line_end)
            
            # VERSIONES PRINCIPALES EN ROJO GRANDE (solo versiones actuales y pasadas)
            elif any(version_marker in line for version_marker in [
                "V. 3.6 - Estable (Inferno) - VERSION ACTUAL",
                "V. 3.5 (Inferno) - OPTIMIZACION COMPLETA",
                "V. 3.4 (Inferno) - REFACTORIZACION COMPLETA",
                "V. 3.3 (Inferno) - OPTIMIZACION COMPLETA", 
                "V. 3.2 (Inferno) - VERSION FUNDACIONAL",
                "V. 3.0B (Dante) - VERSION BASE MEJORADA",
                "V. 2.1 (AllInOne) - VERSION ORIGINAL"
            ]) and ("=" not in line):
                self.text_area.tag_add("version", line_start, line_end)
            
            # VERSIONES FUTURAS EN AZUL (V. 4.0 y V. 5.0)
            elif any(future_version in line for future_version in [
                "V. 4.0 (Purgatorio)",
                "V. 5.0 (Paradiso)"
            ]):
                self.text_area.tag_add("section", line_start, line_end)
            
            # VERSIONES EN EVOLUCIÓN: VERDE PEQUEÑO
            elif line.strip().startswith("V. ") and ("→" in line):
                self.text_area.tag_add("version_evolution", line_start, line_end)
            
            # VIÑETAS VERDES
            elif line.startswith("•"):
                self.text_area.tag_add("bullet", line_start, line_end)
            
            # CITAS DE DANTE
            elif "Nel mezzo del cammin" in line or "- Dante Alighieri" in line:
                self.text_area.tag_add("quote", line_start, line_end)
            
            # SEPARADORES
            elif "=" in line and len(line) > 20:
                self.text_area.tag_add("separator", line_start, line_end)
            
            # SECCIONES EN AZUL (excluyendo títulos grandes ya procesados)
            elif line.isupper() and len(line) > 10 and not any(big_title in line for big_title in [
                "EVOLUCION", "RENDIMIENTO ACTUAL", "PROXIMAS VERSIONES", "NOTAS TÉCNICAS"
            ]):
                self.text_area.tag_add("section", line_start, line_end)
        
        self.text_area.configure(state="disabled")