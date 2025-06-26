"""
Utilidades para manejo de archivos y carpetas
"""

import os
import subprocess
import platform
import pyperclip

class FileUtils:
    """Utilidades para operaciones con archivos y carpetas"""
    
    @staticmethod
    def copy_to_clipboard(text):
        """Copia texto al portapapeles"""
        try:
            pyperclip.copy(text)
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def open_folder(path):
        """Abre una carpeta en el explorador del sistema"""
        try:
            if not os.path.exists(path):
                return False, "La ruta no existe"
            
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":  # macOS
                subprocess.Popen(["open", path])
            else:  # Linux y otros Unix
                subprocess.Popen(["xdg-open", path])
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_folder_name(path):
        """Obtiene el nombre de la carpeta desde una ruta"""
        return os.path.basename(path) if path else ""
    
    @staticmethod
    def is_valid_path(path):
        """Verifica si una ruta es válida y existe"""
        return path and os.path.exists(path) and os.path.isdir(path)
    
    @staticmethod
    def get_relative_path(full_path, base_path):
        """Obtiene la ruta relativa desde una ruta base"""
        try:
            return os.path.relpath(full_path, base_path)
        except ValueError:
            return full_path
    
    @staticmethod
    def format_file_size(size_bytes):
        """Formatea el tamaño de archivo en formato legible"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def get_directory_stats(path):
        """Obtiene estadísticas de un directorio"""
        if not FileUtils.is_valid_path(path):
            return None
        
        try:
            total_dirs = 0
            total_files = 0
            total_size = 0
            
            for root, dirs, files in os.walk(path):
                total_dirs += len(dirs)
                total_files += len(files)
                
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        continue  # Ignorar archivos inaccesibles
            
            return {
                'directories': total_dirs,
                'files': total_files,
                'size': total_size,
                'size_formatted': FileUtils.format_file_size(total_size)
            }
        except Exception:
            return None