"""
Constantes de la aplicación Búsqueda Rápida de Carpetas
"""

# Información de la aplicación
APP_VERSION = "V. 1.4"
APP_TITLE = "Búsqueda Rápida de Carpetas"
WINDOW_SIZE = "750x650"
MIN_WINDOW_SIZE = (650, 550)

# Fuentes
FONT_NORMAL = ("Arial", 10)
FONT_TITLE = ("Arial", 16, "bold")
FONT_BUTTONS = ("Arial", 9)
FONT_VERSION = ("Arial", 8)

# Colores
COLORS = {
    'background': "#f6f5f5",
    'dark_gray': "#424242",
    'medium_gray': "#757575", 
    'light_gray': "#e0e0e0",
    'very_light_gray': "#f5f5f5",
    'white': "#ffffff",
    'blue_bar': "#1976D2"
}

# Configuración de archivos
CONFIG_FILE = "config.json"

# Configuración de interfaz
TREE_HEIGHT = 6
PROGRESS_LENGTH = 400
MAIN_PADDING = {'x': 50, 'y': 20}
ENTRY_WIDTH = 40

# Configuración de procesamiento
CHUNK_SIZE = 100
SEARCH_CHUNK_SIZE = 50
PROGRESS_UPDATE_INTERVAL = 1.0
RESULT_UPDATE_INTERVAL = 5
MICRO_SLEEP = 0.01

# Mensajes de estado
MESSAGES = {
    'ready': "Listo para buscar. Presione F2 para enfocar el campo de búsqueda",
    'folder_selected': "Carpeta seleccionada y caché construido",
    'cache_building': "Construyendo caché automáticamente...",
    'cache_completed': "Caché construido exitosamente",
    'no_folder': "Error: Seleccione una ruta primero",
    'no_criteria': "Error: Ingrese un criterio de búsqueda",
    'search_cancelled': "Búsqueda cancelada",
    'cache_cleared': "Caché limpiado"
}