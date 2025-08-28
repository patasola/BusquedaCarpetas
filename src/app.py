# src/app.py - Aplicación Principal V.4.2 - Refactorizada (Compacta)
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
from .window_manager import WindowManager
from .event_manager import EventManager
from .navigation_manager import NavigationManager
from .ui_state_manager import UIStateManager

# Tree Explorer opcional
try:
    from .tree_explorer import TreeExplorer
    TREE_EXPLORER_AVAILABLE = True
except ImportError:
    TREE_EXPLORER_AVAILABLE = False
    TreeExplorer = None

class BusquedaCarpetaApp:
    def __init__(self, master):
        self.master = master
        self.version = "V. 4.2 - Refactorizada"
        self.modo_numerico = True
        self.ruta_carpeta = None
        
        self._init_components()
        self._init_ui()
        self._init_integrations()
        
    def _init_components(self):
        """Inicializa todos los componentes principales"""
        self.window_manager = WindowManager(self.master, self.version)
        self.config = ConfigManager()
        self.ruta_carpeta = self.config.cargar_ruta()
        
        self.cache_manager = CacheManager(self.ruta_carpeta)
        self.search_engine = SearchEngine(self.ruta_carpeta)
        
        self.changelog_viewer = ChangelogViewer(self.master)
        self.about_dialog = AboutDialog(self.master, self.version)
        self.manual_viewer = ManualViewer(self.master)
        
        self.historial_manager = HistorialManager(self)
        self.ui_manager = UIManager(self)
        self.search_coordinator = SearchCoordinator(self)
        
    def _init_ui(self):
        """Inicializa interfaz"""
        self.window_manager.configurar_ventana()
        
        self.main_container = tk.Frame(self.master, bg=Colors.BACKGROUND)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ui = UIComponents(self.main_container, self.version).crear_interfaz_completa()
        
        # Asignar referencias con mapeo correcto
        self.entry = ui['entry']
        self.modo_label = ui['modo_label']
        self.btn_buscar = ui['btn_buscar']
        self.btn_cancelar = ui['btn_cancelar']
        self.tree = ui['tree']
        self.btn_copiar = ui['btn_copiar']
        self.btn_abrir = ui['btn_abrir']
        self.label_estado = ui['label_estado']
        self.label_info_carpeta = ui['label_carpeta_info']  # Mapeo correcto
        self.configurar_scrollbars = ui['configurar_scrollbars']
        
        self.ui_state_manager = UIStateManager(self)
        self.ui_state_manager.configurar_validacion()
        self.ui_state_manager.actualizar_indicador_modo()
        
    def _init_integrations(self):
        """Configura integraciones"""
        self.ui_manager.configurar_referencias(
            self.label_estado.master, self.label_info_carpeta.master)
        
        self.ui_callbacks = UICallbacks(self)
        self.file_manager = FileManager(self.config, self.ui_callbacks)
        self.search_manager = SearchManager(
            self.cache_manager, self.search_engine, None, self.ui_callbacks)
        
        self.event_manager = EventManager(self)
        self.event_manager.configurar_eventos()
        
        self.navigation_manager = NavigationManager(self)
        self.navigation_manager.configurar_navegacion()
        
        self._create_menu()
        self._init_tree_explorer()
        self._finalize_init()
    
    def _init_tree_explorer(self):
        """Inicializa Tree Explorer si disponible"""
        if TREE_EXPLORER_AVAILABLE and TreeExplorer:
            try:
                self.tree_resultados = self.tree
                self.tree_explorer = TreeExplorer(self.master, self)
                self.master.bind("<F6>", lambda e: self.tree_explorer.clear_temp_cache())
            except Exception as e:
                print(f"Error Tree Explorer: {e}")
                self.tree_explorer = None
        else:
            self.tree_explorer = None
    
    def _create_menu(self):
        """Crea menú principal"""
        menubar = Menu(self.master)
        
        # Menú Archivo
        archivo = Menu(menubar, tearoff=0)
        archivo.add_command(label="Seleccionar ruta", command=self.seleccionar_ruta_busqueda)
        archivo.add_separator()
        archivo.add_command(label="Construir cache", command=self.search_coordinator.construir_cache_manual)
        archivo.add_command(label="Verificar problemas", command=self.search_coordinator.verificar_problemas_cache)
        archivo.add_command(label="Limpiar cache", command=self.search_coordinator.limpiar_cache)
        
        if hasattr(self, 'tree_explorer') and self.tree_explorer:
            archivo.add_separator()
            archivo.add_command(label="Limpiar cache temporal (F6)", 
                              command=lambda: self.tree_explorer.clear_temp_cache())
        
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.master.quit)
        
        # Menú Ver
        ver = Menu(menubar, tearoff=0)
        self.ui_manager.configurar_menu_ver(ver)
        ver.add_separator()
        ver.add_command(label="Centrar Ventana", command=self.window_manager.centrar_ventana, accelerator="Ctrl+E")
        ver.add_command(label="Maximizar", command=self.window_manager.maximizar_ventana, accelerator="F11")
        ver.add_command(label="Restaurar", command=self.window_manager.restaurar_ventana, accelerator="Ctrl+R")
        
        # Menú Ayuda
        ayuda = Menu(menubar, tearoff=0)
        ayuda.add_command(label="Manual", command=self.manual_viewer.show_manual, accelerator="F1")
        ayuda.add_separator()
        ayuda.add_command(label="Historial", command=self.changelog_viewer.mostrar_changelog)
        ayuda.add_command(label="Acerca de", command=self.about_dialog.mostrar_acerca_de)
        
        menubar.add_cascade(label="Archivo", menu=archivo)
        menubar.add_cascade(label="Ver", menu=ver)
        menubar.add_cascade(label="Ayuda", menu=ayuda)
        self.master.config(menu=menubar)
    
    def _finalize_init(self):
        """Finaliza inicialización"""
        self.actualizar_info_carpeta()
        
        if (self.ruta_carpeta and os.path.exists(self.ruta_carpeta) and 
            self.cache_manager.necesita_construccion()):
            self.master.after(1000, self.search_coordinator.construir_cache_automatico)
        elif hasattr(self.cache_manager, 'cache'):
            total = self.cache_manager.cache.directorios.get('total', 0)
            if total > 0:
                self.ui_callbacks.actualizar_estado(f"Cache listo: {total:,} directorios")
    
    # Métodos principales
    def buscar_carpeta(self):
        self.search_coordinator.ejecutar_busqueda(self.entry.get().strip())
    
    def seleccionar_ruta_busqueda(self):
        nueva_ruta = self.file_manager.seleccionar_ruta(self.ruta_carpeta)
        if nueva_ruta:
            self.ruta_carpeta = nueva_ruta
            self.cache_manager = CacheManager(nueva_ruta)
            self.search_engine = SearchEngine(nueva_ruta)
            self.search_manager.actualizar_componentes(self.cache_manager, self.search_engine)
            self.actualizar_info_carpeta()
            self.ui_callbacks.actualizar_estado(f"Ruta: {self.file_manager.obtener_nombre_carpeta(nueva_ruta)}")
            self.search_coordinator.construir_cache_automatico()
    
    def actualizar_info_carpeta(self):
        if not self.ruta_carpeta:
            texto = "Sin carpeta • Cache: No disponible"
        else:
            nombre = self.file_manager.obtener_nombre_carpeta(self.ruta_carpeta)
            if self.cache_manager.cache.valido and self.cache_manager.cache.directorios:
                total = self.cache_manager.cache.directorios.get('total', 0)
                timestamp = self.cache_manager.cache.directorios.get('timestamp', 0)
                fecha = time.strftime('%d/%m %H:%M', time.localtime(timestamp))
                
                tree_info = ""
                if hasattr(self, 'tree_explorer') and self.tree_explorer:
                    try:
                        stats = self.tree_explorer.get_cache_stats()
                        tree_info = f" • Tree: {stats['cached_paths']}"
                    except:
                        pass
                
                texto = f"Carpeta: {nombre} • Cache: {total:,} ({fecha}){tree_info}"
            else:
                texto = f"Carpeta: {nombre} • Cache: No disponible"
        
        self.label_info_carpeta.config(text=texto)
    
    # Delegaciones simples
    def cancelar_busqueda(self): 
        self.search_coordinator.cancelar_busqueda()
    
    def cambiar_modo_entrada(self): 
        self.ui_state_manager.cambiar_modo_entrada()
    
    def copiar_ruta_seleccionada(self): 
        self.event_manager.copiar_ruta_seleccionada()
    
    def abrir_carpeta_seleccionada(self): 
        self.event_manager.abrir_carpeta_seleccionada()
    
    def ejecutar_busqueda_desde_historial(self, criterio):
        silenciosa = hasattr(self, 'tree_explorer') and self.tree_explorer
        self.search_coordinator.ejecutar_busqueda(criterio, silenciosa=silenciosa)
    
    def _finalizar_busqueda_con_historial(self, metodo, num_resultados):
        self.search_coordinator.finalizar_busqueda_con_historial(metodo, num_resultados)
    
    def ajustar_layout_para_historial(self, mostrar):
        self.navigation_manager.ajustar_layout_para_historial(mostrar)
    
    def actualizar_navegacion_tab(self):
        self.navigation_manager.actualizar_navegacion_tab()
    
    def on_entry_change(self, event):
        self.ui_state_manager.on_entry_change(event)
    
    def on_tree_select(self, event):
        self.event_manager.on_tree_select(event)
    
    def _actualizar_menu_ver(self):
        self.ui_manager.actualizar_estado_historial()
        self.navigation_manager.actualizar_navegacion_tab()
    
    def _ejecutar_busqueda_silenciosa(self, criterio):
        self.search_coordinator.ejecutar_busqueda(criterio, silenciosa=True)