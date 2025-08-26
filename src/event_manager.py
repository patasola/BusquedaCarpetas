# src/event_manager.py - Gestión de Eventos V.4.1 (Con Atajos de Ventana)
import tkinter as tk

class EventManager:
    """Maneja todos los eventos de la aplicación"""
    
    def __init__(self, app):
        self.app = app
    
    def configurar_eventos(self):
        """Configura todos los eventos de la aplicación"""
        self._configurar_atajos_teclado()
        self._configurar_eventos_entry()
        self._configurar_eventos_tree()
        self._configurar_eventos_botones()
    
    def _configurar_atajos_teclado(self):
        """Configura atajos de teclado globales"""
        # Atajos funcionales existentes
        self.app.master.bind("<F1>", lambda e: self.app.manual_viewer.show_manual())
        self.app.master.bind("<F2>", lambda e: self.app.ui_state_manager.enfocar_y_seleccionar_campo())
        self.app.master.bind("<F3>", lambda e: self.copiar_ruta_seleccionada())
        self.app.master.bind("<F4>", lambda e: self.abrir_carpeta_seleccionada())
        self.app.master.bind("<F5>", lambda e: self.app.ui_state_manager.cambiar_modo_entrada())
        
        # NUEVOS ATAJOS PARA VENTANA
        self.app.master.bind("<F11>", lambda e: self.app.window_manager.maximizar_ventana())
        self.app.master.bind("<Control-e>", lambda e: self.app.window_manager.centrar_ventana())
        self.app.master.bind("<Control-E>", lambda e: self.app.window_manager.centrar_ventana())
        self.app.master.bind("<Control-r>", lambda e: self.app.window_manager.restaurar_ventana())
        self.app.master.bind("<Control-R>", lambda e: self.app.window_manager.restaurar_ventana())
        
        # Atajos de interfaz existentes
        self.app.master.bind("<Control-h>", lambda e: self.app.ui_manager.toggle_historial())
        self.app.master.bind("<Control-H>", lambda e: self.app.ui_manager.toggle_historial())
    
    def _configurar_eventos_entry(self):
        """Configura eventos del campo de entrada"""
        self.app.entry.bind("<Return>", lambda e: self.app.buscar_carpeta())
        self.app.entry.bind("<KeyRelease>", self.app.on_entry_change)
    
    def _configurar_eventos_tree(self):
        """Configura eventos del TreeView"""
        self.app.tree.bind("<<TreeviewSelect>>", self.app.on_tree_select)
        self.app.tree.bind("<Double-1>", lambda e: self.abrir_carpeta_seleccionada())
        self.app.tree.bind("<Return>", lambda e: self.abrir_carpeta_seleccionada())
        self.app.tree.bind("<F3>", lambda e: self.copiar_ruta_seleccionada())
        self.app.tree.bind("<F4>", lambda e: self.abrir_carpeta_seleccionada())
        
        # Navegación en tabla
        self.app.tree.bind("<Up>", self._manejar_navegacion_tabla)
        self.app.tree.bind("<Down>", self._manejar_navegacion_tabla)
        self.app.tree.bind("<Prior>", self._manejar_navegacion_tabla)
        self.app.tree.bind("<Next>", self._manejar_navegacion_tabla)
        self.app.tree.bind("<Home>", self._manejar_navegacion_tabla)
        self.app.tree.bind("<End>", self._manejar_navegacion_tabla)
    
    def _configurar_eventos_botones(self):
        """Configura comandos de botones"""
        self.app.btn_buscar.config(command=self.app.buscar_carpeta)
        self.app.btn_cancelar.config(command=self.app.cancelar_busqueda)
        self.app.btn_copiar.config(command=self.copiar_ruta_seleccionada)
        self.app.btn_abrir.config(command=self.abrir_carpeta_seleccionada)
    
    def _manejar_navegacion_tabla(self, event):
        """Maneja navegación con flechas en la tabla"""
        elementos = self.app.tree.get_children()
        if not elementos:
            return "break"
        
        seleccion_actual = self.app.tree.selection()
        
        if not seleccion_actual:
            self.app.tree.selection_set(elementos[0])
            self.app.tree.focus(elementos[0])
            self.app.tree.see(elementos[0])
            return "break"
        
        # CORREGIDO: Obtener todos los elementos visibles (incluyendo expandidos)
        def get_all_visible_items(parent=""):
            """Obtiene todos los elementos visibles recursivamente"""
            items = []
            for child in self.app.tree.get_children(parent):
                items.append(child)
                # Si está expandido, agregar sus hijos también
                if self.app.tree.item(child, 'open'):
                    items.extend(get_all_visible_items(child))
            return items
        
        elementos_visibles = get_all_visible_items()
        
        if not elementos_visibles:
            return "break"
            
        try:
            indice_actual = elementos_visibles.index(seleccion_actual[0])
        except ValueError:
            # Si el elemento seleccionado no está en la lista, seleccionar el primero
            self.app.tree.selection_set(elementos_visibles[0])
            self.app.tree.focus(elementos_visibles[0])
            self.app.tree.see(elementos_visibles[0])
            return "break"
        
        nuevo_indice = indice_actual
        
        if event.keysym == "Up":
            nuevo_indice = max(0, indice_actual - 1)
        elif event.keysym == "Down":
            nuevo_indice = min(len(elementos_visibles) - 1, indice_actual + 1)
        elif event.keysym == "Prior":  # Page Up
            nuevo_indice = max(0, indice_actual - 5)
        elif event.keysym == "Next":   # Page Down
            nuevo_indice = min(len(elementos_visibles) - 1, indice_actual + 5)
        elif event.keysym == "Home":
            nuevo_indice = 0
        elif event.keysym == "End":
            nuevo_indice = len(elementos_visibles) - 1
        
        if nuevo_indice != indice_actual:
            nuevo_elemento = elementos_visibles[nuevo_indice]
            self.app.tree.selection_set(nuevo_elemento)
            self.app.tree.focus(nuevo_elemento)
            self.app.tree.see(nuevo_elemento)
        
        return "break"
    
    def on_tree_select(self, event):
        """Maneja selección en el TreeView"""
        if self.app.ui_callbacks.hay_seleccion():
            self.app.btn_abrir.config(state=tk.NORMAL)
            self.app.btn_copiar.config(state=tk.NORMAL)
        else:
            self.app.btn_abrir.config(state=tk.DISABLED)
            self.app.btn_copiar.config(state=tk.DISABLED)
        
        self.app.configurar_scrollbars()
    
    def abrir_carpeta_seleccionada(self):
        """Abre la carpeta seleccionada"""
        seleccion = self.app.ui_callbacks.obtener_seleccion_tabla()
        if not seleccion:
            self.app.ui_callbacks.mostrar_advertencia("Seleccione una carpeta primero")
            return
        
        ruta_abs = self.app.file_manager.obtener_ruta_absoluta(
            self.app.ruta_carpeta, seleccion['ruta_rel']
        )
        
        if not self.app.file_manager.verificar_ruta_existe(ruta_abs):
            self.app.ui_callbacks.mostrar_error(f"La carpeta no existe: {ruta_abs}")
            return
        
        # Abrir carpeta Y copiar ruta automáticamente
        carpeta_abierta = self.app.file_manager.abrir_carpeta(ruta_abs)
        ruta_copiada = self.app.file_manager.copiar_ruta(ruta_abs)
        
        if carpeta_abierta and ruta_copiada:
            self.app.ui_callbacks.actualizar_estado(f"✅ Carpeta abierta y ruta copiada: {seleccion['nombre']}")
        elif carpeta_abierta:
            self.app.ui_callbacks.actualizar_estado(f"📂 Carpeta abierta (error copiando ruta): {seleccion['nombre']}")
        elif ruta_copiada:
            self.app.ui_callbacks.actualizar_estado(f"📋 Ruta copiada (error abriendo carpeta): {seleccion['nombre']}")
        else:
            self.app.ui_callbacks.actualizar_estado(f"❌ Error al abrir y copiar: {seleccion['nombre']}")
    
    def copiar_ruta_seleccionada(self):
        """Copia la ruta de la carpeta seleccionada"""
        seleccion = self.app.ui_callbacks.obtener_seleccion_tabla()
        if not seleccion:
            self.app.ui_callbacks.mostrar_advertencia("Seleccione una carpeta primero")
            return
        
        ruta_abs = self.app.file_manager.obtener_ruta_absoluta(
            self.app.ruta_carpeta, seleccion['ruta_rel']
        )
        
        if self.app.file_manager.copiar_ruta(ruta_abs):
            self.app.ui_callbacks.actualizar_estado(f"Ruta copiada: {seleccion['nombre']}")
        else:
            self.app.ui_callbacks.actualizar_estado(f"Error al copiar: {seleccion['nombre']}")