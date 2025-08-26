# src/app.py - Aplicación Principal V.4.1 - Explorador Integrado (Completo con Ventana)
import os
import tkinter as tk
from tkinter import Menu
import time

from .config import ConfigManager
from .cache_manager import CacheManager
from .search_engine import SearchEngine
from .ui_components import UIComponents, Colors
from .changelog_viewer import ChangelogViewer
from .about_dialog import AboutDialog
from .search_manager import SearchManager
from .file_manager import FileManager
from .ui_callbacks import UICallbacks
from .manual_viewer import ManualViewer
from .historial_manager import HistorialManager
from .ui_manager import UIManager
from .search_coordinator import SearchCoordinator

# NUEVOS MÓDULOS REFACTORIZADOS
from .window_manager import WindowManager
from .event_manager import EventManager
from .navigation_manager import NavigationManager
from .ui_state_manager import UIStateManager

# TREE EXPLORER V.4.1 (OPCIONAL) - VARIABLE GLOBAL
TREE_EXPLORER_AVAILABLE = False
TreeExplorer = None

try:
    from .tree_explorer import TreeExplorer
    TREE_EXPLORER_AVAILABLE = True
    print("✅ Tree Explorer disponible")
except ImportError:
    print("⚠️ Tree Explorer no disponible")

