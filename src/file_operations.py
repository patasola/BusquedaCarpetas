# src/file_operations.py
import os
import platform
import subprocess
from datetime import datetime
from tkinter import messagebox

class FileOperations:
    """Maneja operaciones con archivos y directorios"""
    
    def __init__(self, explorer_manager):
        self.explorer_manager = explorer_manager
    
    def get_directory_contents(self, directory_path):
        """Obtiene el contenido de un directorio ordenado"""
        try:
            items = []
            for entry in os.scandir(directory_path):
                try:
                    nombre = entry.name
                    es_dir = entry.is_dir()
                    
                    try:
                        fecha_mod = datetime.fromtimestamp(
                            entry.stat().st_mtime
                        ).strftime("%d/%m/%Y %H:%M")
                    except:
                        fecha_mod = "N/A"
                    
                    full_path = entry.path
                    items.append((nombre, es_dir, fecha_mod, full_path))
                    
                except PermissionError:
                    continue
                except Exception as e:
                    print(f"Error procesando {entry.name}: {e}")
                    continue
            
            # Ordenar: carpetas primero, luego archivos, alfabéticamente
            items.sort(key=lambda x: (not x[1], x[0].lower()))
            return items
            
        except PermissionError:
            print(f"Permiso denegado: {directory_path}")
            return None
        except Exception as e:
            print(f"Error listando directorio: {e}")
            return None
    
    def has_subdirectories(self, directory_path):
        """Verifica si un directorio tiene subdirectorios"""
        try:
            for entry in os.scandir(directory_path):
                if entry.is_dir():
                    return True
            return False
        except PermissionError:
            return False
        except Exception:
            return False
    
    def rename_item(self, old_path, new_name):
        """Renombra un archivo o carpeta"""
        try:
            # Validar nombre
            caracteres_invalidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            if any(char in new_name for char in caracteres_invalidos):
                messagebox.showwarning(
                    "Nombre inválido",
                    f"El nombre no puede contener: {' '.join(caracteres_invalidos)}"
                )
                return False
            
            old_dir = os.path.dirname(old_path)
            new_path = os.path.join(old_dir, new_name)
            
            if os.path.exists(new_path):
                messagebox.showwarning(
                    "Nombre duplicado",
                    f"Ya existe un elemento con el nombre:\n{new_name}"
                )
                return False
            
            os.rename(old_path, new_path)
            return True
            
        except PermissionError:
            messagebox.showerror(
                "Error de permisos",
                "No tiene permisos para renombrar este elemento"
            )
            return False
        except Exception as e:
            messagebox.showerror(
                "Error al renombrar",
                f"No se pudo renombrar:\n{str(e)}"
            )
            return False
    
    def open_item(self, path):
        """Abre un archivo o carpeta con la aplicación predeterminada"""
        try:
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', path])
            else:  # Linux y otros
                subprocess.run(['xdg-open', path])
            
            if hasattr(self.explorer_manager.app, 'label_estado'):
                nombre = os.path.basename(path)
                self.explorer_manager.app.label_estado.config(
                    text=f"Abriendo: {nombre}"
                )
                
        except Exception as e:
            messagebox.showerror(
                "Error al abrir",
                f"No se pudo abrir el elemento:\n{str(e)}"
            )
    
    def delete_item(self, path):
        """Elimina un archivo o carpeta (intenta usar papelera)"""
        try:
            # Verificar permisos
            if not os.access(path, os.W_OK):
                messagebox.showerror(
                    "Error de permisos",
                    "No tiene permisos para eliminar este elemento"
                )
                return False
            
            # Intentar usar papelera de reciclaje primero (más seguro)
            try:
                import send2trash
                send2trash.send2trash(path)
                print(f"[DEBUG] Enviado a papelera: {path}")
                return True
            except ImportError:
                # Si send2trash no está instalado, eliminar permanentemente
                print("[WARNING] send2trash no disponible, eliminación permanente")
                response = messagebox.askyesno(
                    "Eliminación permanente",
                    "La biblioteca 'send2trash' no está instalada.\n\n"
                    "El elemento será ELIMINADO PERMANENTEMENTE.\n\n"
                    "¿Deseas continuar?",
                    icon='warning'
                )
                
                if not response:
                    return False
                
                # Eliminar permanentemente
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                
                print(f"[DEBUG] Eliminado permanentemente: {path}")
                return True
                
        except PermissionError:
            messagebox.showerror(
                "Error de permisos",
                "No tiene permisos para eliminar este elemento"
            )
            return False
        except OSError as e:
            messagebox.showerror(
                "Error al eliminar",
                f"No se pudo eliminar el elemento:\n{str(e)}"
            )
            return False
        except Exception as e:
            messagebox.showerror(
                "Error inesperado",
                f"Error al eliminar:\n{str(e)}"
            )
            return False