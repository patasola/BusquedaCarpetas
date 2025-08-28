# src/ui_state_manager.py - Gestión de Estado de UI V.4.2 (Refactorizado)
import tkinter as tk

class UIStateManager:
    """Maneja el estado de la interfaz (modo entrada, validación, etc.)"""
    
    def __init__(self, app):
        self.app = app
        self.modo_entrada = "normal"
    
    def configurar_validacion(self):
        """Configura la validación del campo de entrada"""
        try:
            vcmd = (self.app.master.register(self._validar_entrada), '%P')
            self.app.entry.configure(validate="key", validatecommand=vcmd)
            self.app.entry.bind('<KeyRelease>', self.on_entry_change)
        except Exception as e:
            print(f"Error configurando validación: {e}")
    
    def _validar_entrada(self, nuevo_texto):
        """Valida el texto de entrada en tiempo real"""
        try:
            if not nuevo_texto:
                self._actualizar_boton_buscar(False)
                return True
            
            if len(nuevo_texto.strip()) >= 1:
                self._actualizar_boton_buscar(True)
            else:
                self._actualizar_boton_buscar(False)
            
            return True
        except Exception as e:
            print(f"Error en validación: {e}")
            return True
    
    def _actualizar_boton_buscar(self, habilitar):
        """Actualiza el estado del botón buscar"""
        try:
            if habilitar and hasattr(self.app, 'ruta_carpeta') and self.app.ruta_carpeta:
                self.app.btn_buscar.configure(state='normal')
            else:
                self.app.btn_buscar.configure(state='disabled')
        except Exception as e:
            print(f"Error actualizando botón: {e}")
    
    def configurar_modo_entrada(self, modo):
        """Configura el modo de entrada de texto"""
        self.modo_entrada = modo
        
        configs = {
            "buscando": {
                'entry': {'state': 'disabled'},
                'btn_buscar': {'state': 'disabled', 'text': 'Buscando...'}
            },
            "error": {
                'entry': {'bg': '#ffebee'}
            },
            "normal": {
                'entry': {'state': 'normal', 'bg': 'white'},
                'btn_buscar': {'state': 'normal', 'text': 'Buscar'}
            }
        }
        
        config = configs.get(modo, configs["normal"])
        
        if 'entry' in config:
            self.app.entry.configure(**config['entry'])
        if 'btn_buscar' in config:
            self.app.btn_buscar.configure(**config['btn_buscar'])
    
    def validar_entrada(self, texto):
        """Valida el texto de entrada"""
        if not texto or not texto.strip():
            return False, "El criterio de búsqueda no puede estar vacío"
        
        if len(texto.strip()) < 2:
            return False, "El criterio debe tener al menos 2 caracteres"
        
        return True, ""
    
    def actualizar_estado_botones(self, hay_seleccion=False):
        """Actualiza el estado de los botones según la selección"""
        estado = 'normal' if hay_seleccion else 'disabled'
        
        for btn_attr in ['btn_copiar', 'btn_abrir']:
            if hasattr(self.app, btn_attr):
                getattr(self.app, btn_attr).configure(state=estado)
    
    def cambiar_modo_entrada(self):
        """Cambia entre modo numérico y alfanumérico"""
        self.app.modo_numerico = not self.app.modo_numerico
        self.actualizar_indicador_modo()
    
    def actualizar_indicador_modo(self):
        """Actualiza el indicador visual del modo actual"""
        if self.app.modo_numerico:
            self.app.modo_label.config(text="[123] Numérico", fg="#006600")
        else:
            self.app.modo_label.config(text="[ABC] Alfanumérico", fg="#0066cc")
    
    def enfocar_y_seleccionar_campo(self):
        """Enfoca el campo de búsqueda y selecciona todo el texto (F2)"""
        try:
            self.app.entry.focus_set()
            self.app.entry.select_range(0, tk.END)
            self.app.entry.icursor(tk.END)
        except Exception as e:
            print(f"Error enfocando campo: {e}")
    
    def on_entry_change(self, event):
        """Maneja cambios en el campo de entrada"""
        try:
            texto = self.app.entry.get().strip()
            
            if texto and hasattr(self.app, 'ruta_carpeta') and self.app.ruta_carpeta:
                self.app.btn_buscar.configure(state='normal')
            else:
                self.app.btn_buscar.configure(state='disabled')
                
        except Exception as e:
            print(f"Error en on_entry_change: {e}")