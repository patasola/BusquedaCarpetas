# src/window_manager.py - Gestión de Ventana V.4.5 - Con redimensionamiento adaptativo
from .ui_components import Colors

class WindowManager:
    """Maneja configuración y propiedades de la ventana con redimensionamiento inteligente"""
    
    def __init__(self, master, version):
        self.master = master
        self.version = version
        
        # Dimensiones de pantalla
        self.screen_width = None
        self.screen_height = None
        self.pixels_per_cm = None
        self.panel_width = None
        
        # Control de redimensionamiento
        self.current_panel_count = 0
        self.base_app_width = 900  # Ancho inicial de la app
        self.user_resized_manually = False
        self.manual_app_width = None
    
    def configurar_ventana(self):
        """Configura las propiedades básicas de la ventana"""
        self.master.title(f"Búsqueda de Carpetas v{self.version}")
        self.master.configure(bg=Colors.BACKGROUND)
        self.master.resizable(True, True)
        
        # Calcular dimensiones
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.pixels_per_cm = self.screen_width / 33.3
        
        # Ancho de cada panel (8cm)
        panel_width_cm = 6.5  # Cambiado de 8 a 6.5cm (~500px en lugar de 615px)
        self.panel_width = int(panel_width_cm * self.pixels_per_cm)
        
        # Tamaño inicial
        initial_height = 700
        x = max(0, (self.screen_width - self.base_app_width) // 2)
        y = max(0, (self.screen_height - initial_height) // 2)
        
        self.master.geometry(f"{self.base_app_width}x{initial_height}+{x}+{y}")
        self.master.minsize(400, 300)
        
        # Detectar redimensionamiento manual
        self.master.bind('<Configure>', self._on_window_resize)
        
        print(f"[DEBUG] Ventana configurada:")
        print(f"  - Tamaño inicial: {self.base_app_width}x{initial_height}")
        print(f"  - Panel width: {self.panel_width}px ({panel_width_cm}cm)")
        print(f"  - Pantalla: {self.screen_width}x{self.screen_height}")
        
        self.master.update_idletasks()
    
    def _on_window_resize(self, event):
        """Detecta cuando el usuario redimensiona manualmente"""
        # Solo procesar eventos de la ventana principal
        if event.widget != self.master:
            return
        
        # Calcular ancho esperado automático
        expected_width = self._calculate_expected_width()
        current_width = self.master.winfo_width()
        
        # Si difiere significativamente, el usuario está redimensionando
        if abs(current_width - expected_width) > 30:
            self.user_resized_manually = True
            self.manual_app_width = current_width - (self.current_panel_count * self.panel_width)
            print(f"[DEBUG] Redimensionamiento manual detectado: {current_width}px")
    
    def _calculate_expected_width(self):
        """Calcula el ancho esperado según paneles activos"""
        if self.manual_app_width:
            app_width = self.manual_app_width
        else:
            app_width = self.base_app_width
        
        return app_width + (self.current_panel_count * self.panel_width)
    
    def add_panel(self):
        """Agrega un panel con redimensionamiento inteligente"""
        self.current_panel_count += 1
        self._smart_resize()
        print(f"[DEBUG] Panel agregado. Total: {self.current_panel_count}")
    
    
    def update_panel_count(self, count):
        """Actualiza el contador de paneles"""
        if count != self.current_panel_count:
            diff = count - self.current_panel_count
            self.current_panel_count = count
            
            if diff > 0:
                self._smart_resize()
            elif diff < 0:
                self._smart_resize()
    
    def get_current_panel_count(self):
        """Obtiene la cantidad actual de paneles"""
        return self.current_panel_count
    
    def get_panel_width(self):
        """Obtiene el ancho calculado para paneles laterales"""
        return self.panel_width if self.panel_width else 300
    
    def reset_manual_resize(self):
        """Resetea el estado de redimensionamiento manual"""
        self.user_resized_manually = False
        self.manual_app_width = None
        print("[DEBUG] Estado de resize manual reseteado")
    
    def centrar_ventana(self):
        """Centra la ventana manteniendo su tamaño actual"""
        try:
            self.master.update_idletasks()
            window_width = self.master.winfo_width()
            window_height = self.master.winfo_height()
            
            x = max(0, (self.screen_width - window_width) // 2)
            y = max(0, (self.screen_height - window_height) // 2)
            
            self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
            print(f"[DEBUG] Ventana centrada")
        except Exception as e:
            print(f"[ERROR] Error centrando: {e}")
    
    def get_screen_info(self):
        """Obtiene información de la pantalla"""
        return {
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'window_width': self.master.winfo_width(),
            'window_height': self.master.winfo_height(),
            'panel_width': self.panel_width,
            'current_panel_count': self.current_panel_count,
            'base_app_width': self.base_app_width,
            'user_resized': self.user_resized_manually
        }