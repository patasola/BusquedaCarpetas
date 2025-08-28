# src/event_manager.py - Gestión de Eventos V.4.2 (Refactorizado y Corregido)
import tkinter as tk

class EventManager:
    """Maneja todos los eventos de la aplicación"""
    
    def __init__(self, app):
        self.app = app
    
    def configurar_eventos(self):
        """Configura todos los eventos de la aplicación"""
        self._config_atajos_teclado()
        self._config_eventos_entry()
        self._config_eventos_tree()
        self._config_eventos_botones()
    
    def _config_atajos_teclado(self):
        """Configura atajos de teclado globales"""
        atajos = {
            "<F1>": lambda e: self.app.manual_viewer.show_manual(),
            "<F2>": lambda e: self._fix_f2_focus(),
            "<F3>": lambda e: self.copiar_ruta_seleccionada(),
            "<F5>": lambda e: self.app.ui_state_manager.cambiar_modo_entrada(),
            "<F11>": lambda e: self.app.window_manager.maximizar_ventana(),
            "<Control-e>": lambda e: self.app.window_manager.centrar_ventana(),
            "<Control-E>": lambda e: self.app.window_manager.centrar_ventana(),
            "<Control-r>": lambda e: self.app.window_manager.restaurar_ventana(),
            "<Control-R>": lambda e: self.app.window_manager.restaurar_ventana(),
            "<Control-h>": lambda e: self.app.ui_manager.toggle_historial(),
            "<Control-H>": lambda e: self.app.ui_manager.toggle_historial(),
        }
        
        for key, cmd in atajos.items():
            self.app.master.bind(key, cmd)
    
    def _fix_f2_focus(self):
        """Corrige el F2 para que funcione correctamente"""
        try:
            # Habilitar Entry
            self.app.entry.configure(state='normal')
            
            # Limpiar eventos problemáticos del TreeView
            for evento in ['<Key>', '<KeyPress>', '<KeyRelease>', '<Tab>', '<Shift-Tab>']:
                try:
                    self.app.tree.unbind(evento)
                except:
                    pass
            
            # Configurar TreeView y Entry
            self.app.tree.configure(takefocus=False)
            self.app.entry.focus_force()
            self.app.entry.select_range(0, tk.END)
            self.app.entry.icursor(tk.END)
            
            # Restaurar TreeView después
            def restaurar():
                try:
                    self.app.tree.configure(takefocus=True)
                    self.app.tree.bind("<<TreeviewSelect>>", self.app.on_tree_select)
                    self.app.tree.bind("<Double-1>", lambda e: self.abrir_carpeta_seleccionada())
                    self.app.tree.bind("<F3>", lambda e: self.copiar_ruta_seleccionada())
                    self.app.tree.bind("<F4>", lambda e: self.abrir_carpeta_seleccionada())
                except:
                    pass
            
            self.app.master.after(200, restaurar)
            
        except Exception as e:
            print(f"Error en F2: {e}")
    
    def _config_eventos_entry(self):
        """Configura eventos del campo de entrada"""
        self.app.entry.bind("<Return>", lambda e: self.app.buscar_carpeta())
        self.app.entry.bind("<KeyRelease>", self.app.on_entry_change)
    
    def _config_eventos_tree(self):
        """Configura eventos del TreeView"""
        bindings = {
            "<<TreeviewSelect>>": self.app.on_tree_select,
            "<Double-1>": lambda e: self.abrir_carpeta_seleccionada(),
            "<Return>": lambda e: self.abrir_carpeta_seleccionada(),
            "<F3>": lambda e: self.copiar_ruta_seleccionada(),
            "<F4>": lambda e: self.abrir_carpeta_seleccionada(),
        }
        
        for event, cmd in bindings.items():
            self.app.tree.bind(event, cmd)
        
        # Navegación con flechas
        nav_keys = ["<Up>", "<Down>", "<Prior>", "<Next>", "<Home>", "<End>"]
        for key in nav_keys:
            self.app.tree.bind(key, self._manejar_navegacion_tabla)
    
    def _config_eventos_botones(self):
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
        
        seleccion = self.app.tree.selection()
        if not seleccion:
            self._seleccionar_elemento(elementos[0])
            return "break"
        
        elementos_visibles = self._get_elementos_visibles()
        if not elementos_visibles:
            return "break"
        
        try:
            indice = elementos_visibles.index(seleccion[0])
        except ValueError:
            self._seleccionar_elemento(elementos_visibles[0])
            return "break"
        
        # Calcular nuevo índice
        movimientos = {
            "Up": max(0, indice - 1),
            "Down": min(len(elementos_visibles) - 1, indice + 1),
            "Prior": max(0, indice - 5),  # Page Up
            "Next": min(len(elementos_visibles) - 1, indice + 5),  # Page Down
            "Home": 0,
            "End": len(elementos_visibles) - 1
        }
        
        nuevo_indice = movimientos.get(event.keysym, indice)
        if nuevo_indice != indice:
            self._seleccionar_elemento(elementos_visibles[nuevo_indice])
        
        return "break"
    
    def _get_elementos_visibles(self):
        """Obtiene todos los elementos visibles recursivamente"""
        def obtener_recursivo(parent=""):
            items = []
            for child in self.app.tree.get_children(parent):
                items.append(child)
                if self.app.tree.item(child, 'open'):
                    items.extend(obtener_recursivo(child))
            return items
        
        return obtener_recursivo()
    
    def _seleccionar_elemento(self, elemento):
        """Selecciona un elemento del tree"""
        self.app.tree.selection_set(elemento)
        self.app.tree.focus(elemento)
        self.app.tree.see(elemento)
    
    def on_tree_select(self, event):
        """Maneja selección en el TreeView"""
        hay_seleccion = len(self.app.tree.selection()) > 0
        estado = tk.NORMAL if hay_seleccion else tk.DISABLED
        
        self.app.btn_abrir.config(state=estado)
        self.app.btn_copiar.config(state=estado)
        self.app.configurar_scrollbars()
    
    def abrir_carpeta_seleccionada(self):
        """Abre la carpeta seleccionada"""
        seleccion = self.app.ui_callbacks.obtener_seleccion_tabla()
        if not seleccion:
            self._actualizar_estado("Seleccione una carpeta primero")
            return
        
        ruta_abs = self.app.file_manager.obtener_ruta_absoluta(
            self.app.ruta_carpeta, seleccion['ruta_rel']
        )
        
        if not self.app.file_manager.verificar_ruta_existe(ruta_abs):
            self._actualizar_estado(f"La carpeta no existe: {ruta_abs}")
            return
        
        nombre = seleccion['nombre']
        
        try:
            # Intentar abrir y copiar - asumir éxito a menos que haya excepción
            self.app.file_manager.abrir_carpeta(ruta_abs)
            self.app.file_manager.copiar_ruta(ruta_abs)
            
            # Si llegamos aquí, asumir que funcionó
            self._actualizar_estado(f"Carpeta abierta y ruta copiada: {nombre}")
                    
        except Exception as e:
            self._actualizar_estado(f"Error abriendo carpeta: {nombre} - {str(e)}")
    
    def copiar_ruta_seleccionada(self):
        """Copia la ruta de la carpeta seleccionada"""
        seleccion = self.app.ui_callbacks.obtener_seleccion_tabla()
        if not seleccion:
            self._actualizar_estado("Seleccione una carpeta primero")
            return
        
        ruta_abs = self.app.file_manager.obtener_ruta_absoluta(
            self.app.ruta_carpeta, seleccion['ruta_rel']
        )
        
        nombre = seleccion['nombre']
        
        try:
            # Intentar copiar - asumir éxito a menos que haya excepción
            self.app.file_manager.copiar_ruta(ruta_abs)
            self._actualizar_estado(f"Ruta copiada: {nombre}")
                    
        except Exception as e:
            self._actualizar_estado(f"Error copiando ruta: {nombre} - {str(e)}")
    
    def _actualizar_estado(self, mensaje):
        """Helper para actualizar estado"""
        self.app.ui_callbacks.actualizar_estado(mensaje)