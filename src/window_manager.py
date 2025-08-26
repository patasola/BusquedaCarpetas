# src/window_manager.py - Gestión de Ventana V.4.1 (Centrado Corregido)
from .ui_components import Colors

class WindowManager:
    """Maneja configuración y propiedades de la ventana principal"""
    
    def __init__(self, master, version):
        self.master = master
        self.version = version
    
    def configurar_ventana(self):
        """Configura las propiedades básicas de la ventana"""
        # Configurar título y fondo
        self.master.title(f"Búsqueda de Carpetas v{self.version}")
        self.master.configure(bg=Colors.BACKGROUND)
        self.master.resizable(True, True)
        
        # Configurar tamaño inicial
        window_width = 1200
        window_height = 700
        
        # Obtener dimensiones de la pantalla
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        # Calcular posición centrada
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Aplicar geometría con posición centrada
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configurar tamaño mínimo
        self.master.minsize(800, 500)
        
        # Forzar actualización para asegurar centrado
        self.master.update_idletasks()
        
        # Opcional: Centrar nuevamente después de que se carguen todos los componentes
        self.master.after(100, self._recentrar_si_necesario)
    
    def _recentrar_si_necesario(self):
        """Re-centra la ventana si no está en la posición correcta"""
        try:
            # Obtener posición actual
            self.master.update_idletasks()
            
            current_x = self.master.winfo_x()
            current_y = self.master.winfo_y()
            current_width = self.master.winfo_width()
            current_height = self.master.winfo_height()
            
            # Obtener dimensiones de pantalla
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            
            # Calcular posición ideal centrada
            ideal_x = (screen_width - current_width) // 2
            ideal_y = (screen_height - current_height) // 2
            
            # Si la ventana no está cerca del centro, recentrarla
            if abs(current_x - ideal_x) > 100 or abs(current_y - ideal_y) > 100:
                self.master.geometry(f"{current_width}x{current_height}+{ideal_x}+{ideal_y}")
                
        except Exception as e:
            # Si hay algún error, ignorar silenciosamente
            pass
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla (método público)"""
        try:
            self.master.update_idletasks()
            
            # Obtener dimensiones actuales de la ventana
            window_width = self.master.winfo_width()
            window_height = self.master.winfo_height()
            
            # Obtener dimensiones de la pantalla
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            
            # Calcular posición centrada
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Asegurar que no quede fuera de la pantalla
            x = max(0, min(x, screen_width - window_width))
            y = max(0, min(y, screen_height - window_height))
            
            # Aplicar nueva posición
            self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        except Exception as e:
            # Si hay error, usar posición por defecto
            self.master.geometry("1200x700+100+100")
    
    def maximizar_ventana(self):
        """Maximiza la ventana"""
        try:
            self.master.state('zoomed')  # Windows
        except:
            try:
                self.master.attributes('-zoomed', True)  # Linux
            except:
                # Fallback: simular maximizado
                screen_width = self.master.winfo_screenwidth()
                screen_height = self.master.winfo_screenheight()
                self.master.geometry(f"{screen_width-100}x{screen_height-100}+50+25")
    
    def restaurar_ventana(self):
        """Restaura la ventana al tamaño normal"""
        try:
            self.master.state('normal')
            self.centrar_ventana()
        except:
            self.master.geometry("1200x700")
            self.centrar_ventana()
    
    def get_screen_info(self):
        """Obtiene información de la pantalla"""
        return {
            'screen_width': self.master.winfo_screenwidth(),
            'screen_height': self.master.winfo_screenheight(),
            'window_width': self.master.winfo_width(),
            'window_height': self.master.winfo_height(),
            'window_x': self.master.winfo_x(),
            'window_y': self.master.winfo_y()
        }