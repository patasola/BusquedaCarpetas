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
    
    def remove_panel(self):
        """Remueve un panel con redimensionamiento inteligente"""
        self.current_panel_count = max(0, self.current_panel_count - 1)
        self._smart_resize()
        print(f"[DEBUG] Panel removido. Total: {self.current_panel_count}")
    
    def _smart_resize(self):
        """Redimensionamiento inteligente: mezcla de encoger app + crecer ventana"""
        try:
            # Obtener dimensiones actuales
            current_total_width = self.master.winfo_width()
            current_app_width = current_total_width - ((self.current_panel_count - 1) * self.panel_width)
            
            # Calcular ancho necesario para todos los paneles
            panels_width = self.current_panel_count * self.panel_width
            
            # ESTRATEGIA MIXTA:
            # 1. Calcular ancho ideal (sin restricciones)
            if self.manual_app_width:
                ideal_app_width = self.manual_app_width
            else:
                ideal_app_width = self.base_app_width
            
            ideal_total_width = ideal_app_width + panels_width
            
            # 2. Verificar si cabe en pantalla (dejar margen de 50px)
            max_available_width = self.screen_width - 50
            
            if ideal_total_width > max_available_width:
                # NO CABE: Aplicar estrategia mixta
                available_for_app = max_available_width - panels_width
                
                # La app se encoge, pero no menos del 50% de su tamaño ideal
                min_app_width = max(400, ideal_app_width * 0.5)
                new_app_width = max(min_app_width, available_for_app)
                new_total_width = new_app_width + panels_width
                
                # Si aún no cabe, reducir ancho de paneles proporcionalmente
                if new_total_width > max_available_width:
                    new_total_width = max_available_width
                    new_app_width = max_available_width - panels_width
                
                print(f"[DEBUG] Ajuste por límite de pantalla:")
                print(f"  - App: {ideal_app_width}px → {int(new_app_width)}px")
                print(f"  - Total: {ideal_total_width}px → {int(new_total_width)}px")
            else:
                # SÍ CABE: Mezcla equilibrada (70% crece ventana, 30% encoge app)
                if self.current_panel_count > 0:
                    # Al agregar panel: app se encoge un 30% del ancho del panel
                    shrink_amount = self.panel_width * 0.3
                    new_app_width = ideal_app_width - (shrink_amount * self.current_panel_count)
                    new_app_width = max(500, new_app_width)  # Mínimo razonable
                else:
                    # Sin paneles: volver al tamaño ideal
                    new_app_width = ideal_app_width
                
                new_total_width = new_app_width + panels_width
                
                print(f"[DEBUG] Mezcla equilibrada (70-30):")
                print(f"  - App: {ideal_app_width}px → {int(new_app_width)}px")
                print(f"  - Paneles: {panels_width}px")
                print(f"  - Total: {int(new_total_width)}px")
            
            # 3. Centrar en pantalla
            current_x = self.master.winfo_x()
            current_y = self.master.winfo_y()
            
            # Si está primera vez o muy descentrado, centrar
            if self.current_panel_count == 1:
                current_x = max(0, (self.screen_width - int(new_total_width)) // 2)
            
            # 4. Aplicar geometría
            self.master.geometry(f"{int(new_total_width)}x{self.master.winfo_height()}+{current_x}+{current_y}")
            
            # 5. Actualizar estado
            if not self.user_resized_manually:
                self.base_app_width = int(new_app_width)
            
            self.master.update_idletasks()
            
            # Después de aplicar, permitir redimensionamiento manual
            self.master.after(100, self._enable_manual_resize)
            
        except Exception as e:
            print(f"[ERROR] Error en smart_resize: {e}")
    
    def _enable_manual_resize(self):
        """Permite que eventos de resize sean detectados como manuales"""
        # Simplemente dejamos que _on_window_resize haga su trabajo
        pass
    
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