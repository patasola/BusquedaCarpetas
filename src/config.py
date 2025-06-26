# src/config.py - Gestor de Configuración
"""
Maneja la configuración persistente de la aplicación
"""

import json
import os

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.config = {}
        self.cargar_config()

    def cargar_config(self):
        """Carga la configuración desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            self.config = {}

    def guardar_config(self):
        """Guarda la configuración a archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def cargar_ruta(self):
        """Carga la ruta de carpeta guardada"""
        return self.config.get('ruta_carpeta', '')

    def guardar_ruta(self, ruta):
        """Guarda la ruta de carpeta"""
        self.config['ruta_carpeta'] = ruta
        self.guardar_config()