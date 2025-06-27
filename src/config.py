# src/config.py - Gestor de Configuración
"""
Maneja la configuración persistente de la aplicación
"""

import json
import os

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.config_data = {}
        self.cargar_configuracion()

    def cargar_configuracion(self):
        """Carga la configuración desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            self.config_data = {}

    def guardar_configuracion(self):
        """Guarda la configuración a archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def cargar_ruta(self):
        """Carga la ruta guardada"""
        return self.config_data.get('ruta_carpeta', '')

    def guardar_ruta(self, ruta):
        """Guarda la ruta seleccionada"""
        self.config_data['ruta_carpeta'] = ruta
        self.guardar_configuracion()

    def cargar_geometria_ventana(self):
        """Carga la geometría de ventana guardada"""
        return self.config_data.get('geometria_ventana', '')

    def guardar_geometria_ventana(self, geometria):
        """Guarda la geometría de ventana"""
        self.config_data['geometria_ventana'] = geometria
        self.guardar_configuracion()