class BusquedaCarpetaApp:
    def __init__(self, master):
        self.master = master
        self.version = "V. 4.1 - Explorador Integrado"
        
        # VARIABLES DE ESTADO
        self.modo_numerico = True
        self.ruta_carpeta = None
        
        # INICIALIZACIÓN MODULAR
        self._inicializar_componentes_core()
        self._crear_interfaz()
        self._configurar_integraciones()
        self._inicializar_tree_explorer()
        
    def _inicializar_componentes_core(self):
        """Inicializa componentes principales"""
        # Window Manager - maneja ventana y configuración
        self.window_manager = WindowManager(self.master, self.version)
        
        # Configuración básica
        self.config = ConfigManager()
        self.ruta_carpeta = self.config.cargar_ruta()
        
        # Managers principales - CORREGIDO: pasar ruta_carpeta en lugar de self
        self.cache_manager = CacheManager(self.ruta_carpeta)
        self.search_engine = SearchEngine(self.ruta_carpeta)
        
        # Viewers
        self.changelog_viewer = ChangelogViewer(self.master)
        self.about_dialog = AboutDialog(self.master, self.version)
        self.manual_viewer = ManualViewer(self.master)
        
        # Managers avanzados
        self.historial_manager = HistorialManager(self)
        self.ui_manager = UIManager(self)
        self.search_coordinator = SearchCoordinator(self)
        
    def _crear_interfaz(self):
        """Crea la interfaz principal"""
        # Configurar ventana
        self.window_manager.configurar_ventana()
        
        # Crear container principal
        self.main_container = tk.Frame(self.master, bg=Colors.BACKGROUND)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Crear interfaz usando UI Components
        ui_components = UIComponents(self.main_container, self.version)
        elementos = ui_components.crear_interfaz_completa()
        
        # Asignar referencias de elementos UI
        self._asignar_referencias_ui(elementos)
        
        # Configurar validación y modo
        self.ui_state_manager = UIStateManager(self)
        self.ui_state_manager.configurar_validacion()
        self.ui_state_manager.actualizar_indicador_modo()
        
    def _asignar_referencias_ui(self, elementos):
        """Asigna referencias de elementos UI"""
        self.entry = elementos['entry']
        self.modo_label = elementos['modo_label']
        self.btn_buscar = elementos['btn_buscar']
        self.btn_cancelar = elementos['btn_cancelar']
        self.tree = elementos['tree']
        self.btn_copiar = elementos['btn_copiar']
        self.btn_abrir = elementos['btn_abrir']
        self.label_estado = elementos['label_estado']
        self.label_info_carpeta = elementos['label_carpeta_info']
        self.configurar_scrollbars = elementos['configurar_scrollbars']
        
    def _configurar_integraciones(self):
        """Configura integraciones entre managers"""
        # UI Manager
        self.ui_manager.configurar_referencias(
            self.label_estado.master,  # status_frame
            self.label_info_carpeta.master  # cache_frame
        )
        
        # Managers de negocio
        self.ui_callbacks = UICallbacks(self)
        self.file_manager = FileManager(self.config, self.ui_callbacks)
        self.search_manager = SearchManager(
            self.cache_manager, self.search_engine, 
            None, self.ui_callbacks
        )
        
        # Event Manager - maneja todos los eventos
        self.event_manager = EventManager(self)
        self.event_manager.configurar_eventos()
        
        # Navigation Manager - maneja navegación
        self.navigation_manager = NavigationManager(self)
        self.navigation_manager.configurar_navegacion()
        
        # Crear menú
        self._crear_menu()
        
        # Inicialización final
        self._inicializacion_final()
        
    def _inicializar_tree_explorer(self):
        """Inicializa Tree Explorer V.4.1 si está disponible"""
        global TREE_EXPLORER_AVAILABLE, TreeExplorer
        
        if TREE_EXPLORER_AVAILABLE and TreeExplorer is not None:
            try:
                # Crear alias para compatibilidad
                self.tree_resultados = self.tree
                
                # Inicializar tree explorer
                self.tree_explorer = TreeExplorer(self.master, self)
                print("✅ Tree Explorer V.4.1 inicializado")
                
                # Configurar F6 para limpiar cache temporal
                self.master.bind("<F6>", lambda e: self.tree_explorer.clear_temp_cache())
                
            except Exception as e:
                print(f"⚠️ Error inicializando Tree Explorer: {e}")
                TREE_EXPLORER_AVAILABLE = False
                self.tree_explorer = None
        else:
            self.tree_explorer = None
            print("ℹ️ Funcionando en modo V.4.0 (sin Tree Explorer)")
    
    def _crear_menu(self):
        """Crea el menú principal"""
        menubar = Menu(self.master)
        
        # Menú Archivo
        menu_archivo = Menu(menubar, tearoff=0)
        menu_archivo.add_command(
            label="Seleccionar ruta de búsqueda", 
            command=self.seleccionar_ruta_busqueda
        )
        menu_archivo.add_separator()
        menu_archivo.add_command(
            label="Construir cache de directorios", 
            command=self.search_coordinator.construir_cache_manual
        )
        menu_archivo.add_command(
            label="Verificar problemas", 
            command=self.search_coordinator.verificar_problemas_cache
        )
        menu_archivo.add_command(
            label="Limpiar cache", 
            command=self.search_coordinator.limpiar_cache
        )
        menu_archivo.add_separator()
        
        # Opción F6 solo si Tree Explorer está disponible
        global TREE_EXPLORER_AVAILABLE
        if TREE_EXPLORER_AVAILABLE and hasattr(self, 'tree_explorer') and self.tree_explorer:
            menu_archivo.add_command(
                label="Limpiar cache temporal (F6)", 
                command=lambda: self.tree_explorer.clear_temp_cache()
            )
            menu_archivo.add_separator()
            
        menu_archivo.add_command(label="Salir", command=self.master.quit)
        
        # Menú Ver (AMPLIADO CON OPCIONES DE VENTANA)
        menu_ver = Menu(menubar, tearoff=0)
        
        # Opciones de interfaz existentes
        self.menu_ver = self.ui_manager.configurar_menu_ver(menu_ver)
        
        # NUEVO: Separador y opciones de ventana
        menu_ver.add_separator()
        menu_ver.add_command(
            label="🎯 Centrar Ventana",
            command=self.window_manager.centrar_ventana,
            accelerator="Ctrl+E"
        )
        menu_ver.add_command(
            label="🔲 Maximizar",
            command=self.window_manager.maximizar_ventana,
            accelerator="F11"
        )
        menu_ver.add_command(
            label="🗗 Restaurar",
            command=self.window_manager.restaurar_ventana,
            accelerator="Ctrl+R"
        )
        
        # Menú Ayuda
        menu_ayuda = Menu(menubar, tearoff=0)
        menu_ayuda.add_command(
            label="📚 Manual Técnico Completo", 
            command=self.manual_viewer.show_manual,
            accelerator="F1"
        )
        menu_ayuda.add_separator()
        menu_ayuda.add_command(
            label="📋 Historial de Cambios", 
            command=self.changelog_viewer.mostrar_changelog
        )
        menu_ayuda.add_command(
            label="ℹ️ Acerca de", 
            command=self.about_dialog.mostrar_acerca_de
        )
        
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menubar.add_cascade(label="Ver", menu=menu_ver)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        self.master.config(menu=menubar)
    
    def _inicializacion_final(self):
        """Inicialización final de la aplicación"""
        self.actualizar_info_carpeta()
        
        if self.ruta_carpeta and os.path.exists(self.ruta_carpeta):
            if not self.cache_manager.cache.valido:
                self.master.after(500, self.search_coordinator.construir_cache_automatico)
    
    # MÉTODOS DELEGADOS A MANAGERS
    def buscar_carpeta(self):
        """Delega búsqueda al search coordinator"""
        criterio = self.entry.get().strip()
        self.search_coordinator.ejecutar_busqueda(criterio)
    
    def seleccionar_ruta_busqueda(self):
        """Delega selección de ruta al file manager"""
        nueva_ruta = self.file_manager.seleccionar_ruta(self.ruta_carpeta)
        
        if nueva_ruta:
            self.ruta_carpeta = nueva_ruta
            self._actualizar_componentes_ruta()
    
    def _actualizar_componentes_ruta(self):
        """Actualiza componentes cuando cambia la ruta"""
        # CORREGIDO: Crear nuevos managers con la nueva ruta
        self.cache_manager = CacheManager(self.ruta_carpeta)
        self.search_engine = SearchEngine(self.ruta_carpeta)
        
        self.search_manager.actualizar_componentes(self.cache_manager, self.search_engine)
        
        self.actualizar_info_carpeta()
        nombre_carpeta = self.file_manager.obtener_nombre_carpeta(self.ruta_carpeta)
        self.ui_callbacks.actualizar_estado(f"Ruta establecida: {nombre_carpeta}")
        
        self.search_coordinator.construir_cache_automatico()
    
    def actualizar_info_carpeta(self):
        """Actualiza información de la carpeta en la barra"""
        if not self.ruta_carpeta:
            texto = "No hay carpeta seleccionada • Cache: No disponible"
        else:
            nombre_carpeta = self.file_manager.obtener_nombre_carpeta(self.ruta_carpeta)
            
            if self.cache_manager.cache.valido and self.cache_manager.cache.directorios:
                total_dirs = self.cache_manager.cache.directorios.get('total', 0)
                timestamp = self.cache_manager.cache.directorios.get('timestamp', 0)
                fecha_cache = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(timestamp))
                
                # Agregar info de tree explorer si está disponible
                tree_info = ""
                if hasattr(self, 'tree_explorer') and self.tree_explorer:
                    try:
                        stats = self.tree_explorer.get_cache_stats()
                        tree_info = f" • Tree: {stats['cached_paths']} rutas"
                    except:
                        tree_info = ""
                
                texto = f"Carpeta: {nombre_carpeta} • Cache: {total_dirs:,} directorios ({fecha_cache}){tree_info}"
            else:
                texto = f"Carpeta: {nombre_carpeta} • Cache: No disponible"
        
        self.label_info_carpeta.config(text=texto)
    
    # MÉTODOS DE COMPATIBILIDAD V.4.0
    def cambiar_modo_entrada(self):
        """Delega al UI State Manager"""
        self.ui_state_manager.cambiar_modo_entrada()
    
    def copiar_ruta_seleccionada(self):
        """Delega al Event Manager"""
        self.event_manager.copiar_ruta_seleccionada()
    
    def abrir_carpeta_seleccionada(self):
        """Delega al Event Manager"""
        self.event_manager.abrir_carpeta_seleccionada()
    
    def cancelar_busqueda(self):
        """Delega al search coordinator"""
        self.search_coordinator.cancelar_busqueda()
    
    # MÉTODOS PARA COMPATIBILIDAD CON MANAGERS EXISTENTES
    def _ejecutar_busqueda_silenciosa(self, criterio):
        """Ejecuta búsqueda silenciosa para historial"""
        print(f"🔍 APP._EJECUTAR_BUSQUEDA_SILENCIOSA: criterio='{criterio}'")
        self.search_coordinator.ejecutar_busqueda(criterio, silenciosa=True)
    
    def ejecutar_busqueda_desde_historial(self, criterio):
        """NUEVO: Método específico para búsquedas desde historial"""
        print(f"🔍 APP.EJECUTAR_BUSQUEDA_DESDE_HISTORIAL: criterio='{criterio}'")
        
        # Forzar que sea con tree explorer
        if hasattr(self, 'tree_explorer') and self.tree_explorer:
            print("🔍 Forzando búsqueda desde historial con tree_explorer")
            self.search_coordinator.ejecutar_busqueda(criterio, silenciosa=True)
        else:
            print("🔍 Tree explorer no disponible, usando búsqueda normal")
            self.search_coordinator.ejecutar_busqueda(criterio, silenciosa=False)
    
    def _finalizar_busqueda_con_historial(self, metodo, num_resultados):
        """Finaliza búsqueda y actualiza historial"""
        self.search_coordinator.finalizar_busqueda_con_historial(metodo, num_resultados)
    
    def ajustar_layout_para_historial(self, mostrar_historial):
        """Ajusta layout para historial"""
        self.navigation_manager.ajustar_layout_para_historial(mostrar_historial)
    
    def actualizar_navegacion_tab(self):
        """Actualiza navegación tab"""
        self.navigation_manager.actualizar_navegacion_tab()
    
    def on_entry_change(self, event):
        """Maneja cambios en el campo de entrada"""
        self.ui_state_manager.on_entry_change(event)
    
    def on_tree_select(self, event):
        """Maneja selección en la tabla"""
        self.event_manager.on_tree_select(event)
    
    def _actualizar_menu_ver(self):
        """Actualiza el estado del menú Ver"""
        self.ui_manager.actualizar_estado_historial()
        # ACTUALIZAR NAVEGACIÓN TAB cuando cambie la visibilidad del historial
        self.navigation_manager.actualizar_navegacion_tab()