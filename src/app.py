# src/app.py - Aplicación Principal V.4.5 - REFACTORIZADO
import os
import tkinter as tk
import time

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
        self.version = "V. 4.5 - Paneles Duales con Redimensión"
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
        
        # Configurar ventana
        self.window_manager.configurar_ventana()
        self.tree_explorer = None
        
        # Inicializar
        self._init_ui()
        self._init_managers()
        self._configure_app()
        self._start_location_rotation()
        self._cargar_cache_inteligente()
        
        print(f"[PROFILE] App iniciada en: {time.time() - start_time:.3f}s")
        
        # Crear barra de atajos global
        self.create_global_shortcuts_bar()

    def _cargar_cache_inteligente(self):
        """Carga cache solo si no existe"""
        try:
            cache_cargado = self.cache_manager.cargar_cache()
            
            if cache_cargado and self.cache_manager.cache.valido:
                stats = self.cache_manager.get_cache_stats()
                if stats.get('carpetas', 0) > 0:
                    return True
            
            if self.ruta_carpeta and os.path.exists(self.ruta_carpeta):
                import threading
                threading.Thread(target=self.cache_manager.construir_cache, daemon=True).start()
                return True
            
            return False
        except:
            return False

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
        """Maneja selección en TreeView"""
        hay_seleccion = len(self.tree.selection()) > 0
        estado = tk.NORMAL if hay_seleccion else tk.DISABLED
        
        self.btn_abrir.config(state=estado)
        self.btn_copiar.config(state=estado)
        
        # Sincronizar con explorador
        if hay_seleccion and hasattr(self, 'file_explorer_manager') and self.file_explorer_manager:
            if self.file_explorer_manager.is_visible():
                try:
                    ruta = self._obtener_ruta_absoluta_seleccionada()
                    if ruta and os.path.exists(ruta) and os.path.isdir(ruta):
                        self.file_explorer_manager.load_directory(ruta)
                except:
                    pass
        
        if callable(self.configurar_scrollbars):
            self.configurar_scrollbars()

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

    # Métodos de gestión de paneles
    def get_next_available_column(self):
        return self.dual_panel_manager.get_next_available_column()

    def assign_panel_position(self, panel_type):
        return self.dual_panel_manager.assign_panel_position(panel_type)

    def release_panel_position(self, panel_type):
        return self.dual_panel_manager.release_panel_position(panel_type)


    def toggle_explorador(self):
        return self.keyboard_manager.toggle_explorador()

    def toggle_barra_cache(self):
        if hasattr(self, 'ui_manager'):
            self.ui_manager.toggle_barra_cache()

    def toggle_barra_estado(self):
        if hasattr(self, 'ui_manager'):
            self.ui_manager.toggle_barra_estado()

    # Métodos de navegación
    
    def actualizar_info_carpeta(self):
        """Actualiza información de la carpeta seleccionada en la UI"""
        try:
            if hasattr(self, 'ruta_carpeta') and self.ruta_carpeta:
                # Aquí se actualizaría algún label o status con info de la carpeta
                # Por ahora, solo logging
                print(f"[INFO] Carpeta actualizada: {self.ruta_carpeta}")
                
                # Si existe un label de carpeta, actualizarlo
                if hasattr(self, 'label_carpeta'):
                    nombre_carpeta = os.path.basename(self.ruta_carpeta)
                    self.label_carpeta.config(text=f"📁 {nombre_carpeta}")
        except Exception as e:
            print(f"[ERROR] actualizar_info_carpeta: {e}")

    def configurar_navegacion_completa(self):
        self.keyboard_manager.configurar_navegacion_completa()

    def focus_widget_and_break(self, widget):
        return self.keyboard_manager.focus_widget_and_break(widget)

    # Utilidades
    def on_entry_click(self):
        self.entry.configure(state='normal')
        self.entry.focus_set()

    def obtener_seleccion_tabla(self):
        return self.ui_callbacks.obtener_seleccion_tabla()

    # Delegación
    def buscar_carpetas(self, criterio):
        return self.search_coordinator.ejecutar_busqueda(criterio)

    def mostrar_resultados(self, resultados, criterio, metodo="C"):
        self.ui_callbacks.mostrar_resultados(resultados, criterio, metodo)

    def actualizar_estado(self, mensaje):
        self.ui_callbacks.actualizar_estado(mensaje)

    def finalizar_busqueda_async(self, resultados, criterio):
        self.ui_callbacks.finalizar_busqueda_async(resultados, criterio)

    def deshabilitar_busqueda(self):
        self.ui_callbacks.deshabilitar_busqueda()

    def habilitar_busqueda(self):
        self.ui_callbacks.habilitar_busqueda()

    def _finalizar_busqueda_con_historial(self, metodo, num_resultados):
        if hasattr(self, 'search_coordinator'):
            self.search_coordinator.finalizar_busqueda_con_historial(metodo, num_resultados)
    
    def create_global_shortcuts_bar(self):
        """Crea una barra de estado global con todos los atajos de teclado"""
        # Frame en la parte inferior de la ventana principal
        self.shortcuts_bar = tk.Frame(self.master, bg='#34495e', height=26)
        self.shortcuts_bar.pack(side='bottom', fill='x')
        self.shortcuts_bar.pack_propagate(False)
        
        # Frame interior para mejor control
        inner_frame = tk.Frame(self.shortcuts_bar, bg='#34495e')
        inner_frame.pack(fill='both', expand=True, padx=10, pady=3)
        
        # Lista de atajos con sus descripciones
        shortcuts = [
            ("F4", "Cambiar Modo", "#e67e22"),
            ("F5", "Enfocar Editor", "#3498db"),
            ("F6", "Copiar Ruta", "#9b59b6"),
            ("F7", "Abrir Archivo", "#e74c3c"),
            ("Ctrl+Shift+E", "Explorador", "#2ecc71"),
            ("Ctrl+Shift+H", "Historial", "#f39c12"),
            ("F12", "Cambiar Tema", "#8e44ad"),
        ]
        
        for i, (key, desc, color) in enumerate(shortcuts):
            if i > 0:
                # Separador
                tk.Label(inner_frame, text="│", bg='#34495e', 
                        fg='#7f8c8d', font=('Segoe UI', 9)).pack(side='left', padx=5)
            
            # Tecla
            tk.Label(inner_frame, text=key, bg='#34495e', 
                    fg=color, font=('Segoe UI', 9, 'bold')).pack(side='left')
            
            # Descripción
            tk.Label(inner_frame, text=f": {desc}", bg='#34495e', 
                    fg='#ecf0f1', font=('Segoe UI', 9)).pack(side='left')
    
    def _start_main_resize(self, event):
        """Inicia redimensionamiento de la app principal"""
        self.resize_start_x = event.x_root
        self.resize_start_width = self.main_container_wrapper.winfo_width()

    def _do_main_resize(self, event):
        """Realiza redimensionamiento de la app principal"""
        if not hasattr(self, 'main_container_wrapper'):
            return
        
        # Calcular diferencia
        diff = event.x_root - self.resize_start_x
        new_width = self.resize_start_width + diff
        
        # Limitar ancho (mínimo 600px, máximo según pantalla)
        screen_width = self.master.winfo_screenwidth()
        new_width = max(600, min(screen_width - 300, new_width))
        
        # Aplicar nuevo ancho al wrapper del main container
        self.main_container_wrapper.config(width=new_width)
        self.main_container_wrapper.pack_propagate(False)