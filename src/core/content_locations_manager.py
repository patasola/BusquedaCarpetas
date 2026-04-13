# src/core/content_locations_manager.py
import json
import os

class ContentLocationsManager:
    """Gestiona la persistencia de carpetas configuradas para búsqueda de contenido"""
    
    def __init__(self, config_path="content_locations.json"):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config_path)
        self.locations = self._load()

    def _load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.locations, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CONTENT] Error guardando config: {e}")

    def add_location(self, path, name):
        # Evitar duplicados
        if any(loc['path'] == path for loc in self.locations):
            return False
        
        self.locations.append({
            'path': path,
            'name': name,
            'enabled': True,
            'last_indexed': None
        })
        self.save()
        return True

    def remove_location(self, path):
        self.locations = [loc for loc in self.locations if loc['path'] != path]
        self.save()

    def get_enabled_locations(self):
        return [loc for loc in self.locations if loc.get('enabled', True)]
