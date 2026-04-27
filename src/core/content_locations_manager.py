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
                    locs = json.load(f)
                # Normalizar valores None para que se muestren correctamente en UI
                for loc in locs:
                    if not loc.get('last_indexed'):
                        loc['last_indexed'] = 'Nunca'
                    if not loc.get('last_duration'):
                        loc['last_duration'] = '-'
                return locs
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
            'index_content': True,  # V.6.6 - Permite saltar extracción de texto
            'last_indexed': 'Nunca',
            'last_duration': '-'
        })
        self.save()
        return True

    def remove_location(self, path):
        self.locations = [loc for loc in self.locations if loc['path'] != path]
        self.save()

    def get_enabled_locations(self):
        return [loc for loc in self.locations if loc.get('enabled', True)]
