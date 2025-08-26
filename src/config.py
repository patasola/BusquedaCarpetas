# src/config.py - Gestor de Configuración V.4.1 (Optimizado)
import os
import json

class ConfigManager:
    """Gestor de configuración de la aplicación"""
    
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "ruta_carpeta": os.path.expanduser("~"),
            "version": "4.1"
        }
        self.config = self.cargar_config()
    
    def cargar_config(self):
        """Carga la configuración desde el archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Asegurar que tiene todas las claves necesarias
                    for key, value in self.default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
        except Exception:
            pass
        
        return self.default_config.copy()
    
    def guardar_config(self):
        """Guarda la configuración al archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def get_ruta_carpeta(self):
        """Obtiene la ruta de la carpeta base"""
        ruta = self.config.get("ruta_carpeta", self.default_config["ruta_carpeta"])
        
        # Verificar que la ruta existe, si no usar el directorio home
        if not os.path.exists(ruta):
            ruta = os.path.expanduser("~")
            self.set_ruta_carpeta(ruta)
        
        return ruta
    
    def set_ruta_carpeta(self, ruta):
        """Establece la ruta de la carpeta base"""
        if os.path.exists(ruta):
            self.config["ruta_carpeta"] = ruta
            self.guardar_config()
            return True
        return False
    
    def cargar_ruta(self):
        """Obtiene la ruta de la carpeta base (alias para compatibilidad)"""
        return self.get_ruta_carpeta()
    
    def guardar_ruta(self, ruta):
        """Establece la ruta de la carpeta base (alias para compatibilidad)"""
        return self.set_ruta_carpeta(ruta)
    
    def get_version(self):
        """Obtiene la versión de la aplicación"""
        return self.config.get("version", self.default_config["version"])