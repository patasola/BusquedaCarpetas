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
from .utils import copy_to_clipboard, open_folder, get_folder_name, is_valid_path
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
        self.search_engine = SearchEngine()
        self.ui = UIComponents(master, self.version)

        # Variables de estado
        self.resultados = []
        self.ruta_carpeta_actual = None
        self.busqueda_activa = False

        # Configurar interfaz
        self.elementos_ui = self.ui.crear_interfaz_completa()
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
        ruta = self.config.cargar_ruta()
        if ruta and is_valid_path(ruta):
            self.ruta_carpeta_actual = ruta
            self.cache_manager.ruta_base = ruta
            
            if self.cache_manager.is_cache_valid(ruta):
                cache_info = self.cache_manager.get_cache_info()
                if cache_info:
                    total_dirs = cache_info['total_directories']
                    self.actualizar_info_cache(
                        f"Carpeta: {get_folder_name(ruta)} | Caché: {total_dirs:,} directorios ✓"
                    )
            else:
                self.actualizar_info_cache(
                    f"Carpeta: {get_folder_name(ruta)} | Caché: No construido"
                )
        else:
            self.actualizar_info_cache("Sin carpeta seleccionada")

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
        self.master.bind("<F2>", lambda e: self.elementos_ui['entry'].focus())
        self.master.bind("<F3>", lambda e: self.copiar_ruta_seleccionada())
        self.master.bind("<F4>", lambda e: self.abrir_carpeta_seleccionada())
        
        self.elementos_ui['entry'].bind("<Return>", lambda e: self.buscar_carpeta())
        self.elementos_ui['btn_buscar'].config(command=self.buscar_carpeta)
        self.elementos_ui['btn_cancelar'].config(command=self.cancelar_operacion)
        self.elementos_ui['btn_copiar'].config(command=self.copiar_ruta_seleccionada)
        self.elementos_ui['btn_abrir'].config(command=self.abrir_carpeta_seleccionada)

    def seleccionar_ruta_busqueda(self):
        """Selecciona ruta y construye caché automáticamente"""
        ruta_inicial = self.ruta_carpeta_actual if self.ruta_carpeta_actual else None
        ruta = filedialog.askdirectory(
            title="Seleccionar ruta de búsqueda",
            initialdir=ruta_inicial
        )
        
        if ruta:
            self.ruta_carpeta_actual = ruta
            self.config.guardar_ruta(ruta)
            
            # Limpiar caché anterior
            self.cache_manager.invalidate_cache()
            
            # Actualizar info
            folder_name = get_folder_name(ruta)
            self.actualizar_info_cache(f"Carpeta: {folder_name} | Caché: Construyendo...")
            self.actualizar_estado(f"Ruta establecida: {folder_name} - Construyendo caché...")
            
            # Construir caché automáticamente
            self.construir_cache_automatico()

    def construir_cache_automatico(self):
        """Construye el caché automáticamente después de seleccionar carpeta"""
        if not self.ruta_carpeta_actual or self.busqueda_activa:
            return
            
        self.elementos_ui['btn_buscar'].config(state=tk.DISABLED)
        
        self.cache_manager.build_cache_async(
            self.ruta_carpeta_actual,
            completion_callback=self.on_cache_build_complete
        )

    def construir_cache_manual(self):
        """Construye el caché manualmente desde el menú"""
        if not self.ruta_carpeta_actual:
            self.actualizar_estado(MESSAGES['no_folder'])
            return
            
        if self.busqueda_activa:
            return
            
        self.elementos_ui['btn_buscar'].config(state=tk.DISABLED)
        
        folder_name = get_folder_name(self.ruta_carpeta_actual)
        self.actualizar_info_cache(f"Carpeta: {folder_name} | Caché: Construyendo...")
        
        self.cache_manager.build_cache_async(
            self.ruta_carpeta_actual,
            completion_callback=self.on_cache_build_complete
        )

    def on_cache_build_complete(self, success, total_dirs):
        """Callback cuando se completa la construcción del caché"""
        self.master.after(0, lambda: self._handle_cache_build_complete(success, total_dirs))

    def _handle_cache_build_complete(self, success, total_dirs):
        """Maneja la finalización de la construcción del caché"""
        self.elementos_ui['btn_buscar'].config(state=tk.NORMAL)
        
        if success:
            folder_name = get_folder_name(self.ruta_carpeta_actual)
            self.actualizar_info_cache(
                f"Carpeta: {folder_name} | Caché: {total_dirs:,} directorios ✓"
            )
            self.actualizar_estado(MESSAGES['cache_completed'])
        else:
            folder_name = get_folder_name(self.ruta_carpeta_actual)
            self.actualizar_info_cache(
                f"Carpeta: {folder_name} | Caché: Error en construcción"
            )

    def limpiar_cache(self):
        """Limpia el caché"""
        self.cache_manager.clear_cache()
        
        if self.ruta_carpeta_actual:
            folder_name = get_folder_name(self.ruta_carpeta_actual)
            self.actualizar_info_cache(f"Carpeta: {folder_name} | Caché: Limpiado")
        else:
            self.actualizar_info_cache("Sin carpeta seleccionada")
            
        self.actualizar_estado(MESSAGES['cache_cleared'])

    def buscar_carpeta(self, event=None):
        """Ejecuta la búsqueda de carpetas"""
        if self.busqueda_activa or self.cache_manager.construyendo_cache:
            return

        if not self.ruta_carpeta_actual:
            self.actualizar_estado(MESSAGES['no_folder'])
            return

        criterio = self.elementos_ui['entry'].get().strip()
        if not criterio:
            self.actualizar_estado(MESSAGES['no_criteria'])
            return

        # Búsqueda en caché
        if self.cache_manager.is_cache_valid(self.ruta_carpeta_actual):
            resultados_cache = self.cache_manager.search_in_cache(
                criterio, 
                status_callback=self.actualizar_estado
            )
            if resultados_cache is not None:
                self.mostrar_resultados(resultados_cache)
                self.elementos_ui['progress'].config(value=100)
                self.elementos_ui['label_porcentaje'].config(text="100%")
                return

        # Búsqueda tradicional
        self.preparar_busqueda()
        self.busqueda_activa = True
        self.elementos_ui['btn_cancelar'].config(state=tk.NORMAL)
        
        # Ejecutar en un hilo separado
        threading.Thread(
            target=self._ejecutar_busqueda_tradicional,
            args=(criterio,),
            daemon=True
        ).start()

    def _ejecutar_busqueda_tradicional(self, criterio):
        """Ejecuta la búsqueda tradicional en un hilo separado"""
        try:
            resultados = self.search_engine.buscar_tradicional(
                criterio,
                self.ruta_carpeta_actual,
                progress_callback=self.actualizar_progreso,
                cancel_check=lambda: not self.busqueda_activa
            )
            
            self.master.after(0, lambda: self._finalizar_busqueda(True, resultados))
        except Exception as e:
            self.master.after(0, lambda: self._finalizar_busqueda(False, str(e)))

    def _finalizar_busqueda(self, success, resultados):
        """Finaliza la búsqueda y muestra resultados"""
        self.busqueda_activa = False
        self.elementos_ui['btn_cancelar'].config(state=tk.DISABLED)
        
        if success:
            self.mostrar_resultados(resultados)
            self.elementos_ui['progress'].config(value=100)
            self.elementos_ui['label_porcentaje'].config(text="100%")
        else:
            self.actualizar_estado(f"Error en búsqueda: {resultados}")

    def preparar_busqueda(self):
        """Prepara la interfaz para una búsqueda"""
        self.limpiar_resultados()
        self.elementos_ui['progress'].config(value=0)
        self.elementos_ui['label_porcentaje'].config(text="0%")

    def cancelar_operacion(self):
        """Cancela la operación activa (búsqueda o construcción de caché)"""
        if self.busqueda_activa:
            self.busqueda_activa = False
            self.elementos_ui['btn_cancelar'].config(state=tk.DISABLED)
            self.actualizar_estado(MESSAGES['search_cancelled'])
        elif self.cache_manager.construyendo_cache:
            self.cache_manager.cancel_build()
            self.elementos_ui['btn_buscar'].config(state=tk.NORMAL)
            if self.ruta_carpeta_actual:
                folder_name = get_folder_name(self.ruta_carpeta_actual)
                self.actualizar_info_cache(f"Carpeta: {folder_name} | Caché: Construcción cancelada")

    def mostrar_resultados(self, resultados):
        """Muestra los resultados en el TreeView"""
        self.elementos_ui['tree'].delete(*self.elementos_ui['tree'].get_children())
        self.resultados = resultados
        
        if not resultados:
            self.elementos_ui['tree'].insert("", "end", values=("No se encontraron resultados", ""))
            return
            
        for nombre, ruta_relativa, _ in resultados:
            self.elementos_ui['tree'].insert("", "end", values=(nombre, ruta_relativa))

    def limpiar_resultados(self):
        """Limpia los resultados mostrados"""
        self.elementos_ui['tree'].delete(*self.elementos_ui['tree'].get_children())
        self.resultados = []
        self.elementos_ui['progress'].config(value=0)
        self.elementos_ui['label_porcentaje'].config(text="0%")

    def actualizar_botones_acciones(self, event=None):
        """Actualiza el estado de los botones de acción"""
        seleccionado = bool(self.elementos_ui['tree'].selection())
        self.elementos_ui['btn_copiar'].config(state=tk.NORMAL if seleccionado else tk.DISABLED)
        self.elementos_ui['btn_abrir'].config(state=tk.NORMAL if seleccionado else tk.DISABLED)

    def obtener_ruta_seleccionada(self):
        """Obtiene la ruta del elemento seleccionado"""
        seleccion = self.elementos_ui['tree'].selection()
        if seleccion:
            idx = self.elementos_ui['tree'].index(seleccion[0])
            if 0 <= idx < len(self.resultados):
                return self.resultados[idx][2]  # Ruta completa
        return None

    def copiar_ruta_seleccionada(self):
        """Copia la ruta seleccionada al portapapeles"""
        ruta = self.obtener_ruta_seleccionada()
        if ruta:
            if copy_to_clipboard(ruta):
                self.actualizar_estado(f"Ruta copiada: {get_folder_name(ruta)}")
            else:
                self.actualizar_estado("Error al copiar ruta")

    def abrir_carpeta_seleccionada(self):
        """Abre la carpeta seleccionada"""
        ruta = self.obtener_ruta_seleccionada()
        if ruta:
            if open_folder(ruta):
                self.actualizar_estado(f"Carpeta abierta: {get_folder_name(ruta)}")
            else:
                self.actualizar_estado("Error al abrir carpeta")

    def actualizar_progreso(self, porcentaje, texto_porcentaje):
        """Actualiza la barra de progreso"""
        self.master.after(0, lambda: [
            self.elementos_ui['progress'].config(value=porcentaje),
            self.elementos_ui['label_porcentaje'].config(text=texto_porcentaje)
        ])

    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje de estado"""
        self.master.after(0, lambda: self.elementos_ui['label_estado'].config(text=mensaje))

    def actualizar_info_cache(self, mensaje):
        """Actualiza la información de carpeta y caché"""
        self.master.after(0, lambda: self.elementos_ui['label_carpeta_info'].config(text=mensaje))