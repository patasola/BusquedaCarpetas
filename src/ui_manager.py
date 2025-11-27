# src/ui_manager.py - Gestión de Elementos de Interfaz V.4.4 (Toggle Corregido)
import tkinter as tk

class UIManager:
    """Gestor de elementos de interfaz y su visibilidad"""
    
    def __init__(self, app):
        self.app = app
        
        # Referencias a frames - se asignarán después
        self.status_frame = None
        self.cache_frame = None
        
        # Flag para prevenir loops en callbacks
        self._updating_vars = False
    
    def configurar_referencias(self, status_frame, cache_frame):
        """Configura las referencias a los frames de las barras"""
        self.status_frame = status_frame
        self.cache_frame = cache_frame
        
        print(f"[DEBUG] Referencias configuradas - Status: {bool(status_frame)}, Cache: {bool(cache_frame)}")
        
        # Asegurar que las barras estén visibles inicialmente
        self._asegurar_barras_visibles()
    
    def _asegurar_barras_visibles(self):
        """Asegura que las barras estén visibles al inicio según variables"""
        try:
            # Barra de cache (arriba de status)
            if self.cache_frame and hasattr(self.app, 'mostrar_barra_cache') and self.app.mostrar_barra_cache.get():
                if self.status_frame and hasattr(self.app, 'mostrar_barra_estado') and self.app.mostrar_barra_estado.get():
                    self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame)
                else:
                    self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X)
                print("[DEBUG] Barra de cache mostrada")
            
            # Barra de estado (abajo)
            if self.status_frame and hasattr(self.app, 'mostrar_barra_estado') and self.app.mostrar_barra_estado.get():
                self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
                print("[DEBUG] Barra de estado mostrada")
        except Exception as e:
            print(f"[ERROR] Error asegurando barras visibles: {e}")
    
    def toggle_barra_estado(self):
        """Alterna la visibilidad de la barra de estado"""
        if self._updating_vars:
            return
            
        try:
            if not self.status_frame or not hasattr(self.app, 'mostrar_barra_estado'):
                print("[DEBUG] No hay referencia a status_frame o variable")
                return
            
            mostrar = self.app.mostrar_barra_estado.get()
            print(f"[DEBUG] toggle_barra_estado - mostrar: {mostrar}")
            
            if mostrar:
                # Mostrar barra de estado
                self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
                
                # Reposicionar barra de cache si está visible
                if (self.cache_frame and 
                    hasattr(self.app, 'mostrar_barra_cache') and 
                    self.app.mostrar_barra_cache.get()):
                    self.cache_frame.pack_forget()
                    self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame)
                
                print("[DEBUG] Barra de estado mostrada")
            else:
                # Ocultar barra de estado
                self.status_frame.pack_forget()
                
                # Reposicionar barra de cache al fondo si está visible
                if (self.cache_frame and 
                    hasattr(self.app, 'mostrar_barra_cache') and 
                    self.app.mostrar_barra_cache.get()):
                    self.cache_frame.pack_forget()
                    self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X)
                
                print("[DEBUG] Barra de estado ocultada")
                
        except Exception as e:
            print(f"[ERROR] Error en toggle_barra_estado: {e}")
    
    def toggle_barra_cache(self):
        """Alterna la visibilidad de la barra de cache"""
        if self._updating_vars:
            return
            
        try:
            if not self.cache_frame or not hasattr(self.app, 'mostrar_barra_cache'):
                print("[DEBUG] No hay referencia a cache_frame o variable")
                return
            
            mostrar = self.app.mostrar_barra_cache.get()
            print(f"[DEBUG] toggle_barra_cache - mostrar: {mostrar}")
            
            if mostrar:
                # Mostrar barra de cache
                if (self.status_frame and 
                    hasattr(self.app, 'mostrar_barra_estado') and 
                    self.app.mostrar_barra_estado.get()):
                    # Si status está visible, cache va antes (arriba)
                    self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame)
                else:
                    # Si status no está visible, cache va al fondo
                    self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X)
                
                print("[DEBUG] Barra de cache mostrada")
            else:
                # Ocultar barra de cache
                self.cache_frame.pack_forget()
                print("[DEBUG] Barra de cache ocultada")
                
        except Exception as e:
            print(f"[ERROR] Error en toggle_barra_cache: {e}")
    
    def toggle_historial(self):
        """Alterna la visibilidad del historial"""
        if hasattr(self.app, 'historial_manager') and self.app.historial_manager:
            self.app.historial_manager.toggle_visibility()
            
            # Actualizar variable sin callback
            if hasattr(self.app, 'mostrar_historial'):
                self._updating_vars = True
                self.app.mostrar_historial.set(self.app.historial_manager.visible)
                self._updating_vars = False
    
    def configurar_menu_ver(self, menu_ver):
        """Configura el menú Ver con los checkbuttons correctos"""
        # Historial de búsquedas
        menu_ver.add_checkbutton(
            label="Historial de Búsquedas",
            variable=self.app.mostrar_historial,
            command=self.toggle_historial,
            accelerator="Ctrl+Alt+H"
        )
        
        # Explorador de archivos 
        menu_ver.add_checkbutton(
            label="Explorador de Archivos", 
            variable=self.app.mostrar_explorador,
            command=self.app.toggle_explorador,
            accelerator="Ctrl+Alt+E"
        )
        
        menu_ver.add_separator()
        
        # Barras de información
        menu_ver.add_checkbutton(
            label="Barra de Información de Cache",
            variable=self.app.mostrar_barra_cache,
            command=self.toggle_barra_cache
        )
        
        menu_ver.add_checkbutton(
            label="Barra de Estado",
            variable=self.app.mostrar_barra_estado,
            command=self.toggle_barra_estado
        )
        
        return menu_ver