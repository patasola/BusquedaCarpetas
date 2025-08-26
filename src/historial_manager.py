# src/historial_manager.py - Barra Lateral Integrada V.4.1 (Búsqueda Optimizada)
import os
import tkinter as tk
from tkinter import messagebox, ttk
import time
import json
import threading
from .constants import Colors

class HistorialManager:
    """Gestor de historial como barra lateral integrada"""
    
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.barra_historial = None
        self.tree = None
        # HISTORIAL SOLO DE LA SESIÓN ACTUAL
        self.historial = []
        self.visible = False
        
        # Para ordenamiento de columnas - SOLO 2 COLUMNAS
        self.orden_columnas = {
            'Hora': 'asc',
            'Criterio': 'asc'
        }
    
    def toggle_visibility(self):
        """Alterna la visibilidad de la barra de historial"""
        if self.visible:
            self.ocultar()
        else:
            self.mostrar()
        
        # Actualizar el menú Ver
        self.parent_app._actualizar_menu_ver()
    
    def mostrar(self):
        """Muestra la barra de historial integrada"""
        if self.visible:
            return
        
        # AJUSTAR LAYOUT PRINCIPAL PARA HACER ESPACIO
        self.parent_app.ajustar_layout_para_historial(True)
        
        self._crear_barra_lateral()
        self.visible = True
        
        # ACTUALIZAR NAVEGACIÓN TAB PARA INCLUIR EL HISTORIAL
        self.parent_app.actualizar_navegacion_tab()
    
    def ocultar(self):
        """Oculta la barra de historial"""
        if self.barra_historial:
            self.barra_historial.destroy()
            self.barra_historial = None
            self.tree = None
        
        # RESTAURAR LAYOUT PRINCIPAL
        self.parent_app.ajustar_layout_para_historial(False)
        
        self.visible = False
        
        # ACTUALIZAR EL TICK DEL MENÚ Y NAVEGACIÓN TAB
        self.parent_app._actualizar_menu_ver()
    
    def _crear_barra_lateral(self):
        """Crea la barra lateral de historial integrada"""
        
        # Crear frame lateral en la ventana principal - SIN BORDES
        self.barra_historial = tk.Frame(
            self.parent_app.master,
            bg=Colors.BACKGROUND,
            width=350
            # Sin relief ni borderwidth para que se mezcle
        )
        
        # Posicionar a la derecha usando pack - PEGADO AL BORDE DERECHO
        self.barra_historial.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)
        self.barra_historial.pack_propagate(False)
        
        # Header de la barra - COLOR CONSISTENTE CON LA APP
        header_frame = tk.Frame(self.barra_historial, bg=Colors.BACKGROUND, height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Título con colores de la app
        titulo_label = tk.Label(
            header_frame,
            text="📋 Historial de Búsquedas",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TITLE_FG,  # Mismo color que los títulos de la app
            anchor="w"
        )
        titulo_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Botón cerrar con colores de la app
        btn_cerrar_header = tk.Button(
            header_frame,
            text="✕",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.BUTTON_BG,
            fg=Colors.BUTTON_FG,
            relief=tk.FLAT,
            width=3,
            command=self.ocultar,
            cursor="hand2"
        )
        btn_cerrar_header.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Área de contenido
        contenido_frame = tk.Frame(self.barra_historial, bg=Colors.BACKGROUND)
        contenido_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # TreeView del historial - IGUAL FORMATO QUE LA APP PRINCIPAL
        self.tree = ttk.Treeview(
            contenido_frame,
            columns=("Hora", "Criterio"),
            show="headings",
            selectmode="browse",
            height=20,
            style="Custom.Treeview"  # Mismo estilo que la tabla principal
        )
        
        # Configurar encabezados clickeables - SIN FLECHITAS Y CENTRADOS
        self.tree.heading("Hora", text="Hora", anchor=tk.CENTER,
                         command=lambda: self._ordenar_por_columna('Hora'))
        self.tree.heading("Criterio", text="Criterio", anchor=tk.CENTER,
                         command=lambda: self._ordenar_por_columna('Criterio'))
        
        # Configurar columnas - SIN FLECHITAS, CONTENIDO CENTRADO
        self.tree.column("Hora", width=80, anchor=tk.CENTER)
        self.tree.column("Criterio", width=250, anchor=tk.CENTER)
        
        # Scrollbar solo si es necesaria
        scrollbar = ttk.Scrollbar(contenido_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar con scrollbar automática
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar estilos de filas
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('oddrow', background='#f8f9fa')
        
        # Frame de botones inferior - SOLO BOTÓN LIMPIAR
        botones_frame = tk.Frame(self.barra_historial, bg=Colors.BACKGROUND, height=60)
        botones_frame.pack(fill=tk.X, side=tk.BOTTOM)
        botones_frame.pack_propagate(False)
        
        # Solo botón limpiar centrado
        btn_limpiar = tk.Button(
            botones_frame,
            text="🗑️ Limpiar",
            font=("Segoe UI", 9),
            bg="#ffebee",
            fg="#c62828",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self._limpiar_historial,
            cursor="hand2"
        )
        btn_limpiar.pack(pady=15)  # Centrado
        
        # Configurar eventos
        self.tree.bind("<<TreeviewSelect>>", self._on_seleccion)
        self.tree.bind("<Double-1>", lambda e: self._repetir_busqueda())
        self.tree.bind("<Return>", lambda e: self._repetir_busqueda())
        self.tree.bind("<F3>", lambda e: self._repetir_busqueda())
        self.tree.bind("<F4>", lambda e: self._abrir_primera_carpeta())
        self.tree.bind("<Delete>", lambda e: self._eliminar_entrada())
        
        # NAVEGACIÓN CON FLECHAS EN EL HISTORIAL
        self.tree.bind("<Up>", self._manejar_navegacion_historial)
        self.tree.bind("<Down>", self._manejar_navegacion_historial)
        self.tree.bind("<Prior>", self._manejar_navegacion_historial)  # Page Up
        self.tree.bind("<Next>", self._manejar_navegacion_historial)   # Page Down
        self.tree.bind("<Home>", self._manejar_navegacion_historial)
        self.tree.bind("<End>", self._manejar_navegacion_historial)
        
        # MEJORAR EL FOCO EN EL HISTORIAL
        self.tree.bind("<FocusIn>", self._on_focus_in_historial)
        
        # Llenar con datos
        self._actualizar_tabla()
        
        # Forzar actualización visual
        self.parent_app.master.update_idletasks()
    
    def _actualizar_tabla(self):
        """Actualiza la tabla del historial"""
        if not self.tree:
            return
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.historial:
            # Mostrar mensaje cuando está vacío - SIN COLUMNA RESULTADOS
            self.tree.insert("", "end", 
                           values=("--:--", "Sin búsquedas aún"),
                           tags=('evenrow',))
            return
        
        # Agregar entradas del historial - SIN COLUMNA RESULTADOS
        for i, entrada in enumerate(self.historial):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Truncar criterio para barra lateral
            criterio = entrada["criterio"]
            if len(criterio) > 35:
                criterio = criterio[:32] + "..."
            
            self.tree.insert("", "end",
                           values=(
                               entrada["hora"],
                               criterio
                           ),
                           tags=(tag,))
    
    def _on_seleccion(self, event):
        """Maneja la selección en la barra de historial - OPTIMIZADO"""
        if not self.tree.selection() or not self.historial:
            return
            
        # Obtener entrada seleccionada
        item_id = self.tree.selection()[0]
        item_index = self.tree.index(item_id)
        
        # Verificar que no sea la fila de "Sin búsquedas aún"
        if not self.historial:
            return
            
        if 0 <= item_index < len(self.historial):
            entrada = self.historial[item_index]
            criterio = entrada["criterio"]
            
            # Establecer criterio en campo principal
            self.parent_app.entry.delete(0, tk.END)
            self.parent_app.entry.insert(0, criterio)
            
            # OPTIMIZADO: Búsqueda SOLO en cache para historial
            print(f"📋 HISTORIAL: Búsqueda rápida desde cache para '{criterio}'")
            self._busqueda_rapida_cache(criterio)
    
    def _busqueda_rapida_cache(self, criterio):
        """NUEVO: Búsqueda rápida solo en cache para historial"""
        try:
            # Verificar si hay cache válido
            if not self.parent_app.cache_manager.cache.valido:
                print("📋 HISTORIAL: Cache no válido, mostrando mensaje")
                self.parent_app.ui_callbacks.actualizar_estado("📋 Cache no disponible para búsqueda rápida")
                return
            
            # Buscar solo en cache (mucho más rápido)
            print(f"📋 HISTORIAL: Buscando '{criterio}' solo en cache...")
            resultados = self.parent_app.cache_manager.buscar_en_cache(criterio)
            
            if resultados:
                print(f"📋 HISTORIAL: Cache encontró {len(resultados)} resultados")
                self._mostrar_resultados_rapidos(resultados, "Cache (Historial)")
            else:
                print(f"📋 HISTORIAL: Cache sin resultados para '{criterio}'")
                self.parent_app.ui_callbacks.actualizar_estado(f"📋 Sin resultados en cache para '{criterio}' (usar búsqueda normal para tradicional)")
                # Limpiar tabla si no hay resultados
                self.parent_app.ui_callbacks.limpiar_resultados()
                
        except Exception as e:
            print(f"📋 ERROR en búsqueda rápida: {e}")
            self.parent_app.ui_callbacks.actualizar_estado("📋 Error en búsqueda rápida desde historial")
    
    def _mostrar_resultados_rapidos(self, resultados, metodo):
        """Muestra resultados de búsqueda rápida desde historial"""
        print(f"📋 HISTORIAL._MOSTRAR_RESULTADOS_RAPIDOS: {len(resultados)} resultados, método={metodo}")
        
        # USAR tree_explorer si está disponible (V.4.1)
        if hasattr(self.parent_app, 'tree_explorer') and self.parent_app.tree_explorer:
            print("📋 HISTORIAL: Usando tree_explorer para mostrar resultados rápidos")
            # Formatear resultados para tree_explorer
            formatted_results = []
            for nombre, ruta_rel, ruta_abs in resultados:
                formatted_results.append({
                    'name': nombre,
                    'path': ruta_abs,
                    'files': 0,  # No calcular para speed
                    'size': '0 B'  # No calcular para speed
                })
            
            # Usar tree_explorer para mostrar
            self.parent_app.tree_explorer.populate_search_results(formatted_results)
            
        else:
            print("📋 HISTORIAL: Usando TreeView V.4.0 (fallback)")
            # Fallback: Limpiar tabla principal
            for item in self.parent_app.tree.get_children():
                self.parent_app.tree.delete(item)
            
            # Insertar resultados formato V.4.1
            for i, (nombre, ruta_rel, ruta_abs) in enumerate(resultados):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.parent_app.tree.insert("", "end", 
                                          text=f"📂 {nombre}",
                                          values=(metodo, ruta_rel),
                                          tags=(tag,))
        
        # Actualizar estado
        self.parent_app.ui_callbacks.actualizar_estado(
            f"📋 {len(resultados)} resultados desde cache (historial) - Búsqueda rápida"
        )
        
        # Configurar scrollbars
        if hasattr(self.parent_app, 'configurar_scrollbars'):
            self.parent_app.configurar_scrollbars()
    
    def _ordenar_por_columna(self, columna):
        """Ordena el historial por la columna especificada"""
        # CORREGIDO: Solo 2 columnas válidas
        columnas_validas = ['Hora', 'Criterio']
        
        if columna not in columnas_validas:
            return
        
        # Alternar orden
        orden_actual = self.orden_columnas[columna]
        nuevo_orden = 'desc' if orden_actual == 'asc' else 'asc'
        self.orden_columnas[columna] = nuevo_orden
        
        # Actualizar encabezado
        simbolo = '↑' if nuevo_orden == 'asc' else '↓'
        self.tree.heading(columna, text=f"{columna} {simbolo}")
        
        # Limpiar otros encabezados - SIN FLECHITAS
        for col in columnas_validas:
            if col != columna:
                self.tree.heading(col, text=col)
                self.orden_columnas[col] = 'asc'
        
        # Ordenar historial
        reverse = (nuevo_orden == 'desc')
        
        if columna == 'Hora':
            self.historial.sort(key=lambda x: x['timestamp'], reverse=reverse)
        elif columna == 'Criterio':
            self.historial.sort(key=lambda x: x['criterio'].lower(), reverse=reverse)
        
        # Actualizar tabla
        self._actualizar_tabla()
    
    def _repetir_busqueda(self):
        """Repite la búsqueda seleccionada como búsqueda COMPLETA"""
        if not self.tree.selection() or not self.historial:
            return
        
        item_id = self.tree.selection()[0]
        item_index = self.tree.index(item_id)
        
        if 0 <= item_index < len(self.historial):
            entrada = self.historial[item_index]
            
            # Ejecutar búsqueda COMPLETA (cache + tradicional si es necesario)
            print(f"📋 HISTORIAL: Ejecutando búsqueda COMPLETA para '{entrada['criterio']}'")
            self.parent_app.entry.delete(0, tk.END)
            self.parent_app.entry.insert(0, entrada["criterio"])
            self.parent_app.entry.focus()
            self.parent_app.buscar_carpeta()
    
    def _abrir_primera_carpeta(self):
        """Abre la primera carpeta encontrada en la búsqueda seleccionada"""
        if not self.tree.selection() or not self.historial:
            return
        
        # Repetir búsqueda primero
        self._repetir_busqueda()
        
        # Esperar y abrir primera carpeta
        def abrir_despues():
            if self.parent_app.tree.get_children():
                primer_item = self.parent_app.tree.get_children()[0]
                self.parent_app.tree.selection_set(primer_item)
                self.parent_app.tree.focus(primer_item)
                self.parent_app.abrir_carpeta_seleccionada()
        
        self.parent_app.master.after(500, abrir_despues)
    
    def _eliminar_entrada(self):
        """Elimina la entrada seleccionada del historial"""
        if not self.tree.selection() or not self.historial:
            return
        
        item_id = self.tree.selection()[0]
        item_index = self.tree.index(item_id)
        
        if 0 <= item_index < len(self.historial):
            del self.historial[item_index]
            self._actualizar_tabla()
    
    def _limpiar_historial(self):
        """Limpia todo el historial de la sesión"""
        if not self.historial:
            return
            
        if messagebox.askquestion("Limpiar historial", 
                                 "¿Limpiar todo el historial de esta sesión?") == "yes":
            self.historial.clear()
            self._actualizar_tabla()
    
    def agregar_busqueda(self, criterio, metodo, num_resultados, tiempo):
        """Agrega una nueva búsqueda al historial"""
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
        
        # Agregar al inicio (más reciente primero)
        self.historial.insert(0, entrada)
        
        # Limitar a 50 entradas por sesión
        if len(self.historial) > 50:
            self.historial = self.historial[:50]
        
        # Actualizar tabla si está visible
        if self.visible and self.tree:
            self._actualizar_tabla()
            # Actualizar navegación Tab
            self.parent_app.actualizar_navegacion_tab()
    
    def _manejar_navegacion_historial(self, event):
        """Maneja la navegación con flechas dentro del historial"""
        if not self.tree:
            return "break"
        
        elementos = self.tree.get_children()
        if not elementos:
            return "break"
        
        # CORREGIDO: No depender del historial real, usar los elementos del TreeView
        seleccion_actual = self.tree.selection()
        
        if not seleccion_actual:
            # Si no hay selección, ir al primer elemento
            self.tree.selection_set(elementos[0])
            self.tree.focus(elementos[0])
            self.tree.see(elementos[0])
            return "break"
        
        # Encontrar el índice actual
        try:
            indice_actual = elementos.index(seleccion_actual[0])
        except ValueError:
            # Si hay problemas, ir al primer elemento
            self.tree.selection_set(elementos[0])
            self.tree.focus(elementos[0])
            self.tree.see(elementos[0])
            return "break"
        
        nuevo_indice = indice_actual
        
        if event.keysym == "Up":
            nuevo_indice = max(0, indice_actual - 1)
        elif event.keysym == "Down":
            nuevo_indice = min(len(elementos) - 1, indice_actual + 1)
        elif event.keysym == "Prior":  # Page Up
            nuevo_indice = max(0, indice_actual - 5)
        elif event.keysym == "Next":   # Page Down
            nuevo_indice = min(len(elementos) - 1, indice_actual + 5)
        elif event.keysym == "Home":
            nuevo_indice = 0
        elif event.keysym == "End":
            nuevo_indice = len(elementos) - 1
        
        # Solo cambiar si es diferente
        if nuevo_indice != indice_actual and 0 <= nuevo_indice < len(elementos):
            nuevo_elemento = elementos[nuevo_indice]
            self.tree.selection_set(nuevo_elemento)
            self.tree.focus(nuevo_elemento)
            self.tree.see(nuevo_elemento)
        
        return "break"
    
    def _on_focus_in_historial(self, event):
        """Maneja cuando el TreeView del historial recibe el foco"""
        if not self.tree:
            return
        
        elementos = self.tree.get_children()
        if elementos and not self.tree.selection():
            # Si hay elementos pero no hay selección, seleccionar el primero
            self.tree.selection_set(elementos[0])
            self.tree.focus(elementos[0])
            self.tree.see(elementos[0])
    
    # NO persistir historial - solo sesión actual