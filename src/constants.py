# src/constants.py - Constantes V.4.5 (Refactored - sin clase Colors)

# Información de la aplicación
APP_VERSION = "V. 4.5 - Paneles Duales con Redimensión"
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

# NOTA: Colores ahora se obtienen desde theme_manager.py
# La clase Colors fue eliminada para evitar duplicación

class Fonts:
    BUTTONS = ("Segoe UI", 9)
    NORMAL = ("Segoe UI", 9)
    TITLE = ("Segoe UI", 14, "bold")
    VERSION = ("Segoe UI", 8)
    TABLE_HEADER = ("Segoe UI", 10, "bold")

class Messages:
    READY = "F1: Ayuda • F5: Buscar • F6: Copiar • F7: Abrir • Tab: Navegar"
    FOLDER_SELECTED = "Carpeta seleccionada y caché construido"
    CACHE_BUILDING = "Construyendo caché automáticamente..."
    CACHE_COMPLETED = "Caché construido exitosamente"
    NO_FOLDER = "Error: Seleccione una ruta primero"
    NO_CRITERIA = "Error: Ingrese un criterio de búsqueda"
    SEARCH_CANCELLED = "Búsqueda cancelada"
    CACHE_CLEARED = "Caché limpiado"
    NUMERIC_MODE = "[123] Numérico"
    ALPHA_MODE = "[ABC] Alfanumérico"

# Constantes legacy para compatibilidad (valores temporales)
# TODO: Migrar código existente a usar theme_manager
COLORS = {
    'background': "#f6f5f5",
    'dark_gray': "#424242",
    'medium_gray': "#757575",
    'light_gray': "#e0e0e0",
    'very_light_gray': "#f5f5f5",
    'white': "#ffffff",
    'blue_bar': "#1976D2",
    'cache_bar': "#F0F8FF",
    'table_header': "#f8f9fa",
    'table_alt_row': "#f8f9fa"
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