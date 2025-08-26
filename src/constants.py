# src/constants.py - Constantes V.3.7
APP_VERSION = "V. 3.7 - Estable (Inferno)"
APP_TITLE = "Búsqueda Rápida de Carpetas"
WINDOW_SIZE = "660x480"
MIN_WINDOW_SIZE = (650, 470)

CONFIG_FILE = "config.json"

TREE_HEIGHT = 5  # Aumentado para mejor visualización
PROGRESS_LENGTH = 350
MAIN_PADDING = {'x': 30, 'y': 15}
ENTRY_WIDTH = 35

CHUNK_SIZE = 100
SEARCH_CHUNK_SIZE = 50
PROGRESS_UPDATE_INTERVAL = 1.0
RESULT_UPDATE_INTERVAL = 5
MICRO_SLEEP = 0.01

COLORS = {
    'background': "#f6f5f5",
    'dark_gray': "#424242",
    'medium_gray': "#757575", 
    'light_gray': "#e0e0e0",
    'very_light_gray': "#f5f5f5",
    'white': "#ffffff",
    'blue_bar': "#1976D2",
    'cache_bar': "#F0F8FF",  # Azul Alice Blue para barra de caché
    'table_header': "#f8f9fa",  # Gris claro para encabezados
    'table_alt_row': "#f8f9fa"  # Filas alternadas
}

class Colors:
    BACKGROUND = "#f6f5f5"
    TITLE_FG = "#424242"
    INFO_FG = "#424242"
    TREE_FG = "#424242"
    BUTTON_BG = "#e0e0e0"
    BUTTON_FG = "#424242"
    DARK_GRAY = "#424242"
    MEDIUM_GRAY = "#757575"
    LIGHT_GRAY = "#e0e0e0"
    VERY_LIGHT_GRAY = "#f5f5f5"
    WHITE = "#ffffff"
    BLUE_BAR = "#1976D2"
    CACHE_BAR_BG = "#F0F8FF"  # Azul muy claro
    STATUS_BAR_BG = "SystemButtonFace"

class Fonts:
    BUTTONS = ("Segoe UI", 9)
    NORMAL = ("Segoe UI", 9)
    TITLE = ("Segoe UI", 14, "bold")
    VERSION = ("Segoe UI", 8)
    TABLE_HEADER = ("Segoe UI", 10, "bold")  # Nueva fuente para encabezados de tabla

FONT_NORMAL = ("Segoe UI", 9)
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_BUTTONS = ("Segoe UI", 9)
FONT_VERSION = ("Segoe UI", 8)
FONT_TABLE_HEADER = ("Segoe UI", 10, "bold")

MESSAGES = {
    'ready': "Listo para buscar. Presione F2 para enfocar búsqueda (selecciona todo) • F5 para cambiar modo",
    'folder_selected': "Carpeta seleccionada y caché construido",
    'cache_building': "Construyendo caché automáticamente...",
    'cache_completed': "Caché construido exitosamente",
    'no_folder': "Error: Seleccione una ruta primero",
    'no_criteria': "Error: Ingrese un criterio de búsqueda",
    'search_cancelled': "Búsqueda cancelada",
    'cache_cleared': "Caché limpiado",
    'numeric_mode': "[123] Numérico",
    'alpha_mode': "[ABC] Alfanumérico"
}