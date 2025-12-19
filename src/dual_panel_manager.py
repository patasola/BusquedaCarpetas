# src/dual_panel_manager.py - Gestión de Paneles Duales V.4.5 - OPTIMIZADO
import tkinter as tk

class DualPanelManager:
    """Gestiona el sistema de paneles duales sin solapamiento"""
    
    def __init__(self, app):
        self.app = app
        self.panel_positions = {
            'historial': None,
            'explorador': None
        }
        self.occupied_columns = set()  # Columnas actualmente ocupadas
        self.original_width = 0
    
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
        """Asigna posición a un panel y EXPANDE la ventana MANTENIÉNDOLA CENTRADA"""
        if panel_type not in self.panel_positions:
            print(f"[ERROR] Panel tipo desconocido: {panel_type}")
            return 1
        
        # Si ya tiene posición, devolverla
        if self.panel_positions[panel_type] is not None:
            return self.panel_positions[panel_type]
        
        # Guardar ancho original si es el primer panel
        if len(self.occupied_columns) == 0:
            self.original_width = self.app.master.winfo_width()
        
        # Obtener siguiente columna disponible
        column = self.get_next_available_column()
        self.panel_positions[panel_type] = column
        self.occupied_columns.add(column)
        
        # Notificar al window_manager
        if hasattr(self.app, 'window_manager'):
            self.app.window_manager.add_panel()
        
        # EXPANDIR VENTANA Y RE-CENTRAR
        try:
            # Verificar si está maximizada (Windows)
            is_maximized = False
            try:
                if self.app.master.state() == 'zoomed':
                    is_maximized = True
            except:
                pass
                
            if is_maximized:
                print("[LAYOUT] Ventana maximizada, no se puede redimensionar")
            else:
                current_width = self.app.master.winfo_width()
                current_height = self.app.master.winfo_height()
                
                # Fix para startup: si width es muy pequeño (no renderizado), usar default
                if current_width < 100:
                    current_width = 600
                    current_height = 500
                
                screen_width = self.app.master.winfo_screenwidth()
                screen_height = self.app.master.winfo_screenheight()
                
                # Ancho estimado del panel (aprox 300px)
                panel_width = 300
                new_width = current_width + panel_width
                
                # Calcular nueva posición X para mantener el centro
                # Centro actual de la pantalla
                center_x = screen_width // 2
                center_y = screen_height // 2
                
                # Nueva esquina superior izquierda
                new_x = center_x - (new_width // 2)
                new_y = center_y - (current_height // 2)
                
                # Asegurar que no quede fuera de pantalla (izquierda/arriba)
                new_x = max(0, new_x)
                new_y = max(0, new_y)
                
                # No exceder ancho de pantalla
                if new_width < screen_width - 50:
                    self.app.master.geometry(f"{new_width}x{current_height}+{new_x}+{new_y}")
                    print(f"[LAYOUT] Ventana expandida a {new_width}px y re-centrada en {new_x},{new_y}")
            
        except Exception as e:
            print(f"[LAYOUT] Error redimensionando ventana: {e}")
        
        # Mostrar grip de redimensionamiento cuando hay paneles
        if hasattr(self.app, 'main_grip') and len(self.occupied_columns) > 0:
            try:
                self.app.main_grip.pack(side='right', fill='y', before=self.app.main_container)
            except Exception as e:
                pass
        
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
                    pass
            
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