"""
Gestión de configuración para la aplicación Búsqueda Rápida de Carpetas
"""

import json
import os
from constants import CONFIG_FILE

class ConfigManager:
    """Gestiona la configuración de la aplicación"""
    
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config = self._load_config()
    
    def _load_config(self):
        """Carga la configuración desde el archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return {}
    
    def save_config(self):
        """Guarda la configuración al archivo"""
        try:
            with open(self.config_file, "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def get_folder_path(self):
        """Obtiene la ruta de carpeta guardada"""
        return self.config.get("ruta_carpeta", "")
    
    def set_folder_path(self, path):
        """Establece la ruta de carpeta"""
        self.config["ruta_carpeta"] = path
        self.save_config()
    
    def get_window_geometry(self):
        """Obtiene la geometría de ventana guardada"""
        return self.config.get("window_geometry")
    
    def set_window_geometry(self, geometry):
        """Establece la geometría de ventana"""
        self.config["window_geometry"] = geometry
        self.save_config()