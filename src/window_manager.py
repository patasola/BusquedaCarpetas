# src/window_manager.py - Gestión de Ventana V.4.2 (Refactorizado)
from .ui_components import Colors

class WindowManager:
    """Maneja configuración y propiedades de la ventana principal"""
    
    def __init__(self, master, version):
        self.master = master
        self.version = version
    
    def configurar_ventana(self):
        """Configura las propiedades básicas de la ventana"""
        self.master.title(f"Búsqueda de Carpetas v{self.version}")
        self.master.configure(bg=Colors.BACKGROUND)
        self.master.resizable(True, True)
        
        # Configurar tamaño y posición inicial
        window_width, window_height = 1200, 700
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.master.minsize(800, 500)
        self.master.update_idletasks()
        
        # Re-centrar después de cargar componentes
        self.master.after(100, self._recentrar_si_necesario)
    
    def _recentrar_si_necesario(self):
        """Re-centra la ventana si no está en la posición correcta"""
        try:
            self.master.update_idletasks()
            
            current_x = self.master.winfo_x()
            current_y = self.master.winfo_y()
            current_width = self.master.winfo_width()
            current_height = self.master.winfo_height()
            
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            
            ideal_x = (screen_width - current_width) // 2
            ideal_y = (screen_height - current_height) // 2
            
            if abs(current_x - ideal_x) > 100 or abs(current_y - ideal_y) > 100:
                self.master.geometry(f"{current_width}x{current_height}+{ideal_x}+{ideal_y}")
                
        except Exception:
            pass
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        try:
            self.master.update_idletasks()
            
            window_width = self.master.winfo_width()
            window_height = self.master.winfo_height()
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            
            x = max(0, min((screen_width - window_width) // 2, screen_width - window_width))
            y = max(0, min((screen_height - window_height) // 2, screen_height - window_height))
            
            self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
        except Exception:
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