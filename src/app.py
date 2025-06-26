# src/app.py - Clase Principal de la Aplicación
"""
Búsqueda Rápida de Carpetas v1.4
Clase principal con interfaz y lógica de aplicación
"""

import tkinter as tk
from tkinter import ttk, filedialog, Menu
import os
import threading
import time

from .config import ConfigManager
from .cache_manger import CacheManager
from .search_engine import SearchEngine
from .ui_components import UIComponents
from utils import FileUtils
from .constants import *

class BusquedaCarpetaApp:
    def __init__(self, master):
        self.master = master
        master.title(APP_TITLE)
        master.geometry(WINDOW_SIZE)
        master.configure(bg=COLORS['background'])
        master.minsize(*MIN_WINDOW_SIZE)

        # Versión de la aplicación
        self.version = APP_VERSION

        # Centrar la ventana
        self.centrar_ventana()

        # Inicializar componentes
        self.config = ConfigManager()
        self.cache_manager = CacheManager(
            progress_callback=self.actualizar_progreso,
            status_callback=self.actualizar_estado
        )
        self.search_engine = SearchEngine(
            progress_callback=self.actualizar_progreso,
            status_callback=self.actualizar_estado,
            results_callback=self.mostrar_resultados_parciales
        )
        self.ui = UIComponents(master)

        # Variables de estado
        self.resultados = []
        self.ruta_carpeta_actual = None

        # Configurar interfaz
        self.crear_interfaz()
        self.crear_menu()
        self.configurar_eventos()

        # Cargar configuración inicial
        self.cargar_configuracion_inicial()

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.master.update_idletasks()
        ancho = self.master.winfo_width()
        alto = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.master.winfo_screenheight() // 2) - (alto // 2)
        self.master.geometry(f'+{x}+{y}')

    def cargar_configuracion_inicial(self):
        """Carga la configuración inicial y actualiza el estado"""
        ruta = self.config.get_folder_path()
        if ruta and FileUtils.is_valid_path(ruta):
            self.ruta_carpeta_actual = ruta
            self.cache_manager.ruta_base = ruta
            
            # Verificar si existe cache para esta ruta
            if self.cache_manager.is_cache_valid(ruta):
                cache_info = self.cache_manager.get_cache_info()
                if cache_info:
                    total_dirs = cache_info['total_directories']
                    self.actualizar_info_cache(
                        f"Carpeta: {FileUtils.get_folder_name(ruta)} | Caché: {total_dirs:,} directorios ✓"
                    )
                else:
                    self.actualizar_info_cache(
                        f"Carpeta: {FileUtils.get_folder_name(ruta)} | Caché: No construido"
                    )
            else:
                self.actualizar_info_cache(
                    f"Carpeta: {FileUtils.get_folder_name(ruta)} | Caché: No construido"
                )
        else:
            self.actualizar_info_cache("Sin carpeta seleccionada")

    def crear_interfaz(self):
        """Crea la interfaz usando el componente UI"""
        # Frame principal
        self.main_frame = self.ui.crear_frame_principal()
        
        # Título
        self.ui.crear_titulo(self.main_frame)
        
        # Campo de búsqueda
        self.entry = self.ui.crear_campo_busqueda(
            self.main_frame, 
            callback_enter=self.buscar_carpeta
        )
        
        # Botones de búsqueda (sin botón de caché)
        self.btn_buscar, self.btn_cancelar = self.ui.crear_botones_busqueda(
            self.main_frame,
            callback_buscar=self.buscar_carpeta,
            callback_cancelar=self.cancelar_operacion
        )
        
        # Barra de progreso
        self.progress, self.label_porcentaje = self.ui.crear_barra_progreso(self.main_frame)
        
        # TreeView de resultados
        self.tree = self.ui.crear_treeview_resultados(
            self.main_frame,
            callback_select=self.actualizar_botones_acciones
        )
        
        # Botones de acciones
        self.btn_copiar, self.btn_abrir = self.ui.crear_botones_acciones(
            self.main_frame,
            callback_copiar=self.copiar_ruta_seleccionada,
            callback_abrir=self.abrir_carpeta_seleccionada
        )
        
        # Barra de estado
        self.label_estado, self.label_version = self.ui.crear_barra_estado(self.main_frame)
        
        # Línea de información de caché (nueva)
        self.label_cache_info = self.ui.crear_info_cache(self.main_frame)

    def crear_menu(self):
        """Crea el menú de la aplicación"""
        menubar = Menu(self.master)
        
        menu_archivo = Menu(menubar, tearoff=0)
        menu_archivo.add_command(
            label="Seleccionar ruta de búsqueda", 
            command=self.seleccionar_ruta_busqueda
        )
        menu_archivo.add_separator()
        menu_archivo.add_command(
            label="Construir caché de directorios", 
            command=self.construir_cache_manual
        )
        menu_archivo.add_command(
            label="Limpiar caché", 
            command=self.limpiar_cache
        )
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.master.quit)
        
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        self.master.config(menu=menubar)

    def configurar_eventos(self):
        """Configura eventos y atajos de teclado"""
        self.master.bind("<F2>", lambda e: self.entry.focus())
        self.master.bind("<F3>", lambda e: self.copiar_ruta_seleccionada())
        self.master.bind("<F4>", lambda e: self.abrir_carpeta_seleccionada())
        
        self.entry.bind("<Return>", lambda e: self.buscar_carpeta())
        self.tree.bind("<<TreeviewSelect>>", self.actualizar_botones_acciones)

    def seleccionar_ruta_busqueda(self):
        """Selecciona ruta y construye caché automáticamente"""
        ruta_inicial = self.ruta_carpeta_actual if self.ruta_carpeta_actual else None
        ruta = filedialog.askdirectory(
            title="Seleccionar ruta de búsqueda",
            initialdir=ruta_inicial
        )
        
        if ruta:
            self.ruta_carpeta_actual = ruta
            self.config.set_folder_path(ruta)
            
            # Limpiar caché anterior
            self.cache_manager.invalidate_cache()
            
            # Actualizar info inmediatamente
            folder_name = FileUtils.get_folder_name(ruta)
            self.actualizar_info_cache(f"Carpeta: {folder_name} | Caché: Construyendo...")
            self.actualizar_estado(f"Ruta establecida: {folder_name} - Construyendo caché automáticamente...")
            
            # Construir caché automáticamente
            self.construir_cache_automatico()

    def construir_cache_automatico(self):
        """Construye el caché automáticamente después de seleccionar carpeta"""
        if not self.ruta_carpeta_actual:
            return
            
        if self.cache_manager.construyendo_cache or self.search_engine.is_searching():
            return
            
        # Deshabilitar botón de búsqueda mientras se construye el caché
        self.btn_buscar.config(state=tk.DISABLED)
        
        # Iniciar construcción del caché
        self.cache_manager.build_cache_async(
            self.ruta_carpeta_actual,
            completion_callback=self.on_cache_build_complete
        )

    def construir_cache_manual(self):
        """Construye el caché manualmente desde el menú"""
        if not self.ruta_carpeta_actual:
            self.actualizar_estado(MESSAGES['no_folder'])
            return
            
        if self.cache_manager.construyendo_cache or self.search_engine.is_searching():
            return
            
        # Deshabilitar botón de búsqueda
        self.btn_buscar.config(state=tk.DISABLED)
        
        folder_name = FileUtils.get_folder_name(self.ruta_carpeta_actual)
        self.actualizar_info_cache(f"Carpeta: {folder_name} | Caché: Construyendo...")
        
        # Iniciar construcción del caché
        self.cache_manager.build_cache_async(
            self.ruta_carpeta_actual,
            completion_callback=self.on_cache_build_complete
        )

    def on_cache_build_complete(self, success, total_dirs):
        """Callback cuando se completa la construcción del caché"""
        self.master.after(0, lambda: self._handle_cache_build_complete(success, total_dirs))

    def _handle_cache_build_complete(self, success, total_dirs):
        """Maneja la finalización de la construcción del caché en el hilo principal"""
        self.btn_buscar.config(state=tk.NORMAL)
        
        if success:
            folder_name = FileUtils.get_folder_name(self.ruta_carpeta_actual)
            self.actualizar_info_cache(
                f"Carpeta: {folder_name} | Caché: {total_dirs:,} directorios ✓"
            )
        else:
            folder_name = FileUtils.get_folder_name(self.ruta_carpeta_actual)
            self.actualizar_info_cache(
                f"Carpeta: {folder_name} | Caché: Error en construcción"
            )

    def limpiar_cache(self):
        """Limpia el caché"""
        self.cache_manager.clear_cache()
        
        if self.ruta_carpeta_actual:
            folder_name = FileUtils.get_folder_name(self.ruta_carpeta_actual)
            self.actualizar_info_cache(f"Carpeta: {folder_name} | Caché: Limpiado")
        else:
            self.actualizar_info_cache("Sin carpeta seleccionada")
            
        self.actualizar_estado(MESSAGES['cache_cleared'])

    def buscar_carpeta(self, event=None):
        """Ejecuta la búsqueda de carpetas"""
        if self.search_engine.is_searching() or self.cache_manager.construyendo_cache:
            return

        if not self.ruta_carpeta_actual:
            self.actualizar_estado(MESSAGES['no_folder'])
            return

        criterio = self.entry.get().strip()
        if not criterio:
            self.actualizar_estado(MESSAGES['no_criteria'])
            return

        # Intentar búsqueda en caché primero
        if self.cache_manager.is_cache_valid(self.ruta_carpeta_actual):
            resultados_cache = self.cache_manager.search_in_cache(
                criterio, 
                status_callback=self.actualizar_estado
            )
            if resultados_cache is not None:
                self.mostrar_resultados(resultados_cache)
                self.progress.config(value=100)
                self.label_porcentaje.config(text="100%")
                return

        # Búsqueda tradicional
        self.preparar_busqueda(criterio)
        self.search_engine.search_async(
            self.ruta_carpeta_actual,
            criterio,
            completion_callback=self.on_search_complete
        )

    def preparar_busqueda(self, criterio):
        """Prepara la interfaz para una búsqueda tradicional"""
        self.limpiar_resultados()
        self.btn_cancelar.config(state=tk.NORMAL)
        self.btn_buscar.config(state=tk.DISABLED)
        self.progress.config(value=0)
        self.label_porcentaje.config(text="0%")

    def on_search_complete(self, success, resultados):
        """Callback cuando se completa la búsqueda"""
        self.master.after(0, lambda: self._handle_search_complete(success, resultados))

    def _handle_search_complete(self, success, resultados):
        """Maneja la finalización de la búsqueda en el hilo principal"""
        self.btn_cancelar.config(state=tk.DISABLED)
        self.btn_buscar.config(state=tk.NORMAL)
        
        if success:
            self.mostrar_resultados(resultados)
            self.progress.config(value=100)

    def cancelar_operacion(self):
        """Cancela la operación activa (búsqueda o construcción de caché)"""
        if self.search_engine.is_searching():
            self.search_engine.cancel_search()
            self.btn_cancelar.config(state=tk.DISABLED)
            self.btn_buscar.config(state=tk.NORMAL)
        elif self.cache_manager.construyendo_cache:
            self.cache_manager.cancel_build()
            self.btn_buscar.config(state=tk.NORMAL)
            if self.ruta_carpeta_actual:
                folder_name = FileUtils.get_folder_name(self.ruta_carpeta_actual)
                self.actualizar_info_cache(f"Carpeta: {folder_name} | Caché: Construcción cancelada")

    def mostrar_resultados(self, resultados):
        """Muestra los resultados en el TreeView"""
        self.tree.delete(*self.tree.get_children())
        self.resultados = resultados
        
        if not resultados:
            self.tree.insert("", "end", values=("No se encontraron resultados", ""))
            return
            
        for nombre, ruta_relativa, _ in resultados:
            self.tree.insert("", "end", values=(nombre, ruta_relativa))

    def mostrar_resultados_parciales(self, resultados):
        """Muestra resultados parciales durante la búsqueda"""
        self.master.after(0, lambda: self.mostrar_resultados(resultados))

    def limpiar_resultados(self):
        """Limpia los resultados mostrados"""
        self.tree.delete(*self.tree.get_children())
        self.resultados = []
        self.progress.config(value=0)
        self.label_porcentaje.config(text="0%")

    def actualizar_botones_acciones(self, event=None):
        """Actualiza el estado de los botones de acción"""
        seleccionado = bool(self.tree.selection())
        self.btn_copiar.config(state=tk.NORMAL if seleccionado else tk.DISABLED)
        self.btn_abrir.config(state=tk.NORMAL if seleccionado else tk.DISABLED)

    def obtener_ruta_seleccionada(self):
        """Obtiene la ruta del elemento seleccionado"""
        seleccion = self.tree.selection()
        if seleccion:
            idx = self.tree.index(seleccion[0])
            if 0 <= idx < len(self.resultados):
                return self.resultados[idx][2]  # Ruta completa
        return None

    def copiar_ruta_seleccionada(self):
        """Copia la ruta seleccionada al portapapeles"""
        ruta = self.obtener_ruta_seleccionada()
        if ruta:
            success, error = FileUtils.copy_to_clipboard(ruta)
            if success:
                self.actualizar_estado(f"Ruta copiada: {FileUtils.get_folder_name(ruta)}")
            else:
                self.actualizar_estado(f"Error al copiar ruta: {error}")

    def abrir_carpeta_seleccionada(self):
        """Abre la carpeta seleccionada"""
        ruta = self.obtener_ruta_seleccionada()
        if ruta:
            success, error = FileUtils.open_folder(ruta)
            if success:
                self.actualizar_estado(f"Carpeta abierta: {FileUtils.get_folder_name(ruta)}")
            else:
                self.actualizar_estado(f"Error al abrir carpeta: {error}")

    def actualizar_progreso(self, porcentaje, texto_porcentaje):
        """Actualiza la barra de progreso"""
        self.master.after(0, lambda: [
            self.progress.config(value=porcentaje),
            self.label_porcentaje.config(text=texto_porcentaje)
        ])

    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje de estado"""
        self.master.after(0, lambda: self.label_estado.config(text=mensaje))

    def actualizar_info_cache(self, mensaje):
        """Actualiza la información de carpeta y caché"""
        self.master.after(0, lambda: self.label_cache_info.config(text=mensaje))