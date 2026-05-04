# src/config.py - Gestor de Configuración V.4.2 (Refactorizado)
import os
import json

class ConfigManager:
    """Gestor de configuración de la aplicación"""
    
    def __init__(self):
        # Guardar configuración en AppData para persistencia entre versiones del EXE
        app_data = os.environ.get('LOCALAPPDATA', os.environ.get('APPDATA', os.path.expanduser("~")))
        config_dir = os.path.join(app_data, "BusquedaCarpetas")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
            
        self.config_file = os.path.join(config_dir, "config.json")
        self.default_config = {
            "ruta_carpeta": os.path.expanduser("~"),
            "version": "7.3",
            "theme": "claro",
            "window_geometry": "990x700+100+100",
            "show_history": False,
            "show_explorer": False,
            "manual_app_width": None,
            "explorer_width": 350,
            "history_width": 300,
            # Column Widths (Estructura unificada V.5.0)
            "main_column_widths": {
                "visible_columns": ["#0", "Método", "Ruta"],
                "widths": {"#0": 200, "Método": 35, "Ruta": 300}
            },
            "explorer_column_widths": {
                "visible_columns": ["#0", "Fecha"],
                "widths": {"#0": 250, "Fecha": 120}
            },
            "history_column_widths": {
                "visible_columns": ["Criterio", "Metodo", "Resultados", "Tiempo", "Fecha"],
                "widths": {"Criterio": 120, "Metodo": 40, "Resultados": 60, "Tiempo": 60, "Fecha": 60}
            }
        }
        self.config = self._load_config()
    
    def get(self, key, default=None):
        """Obtiene un valor de configuración"""
        return self.config.get(key, default if default is not None else self.default_config.get(key))

    def set(self, key, value):
        """Establece un valor de configuración"""
        self.config[key] = value
        self._save_config()

    def _load_config(self):
        """Carga configuración con fallback a defaults"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge con defaults para claves faltantes
                    return {**self.default_config, **config}
        except Exception:
            pass
        
        return self.default_config.copy()
    
    def _save_config(self):
        """Guarda configuración a archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def cargar_ruta(self):
        """Obtiene ruta válida de carpeta base"""
        ruta = self.config.get("ruta_carpeta", self.default_config["ruta_carpeta"])
        
        # Validar existencia, usar home si no existe
        if not os.path.exists(ruta):
            ruta = os.path.expanduser("~")
            self.guardar_ruta(ruta)
        
        return ruta
    
    def guardar_ruta(self, ruta):
        """Guarda ruta si es válida"""
        if os.path.exists(ruta):
            self.config["ruta_carpeta"] = ruta
            self._save_config()
            return True
        return False
    
    # Métodos de compatibilidad
    def cargar_config(self):
        return self._load_config()
    
    def guardar_config(self):
        self._save_config()
    
    def get_ruta_carpeta(self):
        return self.cargar_ruta()
    
    def set_ruta_carpeta(self, ruta):
        return self.guardar_ruta(ruta)
    
    def get_version(self):
        return self.config.get("version", self.default_config["version"])