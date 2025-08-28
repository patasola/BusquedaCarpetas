# src/utils.py - Utilidades del sistema V.4.2 (Refactorizado)
import os
import subprocess
import platform
import tkinter as tk

def abrir_carpeta(ruta):
    """Abre una carpeta en el explorador del sistema"""
    try:
        sistema = platform.system()
        
        commands = {
            "Windows": ['explorer', ruta],
            "Darwin": ['open', ruta],
            "Linux": ['xdg-open', ruta]
        }
        
        command = commands.get(sistema)
        if command:
            subprocess.run(command, check=True)
            return True
        
        return False
        
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False

def copiar_portapapeles(texto):
    """Copia texto al portapapeles"""
    try:
        root = tk.Tk()
        root.withdraw()
        
        root.clipboard_clear()
        root.clipboard_append(texto)
        root.update()
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
    
    while tamaño_bytes >= 1024.0 and i < len(unidades) - 1:
        tamaño_bytes /= 1024.0
        i += 1
    
    return f"{tamaño_bytes:.1f} {unidades[i]}"