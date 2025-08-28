# src/constants.py - Constantes V.4.2 (Refactorizado)

# Información de la aplicación
APP_VERSION = "V. 4.2 - Refactorizada"
APP_TITLE = "Búsqueda Rápida de Carpetas"

# Configuración de ventana
WINDOW_SIZE = "1200x700"
MIN_WINDOW_SIZE = (800, 500)

# Archivos de configuración
CONFIG_FILE = "config.json"

# Configuración de UI
TREE_HEIGHT = 5
MAIN_PADDING = {'x': 20, 'y': 10}
ENTRY_WIDTH = 30

# Límites de rendimiento
MAX_CARPETAS = 50000
MAX_TIEMPO_SEGUNDOS = 30
MAX_PROFUNDIDAD = 6
MAX_RESULTADOS = 2000

# Intervalos de actualización
PROGRESS_UPDATE_INTERVAL = 100  # Cada 100 carpetas
RESULT_UPDATE_INTERVAL = 5      # Cada 5%

class Colors:
    # Colores principales
    BACKGROUND = "#f6f5f5"
    TITLE_FG = "#424242"
    INFO_FG = "#424242"
    TREE_FG = "#424242"
    TREE_BG = "#ffffff"
    TREE_SELECT_BG = "#e3f2fd"
    TREE_SELECT_FG = "#0d47a1"
    
    # Botones
    BUTTON_BG = "#e0e0e0"
    BUTTON_FG = "#424242"
    BUTTON_ACTIVE_BG = "#d0d0d0"
    
    # Grises
    DARK_GRAY = "#424242"
    MEDIUM_GRAY = "#757575"
    LIGHT_GRAY = "#e0e0e0"
    VERY_LIGHT_GRAY = "#f5f5f5"
    WHITE = "#ffffff"
    
    # Barras
    BLUE_BAR = "#1976D2"
    CACHE_BAR_BG = "#F0F8FF"
    STATUS_BAR_BG = "SystemButtonFace"
    
    # Encabezados de tabla
    TABLE_HEADER = "#f8f9fa"
    TABLE_ALT_ROW = "#f8f9fa"

class Fonts:
    BUTTONS = ("Segoe UI", 9)
    NORMAL = ("Segoe UI", 9)
    TITLE = ("Segoe UI", 14, "bold")
    VERSION = ("Segoe UI", 8)
    TABLE_HEADER = ("Segoe UI", 10, "bold")

class Messages:
    READY = "F2: Enfocar búsqueda • F3: Copiar • F4: Abrir • F5: Modo • Tab: Navegar"
    FOLDER_SELECTED = "Carpeta seleccionada y caché construido"
    CACHE_BUILDING = "Construyendo caché automáticamente..."
    CACHE_COMPLETED = "Caché construido exitosamente"
    NO_FOLDER = "Error: Seleccione una ruta primero"
    NO_CRITERIA = "Error: Ingrese un criterio de búsqueda"
    SEARCH_CANCELLED = "Búsqueda cancelada"
    CACHE_CLEARED = "Caché limpiado"
    NUMERIC_MODE = "[123] Numérico"
    ALPHA_MODE = "[ABC] Alfanumérico"

# Constantes legacy para compatibilidad
COLORS = {
    'background': Colors.BACKGROUND,
    'dark_gray': Colors.DARK_GRAY,
    'medium_gray': Colors.MEDIUM_GRAY,
    'light_gray': Colors.LIGHT_GRAY,
    'very_light_gray': Colors.VERY_LIGHT_GRAY,
    'white': Colors.WHITE,
    'blue_bar': Colors.BLUE_BAR,
    'cache_bar': Colors.CACHE_BAR_BG,
    'table_header': Colors.TABLE_HEADER,
    'table_alt_row': Colors.TABLE_ALT_ROW
}

FONT_NORMAL = Fonts.NORMAL
FONT_TITLE = Fonts.TITLE
FONT_BUTTONS = Fonts.BUTTONS
FONT_VERSION = Fonts.VERSION
FONT_TABLE_HEADER = Fonts.TABLE_HEADER

MESSAGES = {
    'ready': Messages.READY,
    'folder_selected': Messages.FOLDER_SELECTED,
    'cache_building': Messages.CACHE_BUILDING,
    'cache_completed': Messages.CACHE_COMPLETED,
    'no_folder': Messages.NO_FOLDER,
    'no_criteria': Messages.NO_CRITERIA,
    'search_cancelled': Messages.SEARCH_CANCELLED,
    'cache_cleared': Messages.CACHE_CLEARED,
    'numeric_mode': Messages.NUMERIC_MODE,
    'alpha_mode': Messages.ALPHA_MODE
}