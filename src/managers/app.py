# src/app.py - Aplicación Principal V.5.0 (Luce Intellettual) - REFACTORIZADO
import os
import tkinter as tk
import time


from ..core.config import ConfigManager
from ..core.cache_manager import CacheManager
from ..core.search_engine import SearchEngine
from .search_coordinator import SearchCoordinator
from .search_manager import SearchManager
from ..ui.ui_components import UIComponents
from .ui_manager import UIManager
from .event_manager import EventManager
from .navigation_manager import NavigationManager
from .file_manager import FileManager
from .historial_manager import HistorialManager
from .window_manager import WindowManager
from .file_explorer_manager import FileExplorerManager
from .menu_manager import MenuManager
from .dual_panel_manager import DualPanelManager
from .keyboard_manager import KeyboardManager
from ..core.multi_location_search import MultiLocationSearch
from .search_methods import SearchMethods
from ..ui.results_display import ResultsDisplay
from ..ui.theme_manager import ThemeManager
from .column_manager import ColumnManager



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

from ..core.constants import APP_VERSION

class BusquedaCarpetaApp:
    def __init__(self, master):
        self.master = master
        self.config = ConfigManager() # Cargar configuración global
        
        start_time = time.time()
        self.version = APP_VERSION
        
        # Cargar estados desde configuración
        self.mostrar_explorador = tk.BooleanVar(value=self.config.get("show_explorer", False))
        self.mostrar_historial = tk.BooleanVar(value=self.config.get("show_history", False))
        self.incluir_archivos = tk.BooleanVar(value=False)
        self._selection_timer = None
        self.mostrar_barra_cache = tk.BooleanVar(value=self.config.get("show_cache_bar", True))
        self.mostrar_barra_estado = tk.BooleanVar(value=self.config.get("show_status_bar", True))
        self.modo_numerico = True
        self._is_initializing = True 
        
        # Sincronizar cambios de UI con configuración
        self.mostrar_explorador.trace_add("write", lambda *a: self.config.set("show_explorer", self.mostrar_explorador.get()))
        self.mostrar_historial.trace_add("write", lambda *a: self.config.set("show_history", self.mostrar_historial.get()))
        
        # 1. Configuración y Estilo (Crítico)
        self.config = ConfigManager()
        self.ruta_carpeta = self.config.cargar_ruta()
        self.theme_manager = ThemeManager(self, tema_inicial=self.config.get("theme", "claro"))
        
        # 2. Window Manager
        self.window_manager = WindowManager(master, self.version, self)
        self.window_manager.configurar_ventana(
            saved_geometry=self.config.get("window_geometry"),
            manual_app_width=self.config.get("manual_app_width")
        )
        
        # 3. Motores de Búsqueda Básicos
        self.cache_manager = CacheManager(self.ruta_carpeta)
        self.search_engine = SearchEngine(self.ruta_carpeta)
        self.multi_location_search = MultiLocationSearch(self)
        self.dual_panel_manager = DualPanelManager(self)
        
        # 4. Inicialización de UI Core
        self._init_ui()
        self._init_managers_core()
        
        # 5. CARGA DIFERIDA (Para arranque instantáneo)
        # Retrasamos lo más pesado unos milisegundos para que la ventana aparezca YA
        self.master.after(50, self._deferred_initialization)
        
        # Protocolo de cierre
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        print(f"[PROFILE] App Skeleton cargado en: {time.time() - start_time:.3f}s")

    def _deferred_initialization(self):
        """Inicialización escalonada para evitar congelamiento de UI"""
        print("[INIT] Iniciando carga diferida por micro-tareas...")
        
        # 1. Base de Datos (ODBC) - Totalmente asíncrona
        try:
            from ..core.database_manager import DatabaseManager
            self.database_manager = DatabaseManager(self)
            self.database_manager.iniciar_conexion_asincrona()
        except: pass

        # 2. Siguiente paso: Búsqueda por Contenido (con 100ms de respiro para la UI)
        self.master.after(100, self._deferred_step_content_search)

    def _deferred_step_content_search(self):
        """Paso 2: Inicializar búsqueda por contenido"""
        self._init_content_search()
        # 3. Siguiente paso: Configuración de managers y atajos
        self.master.after(100, self._deferred_step_configure_app)

    def _deferred_step_configure_app(self):
        """Paso 3: Configuración de managers y atajos"""
        self._configure_app()
        self.create_global_shortcuts_bar()
        self._start_location_rotation()
        # 4. Siguiente paso: Cargas pesadas de cache en background
        self.master.after(100, self._deferred_step_background_loads)

    def _deferred_step_background_loads(self):
        """Paso 4: Cargas pesadas en hilos separados"""
        import threading
        # 1. Carga de carpeta principal
        threading.Thread(target=self._cargar_cache_inteligente, daemon=True).start()
        
        # 2. Precarga paralela de ubicaciones adicionales
        if hasattr(self, 'search_coordinator'):
            self.search_coordinator.pre_cargar_ubicaciones_adicionales()
        
        # 5. Restaurar visibilidad de paneles (último paso)
        self.master.after(200, self._restore_panel_visibility_safe)
        
        # 6. Limpieza final retardada
        self.master.after(3000, self._deferred_step_final_cleanup)

    def _deferred_step_final_cleanup(self):
        """Limpieza periódica tras el arranque"""
        if hasattr(self, 'search_coordinator'):
            self.search_coordinator.verificar_problemas_cache_silencioso()
        
        
        

    def _restore_panel_visibility_safe(self):
        """Restaura la visibilidad de los paneles de forma segura sin disparar resizes"""
        try:
            # Leer valores de la configuración
            restaurar_historial = self.config.get("show_history", False)
            restaurar_explorador = self.config.get("show_explorer", False)
            
            print(f"[DEBUG] Restaurando paneles (Síncrono) - Historial: {restaurar_historial}, Explorador: {restaurar_explorador}")
            
            # Aplicar visibilidad
            history_col = self.config.get("history_assigned_col", 1)
            explorer_col = self.config.get("explorer_assigned_col", 2)
            
            if history_col == explorer_col:
                history_col, explorer_col = 1, 2
                
            paneles = []
            if restaurar_historial:
                paneles.append(('historial', history_col, self.toggle_historial))
            if restaurar_explorador:
                paneles.append(('explorador', explorer_col, self.toggle_explorador))
                
            paneles.sort(key=lambda x: x[1] if x[1] is not None else 99)
            
            # Abrir en orden
            for p_type, col, method in paneles:
                method()
            
            # Finalizar inicialización
            self._finish_initialization()
        except Exception as e:
            print(f"[ERROR] Error restaurando paneles: {e}")
            self._is_initializing = False

    def _finish_initialization(self):
        self._is_initializing = False
        print("[DEBUG] Inicialización completa. Redimensionamiento inteligente habilitado.")
        
    def _cargar_cache_inteligente(self):
        """Carga cache en segundo plano"""
        try:
            # Carga síncrona del PKL (ahora corre en thread)
            print("[CACHE] Iniciando carga en background...")
            cache_cargado = self.cache_manager.cargar_cache()
            
            # Si se cargó correctamente
            if cache_cargado and self.cache_manager.cache.valido:
                stats = self.cache_manager.get_cache_stats()
                print(f"[CACHE] Cache cargado exitosamente. Carpetas: {stats.get('carpetas', 0)}")
                return True
            
            # Si no hay caché válido, iniciar construcción (ya es threaded internamente, pero aquí es seguro)
            if self.ruta_carpeta and os.path.exists(self.ruta_carpeta):
                print("[CACHE] Cache no válido o inexistente. Iniciando construcción...")
                self.cache_manager.construir_cache()
                return True
            
            return False
        except Exception as e:
            print(f"[ERROR] Falló carga de caché en background: {e}")
            return False

    def save_ui_settings(self):
        """Guarda las preferencias actuales de la interfaz"""
        try:
            # 1. Geometría y posición ABSOLUTA
            # master.winfo_geometry() puede devolver "+0+0" si se llama muy rápido
            # Capturamos los valores reales del gestor de ventanas
            self.master.update_idletasks()
            w = self.master.winfo_width()
            h = self.master.winfo_height()
            x = self.master.winfo_x()
            y = self.master.winfo_y()
            
            # Guardamos formato estandar: WxH+X+Y
            geometry = f"{w}x{h}+{x}+{y}"
            self.config.set("window_geometry", geometry)
            
            # 2. Ancho manual de la app (si se redimensionó)
            if hasattr(self, 'window_manager'):
                # Actualizar el ancho manual actual antes de guardar
                if self.window_manager.user_resized_manually:
                    self.config.set("manual_app_width", self.window_manager.manual_app_width)
                else:
                    self.config.set("manual_app_width", None)
            
            # 3. Tema actual
            if hasattr(self, 'theme_manager'):
                self.config.set("theme", self.theme_manager.tema_actual)
            
            # 4. Paneles abiertos e ÍNDICES de columna
            show_history_val = False
            history_col = None
            if hasattr(self, 'historial_manager') and self.historial_manager:
                show_history_val = self.historial_manager.visible
                history_col = self.historial_manager.assigned_column
            
            show_explorer_val = False
            explorer_col = None
            if hasattr(self, 'file_explorer_manager') and self.file_explorer_manager:
                show_explorer_val = self.file_explorer_manager.is_visible()
                explorer_col = self.file_explorer_manager.assigned_column
                
            self.config.set("show_history", show_history_val)
            self.config.set("history_assigned_col", history_col)
            self.config.set("show_explorer", show_explorer_val)
            self.config.set("explorer_assigned_col", explorer_col)
            
            # 5. Anchos de paneles individuales (Validar > 50px)
            if hasattr(self, 'file_explorer_manager'):
                w = self.file_explorer_manager.get_current_width()
                if w and w > 50: 
                    self.config.set("explorer_width", w)
            
            if hasattr(self, 'historial_manager'):
                w = self.historial_manager.get_current_width()
                if w and w > 50: 
                    self.config.set("history_width", w)
            
            # 6. Anchos de columnas y estados de TreeView (Delegado a ColumnManager)
            # Principal
            if hasattr(self, 'results_column_config'):
                self.results_column_config.save_config()
            
            # Explorador
            if hasattr(self, 'file_explorer_manager') and self.file_explorer_manager.tree:
                try:
                    tree = self.file_explorer_manager.tree
                    cols = ["#0"] + list(tree["columns"])
                    widths = {str(col): tree.column(col, 'width') for col in cols}
                    self.config.set("explorer_column_widths", widths)
                except: pass
                
            # Historial
            if hasattr(self, 'historial_manager'):
                if hasattr(self.historial_manager, 'tree') and self.historial_manager.tree:
                    tree = self.historial_manager.tree
                    cols = list(tree["columns"])
                    widths = {str(col): tree.column(col, 'width') for col in cols}
                    self.config.set("history_column_widths", widths)

            # Guardar a disco inmediatamente
            self.config.guardar_config()
            print(f"[DEBUG] Preferencias de UI (Geometría: {geometry}) y columnas guardadas")
        except Exception as e:
            print(f"[ERROR] Error guardando preferencias: {e}")

    def _init_ui(self):
        """Inicializa interfaz"""
        self.app_frame = tk.Frame(self.master)
        self.app_frame.pack(fill='both', expand=True)
        
        self.dual_panel_manager.configure_grid(self.app_frame)
        
        # Contenedor principal de la app (sin grip por ahora)
        self.main_container = tk.Frame(self.app_frame)
        self.main_container.grid(row=0, column=0, sticky='nsew')
        
        # Crear UI dentro del main_container
        col_widths = self.config.get("main_column_widths")
        ui = UIComponents(self.main_container, self.version).crear_interfaz_completa(col_widths=col_widths)
        
        # Asignar referencias
        for ref in ['entry', 'modo_label', 'btn_buscar', 'btn_cancelar', 'tree', 
                    'btn_copiar', 'btn_abrir', 'label_estado', 'label_carpeta_info', 'configurar_scrollbars', 'chk_archivos']:
            setattr(self, ref, ui[ref])
            
        self.chk_archivos.config(variable=self.incluir_archivos)
        
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

    def _init_managers_core(self):
        """Inicializa solo los managers esenciales para el UI base"""
        self.search_methods = SearchMethods(self)
        self.results_display = ResultsDisplay(self)
        self.theme_manager.aplicar_tema()
        self.ui_manager = UIManager(self)
        self.ui_manager.configurar_validacion()
        self.search_manager = SearchManager(self.cache_manager, self.search_engine, None, self.ui_manager)
        self.search_coordinator = SearchCoordinator(self)
        self.event_manager = EventManager(self)
        self.navigation_manager = NavigationManager(self)
        self.file_manager = FileManager(self.config, self.ui_manager)
        self.historial_manager = HistorialManager(self)
        self.historial_column_config = ColumnManager(None, "historial", app=self)
        self.file_explorer_manager = FileExplorerManager(self)
        self.file_explorer_manager.on_file_change_callback = self._on_explorer_file_change
        self.keyboard_manager = KeyboardManager(self)
        self.menu_manager = MenuManager(self)
        from .tree_expansion_handler import TreeExpansionHandler
        self.tree_expansion_handler = TreeExpansionHandler(self)
        if hasattr(self, 'tree') and self.tree:
            self.results_column_config = ColumnManager(self.tree, "results", app=self)

    def _init_managers(self):
        # Mantenemos este para compatibilidad, pero usamos core y deferred
        pass

    def _configure_app(self):
        """Configuración final"""
        self.menu_manager.create_menu_bar()
        self.keyboard_manager.configure_all_shortcuts()
        self.event_manager.configurar_eventos()  # ACTIVAR ATAJOS NUEVOS
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
    def buscar_carpeta(self, silenciosa=False):
        """Búsqueda principal"""
        criterio = self.entry.get().strip()
        if not criterio:
            if not silenciosa:
                self.ui_manager.mostrar_advertencia("Ingrese un criterio de búsqueda")
            return
        
        # En búsqueda automática (silenciosa), NO deshabilitar el entry para no robar foco
        self.ui_manager.deshabilitar_busqueda(incluir_entry=not silenciosa)
        
        if not silenciosa:
            self.btn_buscar.configure(text='Buscando...')
            self.ui_manager.actualizar_estado("Iniciando...")
        
        self.master.after(1, lambda: self.search_methods.ejecutar_busqueda(criterio, silenciosa=silenciosa))

    def cancelar_busqueda(self):
        """Cancela búsqueda"""
        self.search_coordinator.cancelar_busqueda()

    def on_tree_select(self, event):
        """Maneja selección en TreeView con DEBOUNCE"""
        hay_seleccion = len(self.tree.selection()) > 0
        estado = tk.NORMAL if hay_seleccion else tk.DISABLED
        
        self.btn_abrir.config(state=estado)
        self.btn_copiar.config(state=estado)
        
        # Cancelar timer anterior si existe
        if self._selection_timer:
            self.master.after_cancel(self._selection_timer)
            self._selection_timer = None
            
        # Sincronizar con explorador (con retraso de 300ms)
        if hay_seleccion and hasattr(self, 'file_explorer_manager') and self.file_explorer_manager:
            if self.file_explorer_manager.is_visible():
                # Sincronización rápida (300ms) sin robar foco del teclado
                self._selection_timer = self.master.after(300, self._sync_explorer_delayed)
        
        if callable(self.configurar_scrollbars):
            self.configurar_scrollbars()

    def _sync_explorer_delayed(self):
        """Ejecuta la sincronización después del debounce"""
        try:
            ruta = self._obtener_ruta_absoluta_seleccionada()
            if ruta and os.path.exists(ruta):
                if self.file_explorer_manager.is_visible():
                    if os.path.isdir(ruta):
                        # Para carpetas: mostrar su contenido (nueva raíz)
                        self.file_explorer_manager.load_directory(ruta)
                    else:
                        # Para archivos: resaltar su ubicación
                        self.file_explorer_manager.focus_path(ruta)
        except Exception as e:
            print(f"Error en sync delayed: {e}")
        finally:
            self._selection_timer = None

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
            
            # Estrategia 1: Buscar en el último valor (Metadata AbsPath)
            if len(values) >= 3:
                posible_abs = values[-1]
                if isinstance(posible_abs, str) and os.path.isabs(posible_abs):
                    return posible_abs
            
            # Estrategia 2: Valor en posición 1 (Ruta Relativa o Absoluta)
            ruta_info = values[1]
            if os.path.isabs(ruta_info):
                return ruta_info
            
            # Estrategia 3: Construir desde ruta base
            if hasattr(self, 'ruta_carpeta') and self.ruta_carpeta:
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

    def update_search_locations(self, locations):
        """Actualiza ubicaciones de búsqueda"""
        self.multi_location_search.reload_locations()
        self.label_carpeta_info.config(text=self.multi_location_search.get_rotation_text())

    def _on_explorer_file_change(self, operation, paths):
        """Maneja cambios de archivos del explorador"""
        print(f'[App] Cambio en explorador: {operation}')
        
        # Mostrar warning de resultados desactualizados
        if hasattr(self, 'label_estado'):
            self.label_estado.config(
                text="⚠️ Los resultados mostrados pueden estar desactualizados",
                fg='#ff6b00'  # Naranja
            )

    # Toggle methods
    def toggle_historial(self):
        return self.keyboard_manager.toggle_historial()

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
        return self.ui_manager.obtener_seleccion_tabla()

    # Delegación
    def buscar_carpetas(self, criterio):
        return self.search_coordinator.ejecutar_busqueda(criterio)

    def mostrar_resultados(self, resultados, criterio, metodo="C"):
        self.ui_manager.mostrar_resultados(resultados, criterio, metodo)

    def actualizar_estado(self, mensaje):
        self.ui_manager.actualizar_estado(mensaje)

    def finalizar_busqueda_async(self, resultados, criterio):
        self.ui_manager.finalizar_busqueda_async()

    def deshabilitar_busqueda(self):
        self.ui_manager.deshabilitar_busqueda()

    def habilitar_busqueda(self):
        self.ui_manager.habilitar_busqueda()

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
        
        # Limitar ancho (mínimo 600px, máxim        new_width = max(600, min(screen_width - 300, new_width))
        
        # Aplicar nuevo ancho al wrapper del main container
        self.main_container_wrapper.config(width=new_width)
        self.main_container_wrapper.pack_propagate(False)

    def _init_content_search(self):
        """Inicializa los componentes de búsqueda por contenido"""
        try:
            from ..core.content_indexer import ContentIndexer
            from ..core.content_locations_manager import ContentLocationsManager
            self.content_indexer = ContentIndexer(self)
            self.content_locations_manager = ContentLocationsManager()
            from ..ui.content_search_modal import ContentSearchModal
            self.content_search_modal = ContentSearchModal(self.master, self)
            self.content_search_modal.modal.title("Búsqueda Avanzada por Contenido V.7.6 - TOTAL CONTROL")
            # ATAJOS DE EMERGENCIA
            self.master.bind_all("<Control-i>", lambda e: self.content_search_modal.show_modal())
            self.master.bind_all("<Control-I>", lambda e: self.content_search_modal.show_modal())
            self.master.bind_all("<Control-o>", lambda e: self._handle_ctrl_o())
            self.master.bind_all("<Control-O>", lambda e: self._handle_ctrl_o())
            self.master.bind_all("<Control-u>", lambda e: self.menu_manager._show_locations_config())
            self.master.bind_all("<Control-U>", lambda e: self.menu_manager._show_locations_config())
            self.master.bind_all("<Escape>", lambda e: self.cancelar_busqueda())
        except Exception as e:
            print(f"[CONTENT] Error inicializando búsqueda por contenido: {e}")

    def _handle_ctrl_o(self):
        """Maneja Ctrl+O de forma contextual"""
        # 1. Si el buscador de contenido está abierto, abrir su resultado
        if hasattr(self, 'content_search_modal') and self.content_search_modal.modal and self.content_search_modal.modal.winfo_exists():
            # No importa el foco exacto, si el buscador es visible, abrimos de ahí
            self.content_search_modal._open_selected_result()
            return

        # 2. Si el explorador de archivos está visible, abrir de ahí
        if hasattr(self, 'file_explorer_manager') and self.file_explorer_manager.is_visible():
            self.file_explorer_manager.open_selected_item()
            return
        
        # 3. Por defecto, usar la lógica estándar del EventManager
        
    def on_close(self):
        """Cierre ordenado de la aplicación guardando preferencias"""
        print("[App] Cerrando y guardando configuración...")
        try:
            self.save_ui_settings()
            if hasattr(self, 'config'):
                self.config.save_config()
            if hasattr(self, 'content_indexer'):
                self.content_indexer.stop_indexing()
        except Exception as e:
            print(f"[ERROR] Error al cerrar: {e}")
        self.master.destroy()

    def save_ui_settings(self):
        """Guarda la geometría (Tamaño + Posición) y preferencias de la ventana principal"""
        if hasattr(self, 'master') and hasattr(self, 'config'):
            geom = self.master.geometry()
            self.config.set("window_geometry", geom)
            print(f"[UI] Geometría guardada (X,Y incluido): {geom}")

    def _update_global_status(self):
        """Actualiza la barra azul con el resumen global del índice"""
        if hasattr(self, 'content_indexer') and hasattr(self, 'ui_manager'):
            stats = self.content_indexer.get_index_stats()
            total = stats.get('total_files', 0)
            if hasattr(self.ui_manager, 'status_label_index'):
                self.ui_manager.status_label_index.config(
                    text=f" 🗃️ Total Archivos en Índice: {total:,} | V.6.3 - PARADISO"
                )
