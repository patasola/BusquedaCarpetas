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
from .cache import CacheManager
from .search_engine import SearchEngine
from .ui_components import UIComponents
from .utils import copy_to_clipboard, open_folder

class BusquedaCarpetaApp:
    def __init__(self, master):
        self.master = master
        master.title("Búsqueda Rápida de Carpetas")
        master.geometry("750x700")  # Aumenté altura para nueva línea
        master.configure(bg="#f6f5f5")
        master.minsize(650, 600)

        # Versión de la aplicación
        self.version = "V. 1.4"

        # Centrar la ventana
        self.centrar_ventana()

        # Inicializar componentes
        self.config = ConfigManager()
        self.cache_manager = CacheManager()
        self.search_engine = SearchEngine()
        self.ui = UIComponents(master, self.version)

        # Variables de estado
        self.busqueda_activa = False
        self.busqueda_cancelada = False
        self.search_thread = None
        self.resultados = []
        self.tiempo_inicio = 0

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
        ruta = self.config.cargar_ruta()
        if ruta and os.path.exists(ruta):
            self.cache_manager.ruta_carpeta = ruta
            # Verificar si existe cache para esta ruta
            if self.cache_manager.cache_valido and self.cache_manager.cache_directorios:
                cache_info = f"Cache: {len(self.cache_manager.cache_directorios.get('directorios', []))} directorios"
            else:
                cache_info = "Cache: No construido"
            
            self.actualizar_info_carpeta(f"Carpeta: {os.path.basename(ruta)} | {cache_info}")
        else:
            self.actualizar_info_carpeta("Carpeta: No seleccionada | Cache: No disponible")

    def crear_interfaz(self):
        """Crea la interfaz usando el componente UI"""
        elementos = self.ui.crear_interfaz_completa()
        
        # Guardar referencias a elementos importantes
        self.entry = elementos['entry']
        self.btn_buscar = elementos['btn_buscar']
        self.btn_cancelar = elementos['btn_cancelar']
        self.progress = elementos['progress']
        self.label_porcentaje = elementos['label_porcentaje']
        self.tree = elementos['tree']
        self.btn_copiar = elementos['btn_copiar']
        self.btn_abrir = elementos['btn_abrir']
        self.label_estado = elementos['label_estado']
        self.label_carpeta_info = elementos['label_carpeta_info']  # Nueva línea de info

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
            label="Construir cache de directorios", 
            command=self.construir_cache_manual
        )
        menu_archivo.add_command(
            label="Limpiar cache", 
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
        """Selecciona ruta y construye cache automáticamente"""
        ruta_inicial = self.cache_manager.ruta_carpeta if self.cache_manager.ruta_carpeta else None
        ruta = filedialog.askdirectory(
            title="Seleccionar ruta de búsqueda",
            initialdir=ruta_inicial
        )
        
        if ruta:
            self.cache_manager.ruta_carpeta = ruta
            self.config.guardar_ruta(ruta)
            
            # Limpiar cache anterior
            self.cache_manager.limpiar_cache()
            
            # Actualizar info inmediatamente
            self.actualizar_info_carpeta(f"Carpeta: {os.path.basename(ruta)} | Cache: Construyendo...")
            self.actualizar_estado(f"Ruta establecida: {os.path.basename(ruta)} - Construyendo cache automáticamente...")
            
            # Construir cache automáticamente
            self.construir_cache_automatico()

    def construir_cache_automatico(self):
        """Construye el cache automáticamente después de seleccionar carpeta"""
        if not self.cache_manager.ruta_carpeta:
            return
            
        if self.cache_manager.construyendo_cache or self.busqueda_activa:
            return
            
        self.cache_manager.construyendo_cache = True
        self.btn_buscar.config(state=tk.DISABLED)
        
        cache_thread = threading.Thread(
            target=self.ejecutar_construccion_cache,
            daemon=True
        )
        cache_thread.start()

    def construir_cache_manual(self):
        """Construye el cache manualmente desde el menú"""
        if not self.cache_manager.ruta_carpeta:
            self.actualizar_estado("Error: Seleccione una ruta primero")
            return
            
        if self.cache_manager.construyendo_cache or self.busqueda_activa:
            return
            
        self.cache_manager.construyendo_cache = True
        self.btn_buscar.config(state=tk.DISABLED)
        
        self.actualizar_info_carpeta(
            f"Carpeta: {os.path.basename(self.cache_manager.ruta_carpeta)} | Cache: Construyendo..."
        )
        
        cache_thread = threading.Thread(
            target=self.ejecutar_construccion_cache,
            daemon=True
        )
        cache_thread.start()

    def ejecutar_construccion_cache(self):
        """Ejecuta la construcción del cache en hilo separado"""
        try:
            self.actualizar_estado("Construyendo cache de directorios...")
            self.progress["value"] = 0
            self.label_porcentaje.config(text="0%")
            
            inicio = time.time()
            cache_temp = []
            processed_dirs = 0
            chunk_size = 100
            
            # Recopilar todos los directorios
            for root, dirs, _ in os.walk(self.cache_manager.ruta_carpeta):
                if not self.cache_manager.construyendo_cache:
                    return
                    
                for dir_name in dirs:
                    path = os.path.join(root, dir_name)
                    ruta_relativa = os.path.relpath(path, self.cache_manager.ruta_carpeta)
                    cache_temp.append((dir_name, ruta_relativa, path))
                    processed_dirs += 1
                    
                    # Actualizar progreso cada chunk
                    if processed_dirs % chunk_size == 0:
                        tiempo_transcurrido = time.time() - inicio
                        progreso = min(95, 20 * (tiempo_transcurrido ** 0.3))
                        self.actualizar_progreso(progreso, tiempo_transcurrido)
                        
                        velocidad = processed_dirs / tiempo_transcurrido if tiempo_transcurrido > 0 else 0
                        self.actualizar_estado(
                            f"Construyendo cache: {processed_dirs:,} directorios ({velocidad:.0f}/s)"
                        )
                        
                        # Actualizar info de carpeta
                        carpeta_nombre = os.path.basename(self.cache_manager.ruta_carpeta)
                        self.actualizar_info_carpeta(
                            f"Carpeta: {carpeta_nombre} | Cache: {processed_dirs:,} directorios..."
                        )
                        
                        time.sleep(0.01)
            
            if self.cache_manager.construyendo_cache:
                # Guardar cache
                self.cache_manager.guardar_cache(cache_temp)
                
                tiempo_total = time.time() - inicio
                self.actualizar_progreso(100, tiempo_total)
                
                carpeta_nombre = os.path.basename(self.cache_manager.ruta_carpeta)
                self.actualizar_info_carpeta(
                    f"Carpeta: {carpeta_nombre} | Cache: {len(cache_temp):,} directorios ✓"
                )
                
                self.actualizar_estado(
                    f"Cache construido: {len(cache_temp):,} directorios en {tiempo_total:.1f}s"
                )
                
        except Exception as e:
            self.actualizar_estado(f"Error construyendo cache: {str(e)}")
        finally:
            self.cache_manager.construyendo_cache = False
            self.btn_buscar.config(state=tk.NORMAL)

    def limpiar_cache(self):
        """Limpia el cache"""
        self.cache_manager.limpiar_cache()
        
        if self.cache_manager.ruta_carpeta:
            carpeta_nombre = os.path.basename(self.cache_manager.ruta_carpeta)
            self.actualizar_info_carpeta(f"Carpeta: {carpeta_nombre} | Cache: Limpiado")
        else:
            self.actualizar_info_carpeta("Carpeta: No seleccionada | Cache: No disponible")
            
        self.actualizar_estado("Cache limpiado")

    def buscar_carpeta(self, event=None):
        """Ejecuta la búsqueda de carpetas"""
        if self.busqueda_activa or self.cache_manager.construyendo_cache:
            return

        if not self.cache_manager.ruta_carpeta:
            self.actualizar_estado("Error: Seleccione una ruta primero")
            return

        criterio = self.entry.get().strip()
        if not criterio:
            self.actualizar_estado("Error: Ingrese un criterio de búsqueda")
            return

        # Intentar búsqueda en cache primero
        if self.cache_manager.cache_valido and self.cache_manager.cache_directorios:
            resultados_cache = self.search_engine.buscar_en_cache(
                criterio, self.cache_manager.cache_directorios
            )
            if resultados_cache is not None:
                self.mostrar_resultados(resultados_cache)
                self.progress["value"] = 100
                self.label_porcentaje.config(text="100%")
                
                total_cache = self.cache_manager.cache_directorios['total']
                self.actualizar_estado(
                    f"Búsqueda en cache: {len(resultados_cache)} resultados en {total_cache:,} directorios"
                )
                return

        # Búsqueda tradicional
        self.preparar_busqueda(criterio)
        self.search_thread = threading.Thread(
            target=self.ejecutar_busqueda_tradicional,
            args=(criterio,),
            daemon=True
        )
        self.search_thread.start()

    def preparar_busqueda(self, criterio):
        """Prepara la interfaz para una búsqueda tradicional"""
        self.tiempo_inicio = time.time()
        self.limpiar_resultados()
        self.busqueda_activa = True
        self.busqueda_cancelada = False
        self.btn_cancelar.config(state=tk.NORMAL)
        self.btn_buscar.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.label_porcentaje.config(text="0%")
        self.actualizar_estado(f"Cache no disponible. Búsqueda tradicional de '{criterio}'...")

    def ejecutar_busqueda_tradicional(self, criterio):
        """Ejecuta búsqueda tradicional en hilo separado"""
        try:
            resultados = self.search_engine.buscar_tradicional(
                criterio, 
                self.cache_manager.ruta_carpeta,
                self.actualizar_progreso_busqueda,
                lambda: self.busqueda_cancelada
            )
            
            if not self.busqueda_cancelada:
                self.finalizar_busqueda(resultados, criterio)
                
        except Exception as e:
            self.actualizar_estado(f"Error: {str(e)}")
        finally:
            self.busqueda_activa = False
            self.btn_cancelar.config(state=tk.DISABLED)
            self.btn_buscar.config(state=tk.NORMAL)

    def actualizar_progreso_busqueda(self, processed, matches, tiempo_transcurrido, velocidad):
        """Callback para actualizar progreso durante búsqueda tradicional"""
        progreso = min(95, 20 * (tiempo_transcurrido ** 0.3))
        self.actualizar_progreso(progreso, tiempo_transcurrido)
        self.actualizar_estado(
            f"Procesados {processed:,} directorios ({velocidad:.0f}/s) - {matches} coincidencias"
        )

    def cancelar_busqueda(self):
        """Cancela la búsqueda activa"""
        if self.busqueda_activa:
            self.busqueda_cancelada = True
            self.btn_cancelar.config(state=tk.DISABLED)
            tiempo = time.time() - self.tiempo_inicio
            self.actualizar_estado(f"Búsqueda cancelada ({tiempo:.1f} segundos)")

    def finalizar_busqueda(self, resultados, criterio):
        """Finaliza la búsqueda y muestra resultados"""
        self.mostrar_resultados(resultados)
        self.progress["value"] = 100
        
        tiempo = time.time() - self.tiempo_inicio
        processed = getattr(self.search_engine, 'processed_dirs', 0)
        self.label_porcentaje.config(text=f"100% • {tiempo:.1f}s")
        self.actualizar_estado(
            f"Búsqueda completada: {len(resultados)} resultados en {processed:,} directorios ({tiempo:.1f}s)"
        )

    def mostrar_resultados(self, resultados):
        """Muestra los resultados en el TreeView"""
        self.tree.delete(*self.tree.get_children())
        self.resultados = resultados
        
        if not resultados:
            self.tree.insert("", "end", values=("No se encontraron resultados", ""))
            return
            
        for nombre, ruta, _ in resultados:
            self.tree.insert("", "end", values=(nombre, ruta))

    def limpiar_resultados(self):
        """Limpia los resultados mostrados"""
        self.tree.delete(*self.tree.get_children())
        self.resultados = []
        self.progress["value"] = 0
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
                return self.resultados[idx][2]
        return None

    def copiar_ruta_seleccionada(self):
        """Copia la ruta seleccionada al portapapeles"""
        if ruta := self.obtener_ruta_seleccionada():
            if copy_to_clipboard(ruta):
                self.actualizar_estado(f"Ruta copiada: {os.path.basename(ruta)}")
            else:
                self.actualizar_estado("Error al copiar ruta")

    def abrir_carpeta_seleccionada(self):
        """Abre la carpeta seleccionada"""
        if ruta := self.obtener_ruta_seleccionada():
            if open_folder(ruta):
                self.actualizar_estado(f"Carpeta abierta: {os.path.basename(ruta)}")
            else:
                self.actualizar_estado("Error al abrir carpeta")

    def actualizar_progreso(self, porcentaje, tiempo_transcurrido=0):
        """Actualiza la barra de progreso"""
        self.master.after(0, lambda: [
            self.progress.config(value=porcentaje),
            self.label_porcentaje.config(text=f"{int(porcentaje)}% • {tiempo_transcurrido:.1f}s")
        ])

    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje de estado"""
        self.master.after(0, lambda: self.label_estado.config(text=mensaje))

    def actualizar_info_carpeta(self, mensaje):
        """Actualiza la información de carpeta y cache"""
        self.master.after(0, lambda: self.label_carpeta_info.config(text=mensaje))