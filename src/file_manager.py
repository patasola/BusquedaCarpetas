# src/file_manager.py - Gestión de Archivos V.4.2 (Refactorizado)
import os
from tkinter import filedialog

class FileManager:
    def __init__(self, config_manager, ui_callbacks):
        self.config = config_manager
        self.ui_callbacks = ui_callbacks
    
    def seleccionar_ruta(self, ruta_actual=None):
        """Selecciona nueva ruta de búsqueda"""
        try:
            ruta = filedialog.askdirectory(
                title="Seleccionar ruta de búsqueda",
                initialdir=ruta_actual or os.path.expanduser("~"),
                mustexist=True
            )
            
            if ruta and self._validar_ruta(ruta):
                ruta_normalizada = os.path.normpath(ruta)
                self.config.guardar_ruta(ruta_normalizada)
                return ruta_normalizada
                
        except Exception as e:
            self.ui_callbacks.mostrar_error(f"Error al abrir diálogo:\n{str(e)}")
        
        return None
    
    def _validar_ruta(self, ruta):
        """Valida que la ruta sea accesible"""
        validaciones = [
            (os.path.exists(ruta), f"La ruta no existe:\n{ruta}"),
            (os.path.isdir(ruta), f"La ruta no es un directorio:\n{ruta}"),
            (os.access(ruta, os.R_OK), f"Sin permisos de lectura en:\n{ruta}")
        ]
        
        for condicion, mensaje in validaciones:
            if not condicion:
                self.ui_callbacks.mostrar_error(mensaje)
                return False
        
        # Test de escritura
        try:
            test_file = os.path.join(ruta, 'temp_test_access.tmp')
            with open(test_file, 'w') as f:
                f.write('test_access')
            os.remove(test_file)
            return True
        except Exception as e:
            self.ui_callbacks.mostrar_error(f"Sin permisos de escritura:\n{ruta}\n\n{str(e)}")
            return False
    
    def abrir_carpeta(self, ruta):
        """Abre carpeta en el explorador del sistema"""
        try:
            from .utils import abrir_carpeta
            return abrir_carpeta(ruta)
        except Exception:
            return False
    
    def copiar_ruta(self, ruta):
        """Copia ruta al portapapeles"""
        try:
            from .utils import copiar_portapapeles
            return copiar_portapapeles(ruta)
        except Exception:
            return False
    
    def verificar_ruta_existe(self, ruta):
        """Verifica que la ruta existe y es directorio"""
        try:
            return os.path.exists(ruta) and os.path.isdir(ruta)
        except:
            return False
    
    def obtener_nombre_carpeta(self, ruta):
        """Obtiene nombre de la carpeta"""
        try:
            return os.path.basename(ruta) if ruta else ""
        except:
            return ""
    
    def obtener_ruta_absoluta(self, ruta_base, ruta_relativa):
        """Construye ruta absoluta"""
        try:
            return os.path.join(ruta_base, ruta_relativa)
        except:
            return ""