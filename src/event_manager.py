# src/event_manager.py - Gestión de Eventos V.4.2 (Mensajes corregidos)
import tkinter as tk
import os
import subprocess

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
        """Abre la carpeta seleccionada - CORREGIDO FINAL"""
        seleccion = self.app.ui_callbacks.obtener_seleccion_tabla()
        if not seleccion:
            self._actualizar_estado("Seleccione una carpeta primero")
            return
        
        # Obtener ruta absoluta correcta
        ruta_rel = seleccion['ruta_rel']
        
        # Si ya es una ruta absoluta, usarla directamente
        if os.path.isabs(ruta_rel):
            ruta_abs = ruta_rel
        else:
            # Construir ruta absoluta desde la ruta base
            ruta_abs = os.path.join(self.app.ruta_carpeta, ruta_rel)
        
        # Normalizar la ruta
        ruta_abs = os.path.normpath(ruta_abs)
        nombre = seleccion['nombre']
        
        # Verificar que la carpeta existe ANTES de intentar abrir
        if not os.path.exists(ruta_abs):
            self._actualizar_estado(f"La carpeta no existe: {nombre}")
            return
        
        if not os.path.isdir(ruta_abs):
            self._actualizar_estado(f"La ruta no es un directorio: {nombre}")
            return
        
        try:
            # USAR DIRECTAMENTE el método que sabemos que funciona
            exito = self._abrir_carpeta_directo(ruta_abs)
            
            if exito:
                # También copiar la ruta al portapapeles
                if self._copiar_ruta_portapapeles(ruta_abs):
                    self._actualizar_estado(f"Carpeta abierta y ruta copiada: {nombre}")
                else:
                    self._actualizar_estado(f"Carpeta abierta: {nombre}")
            else:
                self._actualizar_estado(f"No se pudo abrir la carpeta: {nombre}")
                
        except Exception as e:
            self._actualizar_estado(f"Error abriendo carpeta {nombre}: {str(e)}")
    
    def _abrir_carpeta_directo(self, ruta):
        """Abre carpeta directamente usando subprocess - CORREGIDO DEFINITIVO"""
        try:
            import platform
            
            sistema = platform.system()
            
            if sistema == "Windows":
                # Para Windows: usar os.startfile que es más confiable
                try:
                    os.startfile(ruta)
                    return True
                except OSError:
                    # Fallback con subprocess sin verificar returncode
                    subprocess.Popen(['explorer', ruta])
                    return True
            elif sistema == "Darwin":
                subprocess.Popen(['open', ruta])
                return True
            else:
                subprocess.Popen(['xdg-open', ruta])
                return True
            
        except Exception as e:
            print(f"Error abriendo carpeta directamente: {e}")
            return False
    
    def _copiar_ruta_portapapeles(self, ruta):
        """Copia ruta al portapapeles"""
        try:
            self.app.master.clipboard_clear()
            self.app.master.clipboard_append(ruta)
            return True
        except Exception as e:
            print(f"Error copiando al portapapeles: {e}")
            return False
    
    def copiar_ruta_seleccionada(self):
        """Copia la ruta de la carpeta seleccionada"""
        seleccion = self.app.ui_callbacks.obtener_seleccion_tabla()
        if not seleccion:
            self._actualizar_estado("Seleccione una carpeta primero")
            return
        
        # Obtener ruta absoluta correcta
        ruta_rel = seleccion['ruta_rel']
        
        # Si ya es una ruta absoluta, usarla directamente
        if os.path.isabs(ruta_rel):
            ruta_abs = ruta_rel
        else:
            # Construir ruta absoluta desde la ruta base
            ruta_abs = os.path.join(self.app.ruta_carpeta, ruta_rel)
        
        # Normalizar la ruta
        ruta_abs = os.path.normpath(ruta_abs)
        nombre = seleccion['nombre']
        
        try:
            if self._copiar_ruta_portapapeles(ruta_abs):
                self._actualizar_estado(f"Ruta copiada: {nombre}")
            else:
                self._actualizar_estado(f"Error copiando ruta: {nombre}")
                    
        except Exception as e:
            self._actualizar_estado(f"Error copiando ruta {nombre}: {str(e)}")
    
    def _actualizar_estado(self, mensaje):
        """Helper para actualizar estado"""
        self.app.ui_callbacks.actualizar_estado(mensaje)