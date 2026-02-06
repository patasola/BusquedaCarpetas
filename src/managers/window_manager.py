# src/managers/window_manager.py - Gestión de Ventana V.5.0 (Luce Intellettual)
from ..ui.ui_components import Colors

class WindowManager:
    """Maneja configuración y propiedades de la ventana con redimensionamiento inteligente"""
    
    def __init__(self, master, version, app):
        self.master = master
        self.version = version
        self.app = app
        
        # Dimensiones de pantalla
        self.screen_width = None
        self.screen_height = None
        self.pixels_per_cm = None
        self.panel_width = None
        
        # Control de redimensionamiento
        self.current_panel_count = 0
        self.base_app_width = 990  # AUMENTADO 10%: 900px → 990px
        self.user_resized_manually = False
        self.manual_app_width = None
        self._is_auto_resizing = False  # Lock para evitar bucles de eventos
    
    def configurar_ventana(self, saved_geometry=None, manual_app_width=None):
        """Configura las propiedades básicas de la ventana"""
        from ..core.constants import APP_TITLE
        self.master.title(APP_TITLE)
        self.master.configure(bg=Colors.BACKGROUND)
        self.master.resizable(True, True)
        
        # Cargar ancho manual si existe
        if manual_app_width:
            self.manual_app_width = manual_app_width
            print(f"[DEBUG] Ancho manual cargado: {manual_app_width}px")

        # Calcular dimensiones
        self.screen_width = self.master.winfo_screenwidth()
        self.screen_height = self.master.winfo_screenheight()
        self.pixels_per_cm = self.screen_width / 33.3
        
        # Ancho de cada panel (8cm)
        panel_width_cm = 7.15  # AUMENTADO 10%: 6.5cm → 7.15cm (~550px en lugar de ~500px)
        self.panel_width = int(panel_width_cm * self.pixels_per_cm)
        
        # Tamaño inicial o cargado
        initial_height = 700 # Definir aquí para evitar UnboundLocalError
        
        if saved_geometry:
            try:
                self.master.geometry(saved_geometry)
                print(f"[DEBUG] Geometría cargada: {saved_geometry}")
            except:
                x = max(0, (self.screen_width - self.base_app_width) // 2)
                y = max(0, (self.screen_height - initial_height) // 2)
                self.master.geometry(f"{self.base_app_width}x{initial_height}+{x}+{y}")
        else:
            x = max(0, (self.screen_width - self.base_app_width) // 2)
            y = max(0, (self.screen_height - initial_height) // 2)
            self.master.geometry(f"{self.base_app_width}x{initial_height}+{x}+{y}")
        self.master.minsize(600, 400)
        
        # Detectar redimensionamiento manual
        self.master.bind('<Configure>', self._on_window_resize)
        
        print(f"[DEBUG] Ventana configurada:")
        print(f"  - Tamaño inicial: {self.base_app_width}x{initial_height}")
        print(f"  - Panel width: {self.panel_width}px ({panel_width_cm}cm)")
        print(f"  - Pantalla: {self.screen_width}x{self.screen_height}")
        
    def _on_window_resize(self, event):
        """Detecta cuando el usuario redimensiona manualmente"""
        # CRÍTICO: Ignorar eventos durante la inicialización o redimensionamientos automáticos
        if self._is_auto_resizing or (hasattr(self.app, '_is_initializing') and self.app._is_initializing):
            return

        # Solo procesar eventos de la ventana principal
        if event.widget != self.master:
            return
        
        # Calcular ancho esperado automático
        expected_width = self._calculate_expected_width()
        current_width = event.width # Usar el ancho del evento es más fiable
        
        # Calcular ancho de paneles actuales
        if hasattr(self.app, 'dual_panel_manager'):
            current_panels_width = self.app.dual_panel_manager.get_total_panels_width()
        else:
            current_panels_width = self.current_panel_count * self.panel_width

        # Si difiere significativamente, el usuario está redimensionando
        if abs(current_width - expected_width) > 35: # Margen aumentado un poco
            self.user_resized_manually = True
            self.manual_app_width = current_width - current_panels_width
            
            # Guardar preferencias tras redimensionar (Debounced)
            if hasattr(self.app, 'save_ui_settings'):
                if not hasattr(self, '_save_timer'): self._save_timer = None
                if self._save_timer: self.master.after_cancel(self._save_timer)
                self._save_timer = self.master.after(1000, self.app.save_ui_settings)
                
            print(f"[DEBUG] Redimensionamiento manual detectado: {current_width}px (App: {self.manual_app_width}px)")
    
    def _calculate_expected_width(self):
        """Calcula el ancho esperado según paneles activos"""
        if self.manual_app_width:
            app_width = self.manual_app_width
        else:
            app_width = self.base_app_width
        
        # Usar ancho real de paneles si está disponible
        if hasattr(self.app, 'dual_panel_manager'):
            panels_width = self.app.dual_panel_manager.get_total_panels_width()
        else:
            panels_width = self.current_panel_count * self.panel_width
            
        return app_width + panels_width
    
    def add_panel(self):
        """Agrega un panel con redimensionamiento inteligente"""
        self.current_panel_count += 1
        
        # Bloquear si estamos inicializando para respetar la geometría guardada
        if hasattr(self.app, '_is_initializing') and self.app._is_initializing:
            return

        self._smart_resize()
        print(f"[DEBUG] Panel agregado. Total: {self.current_panel_count}")
    
    def remove_panel(self):
        """Remueve un panel con redimensionamiento inteligente"""
        self.current_panel_count = max(0, self.current_panel_count - 1)
        
        if hasattr(self.app, '_is_initializing') and self.app._is_initializing:
            return

        self._smart_resize()
        print(f"[DEBUG] Panel removido. Total: {self.current_panel_count}")
    
    def _smart_resize(self):
        """Redimensionamiento inteligente: mezcla de encoger app + crecer ventana"""
        try:
            # Calcular ancho necesario para todos los paneles de forma precisa
            if hasattr(self.app, 'dual_panel_manager'):
                panels_width = self.app.dual_panel_manager.get_total_panels_width()
            else:
                panels_width = self.current_panel_count * self.panel_width
            
            # ESTRATEGIA MIXTA:
            # 1. Calcular ancho ideal (sin restricciones)
            if self.manual_app_width:
                ideal_app_width = self.manual_app_width
            else:
                ideal_app_width = self.base_app_width
            
            ideal_total_width = ideal_app_width + panels_width
            
            # 2. Verificar si cabe en pantalla (dejar margen de 80px)
            max_available_width = self.screen_width - 80
            
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
                # SÍ CABE: Priorizar mantener el tamaño de la app y solo crecer la ventana
                new_app_width = ideal_app_width
                new_total_width = ideal_total_width
                
                print(f"[DEBUG] Ventana crecida (app intacta):")
                print(f"  - App: {ideal_app_width}px")
                print(f"  - Paneles: {panels_width}px")
                print(f"  - Total: {int(new_total_width)}px")
            
            # 3. Mantener posición Y, ajustar X si es necesario para que quepa
            current_x = self.master.winfo_x()
            current_y = self.master.winfo_y()
            
            if current_x + new_total_width > self.screen_width:
                current_x = max(0, self.screen_width - int(new_total_width) - 40)
            
            # 4. Aplicar geometría con LOCK
            self._is_auto_resizing = True
            try:
                # Asegurar que el alto sea razonable
                h = self.master.winfo_height()
                if h < 300: h = 700 # Fallback si no está mapeada
                
                self.master.geometry(f"{int(new_total_width)}x{h}+{current_x}+{current_y}")
                self.master.update_idletasks()
            finally:
                # Retrasar la liberación del lock para asegurar que los eventos se procesen
                self.master.after(300, self._release_auto_resize_lock)
            
            # 5. Actualizar estado
            if not self.user_resized_manually:
                self.base_app_width = int(new_app_width)
            
            # Después de aplicar, permitir redimensionamiento manual
            self.master.after(100, self._enable_manual_resize)
            
        except Exception as e:
            print(f"[ERROR] Error en smart_resize: {e}")
    
    def _release_auto_resize_lock(self):
        """Libera el lock de redimensionamiento automático"""
        self._is_auto_resizing = False
        print("[DEBUG] Auto-resize lock liberado")

    def _enable_manual_resize(self):
        """Permite que eventos de resize sean detectados como manuales"""
        # Simplemente dejamos que _on_window_resize haga su trabajo
        pass
    
    def update_panel_count(self, count):
        """Actualiza el contador de paneles"""
        if count != self.current_panel_count:
            diff = count - self.current_panel_count
            self.current_panel_count = count
            
            # Bloquear si estamos inicializando
            if hasattr(self.app, '_is_initializing') and self.app._is_initializing:
                return

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