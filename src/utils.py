# src/utils.py - Utilidades generales
"""
Funciones de utilidad para la aplicación
"""

import os
import subprocess
import platform

def copy_to_clipboard(text):
    """Copia texto al portapapeles"""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        # Fallback para sistemas sin pyperclip
        try:
            if platform.system() == "Windows":
                import subprocess
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, text=True)
                process.communicate(input=text)
                return process.returncode == 0
            else:
                return False
        except Exception:
            return False
    except Exception:
        return False

def open_folder(path):
    """Abre una carpeta en el explorador del sistema"""
    try:
        if not os.path.exists(path):
            return False
        
        system = platform.system()
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux y otros Unix
            subprocess.Popen(["xdg-open", path])
        
        return True
    except Exception:
        return False

def get_folder_name(path):
    """Obtiene el nombre de la carpeta desde una ruta"""
    return os.path.basename(path) if path else ""

def is_valid_path(path):
    """Verifica si una ruta es válida y existe"""
    return path and os.path.exists(path) and os.path.isdir(path)

# Clase FileUtils para mantener compatibilidad si fuera necesaria
class FileUtils:
    @staticmethod
    def copy_to_clipboard(text):
        return copy_to_clipboard(text)

    @staticmethod
    def open_folder(path):
        return open_folder(path)

    @staticmethod
    def get_folder_name(path):
        return get_folder_name(path)

    @staticmethod
    def is_valid_path(path):
        return is_valid_path(path)