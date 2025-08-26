# src/utils.py - Utilidades del sistema V.4.1
import os
import subprocess
import platform
import tkinter as tk

def abrir_carpeta(ruta):
    """Abre una carpeta en el explorador del sistema"""
    try:
        sistema = platform.system()
        
        if sistema == "Windows":
            # Windows - usar explorer
            subprocess.run(['explorer', ruta], check=True)
        elif sistema == "Darwin":
            # macOS - usar open
            subprocess.run(['open', ruta], check=True)
        elif sistema == "Linux":
            # Linux - usar xdg-open
            subprocess.run(['xdg-open', ruta], check=True)
        else:
            # Sistema no soportado
            return False
            
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False

def copiar_portapapeles(texto):
    """Copia texto al portapapeles"""
    try:
        # Crear ventana temporal invisible para acceder al portapapeles
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana
        
        # Limpiar portapapeles y copiar texto
        root.clipboard_clear()
        root.clipboard_append(texto)
        
        # Asegurar que el texto se mantenga en el portapapeles
        root.update()
        
        # Destruir ventana temporal
        root.destroy()
        
        return True
        
    except Exception:
        return False

def validar_ruta_existe(ruta):
    """Valida que una ruta existe y es accesible"""
    try:
        return os.path.exists(ruta) and os.path.isdir(ruta)
    except:
        return False

def obtener_info_sistema():
    """Obtiene información básica del sistema"""
    return {
        'sistema': platform.system(),
        'version': platform.version(),
        'arquitectura': platform.architecture()[0],
        'python_version': platform.python_version()
    }

def normalizar_ruta(ruta):
    """Normaliza una ruta del sistema"""
    try:
        return os.path.normpath(os.path.abspath(ruta))
    except:
        return ruta

def formatear_tamaño_archivo(tamaño_bytes):
    """Formatea un tamaño en bytes a formato legible"""
    if tamaño_bytes == 0:
        return "0 B"
    
    unidades = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    
    while tamaño_bytes >= 1024 and i < len(unidades) - 1:
        tamaño_bytes /= 1024.0
        i += 1
    
    return f"{tamaño_bytes:.1f} {unidades[i]}"