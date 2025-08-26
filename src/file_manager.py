# src/file_manager.py - Gestión de Archivos V.3.6
import os
from tkinter import filedialog

class FileManager:
    def __init__(self, config_manager, ui_callbacks):
        self.config = config_manager
        self.ui_callbacks = ui_callbacks
    
    def seleccionar_ruta(self, ruta_actual=None):
        try:
            ruta = filedialog.askdirectory(
                title="Seleccionar ruta de búsqueda",
                initialdir=ruta_actual if ruta_actual else os.path.expanduser("~"),
                mustexist=True
            )
            
            if ruta:
                if self._validar_ruta(ruta):
                    ruta_normalizada = os.path.normpath(ruta)
                    self.config.guardar_ruta(ruta_normalizada)
                    return ruta_normalizada
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            self.ui_callbacks.mostrar_error(f"Error al abrir diálogo de selección:\n{str(e)}")
            return None
    
    def _validar_ruta(self, ruta):
        try:
            if not os.path.exists(ruta):
                self.ui_callbacks.mostrar_error(f"La ruta no existe:\n{ruta}")
                return False
            
            if not os.path.isdir(ruta):
                self.ui_callbacks.mostrar_error(f"La ruta no es un directorio:\n{ruta}")
                return False
            
            if not os.access(ruta, os.R_OK):
                self.ui_callbacks.mostrar_error(f"Sin permisos de lectura en:\n{ruta}")
                return False
            
            test_file = os.path.join(ruta, 'temp_test_access.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test_access')
                os.remove(test_file)
            except Exception as e:
                self.ui_callbacks.mostrar_error(
                    f"Sin permisos de escritura en:\n{ruta}\n\nDetalle: {str(e)}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.ui_callbacks.mostrar_error(f"Error al validar la ruta:\n{str(e)}")
            return False
    
    def abrir_carpeta(self, ruta):
        try:
            from .utils import abrir_carpeta
            return abrir_carpeta(ruta)
            
        except Exception as e:
            return False
    
    def copiar_ruta(self, ruta):
        try:
            from .utils import copiar_portapapeles
            return copiar_portapapeles(ruta)
            
        except Exception as e:
            return False
    
    def verificar_ruta_existe(self, ruta):
        try:
            return os.path.exists(ruta) and os.path.isdir(ruta)
        except:
            return False
    
    def obtener_nombre_carpeta(self, ruta):
        try:
            return os.path.basename(ruta) if ruta else ""
        except:
            return ""
    
    def obtener_ruta_absoluta(self, ruta_base, ruta_relativa):
        try:
            return os.path.join(ruta_base, ruta_relativa)
        except:
            return ""