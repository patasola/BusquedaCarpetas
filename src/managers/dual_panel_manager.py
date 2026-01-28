# src/dual_panel_manager.py - Gestión de Paneles Duales V.4.5

class DualPanelManager:
    """Gestiona el sistema de paneles duales sin solapamiento"""
    
    def __init__(self, app):
        self.app = app
        self.panel_positions = {
            'historial': None,
            'explorador': None
        }
        self.occupied_columns = set()  # Columnas actualmente ocupadas
    
    def configure_grid(self, app_frame):
        """Configura grid con 3 columnas para paneles duales"""
        app_frame.grid_rowconfigure(0, weight=1)
        app_frame.grid_columnconfigure(0, weight=1)  # Columna principal (expandible)
        app_frame.grid_columnconfigure(1, weight=0)  # Panel lateral 1 (fijo)
        app_frame.grid_columnconfigure(2, weight=0)  # Panel lateral 2 (fijo)
    
    def get_next_available_column(self):
        """Obtiene la siguiente columna disponible para un panel lateral"""
        if self.panel_positions['historial'] is None and self.panel_positions['explorador'] is None:
            return 1
        elif self.panel_positions['historial'] == 1 and self.panel_positions['explorador'] is None:
            return 2
        elif self.panel_positions['explorador'] == 1 and self.panel_positions['historial'] is None:
            return 2
        else:
            return 1
      
    def assign_panel_position(self, panel_type):
        """Asigna posición a un panel"""
        if panel_type not in self.panel_positions:
            print(f"[ERROR] Panel tipo desconocido: {panel_type}")
            return 1
        
        # Si ya tiene posición, devolverla
        if self.panel_positions[panel_type] is not None:
            return self.panel_positions[panel_type]
        
        # Obtener siguiente columna disponible
        column = self.get_next_available_column()
        self.panel_positions[panel_type] = column
        self.occupied_columns.add(column)
        
        # Notificar al window_manager
        if hasattr(self.app, 'window_manager'):
            self.app.window_manager.add_panel()
        
        # Mostrar grip de redimensionamiento cuando hay paneles
        if hasattr(self.app, 'main_grip') and len(self.occupied_columns) > 0:
            try:
                self.app.main_grip.pack(side='right', fill='y', before=self.app.main_container)
                print(f"[DEBUG] Grip mostrado. Visible: {self.app.main_grip.winfo_viewable()}")
                print(f"[DEBUG] Grip width: {self.app.main_grip.winfo_width()}")
                print(f"[DEBUG] Grip height: {self.app.main_grip.winfo_height()}")
            except Exception as e:
                print(f"[DEBUG] No se pudo mostrar grip: {e}")
        else:
            print(f"[DEBUG] main_grip existe: {hasattr(self.app, 'main_grip')}")
            print(f"[DEBUG] occupied_columns: {len(self.occupied_columns)}")
        
        print(f"[DEBUG] Panel {panel_type} asignado a columna {column}")
        
        # Actualizar contador de paneles
        active_panels = sum(1 for pos in self.panel_positions.values() if pos is not None)
        if hasattr(self.app, 'window_manager'):
            self.app.window_manager.update_panel_count(active_panels)
        
        return column
    
    def release_panel_position(self, panel_type):
        """Libera la posición de un panel y notifica al window_manager"""
        if panel_type not in self.panel_positions:
            return
        
        old_position = self.panel_positions[panel_type]
        
        if old_position is not None:
            self.panel_positions[panel_type] = None
            self.occupied_columns.discard(old_position)
            
            # Notificar al window_manager
            if hasattr(self.app, 'window_manager'):
                self.app.window_manager.remove_panel()
            
            # Ocultar grip si no hay paneles
            if hasattr(self.app, 'main_grip') and len(self.occupied_columns) == 0:
                try:
                    self.app.main_grip.pack_forget()
                    # Permitir que el contenedor principal se expanda de nuevo
                    if hasattr(self.app, 'main_container_wrapper'):
                        self.app.main_container_wrapper.pack_propagate(True)
                except Exception as e:
                    print(f"[DEBUG] No se pudo ocultar grip: {e}")
            
            print(f"[DEBUG] Panel {panel_type} liberado de columna {old_position}")
            
            # Actualizar contador de paneles
            active_panels = sum(1 for pos in self.panel_positions.values() if pos is not None)
            if hasattr(self.app, 'window_manager'):
                self.app.window_manager.update_panel_count(active_panels)
    
    def get_active_panels_count(self):
        """Devuelve el número de paneles actualmente activos"""
        return sum(1 for pos in self.panel_positions.values() if pos is not None)
    
    def is_column_occupied(self, column):
        """Verifica si una columna está ocupada"""
        return column in self.occupied_columns
    
    def get_panel_at_column(self, column):
        """Devuelve el tipo de panel en una columna específica"""
        for panel_type, pos in self.panel_positions.items():
            if pos == column:
                return panel_type
        return None
    
    def assign_panel_position(self, panel_type):
        """Asigna posición a un panel"""
        if panel_type not in self.panel_positions:
            print(f"[ERROR] Panel tipo desconocido: {panel_type}")
            return 1
        
        # Si ya tiene posición, devolverla
        if self.panel_positions[panel_type] is not None:
            return self.panel_positions[panel_type]
        
        # Obtener siguiente columna disponible
        column = self.get_next_available_column()
        self.panel_positions[panel_type] = column
        self.occupied_columns.add(column)
        
        # Notificar al window_manager
        if hasattr(self.app, 'window_manager'):
            self.app.window_manager.add_panel()
        
        print(f"[DEBUG] Panel {panel_type} asignado a columna {column}")
        
        # NUEVO: Permitir redimensionamiento libre
        self._configure_flexible_resize()
        
        # Actualizar contador de paneles
        active_panels = sum(1 for pos in self.panel_positions.values() if pos is not None)
        if hasattr(self.app, 'window_manager'):
            self.app.window_manager.update_panel_count(active_panels)
        
        return column

    def release_panel_position(self, panel_type):
        """Libera la posición de un panel y notifica al window_manager"""
        if panel_type not in self.panel_positions:
            return
        
        old_position = self.panel_positions[panel_type]
        
        if old_position is not None:
            self.panel_positions[panel_type] = None
            self.occupied_columns.discard(old_position)
            
            # Notificar al window_manager
            if hasattr(self.app, 'window_manager'):
                self.app.window_manager.remove_panel()
            
            print(f"[DEBUG] Panel {panel_type} liberado de columna {old_position}")
            
            # NUEVO: Reconfigurar redimensionamiento
            self._configure_flexible_resize()
            
            # Actualizar contador de paneles
            active_panels = sum(1 for pos in self.panel_positions.values() if pos is not None)
            if hasattr(self.app, 'window_manager'):
                self.app.window_manager.update_panel_count(active_panels)

    def _configure_flexible_resize(self):
        """Configura redimensionamiento flexible para permitir reducir la app"""
        try:
            # Permitir que la ventana se redimensione libremente
            self.app.master.minsize(600, 400)  # Ancho mínimo razonable
            
            # Forzar que el main_container sea flexible
            if hasattr(self.app, 'main_container'):
                self.app.main_container.grid_propagate(False)
            
            print("[DEBUG] Redimensionamiento flexible configurado")
        except Exception as e:
            print(f"[DEBUG] Error configurando resize flexible: {e}")