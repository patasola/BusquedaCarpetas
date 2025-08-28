# src/historial_manager.py - Barra Lateral de Historial V.4.2 (Refactorizada)
import os
import tkinter as tk
from tkinter import messagebox, ttk
import time
from .constants import Colors

class HistorialManager:
    """Gestor de historial como barra lateral integrada"""
    
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.barra_historial = None
        self.tree = None
        self.historial = []
        self.visible = False
        self.orden_columnas = {'Hora': 'asc', 'Criterio': 'asc'}
    
    def toggle_visibility(self):
        """Alterna visibilidad de la barra de historial"""
        if self.visible:
            self.ocultar()
        else:
            self.mostrar()
        
        if hasattr(self.parent_app, '_actualizar_menu_ver'):
            self.parent_app._actualizar_menu_ver()
    
    def mostrar(self):
        """Muestra la barra de historial"""
        if self.visible:
            return
        
        if hasattr(self.parent_app, 'ajustar_layout_para_historial'):
            self.parent_app.ajustar_layout_para_historial(True)
        
        self._crear_barra_lateral()
        self.visible = True
        
        if hasattr(self.parent_app, 'actualizar_navegacion_tab'):
            self.parent_app.actualizar_navegacion_tab()
    
    def ocultar(self):
        """Oculta la barra de historial"""
        if self.barra_historial:
            self.barra_historial.destroy()
            self.barra_historial = None
            self.tree = None
        
        if hasattr(self.parent_app, 'ajustar_layout_para_historial'):
            self.parent_app.ajustar_layout_para_historial(False)
        
        self.visible = False
        
        if hasattr(self.parent_app, '_actualizar_menu_ver'):
            self.parent_app._actualizar_menu_ver()
    
    def _crear_barra_lateral(self):
        """Crea la barra lateral de historial"""
        try:
            parent_container = self.parent_app.main_container.master
            
            # Frame lateral
            self.barra_historial = tk.Frame(
                parent_container,
                bg=Colors.BACKGROUND,
                width=380,
                relief=tk.RIDGE,
                borderwidth=1
            )
            self.barra_historial.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 10), pady=10)
            self.barra_historial.pack_propagate(False)
            
            # Header
            header = tk.Frame(self.barra_historial, bg=Colors.BACKGROUND, height=50)
            header.pack(fill=tk.X, padx=5, pady=5)
            header.pack_propagate(False)
            
            tk.Label(
                header,
                text="Historial de Búsquedas",
                font=("Segoe UI", 12, "bold"),
                bg=Colors.BACKGROUND,
                fg=Colors.TITLE_FG,
                anchor="w"
            ).pack(side=tk.LEFT, padx=10, pady=10)
            
            tk.Button(
                header,
                text="✕",
                font=("Segoe UI", 10, "bold"),
                bg=Colors.BUTTON_BG,
                fg=Colors.BUTTON_FG,
                relief=tk.FLAT,
                width=3,
                command=self.ocultar,
                cursor="hand2"
            ).pack(side=tk.RIGHT, padx=10, pady=10)
            
            # Contenido
            contenido = tk.Frame(self.barra_historial, bg=Colors.BACKGROUND)
            contenido.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # TreeView frame
            tree_frame = tk.Frame(contenido, bg=Colors.BACKGROUND)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            # TreeView del historial
            self.tree = ttk.Treeview(
                tree_frame,
                columns=("Hora", "Criterio"),
                show="headings",
                selectmode="browse",
                height=18,
                style="Custom.Treeview"
            )
            
            # Configurar encabezados clickeables
            self.tree.heading("Hora", text="Hora", anchor=tk.CENTER,
                             command=lambda: self._ordenar_por_columna('Hora'))
            self.tree.heading("Criterio", text="Criterio", anchor=tk.CENTER,
                             command=lambda: self._ordenar_por_columna('Criterio'))
            
            # Configurar columnas
            self.tree.column("Hora", width=80, anchor=tk.CENTER, minwidth=70)
            self.tree.column("Criterio", width=280, anchor=tk.W, minwidth=200)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)
            
            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Configurar estilos
            self.tree.tag_configure('evenrow', background='#ffffff')
            self.tree.tag_configure('oddrow', background='#f8f9fa')
            
            # Frame de botones
            botones_frame = tk.Frame(self.barra_historial, bg=Colors.BACKGROUND, height=60)
            botones_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
            botones_frame.pack_propagate(False)
            
            tk.Button(
                botones_frame,
                text="Limpiar",
                font=("Segoe UI", 9),
                bg="#ffebee",
                fg="#c62828",
                relief=tk.FLAT,
                padx=15,
                pady=8,
                command=self._limpiar_historial,
                cursor="hand2"
            ).pack(pady=15)
            
            # Eventos
            self._configurar_eventos()
            self._actualizar_tabla()
            
            self.parent_app.master.update_idletasks()
            
        except Exception as e:
            print(f"Error creando barra historial: {e}")
    
    def _configurar_eventos(self):
        """Configura eventos del historial"""
        eventos = {
            "<<TreeviewSelect>>": self._on_seleccion,
            "<Double-1>": lambda e: self._repetir_busqueda(),
            "<Return>": lambda e: self._repetir_busqueda(),
            "<F3>": lambda e: self._repetir_busqueda(),
            "<F4>": lambda e: self._abrir_primera_carpeta(),
            "<Delete>": lambda e: self._eliminar_entrada(),
            "<FocusIn>": self._on_focus_in_historial
        }
        
        for evento, comando in eventos.items():
            self.tree.bind(evento, comando)
        
        # Navegación
        nav_keys = ["<Up>", "<Down>", "<Prior>", "<Next>", "<Home>", "<End>"]
        for key in nav_keys:
            self.tree.bind(key, self._manejar_navegacion_historial)
    
    def _actualizar_tabla(self):
        """Actualiza la tabla del historial"""
        if not self.tree:
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.historial:
            self.tree.insert("", "end", 
                           values=("--:--", "Sin búsquedas aún"),
                           tags=('evenrow',))
            return
        
        for i, entrada in enumerate(self.historial):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            criterio = entrada["criterio"]
            if len(criterio) > 35:
                criterio = criterio[:32] + "..."
            
            self.tree.insert("", "end",
                           values=(entrada["hora"], criterio),
                           tags=(tag,))
    
    def _on_seleccion(self, event):
        """Maneja selección en la barra de historial"""
        if not self.tree.selection() or not self.historial:
            return
        
        item_index = self.tree.index(self.tree.selection()[0])
        
        if 0 <= item_index < len(self.historial):
            entrada = self.historial[item_index]
            criterio = entrada["criterio"]
            
            self.parent_app.entry.delete(0, tk.END)
            self.parent_app.entry.insert(0, criterio)
            
            self._busqueda_rapida_cache(criterio)
    
    def _busqueda_rapida_cache(self, criterio):
        """Búsqueda rápida solo en cache para historial"""
        try:
            if not self.parent_app.cache_manager.cache.valido:
                if hasattr(self.parent_app, 'ui_callbacks'):
                    self.parent_app.ui_callbacks.actualizar_estado("Cache no disponible")
                return
            
            resultados = self.parent_app.cache_manager.buscar_en_cache(criterio)
            
            if resultados:
                self._mostrar_resultados_rapidos(resultados, "Cache (Historial)")
            else:
                if hasattr(self.parent_app, 'ui_callbacks'):
                    self.parent_app.ui_callbacks.actualizar_estado(
                        f"Sin resultados en cache para '{criterio}'"
                    )
                    self.parent_app.ui_callbacks.limpiar_resultados()
                
        except Exception as e:
            print(f"Error en búsqueda rápida: {e}")
    
    def _mostrar_resultados_rapidos(self, resultados, metodo):
        """Muestra resultados de búsqueda rápida"""
        if hasattr(self.parent_app, 'tree_explorer') and self.parent_app.tree_explorer:
            formatted_results = []
            for nombre, ruta_rel, ruta_abs in resultados:
                formatted_results.append({
                    'name': nombre,
                    'path': ruta_abs,
                    'files': 0,
                    'size': '0 B'
                })
            
            self.parent_app.tree_explorer.populate_search_results(formatted_results)
        else:
            # Fallback
            for item in self.parent_app.tree.get_children():
                self.parent_app.tree.delete(item)
            
            for i, (nombre, ruta_rel, ruta_abs) in enumerate(resultados):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.parent_app.tree.insert("", "end", 
                                          text=f"📂 {nombre}",
                                          values=(metodo, ruta_rel),
                                          tags=(tag,))
        
        if hasattr(self.parent_app, 'ui_callbacks'):
            self.parent_app.ui_callbacks.actualizar_estado(
                f"{len(resultados)} resultados desde cache (historial)"
            )
        
        if hasattr(self.parent_app, 'configurar_scrollbars'):
            self.parent_app.configurar_scrollbars()
    
    def _ordenar_por_columna(self, columna):
        """Ordena el historial por columna"""
        if columna not in ['Hora', 'Criterio']:
            return
        
        orden_actual = self.orden_columnas[columna]
        nuevo_orden = 'desc' if orden_actual == 'asc' else 'asc'
        self.orden_columnas[columna] = nuevo_orden
        
        simbolo = '↑' if nuevo_orden == 'asc' else '↓'
        self.tree.heading(columna, text=f"{columna} {simbolo}")
        
        # Limpiar otros encabezados
        for col in ['Hora', 'Criterio']:
            if col != columna:
                self.tree.heading(col, text=col)
                self.orden_columnas[col] = 'asc'
        
        # Ordenar
        reverse = (nuevo_orden == 'desc')
        if columna == 'Hora':
            self.historial.sort(key=lambda x: x['timestamp'], reverse=reverse)
        elif columna == 'Criterio':
            self.historial.sort(key=lambda x: x['criterio'].lower(), reverse=reverse)
        
        self._actualizar_tabla()
    
    def _repetir_busqueda(self):
        """Repite la búsqueda seleccionada"""
        if not self.tree.selection() or not self.historial:
            return
        
        item_index = self.tree.index(self.tree.selection()[0])
        if 0 <= item_index < len(self.historial):
            entrada = self.historial[item_index]
            self.parent_app.entry.delete(0, tk.END)
            self.parent_app.entry.insert(0, entrada["criterio"])
            self.parent_app.entry.focus()
            self.parent_app.buscar_carpeta()
    
    def _abrir_primera_carpeta(self):
        """Abre la primera carpeta de la búsqueda seleccionada"""
        self._repetir_busqueda()
        
        def abrir_despues():
            if self.parent_app.tree.get_children():
                primer_item = self.parent_app.tree.get_children()[0]
                self.parent_app.tree.selection_set(primer_item)
                self.parent_app.tree.focus(primer_item)
                if hasattr(self.parent_app, 'abrir_carpeta_seleccionada'):
                    self.parent_app.abrir_carpeta_seleccionada()
        
        self.parent_app.master.after(500, abrir_despues)
    
    def _eliminar_entrada(self):
        """Elimina entrada seleccionada del historial"""
        if not self.tree.selection() or not self.historial:
            return
        
        item_index = self.tree.index(self.tree.selection()[0])
        if 0 <= item_index < len(self.historial):
            del self.historial[item_index]
            self._actualizar_tabla()
    
    def _limpiar_historial(self):
        """Limpia todo el historial"""
        if not self.historial:
            return
        
        if messagebox.askquestion("Limpiar historial", 
                                 "¿Limpiar todo el historial de esta sesión?") == "yes":
            self.historial.clear()
            self._actualizar_tabla()
    
    def _manejar_navegacion_historial(self, event):
        """Maneja navegación con flechas"""
        elementos = self.tree.get_children()
        if not elementos:
            return "break"
        
        seleccion = self.tree.selection()
        if not seleccion:
            self._seleccionar_item(elementos[0])
            return "break"
        
        try:
            indice = elementos.index(seleccion[0])
        except ValueError:
            self._seleccionar_item(elementos[0])
            return "break"
        
        movimientos = {
            "Up": max(0, indice - 1),
            "Down": min(len(elementos) - 1, indice + 1),
            "Prior": max(0, indice - 5),
            "Next": min(len(elementos) - 1, indice + 5),
            "Home": 0,
            "End": len(elementos) - 1
        }
        
        nuevo_indice = movimientos.get(event.keysym, indice)
        if nuevo_indice != indice:
            self._seleccionar_item(elementos[nuevo_indice])
        
        return "break"
    
    def _seleccionar_item(self, elemento):
        """Selecciona un item del historial"""
        self.tree.selection_set(elemento)
        self.tree.focus(elemento)
        self.tree.see(elemento)
    
    def _on_focus_in_historial(self, event):
        """Maneja cuando el historial recibe foco"""
        elementos = self.tree.get_children()
        if elementos and not self.tree.selection():
            self._seleccionar_item(elementos[0])
    
    def agregar_busqueda(self, criterio, metodo, num_resultados, tiempo):
        """Agrega nueva búsqueda al historial"""
        entrada = {
            "timestamp": time.time(),
            "hora": time.strftime("%H:%M:%S"),
            "fecha": time.strftime("%d/%m/%Y"),
            "criterio": criterio,
            "metodo": metodo,
            "resultados": num_resultados,
            "tiempo": tiempo,
            "ruta_base": self.parent_app.ruta_carpeta
        }
        
        self.historial.insert(0, entrada)
        
        # Limitar a 50 entradas
        if len(self.historial) > 50:
            self.historial = self.historial[:50]
        
        if self.visible and self.tree:
            self._actualizar_tabla()
            if hasattr(self.parent_app, 'actualizar_navegacion_tab'):
                self.parent_app.actualizar_navegacion_tab()