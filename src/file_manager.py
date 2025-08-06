import os
from tkinter import filedialog, messagebox

class FileManager:
    """
    Gestiona todas las operaciones relacionadas con archivos y rutas.
    Responsabilidades:
    - Selección de rutas de búsqueda
    - Validación de acceso a directorios
    - Apertura de carpetas en el explorador
    - Copia de rutas al portapapeles
    """
    
    def __init__(self, config_manager, ui_callbacks):
        self.config = config_manager
        self.ui_callbacks = ui_callbacks
        print("DEBUG: FileManager inicializado")
    
    def seleccionar_ruta(self, ruta_actual=None):
        """
        Permite al usuario seleccionar una nueva ruta de búsqueda
        
        Args:
            ruta_actual (str): Ruta actual para usar como directorio inicial
            
        Returns:
            str: Nueva ruta seleccionada y validada, o None si no se seleccionó/validó
        """
        print(f"DEBUG: Abriendo diálogo de selección de ruta. Actual: {ruta_actual}")
        
        try:
            ruta = filedialog.askdirectory(
                title="Seleccionar ruta de búsqueda",
                initialdir=ruta_actual if ruta_actual else os.path.expanduser("~"),
                mustexist=True
            )
            
            if ruta:
                print(f"DEBUG: Usuario seleccionó: {ruta}")
                
                if self._validar_ruta(ruta):
                    ruta_normalizada = os.path.normpath(ruta)
                    self.config.guardar_ruta(ruta_normalizada)
                    print(f"DEBUG: Ruta validada y guardada: {ruta_normalizada}")
                    return ruta_normalizada
                else:
                    print("DEBUG: Ruta no válida")
                    return None
            else:
                print("DEBUG: Usuario canceló selección")
                return None
                
        except Exception as e:
            print(f"ERROR seleccionando ruta: {e}")
            self.ui_callbacks.mostrar_error(f"Error al abrir diálogo de selección:\n{str(e)}")
            return None
    
    def _validar_ruta(self, ruta):
        """
        Valida que se pueda acceder y escribir en la ruta seleccionada
        
        Args:
            ruta (str): Ruta a validar
            
        Returns:
            bool: True si la ruta es válida y accesible
        """
        print(f"DEBUG: Validando ruta: {ruta}")
        
        try:
            # Verificar que existe
            if not os.path.exists(ruta):
                self.ui_callbacks.mostrar_error(f"La ruta no existe:\n{ruta}")
                return False
            
            # Verificar que es un directorio
            if not os.path.isdir(ruta):
                self.ui_callbacks.mostrar_error(f"La ruta no es un directorio:\n{ruta}")
                return False
            
            # Verificar permisos de lectura
            if not os.access(ruta, os.R_OK):
                self.ui_callbacks.mostrar_error(f"Sin permisos de lectura en:\n{ruta}")
                return False
            
            # Probar escritura temporal para verificar acceso completo
            test_file = os.path.join(ruta, 'temp_test_access.tmp')
            try:
                with open(test_file, 'w') as f:
                    f.write('test_access')
                os.remove(test_file)
                print("DEBUG: Prueba de escritura exitosa")
            except Exception as e:
                print(f"DEBUG: Error en prueba de escritura: {e}")
                self.ui_callbacks.mostrar_error(
                    f"Sin permisos de escritura en:\n{ruta}\n\nDetalle: {str(e)}"
                )
                return False
            
            print("DEBUG: Ruta validada exitosamente")
            return True
            
        except Exception as e:
            print(f"ERROR validando ruta: {e}")
            self.ui_callbacks.mostrar_error(f"Error al validar la ruta:\n{str(e)}")
            return False
    
    def abrir_carpeta(self, ruta):
        """
        Abre una carpeta en el explorador del sistema operativo
        
        Args:
            ruta (str): Ruta de la carpeta a abrir
            
        Returns:
            bool: True si se abrió exitosamente
        """
        print(f"DEBUG: Intentando abrir carpeta: {ruta}")
        
        try:
            from .utils import abrir_carpeta
            resultado = abrir_carpeta(ruta)
            
            if resultado:
                print("DEBUG: Carpeta abierta exitosamente")
            else:
                print("DEBUG: Error abriendo carpeta")
                
            return resultado
            
        except Exception as e:
            print(f"ERROR abriendo carpeta: {e}")
            return False
    
    def copiar_ruta(self, ruta):
        """
        Copia una ruta al portapapeles del sistema
        
        Args:
            ruta (str): Ruta a copiar
            
        Returns:
            bool: True si se copió exitosamente
        """
        print(f"DEBUG: Intentando copiar ruta: {ruta}")
        
        try:
            from .utils import copiar_portapapeles
            resultado = copiar_portapapeles(ruta)
            
            if resultado:
                print("DEBUG: Ruta copiada exitosamente")
            else:
                print("DEBUG: Error copiando ruta")
                
            return resultado
            
        except Exception as e:
            print(f"ERROR copiando ruta: {e}")
            return False
    
    def verificar_ruta_existe(self, ruta):
        """
        Verifica si una ruta existe sin mostrar errores
        
        Args:
            ruta (str): Ruta a verificar
            
        Returns:
            bool: True si la ruta existe
        """
        try:
            return os.path.exists(ruta) and os.path.isdir(ruta)
        except:
            return False
    
    def obtener_nombre_carpeta(self, ruta):
        """
        Obtiene el nombre de la carpeta de una ruta
        
        Args:
            ruta (str): Ruta completa
            
        Returns:
            str: Nombre de la carpeta
        """
        try:
            return os.path.basename(ruta) if ruta else ""
        except:
            return ""
    
    def obtener_ruta_absoluta(self, ruta_base, ruta_relativa):
        """
        Combina una ruta base con una ruta relativa
        
        Args:
            ruta_base (str): Ruta base
            ruta_relativa (str): Ruta relativa
            
        Returns:
            str: Ruta absoluta combinada
        """
        try:
            return os.path.join(ruta_base, ruta_relativa)
        except:
            return ""