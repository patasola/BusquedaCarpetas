import tkinter as tk
from .ui_components import UIComponents

class ProgressManager:
    """
    Gestión de progreso que FUNCIONA - versión restaurada y simplificada.
    """
    
    def __init__(self, parent_frame, tree_master):
        self.parent_frame = parent_frame
        self.tree_master = tree_master
        self.progress_frame = None
        self.progress = None
        self.label_porcentaje = None
        self.progress_container = None
        self._visible = False
        self._crear_componentes()
    
    def _crear_componentes(self):
        """Crea componentes con espacio reservado permanente"""
        # El frame principal SIEMPRE ocupa espacio
        self.progress_frame, self.progress, self.label_porcentaje, self.progress_container = UIComponents.create_progress_bar(self.parent_frame)
        
        # Posicionar ANTES del área de resultados pero SIN mostrar contenido
        self.progress_frame.pack(fill=tk.X, pady=(10, 8), before=self.tree_master)
        
        print("DEBUG: Espacio para progreso reservado permanentemente")
    
    def mostrar(self):
        """Muestra solo el PORCENTAJE (sin barra visual)"""
        if self._visible:
            return
            
        print("DEBUG: Mostrando solo porcentaje")
        try:
            # NO mostrar la barra visual - solo configurar el porcentaje
            # self.progress.pack(pady=(5, 5), ipady=8)  # COMENTADO - no mostrar barra
            
            # Mostrar el contenedor y la etiqueta
            self.progress_container.pack(fill=tk.X, pady=5)
            self.label_porcentaje.pack(pady=(0, 5))
            
            # Inicializar valores
            self.progress["value"] = 0  # Mantener sincronizado aunque no sea visible
            self.label_porcentaje.config(text="0%")
            
            self._visible = True
            print("DEBUG: Solo porcentaje mostrado con 0%")
            
        except Exception as e:
            print(f"ERROR mostrando porcentaje: {e}")
    
    def ocultar(self):
        """Oculta el porcentaje"""
        if not self._visible:
            return
            
        print("DEBUG: Ocultando porcentaje")
        try:
            # Ocultar contenido
            if self.label_porcentaje.winfo_viewable():
                self.label_porcentaje.pack_forget()
            if self.progress_container.winfo_viewable():
                self.progress_container.pack_forget()
                
            self._visible = False
            print("DEBUG: Porcentaje ocultado")
            
        except Exception as e:
            print(f"ERROR ocultando porcentaje: {e}")
    
    def actualizar(self, procesados, total):
        """Actualiza el porcentaje"""
        if not self._visible or total <= 0:
            return
            
        try:
            porcentaje = int((procesados / total) * 100)
            porcentaje = min(100, max(0, porcentaje))
            
            # Actualizar ambos elementos para mantener sincronización
            self.progress["value"] = porcentaje  # Mantener sincronizado aunque no sea visible
            self.label_porcentaje.config(text=f"{porcentaje}%")
            
            # Actualización visual controlada
            if porcentaje % 10 == 0:  # Solo actualizar visualmente cada 10%
                self.progress_container.update_idletasks()
            
            print(f"DEBUG: Porcentaje: {procesados}/{total} ({porcentaje}%)")
            
        except Exception as e:
            print(f"ERROR actualizando porcentaje: {e}")
    
    def is_visible(self):
        """Retorna si el porcentaje está visible"""
        return self._visible
    
    def reset(self):
        """Resetea a 0%"""
        if self._visible:
            self.progress["value"] = 0
            self.label_porcentaje.config(text="0%")
            print("DEBUG: Porcentaje reseteado a 0%")