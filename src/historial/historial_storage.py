# src/historial/historial_storage.py - Gestión de persistencia del historial
import json
import os
from datetime import datetime

class HistorialStorage:
    """Maneja carga y guardado del historial en JSON"""
    
    def __init__(self, filename="historial_busquedas.json"):
        self.filename = filename
        self.historial_data = []
    
    def cargar(self):
        """Carga historial desde archivo JSON"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.historial_data = json.load(f)
                print(f"[DEBUG] Historial cargado: {len(self.historial_data)} registros")
                return self.historial_data
            except json.JSONDecodeError:
                print("[ERROR] Error al decodificar JSON del historial")
                self.historial_data = []
                return []
            except Exception as e:
                print(f"[ERROR] Error al cargar historial: {e}")
                self.historial_data = []
                return []
        else:
            print("[DEBUG] No existe archivo de historial, creando nuevo")
            self.historial_data = []
            return []
    
    def guardar(self, data=None):
        """Guarda historial en archivo JSON"""
        if data is not None:
            self.historial_data = data
            
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.historial_data, f, ensure_ascii=False, indent=2)
            print(f"[DEBUG] Historial guardado: {len(self.historial_data)} registros")
            return True
        except Exception as e:
            print(f"[ERROR] Error al guardar historial: {e}")
            return False
    
    def agregar_busqueda(self, criterio, metodo, resultados, tiempo_ms, demandante="", demandado=""):
        """Agrega una nueva búsqueda al historial"""
        registro = {
            "criterio": criterio,
            "metodo": metodo,
            "resultados": resultados,
            "tiempo": tiempo_ms,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "demandante": demandante,
            "demandado": demandado
        }
        
        self.historial_data.insert(0, registro)  # Insertar al inicio
        
        # Limitar a 1000 registros
        if len(self.historial_data) > 1000:
            self.historial_data = self.historial_data[:1000]
        
        self.guardar()
        return registro
    
    def limpiar(self):
        """Limpia todo el historial"""
        self.historial_data = []
        self.guardar()
        print("[INFO] Historial limpiado")
    
    def get_data(self):
        """Retorna los datos del historial"""
        return self.historial_data
