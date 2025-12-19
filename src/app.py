# src/app.py - Aplicación Principal V.4.5 - REFACTORIZADO
import os
import tkinter as tk
import time
import threading

from .config import ConfigManager
from .cache_manager import CacheManager
from .search_engine import SearchEngine
from .search_coordinator import SearchCoordinator
from .search_manager import SearchManager
from .ui_components import UIComponents
from .ui_callbacks import UICallbacks
from .ui_manager import UIManager
from .ui_state_manager import UIStateManager
from .event_manager import EventManager
from .navigation_manager import NavigationManager
from .file_manager import FileManager
from .historial_manager import HistorialManager
from .window_manager import WindowManager
from .file_explorer_manager import FileExplorerManager
from .menu_manager import MenuManager
from .dual_panel_manager import DualPanelManager
from .keyboard_manager import KeyboardManager
from .multi_location_search import MultiLocationSearch
from .search_methods import SearchMethods
from .results_display import ResultsDisplay
from .theme_manager import ThemeManager
from .tree_column_config import TreeColumnConfig

class LocationTooltip:
    """Tooltip para la barra de ubicaciones"""
    def __init__(self, widget, multi_location_search):
        self.widget = widget
        self.multi_search = multi_location_search
        self.tooltip_window = None
        self.after_id = None
        
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.after_id = self.widget.after(500, self._show_tooltip)
    
    def _on_leave(self, event):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
        self._hide_tooltip()
    
    def _show_tooltip(self):
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() - 10
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.configure(bg="#ffffe0", relief="solid", bd=1)
        
        label = tk.Label(self.tooltip_window,
                        text=self.multi_search.get_tooltip_text(),
                        bg="#ffffe0", fg="#000000",
                        font=("Segoe UI", 9),
                        justify='left',
                        padx=8, pady=6)
        label.pack()
        
        self.tooltip_window.update_idletasks()
        tw, th = self.tooltip_window.winfo_reqwidth(), self.tooltip_window.winfo_reqheight()
        sw, sh = self.tooltip_window.winfo_screenwidth(), self.tooltip_window.winfo_screenheight()
        
        if x + tw > sw:
            x = sw - tw - 10
        if y - th < 0:
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        
        self.tooltip_window.geometry(f"+{x}+{y}")
    
    def _hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class BusquedaCarpetaApp:
    def __init__(self, master):
        start_time = time.time()
        
        self.master = master
        self.version = "V. 5.0 - Luce Intellettual"
        self.modo_numerico = True
        
        # Variables para menú Ver
        self.mostrar_barra_cache = tk.BooleanVar(value=True)
        self.mostrar_barra_estado = tk.BooleanVar(value=True)
        self.mostrar_historial = tk.BooleanVar(value=False)
        self.mostrar_explorador = tk.BooleanVar(value=False)
        
        # Configuración
        self.config = ConfigManager()
        self.ruta_carpeta = self.config.cargar_ruta()
        
        # Managers principales
        self.cache_manager = CacheManager(self.ruta_carpeta)
        self.search_engine = SearchEngine(self.ruta_carpeta)
        self.window_manager = WindowManager(master, self.version)
        self.multi_location_search = MultiLocationSearch(self)
        self.dual_panel_manager = DualPanelManager(self)
        
        # Módulos extraídos
        self.search_methods = SearchMethods(self)
        self.results_display = ResultsDisplay(self)
                
        # ODBC Database Manager
        try:
            from .database_manager import DatabaseManager
            self.database_manager = DatabaseManager(self)
        except ImportError:
            self.database_manager = None
        
        # Inicializar UI y Managers
        self._init_managers()
        self._init_ui()
        self._configure_app()
        
        # Configurar ventana
        self.window_manager.configurar_ventana()

        # Iniciar carga de cache diferida (100ms)
        self.master.after(100, self._cargar_cache_inteligente)

    def _cargar_cache_inteligente(self):
        """Carga cache en segundo plano para no bloquear la UI"""
        print("[APP] Iniciando carga de cache en segundo plano...")
        
        # Actualizar estado si es posible
        if hasattr(self, 'ui_callbacks'):
            self.ui_callbacks.actualizar_estado("Cargando índice...", color="blue")
        
        # Iniciar hilo de carga
        threading.Thread(target=self._load_cache_thread, daemon=True).start()

    def _load_cache_thread(self):
        """Hilo de carga de cache"""
        try:
            start_time = time.time()
            
            # Cargar cache (operación pesada)
            cache_cargado = self.cache_manager.cargar_cache()
            
            # Programar actualización de UI en hilo principal
            self.master.after(0, lambda: self._on_cache_loaded(cache_cargado, time.time() - start_time))
            
        except Exception as e:
            print(f"[APP] Error en hilo de carga: {e}")
            self.master.after(0, lambda: self.ui_callbacks.actualizar_estado("Error cargando cache", color="red"))

    def _on_cache_loaded(self, exito, duracion):
        """Callback ejecutado en hilo principal cuando termina la carga"""
        if exito:
            stats = self.cache_manager.get_cache_stats()
            carpetas = stats.get('carpetas', 0)
            print(f"[APP] Cache cargado: {carpetas:,} carpetas en {duracion:.2f}s")
            
            if hasattr(self, 'ui_callbacks'):
                self.ui_callbacks.actualizar_estado(f"Listo. {carpetas:,} carpetas indexadas.", color="green")
                
                # Si el cache está vacío o inválido, sugerir recarga
                if carpetas == 0:
                    self.ui_callbacks.actualizar_estado("Índice vacío. Presione F5 para actualizar.", color="orange")
        else:
            print("[APP] No se pudo cargar cache válido")
            if hasattr(self, 'ui_callbacks'):
                self.ui_callbacks.actualizar_estado("Índice no disponible. Presione F5.", color="orange")

    def _init_ui(self):
        """Inicializa interfaz"""
        self.app_frame = tk.Frame(self.master)
        self.app_frame.pack(fill='both', expand=True)
        
        self.dual_panel_manager.configure_grid(self.app_frame)
        
        # Contenedor principal de la app (sin grip por ahora)
        self.main_container = tk.Frame(self.app_frame)
        self.main_container.grid(row=0, column=0, sticky='nsew')
        
        # Crear UI dentro del main_container
        ui = UIComponents(self.main_container, self.version).crear_interfaz_completa()
        
        # Crear barra de atajos global
        self.create_global_shortcuts_bar()
        
        # Asignar referencias
        for ref in ['entry', 'modo_label', 'btn_buscar', 'btn_cancelar', 'tree', 
                    'btn_copiar', 'btn_abrir', 'label_estado', 'label_carpeta_info', 'configurar_scrollbars']:
            setattr(self, ref, ui[ref])
        
        # Configurar barra clickeable
        self.label_carpeta_info.bind("<Button-1>", lambda e: self.menu_manager._show_locations_config())
        self.label_carpeta_info.configure(cursor="hand2")
        self.location_tooltip = LocationTooltip(self.label_carpeta_info, self.multi_location_search)
        
        # Tree explorer
        try:
            from .tree_explorer import TreeExplorer
            self.tree_explorer = TreeExplorer(self.main_container, self)
        except ImportError:
            self.tree_explorer = None

    def _start_location_rotation(self):
        """Rotación de texto en barra"""
        self.label_carpeta_info.config(text=self.multi_location_search.get_rotation_text())
        self.master.after(3000, self._start_location_rotation)

    def _init_managers(self):
        """Inicializa managers"""
        self.ui_callbacks = UICallbacks(self)
        self.ui_manager = UIManager(self)
        self.ui_state_manager = UIStateManager(self)
        self.ui_state_manager.configurar_validacion()

        # Inicializar gestor de temas
        self.theme_manager = ThemeManager(self, tema_inicial="claro")
        self.theme_manager.aplicar_tema()
        
        self.search_manager = SearchManager(self.cache_manager, self.search_engine, None, self.ui_callbacks)
        self.search_coordinator = SearchCoordinator(self)
        self.event_manager = EventManager(self)
        self.navigation_manager = NavigationManager(self)
        self.file_manager = FileManager(self.config, self.ui_callbacks)
        self.historial_manager = HistorialManager(self)
        # Inicializar columnas del historial cuando el TreeView esté listo
        if hasattr(self.historial_manager, 'tree') and self.historial_manager.tree:
            self.historial_column_config.initialize_when_ready(self.historial_manager.tree)
        # Configurar columnas para TreeView de historial (inicializar cuando esté listo)
        self.historial_column_config = TreeColumnConfig(None, "historial")
        # Se inicializará cuando el historial se muestre por primera vez
        self.file_explorer_manager = FileExplorerManager(self)
        
        # Configurar callback para sincronizar TreeView
        self.file_explorer_manager.on_file_change_callback = self._on_explorer_file_change
        
        self.keyboard_manager = KeyboardManager(self)
        self.menu_manager = MenuManager(self)
        from .tree_expansion_handler import TreeExpansionHandler
        self.tree_expansion_handler = TreeExpansionHandler(self)
        # Configurar columnas para TreeView de resultados
        if hasattr(self, 'tree') and self.tree:
            self.results_column_config = TreeColumnConfig(self.tree, "results")

    def _configure_app(self):
        """Configuración final"""
        self.menu_manager.create_menu_bar()
        self.keyboard_manager.configure_all_shortcuts()
        self.navigation_manager.configurar_navegacion()
        
        # Eventos de botones
        self.btn_buscar.config(command=self.buscar_carpeta)
        self.btn_cancelar.config(command=self.cancelar_busqueda)
        self.btn_copiar.config(command=self.event_manager.copiar_ruta_seleccionada)
        self.btn_abrir.config(command=self.event_manager.abrir_carpeta_seleccionada)
        
        # NUEVO: Configurar expansión de subcarpetas en resultados
        if hasattr(self, 'tree_expansion_handler'):
            self.tree_expansion_handler.configure_tree_expansion()
        
        # Referencias UI
        self.ui_manager.configurar_referencias(*self._find_status_cache_frames())

    def _find_status_cache_frames(self):
        """Busca frames en jerarquía"""
        status_frame = cache_frame = None
        
        def find_frames(widget):
            nonlocal status_frame, cache_frame
            try:
                for child in widget.winfo_children():
                    if hasattr(child, 'winfo_children'):
                        for grandchild in child.winfo_children():
                            if hasattr(self, 'label_estado') and grandchild == self.label_estado:
                                status_frame = child
                            elif hasattr(self, 'label_carpeta_info') and grandchild == self.label_carpeta_info:
                                cache_frame = child
                        find_frames(child)
            except:
                pass
        
        find_frames(self.master)
        return status_frame, cache_frame

    # BÚSQUEDA - Delegada a SearchMethods
    def buscar_carpeta(self):
        """Búsqueda principal"""
        criterio = self.entry.get().strip()
        if not criterio:
            self.ui_callbacks.mostrar_advertencia("Ingrese un criterio de búsqueda")
            return
        
        self.ui_callbacks.deshabilitar_busqueda()
        self.btn_buscar.configure(text='Buscando...')
        self.ui_callbacks.actualizar_estado("Iniciando...")
        
        self.master.after(1, lambda: self.search_methods.ejecutar_busqueda(criterio))

    def cancelar_busqueda(self):
        """Cancela búsqueda"""
        self.search_coordinator.cancelar_busqueda()

    def on_tree_select(self, event):
        """Maneja selección en TreeView con DEBOUNCE"""
        # 1. Actualización visual inmediata (botones)
        hay_seleccion = len(self.tree.selection()) > 0
        estado = tk.NORMAL if hay_seleccion else tk.DISABLED
        self.btn_abrir.config(state=estado)
        self.btn_copiar.config(state=estado)
        
        # 2. Debounce para operaciones pesadas (Sync explorador)
        if hasattr(self, '_selection_timer') and self._selection_timer:
            self.master.after_cancel(self._selection_timer)
            
        self._selection_timer = self.master.after(250, self._procesar_seleccion_diferida)

    def _procesar_seleccion_diferida(self):
        """Procesa la selección después del delay (Debounce)"""
        try:
            if not len(self.tree.selection()):
                return

            
            # Sincronizar con explorador
            if hasattr(self, 'file_explorer_manager') and self.file_explorer_manager:
                if self.file_explorer_manager.is_visible():
                    try:
                        ruta = self._obtener_ruta_absoluta_seleccionada()
                        if ruta and os.path.exists(ruta) and os.path.isdir(ruta):
                            self.file_explorer_manager.load_directory(ruta)
                    except:
                        pass
            
            if callable(self.configurar_scrollbars):
                self.configurar_scrollbars()
                
        except Exception as e:
            print(f"Error en selección diferida: {e}")

    def _obtener_ruta_absoluta_seleccionada(self):
        """Obtiene ruta absoluta del item seleccionado"""
        try:
            selection = self.tree.selection()
            if not selection:
                return None
            
            item = self.tree.item(selection[0])
            values = item['values']
            
            if not values or len(values) < 2:
                return None
            
            metodo, ruta_info = values[0], values[1]
            
            if metodo == "M":
                return ruta_info if os.path.isabs(ruta_info) else None
            
            if os.path.isabs(ruta_info):
                return ruta_info
            elif hasattr(self, 'ruta_carpeta') and self.ruta_carpeta:
                return os.path.normpath(os.path.join(self.ruta_carpeta, ruta_info))
            
            return None
        except:
            return None
            
    def _on_explorer_file_change(self, ruta):
        """Callback cuando cambia el archivo en el explorador"""
        # Implementar si es necesario sincronizar hacia atrás
        pass

    # Métodos de gestión de paneles
    def get_next_available_column(self):
        
        # Contenedor principal de la app (sin grip por ahora)
        self.main_container = tk.Frame(self.app_frame)
        self.main_container.grid(row=0, column=0, sticky='nsew')
        
        # Crear UI dentro del main_container
        ui = UIComponents(self.main_container, self.version).crear_interfaz_completa()
        
        # Crear barra de atajos global
        self.create_global_shortcuts_bar()
        
        # Asignar referencias
        for ref in ['entry', 'modo_label', 'btn_buscar', 'btn_cancelar', 'tree', 
                    'btn_copiar', 'btn_abrir', 'label_estado', 'label_carpeta_info', 'configurar_scrollbars']:
            setattr(self, ref, ui[ref])
        
        # Configurar barra clickeable
        self.label_carpeta_info.bind("<Button-1>", lambda e: self.menu_manager._show_locations_config())
        self.label_carpeta_info.configure(cursor="hand2")
        self.location_tooltip = LocationTooltip(self.label_carpeta_info, self.multi_location_search)
        
        # Tree explorer
        try:
            from .tree_explorer import TreeExplorer
            self.tree_explorer = TreeExplorer(self.main_container, self)
        except ImportError:
            self.tree_explorer = None

    def _start_location_rotation(self):
        """Rotación de texto en barra"""
        self.label_carpeta_info.config(text=self.multi_location_search.get_rotation_text())
        self.master.after(3000, self._start_location_rotation)

    def _init_managers(self):
        """Inicializa managers"""
        self.ui_callbacks = UICallbacks(self)
        self.ui_manager = UIManager(self)
        self.ui_state_manager = UIStateManager(self)
        self.ui_state_manager.configurar_validacion()

        # Inicializar gestor de temas
        self.theme_manager = ThemeManager(self, tema_inicial="claro")
        self.theme_manager.aplicar_tema()
        
        self.search_manager = SearchManager(self.cache_manager, self.search_engine, None, self.ui_callbacks)
        self.search_coordinator = SearchCoordinator(self)
        self.event_manager = EventManager(self)
        self.navigation_manager = NavigationManager(self)
        self.file_manager = FileManager(self.config, self.ui_callbacks)
        self.historial_manager = HistorialManager(self)
        # Inicializar columnas del historial cuando el TreeView esté listo
        if hasattr(self.historial_manager, 'tree') and self.historial_manager.tree:
            self.historial_column_config.initialize_when_ready(self.historial_manager.tree)
        # Configurar columnas para TreeView de historial (inicializar cuando esté listo)
        self.historial_column_config = TreeColumnConfig(None, "historial")
        # Se inicializará cuando el historial se muestre por primera vez
        self.file_explorer_manager = FileExplorerManager(self)
        
        # Configurar callback para sincronizar TreeView
        self.file_explorer_manager.on_file_change_callback = self._on_explorer_file_change
        
        self.keyboard_manager = KeyboardManager(self)
        self.menu_manager = MenuManager(self)
        from .tree_expansion_handler import TreeExpansionHandler
        self.tree_expansion_handler = TreeExpansionHandler(self)
        # Configurar columnas para TreeView de resultados
        if hasattr(self, 'tree') and self.tree:
            self.results_column_config = TreeColumnConfig(self.tree, "results")

    def _configure_app(self):
        """Configuración final"""
        self.menu_manager.create_menu_bar()
        self.keyboard_manager.configure_all_shortcuts()
        self.navigation_manager.configurar_navegacion()
        
        # Eventos de botones
        self.btn_buscar.config(command=self.buscar_carpeta)
        self.btn_cancelar.config(command=self.cancelar_busqueda)
        self.btn_copiar.config(command=self.event_manager.copiar_ruta_seleccionada)
        self.btn_abrir.config(command=self.event_manager.abrir_carpeta_seleccionada)
        
        # NUEVO: Configurar expansión de subcarpetas en resultados
        if hasattr(self, 'tree_expansion_handler'):
            self.tree_expansion_handler.configure_tree_expansion()
        
        # Referencias UI
        self.ui_manager.configurar_referencias(*self._find_status_cache_frames())

    def _find_status_cache_frames(self):
        """Busca frames en jerarquía"""
        status_frame = cache_frame = None
        
        def find_frames(widget):
            nonlocal status_frame, cache_frame
            try:
                for child in widget.winfo_children():
                    if hasattr(child, 'winfo_children'):
                        for grandchild in child.winfo_children():
                            if hasattr(self, 'label_estado') and grandchild == self.label_estado:
                                status_frame = child
                            elif hasattr(self, 'label_carpeta_info') and grandchild == self.label_carpeta_info:
                                cache_frame = child
                        find_frames(child)
            except:
                pass
        
        find_frames(self.master)
        return status_frame, cache_frame

    # BÚSQUEDA - Delegada a SearchMethods
    def buscar_carpeta(self):
        """Búsqueda principal"""
        criterio = self.entry.get().strip()
        if not criterio:
            self.ui_callbacks.mostrar_advertencia("Ingrese un criterio de búsqueda")
            return
        
        self.ui_callbacks.deshabilitar_busqueda()
        self.btn_buscar.configure(text='Buscando...')
        self.ui_callbacks.actualizar_estado("Iniciando...")
        
        self.master.after(1, lambda: self.search_methods.ejecutar_busqueda(criterio))

    def cancelar_busqueda(self):
        """Cancela búsqueda"""
        self.search_coordinator.cancelar_busqueda()

    def on_tree_select(self, event):
        """Maneja selección en TreeView con DEBOUNCE"""
        # 1. Actualización visual inmediata (botones)
        hay_seleccion = len(self.tree.selection()) > 0
        estado = tk.NORMAL if hay_seleccion else tk.DISABLED
        self.btn_abrir.config(state=estado)
        self.btn_copiar.config(state=estado)
        
        # 2. Debounce para operaciones pesadas (Sync explorador)
        if hasattr(self, '_selection_timer') and self._selection_timer:
            self.master.after_cancel(self._selection_timer)
            
        self._selection_timer = self.master.after(250, self._procesar_seleccion_diferida)

    def _procesar_seleccion_diferida(self):
        """Procesa la selección después del delay (Debounce)"""
        try:
            if not len(self.tree.selection()):
                return

            
            # Sincronizar con explorador
            if hasattr(self, 'file_explorer_manager') and self.file_explorer_manager:
                if self.file_explorer_manager.is_visible():
                    try:
                        ruta = self._obtener_ruta_absoluta_seleccionada()
                        if ruta and os.path.exists(ruta) and os.path.isdir(ruta):
                            self.file_explorer_manager.load_directory(ruta)
                    except:
                        pass
            
            if callable(self.configurar_scrollbars):
                self.configurar_scrollbars()
                
        except Exception as e:
            print(f"Error en selección diferida: {e}")

    def _obtener_ruta_absoluta_seleccionada(self):
        """Obtiene ruta absoluta del item seleccionado"""
        try:
            selection = self.tree.selection()
            if not selection:
                return None
            
            item = self.tree.item(selection[0])
            values = item['values']
            
            if not values or len(values) < 2:
                return None
            
            metodo, ruta_info = values[0], values[1]
            
            if metodo == "M":
                return ruta_info if os.path.isabs(ruta_info) else None
            
            if os.path.isabs(ruta_info):
                return ruta_info
            elif hasattr(self, 'ruta_carpeta') and self.ruta_carpeta:
                return os.path.normpath(os.path.join(self.ruta_carpeta, ruta_info))
            
            return None
        except:
            return None
            
    def _on_explorer_file_change(self, ruta):
        """Callback cuando cambia el archivo en el explorador"""
        # Implementar si es necesario sincronizar hacia atrás
        pass

    # Métodos de gestión de paneles
    def get_next_available_column(self):
        return self.dual_panel_manager.get_next_available_column()

    def assign_panel_position(self, panel_type):
        return self.dual_panel_manager.assign_panel_position(panel_type)

    def release_panel_position(self, panel_type):
        return self.dual_panel_manager.release_panel_position(panel_type)

    # Métodos de toggle delegados (Requeridos por MenuManager)
    def toggle_historial(self):
        """Muestra u oculta el historial"""
        if self.mostrar_historial.get():
            col = self.dual_panel_manager.assign_panel_position('historial')
            self.historial_manager.mostrar_en_columna(col)
        else:
            self.historial_manager.ocultar()
            self.dual_panel_manager.release_panel_position('historial')

    def toggle_explorador(self):
        """Muestra u oculta el explorador"""
        if self.mostrar_explorador.get():
            col = self.dual_panel_manager.assign_panel_position('explorador')
            if self.file_explorer_manager:
                self.file_explorer_manager.mostrar_en_columna(col)
        else:
            if self.file_explorer_manager:
                self.file_explorer_manager.ocultar()
            self.dual_panel_manager.release_panel_position('explorador')

    def toggle_barra_cache(self):
        self.ui_manager.toggle_barra_cache()

        self.ui_callbacks = UICallbacks(self)
        self.ui_manager = UIManager(self)
        self.ui_state_manager = UIStateManager(self)
        self.ui_state_manager.configurar_validacion()

        # Inicializar gestor de temas
        self.theme_manager = ThemeManager(self, tema_inicial="claro")
        self.theme_manager.aplicar_tema()
        
        self.search_manager = SearchManager(self.cache_manager, self.search_engine, None, self.ui_callbacks)
        self.search_coordinator = SearchCoordinator(self)
        self.event_manager = EventManager(self)
        self.navigation_manager = NavigationManager(self)
        self.file_manager = FileManager(self.config, self.ui_callbacks)
        self.historial_manager = HistorialManager(self)
        # Inicializar columnas del historial cuando el TreeView esté listo
        if hasattr(self.historial_manager, 'tree') and self.historial_manager.tree:
            self.historial_column_config.initialize_when_ready(self.historial_manager.tree)
        # Configurar columnas para TreeView de historial (inicializar cuando esté listo)
        self.historial_column_config = TreeColumnConfig(None, "historial")
        # Se inicializará cuando el historial se muestre por primera vez
        self.file_explorer_manager = FileExplorerManager(self)
        
        # Configurar callback para sincronizar TreeView
        self.file_explorer_manager.on_file_change_callback = self._on_explorer_file_change
        
        self.keyboard_manager = KeyboardManager(self)
        self.menu_manager = MenuManager(self)
        from .tree_expansion_handler import TreeExpansionHandler
        self.tree_expansion_handler = TreeExpansionHandler(self)
        # Configurar columnas para TreeView de resultados
        if hasattr(self, 'tree') and self.tree:
            self.results_column_config = TreeColumnConfig(self.tree, "results")

    def _configure_app(self):
        """Configuración final"""
        self.menu_manager.create_menu_bar()
        self.keyboard_manager.configure_all_shortcuts()
        self.navigation_manager.configurar_navegacion()
        
        # Eventos de botones
        self.btn_buscar.config(command=self.buscar_carpeta)
        self.btn_cancelar.config(command=self.cancelar_busqueda)
        self.btn_copiar.config(command=self.event_manager.copiar_ruta_seleccionada)
        self.btn_abrir.config(command=self.event_manager.abrir_carpeta_seleccionada)
        
        # NUEVO: Configurar expansión de subcarpetas en resultados
        if hasattr(self, 'tree_expansion_handler'):
            self.tree_expansion_handler.configure_tree_expansion()
        
        # Referencias UI
        self.ui_manager.configurar_referencias(*self._find_status_cache_frames())

    def _find_status_cache_frames(self):
        """Busca frames en jerarquía"""
        status_frame = cache_frame = None
        
        def find_frames(widget):
            nonlocal status_frame, cache_frame
            try:
                for child in widget.winfo_children():
                    if hasattr(child, 'winfo_children'):
                        for grandchild in child.winfo_children():
                            if hasattr(self, 'label_estado') and grandchild == self.label_estado:
                                status_frame = child
                            elif hasattr(self, 'label_carpeta_info') and grandchild == self.label_carpeta_info:
                                cache_frame = child
                        find_frames(child)
            except:
                pass
        
        find_frames(self.master)
        return status_frame, cache_frame

    # BÚSQUEDA - Delegada a SearchMethods
    def buscar_carpeta(self):
        """Búsqueda principal"""
        criterio = self.entry.get().strip()
        if not criterio:
            self.ui_callbacks.mostrar_advertencia("Ingrese un criterio de búsqueda")
            return
        
        self.ui_callbacks.deshabilitar_busqueda()
        self.btn_buscar.configure(text='Buscando...')
        self.ui_callbacks.actualizar_estado("Iniciando...")
        
        self.master.after(1, lambda: self.search_methods.ejecutar_busqueda(criterio))

    def cancelar_busqueda(self):
        """Cancela búsqueda"""
        self.search_coordinator.cancelar_busqueda()

    def on_tree_select(self, event):
        """Maneja selección en TreeView con DEBOUNCE"""
        # 1. Actualización visual inmediata (botones)
        hay_seleccion = len(self.tree.selection()) > 0
        estado = tk.NORMAL if hay_seleccion else tk.DISABLED
        self.btn_abrir.config(state=estado)
        self.btn_copiar.config(state=estado)
        
        # 2. Debounce para operaciones pesadas (Sync explorador)
        if hasattr(self, '_selection_timer') and self._selection_timer:
            self.master.after_cancel(self._selection_timer)
            
        self._selection_timer = self.master.after(250, self._procesar_seleccion_diferida)

    def _procesar_seleccion_diferida(self):
        """Procesa la selección después del delay (Debounce)"""
        try:
            if not len(self.tree.selection()):
                return

            
            # Sincronizar con explorador
            if hasattr(self, 'file_explorer_manager') and self.file_explorer_manager:
                if self.file_explorer_manager.is_visible():
                    try:
                        ruta = self._obtener_ruta_absoluta_seleccionada()
                        if ruta and os.path.exists(ruta) and os.path.isdir(ruta):
                            self.file_explorer_manager.load_directory(ruta)
                    except:
                        pass
            
            if callable(self.configurar_scrollbars):
                self.configurar_scrollbars()
                
        except Exception as e:
            print(f"Error en selección diferida: {e}")

    def _obtener_ruta_absoluta_seleccionada(self):
        """Obtiene ruta absoluta del item seleccionado"""
        try:
            selection = self.tree.selection()
            if not selection:
                return None
            
            item = self.tree.item(selection[0])
            values = item['values']
            
            if not values or len(values) < 2:
                return None
            
            metodo, ruta_info = values[0], values[1]
            
            if metodo == "M":
                return ruta_info if os.path.isabs(ruta_info) else None
            
            if os.path.isabs(ruta_info):
                return ruta_info
            elif hasattr(self, 'ruta_carpeta') and self.ruta_carpeta:
                return os.path.normpath(os.path.join(self.ruta_carpeta, ruta_info))
            
            return None
        except:
            return None
            
    def _on_explorer_file_change(self, ruta):
        """Callback cuando cambia el archivo en el explorador"""
        # Implementar si es necesario sincronizar hacia atrás
        pass

    # Métodos de gestión de paneles
    def get_next_available_column(self):
        return self.dual_panel_manager.get_next_available_column()

    def assign_panel_position(self, panel_type):
        return self.dual_panel_manager.assign_panel_position(panel_type)

    def release_panel_position(self, panel_type):
        return self.dual_panel_manager.release_panel_position(panel_type)

    # Métodos de toggle delegados (Requeridos por MenuManager)
    def toggle_historial(self):
        """Muestra u oculta el historial"""
        if self.mostrar_historial.get():
            col = self.dual_panel_manager.assign_panel_position('historial')
            self.historial_manager.mostrar_en_columna(col)
        else:
            self.historial_manager.ocultar()
            self.dual_panel_manager.release_panel_position('historial')

    def toggle_explorador(self):
        """Muestra u oculta el explorador"""
        if self.mostrar_explorador.get():
            col = self.dual_panel_manager.assign_panel_position('explorador')
            if self.file_explorer_manager:
                self.file_explorer_manager.mostrar_en_columna(col)
        else:
            if self.file_explorer_manager:
                self.file_explorer_manager.ocultar()
            self.dual_panel_manager.release_panel_position('explorador')

    def toggle_barra_cache(self):
        self.ui_manager.toggle_barra_cache()

    def toggle_barra_estado(self):
        self.ui_manager.toggle_barra_estado()
        
    def actualizar_info_carpeta(self):
        """Actualiza la etiqueta de información de la carpeta"""
        if hasattr(self, 'label_carpeta_info'):
            self.label_carpeta_info.config(text=f"Carpeta: {self.ruta_carpeta}")

    def create_global_shortcuts_bar(self):
        """Crea la barra de atajos global en la parte inferior"""
        shortcuts_frame = tk.Frame(self.main_container, bg="#f0f0f0", height=25)
        shortcuts_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        
        # Estilo para las etiquetas de atajos
        style_key = {"font": ("Segoe UI", 8, "bold"), "bg": "#e0e0e0", "fg": "#333333", "padx": 6, "pady": 2}
        style_desc = {"font": ("Segoe UI", 8), "bg": "#f0f0f0", "fg": "#666666", "padx": 2}
        
        shortcuts = [
            ("F1", "Ayuda"),
            ("F4", "Modo"),
            ("F5", "Buscar"),
            ("F6", "Copiar"),
            ("F7", "Abrir"),
            ("F12", "Tema"),
            ("Ctrl+U", "Ubicaciones")
        ]
        
        # Contenedor centrado para los atajos
        container = tk.Frame(shortcuts_frame, bg="#f0f0f0")
        container.pack(expand=True, fill=tk.Y)
        
        for key, desc in shortcuts:
            frame = tk.Frame(container, bg="#f0f0f0")
            frame.pack(side=tk.LEFT, padx=8, pady=2)
            
            lbl_key = tk.Label(frame, text=key, **style_key, relief="solid", bd=1)
            lbl_key.pack(side=tk.LEFT)
            
            lbl_desc = tk.Label(frame, text=desc, **style_desc)
            lbl_desc.pack(side=tk.LEFT)
