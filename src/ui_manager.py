# src/ui_manager.py - Gestión de Elementos de Interfaz V.4.2 (Refactorizado)
import tkinter as tk

class UIManager:
    """Gestor de elementos de interfaz y su visibilidad"""
    
    def __init__(self, app):
        self.app = app
        
        # Variables de estado
        self.mostrar_barra_estado = tk.BooleanVar(value=True)
        self.mostrar_barra_cache = tk.BooleanVar(value=True)
        self.mostrar_historial = tk.BooleanVar(value=False)
        
        # Referencias a frames
        self.status_frame = None
        self.cache_frame = None
        
        # Callbacks para actualizar menú
        self.mostrar_barra_estado.trace_add('write', self._on_barra_estado_change)
        self.mostrar_barra_cache.trace_add('write', self._on_barra_cache_change)
    
    def configurar_referencias(self, status_frame, cache_frame):
        """Configura las referencias a los frames de las barras"""
        self.status_frame = status_frame
        self.cache_frame = cache_frame
        self._asegurar_barras_visibles()
    
    def _asegurar_barras_visibles(self):
        """Asegura que las barras estén visibles al inicio"""
        if self.status_frame and self.mostrar_barra_estado.get():
            self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, anchor='w')
        
        if self.cache_frame and self.mostrar_barra_cache.get():
            if self.mostrar_barra_estado.get():
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame, anchor='w')
            else:
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, anchor='w')
    
    def _on_barra_estado_change(self, *args):
        """Callback cuando cambia el estado de la barra de estado"""
        self.toggle_barra_estado()
    
    def _on_barra_cache_change(self, *args):
        """Callback cuando cambia el estado de la barra de cache"""
        self.toggle_barra_cache()
    
    def toggle_barra_estado(self):
        """Alterna la visibilidad de la barra de estado"""
        if not self.status_frame:
            return
            
        if self.mostrar_barra_estado.get():
            self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, anchor='w')
            if self.mostrar_barra_cache.get() and self.cache_frame:
                self.cache_frame.pack_forget()
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame, anchor='w')
        else:
            self.status_frame.pack_forget()
            if self.mostrar_barra_cache.get() and self.cache_frame:
                self.cache_frame.pack_forget()
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, anchor='w')
    
    def toggle_barra_cache(self):
        """Alterna la visibilidad de la barra de cache"""
        if not self.cache_frame:
            return
            
        if self.mostrar_barra_cache.get():
            if self.mostrar_barra_estado.get() and self.status_frame:
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.status_frame, anchor='w')
            else:
                self.cache_frame.pack(side=tk.BOTTOM, fill=tk.X, anchor='w')
        else:
            self.cache_frame.pack_forget()
    
    def toggle_historial(self):
        """Alterna la visibilidad del historial"""
        self.app.historial_manager.toggle_visibility()
        self._actualizar_variable_sin_callback(self.mostrar_historial, self.app.historial_manager.visible)
    
    def _actualizar_variable_sin_callback(self, variable, valor):
        """Actualiza una variable BooleanVar sin disparar callbacks"""
        callback_info = variable.trace_info()
        for callback_id in callback_info:
            variable.trace_remove(*callback_id)
        
        variable.set(valor)
    
    def actualizar_estado_historial(self):
        """Actualiza el estado del historial sin triggerar eventos"""
        self._actualizar_variable_sin_callback(self.mostrar_historial, self.app.historial_manager.visible)
    
    def configurar_menu_ver(self, menu_ver):
        """Configura el menú Ver con los checkbuttons correctos"""
        menu_ver.add_checkbutton(
            label="Barra de Estado",
            variable=self.mostrar_barra_estado
        )
        menu_ver.add_checkbutton(
            label="Barra de Cache",
            variable=self.mostrar_barra_cache
        )
        menu_ver.add_separator()
        menu_ver.add_checkbutton(
            label="Historial de Búsquedas",
            variable=self.mostrar_historial,
            command=self.toggle_historial,
            accelerator="Ctrl+H"
        )
        
        return menu_ver