# src/utils.py - Utilidades
"""
Funciones utilitarias para operaciones del sistema
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
                subprocess.run(["clip"], input=text, text=True, check=True)
                return True
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["pbcopy"], input=text, text=True, check=True)
                return True
            else:  # Linux
                subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
                return True
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
        else:  # Linux
            subprocess.Popen(["xdg-open", path])
        
        return True
    except Exception:
        return False