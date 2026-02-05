# src/managers/dual_panel_manager.py - Gestión de Paneles Duales V.5.0 (Luce Intellettual)

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
        app_frame.grid_columnconfigure(0, weight=1, minsize=600)  # Columna principal (expandible + minsize)
        app_frame.grid_columnconfigure(1, weight=0)  # Panel lateral 1 (fijo)
        app_frame.grid_columnconfigure(2, weight=0)  # Panel lateral 2 (fijo)

    def get_active_panels_count(self):
        """Devuelve el número de paneles activos"""
        return sum(1 for pos in self.panel_positions.values() if pos is not None)

    def get_total_panels_width(self):
        """Calcula el ancho real total ocupado por los paneles laterales"""
        total = 0
        
        # Historial
        if self.panel_positions['historial'] is not None:
            w = 0
            if hasattr(self.app, 'historial_manager') and hasattr(self.app.historial_manager, 'frame'):
                w = self.app.historial_manager.frame.winfo_width()
            
            # Si aún no está mapeado, usar el valor de configuración
            if w <= 1:
                w = self.app.config.get("history_width", 350)
            total += w
            
        # Explorador
        if self.panel_positions['explorador'] is not None:
            w = 0
            if hasattr(self.app, 'file_explorer_manager') and hasattr(self.app.file_explorer_manager, 'frame'):
                w = self.app.file_explorer_manager.frame.winfo_width()
                
            # Si aún no está mapeado, usar el valor de configuración
            if w <= 1:
                w = self.app.config.get("explorer_width", 350)
            total += w
            
        return total
    
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
            except Exception as e:
                print(f"[DEBUG] No se pudo mostrar grip: {e}")
        
        print(f"[DEBUG] Panel {panel_type} asignado a columna {column}")
        
        # Redimensionamiento flexible
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
            
            # Ocultar grip si no hay paneles
            if hasattr(self.app, 'main_grip') and len(self.occupied_columns) == 0:
                try:
                    self.app.main_grip.pack_forget()
                    # Permitir que el contenedor principal se expanda de nuevo
                    if hasattr(self.app, 'main_container_wrapper'):
                        self.app.main_container_wrapper.pack_propagate(True)
                except Exception as e:
                    print(f"[DEBUG] No se pudo ocultar grip: {e}")
            
            # Limpiar configuración de grid para la columna liberada
            if hasattr(self.app, 'app_frame'):
                self.app.app_frame.grid_columnconfigure(old_position, minsize=0, weight=0)
            
            print(f"[DEBUG] Panel {panel_type} liberado de columna {old_position}")
            
            # Reconfigurar redimensionamiento
            self._configure_flexible_resize()
            
            # Actualizar contador de paneles
            active_panels = sum(1 for pos in self.panel_positions.values() if pos is not None)
            if hasattr(self.app, 'window_manager'):
                self.app.window_manager.update_panel_count(active_panels)

    def _configure_flexible_resize(self):
        """Configura redimensionamiento flexible para permitir reducir la app"""
        try:
            active_count = self.get_active_panels_count()
            
            # Ancho mínimo adaptativo
            if active_count > 0:
                self.app.master.minsize(800, 400)
            else:
                self.app.master.minsize(600, 400)
            
            # Habilitar propagación para que el layout se ajuste
            if hasattr(self.app, 'main_container'):
                self.app.main_container.grid_propagate(True)
            
            print(f"[DEBUG] Redimensionamiento flexible actualizado (Paneles: {active_count})")
        except Exception as e:
            print(f"[DEBUG] Error configurando resize flexible: {e}")