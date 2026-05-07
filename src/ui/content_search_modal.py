# src/ui/content_search_modal.py - Gestión de Búsqueda por Contenido V.6.0 (Empíreo)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time
import re
from datetime import datetime

class ContentSearchModal:
    """Ventana para buscar dentro de archivos y configurar la indexación con controles completos"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.modal = None
        self.config_tree = None
        self.results_tree = None      # Árbol para búsqueda de contenido
        self.files_results_tree = None # Árbol para búsqueda de archivos
        self.config_col_manager = None
        
        # Managers
        if not hasattr(self.app, 'content_indexer'):
             from ..core.content_indexer import ContentIndexer
             self.app.content_indexer = ContentIndexer(self.app)
             
        if not hasattr(self.app, 'content_locations_manager'):
            from ..core.content_locations_manager import ContentLocationsManager
            self.app.content_locations_manager = ContentLocationsManager()
            
        self.indexer = self.app.content_indexer
        self.loc_manager = self.app.content_locations_manager
        
        # Variables de control
        self.progress_var = tk.StringVar(value="Listo")
        self.percent_var = tk.DoubleVar(value=0)
        self.search_query_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Cargando estado del índice...")
        self.timer_str_var = tk.StringVar(value="00:00")
        
        self.start_time = 0
        self.is_indexing = False
        self.common_base_var = tk.StringVar(value="")
        self.preview_window = None  # Ventana para Quick Look
        self.preview_text_widget = None # Referencia al widget de texto
        
        # Filtros por extensión (V.10.0)
        self.search_filter_ext = tk.StringVar(value="all")
        self.filter_buttons = {} # Guardar referencias para cambiar estilos
        
        # Referencias a entries para foco global
        self.search_entry_content = None
        self.search_entry_files = None
        
        self._update_status_from_locs()
    
    def _update_status_from_locs(self):
        latest = None
        for loc in self.loc_manager.locations:
            last = loc.get('last_indexed')
            if last and last != "Nunca":
                try:
                    dt = datetime.strptime(last, "%d/%m/%Y %H:%M")
                    if latest is None or dt > latest: latest = dt
                except: pass
        if latest: self.status_var.set(f"📊 Índice actualizado: {latest.strftime('%d/%m/%Y %H:%M')}")
        else: self.status_var.set("📊 Índice no construido aún")

    def show_modal(self, initial_path=None):
        if self.modal and self.modal.winfo_exists():
            self.modal.lift()
            self.modal.focus_force()
            return
        self._create_modal_window()
        self._create_modal_content()
        self._populate_config_tree()
        
        # Integrar ColumnManager para la tabla de configuración
        from ..managers.column_manager import ColumnManager
        self.config_col_manager = ColumnManager(self.config_tree, "index_config", self.app)
        
        if hasattr(self.app, 'theme_manager'):
            self.app.theme_manager.register_callback(self.aplicar_tema)
            self.aplicar_tema()
            # Aplicar modo oscuro nativo a la ventana modal
            self.app.theme_manager.set_dark_mode_to_window(self.modal)
            
        # PROCESAR RUTA INICIAL SI SE PROPORCIONA
        if initial_path and os.path.exists(initial_path) and os.path.isdir(initial_path):
            if self.loc_manager.add_location(initial_path, os.path.basename(initial_path)):
                self._populate_config_tree()
                self.notebook.select(self.tab_config) # Cambiar a la pestaña de configuración
                self.status_var.set(f"✅ Carpeta añadida dinámicamente: {os.path.basename(initial_path)}")
    
    def _create_modal_window(self):
        self.modal = tk.Toplevel(self.parent)
        self.modal.title("Búsqueda Avanzada por Contenido V.6.3 - PARADISO")
        self.modal.geometry("900x780")
        self.modal.update_idletasks()
        x = (self.modal.winfo_screenwidth() - 900) // 2
        y = (self.modal.winfo_screenheight() - 780) // 2
        self.modal.geometry(f"900x780+{x}+{y}")
        self._closing = False
        
        # Cierre controlado: interceptar X, ESC y Alt+F4
        self.modal.protocol("WM_DELETE_WINDOW", self._on_close)
        self.modal.bind("<Escape>", lambda e: self._on_close())
        
        self.modal.bind("<F12>", lambda e: self.app.theme_manager.toggle_tema())
        self.modal.bind("<Control-l>", lambda e: self._clear_search())
        self.modal.bind("<Control-L>", lambda e: self._clear_search())

    def _on_close(self):
        """Cierre seguro: detiene el indexador y destruye la ventana sin bloquear la app"""
        if self._closing:
            return  # Evitar doble llamado
        self._closing = True
        
        # Desregistrar callback de tema para evitar llamadas post-destroy
        if hasattr(self.app, 'theme_manager'):
            try:
                self.app.theme_manager.theme_callbacks = [
                    cb for cb in self.app.theme_manager.theme_callbacks
                    if cb != self.aplicar_tema
                ]
            except: pass
        
        # Si está indexando, enviar señal de stop y dejar que el hilo termine solo
        if self.is_indexing:
            self.indexer.stop_indexing()
        
        # Destruir inmediatamente - el hilo tiene guardas para modal destruido
        try:
            self.modal.destroy()
        except: pass

    def _create_modal_content(self):
        self.notebook = ttk.Notebook(self.modal)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(10, 0))
        
        # TAB 1: Buscar Texto
        try:
            self.tab_search = tk.Frame(self.notebook)
            self.notebook.add(self.tab_search, text="  🔍 Buscar Texto  ")
            self.results_tree = self._setup_search_view(self.tab_search, "content")
        except Exception as e:
            print(f"Error creando pestaña búsqueda texto: {e}")
            
        # TAB 2: Buscar Archivos
        try:
            self.tab_files = tk.Frame(self.notebook)
            self.notebook.add(self.tab_files, text="  📂 Buscar Archivos  ")
            self.files_results_tree = self._setup_search_view(self.tab_files, "path")
        except Exception as e:
            print(f"Error creando pestaña búsqueda archivos: {e}")
        
        # TAB 3: Configuración
        try:
            self.tab_config = tk.Frame(self.notebook)
            self.notebook.add(self.tab_config, text="  ⚙️ Configuración e Índice  ")
            self._create_config_tab()
        except Exception as e:
            print(f"Error creando pestaña config: {e}")

        self.status_bar_frame = tk.Frame(self.modal, height=35, relief='flat')
        self.status_bar_frame.pack(side='bottom', fill='x')
        self.lbl_status_bar = tk.Label(self.status_bar_frame, textvariable=self.status_var, font=("Segoe UI", 9), padx=15, pady=8)
        self.lbl_status_bar.pack(side='left')
        self.lbl_timer = tk.Label(self.status_bar_frame, textvariable=self.timer_str_var, font=("Consolas", 10, "bold"), padx=15, pady=8)
        self.lbl_timer.pack(side='right')

    def _setup_search_view(self, container, search_type):
        """Crea una vista de búsqueda reutilizable para cualquier tipo de campo"""
        # --- 1. Crear el contenedor de resultados PRIMERO ---
        res_cnt = tk.Frame(container, padx=20)
        res_cnt.pack(side='bottom', fill='both', expand=True, pady=(0, 20))
        
        tree = ttk.Treeview(res_cnt, columns=("file", "path"), show="headings", style="Treeview")
        tree.heading("file", text="Archivo", anchor='w')
        tree.heading("path", text="Ubicación Relativa", anchor='w')
        tree.column("file", width=250, stretch=False)
        tree.column("path", width=500, stretch=False)
        
        v_scroll = ttk.Scrollbar(res_cnt, orient="vertical", command=tree.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x', padx=20)

        # --- 2. Crear el encabezado ---
        header = tk.Frame(container, padx=20, pady=20)
        header.pack(side='top', fill='x')
        
        label_text = "Buscar texto en los archivos:" if search_type == "content" else "Buscar entre los nombres de archivos:"
        tk.Label(header, text=label_text, font=("Segoe UI", 10)).pack(anchor='w')
        
        if search_type == "content":
            self.lbl_ocr_warning = tk.Label(header, text="⚠ PDFs escaneados (imágenes) son invisibles sin OCR.", font=("Segoe UI", 8, "italic"))
            self.lbl_ocr_warning.pack(anchor='w', pady=(0, 2))
            
            # Guía de sintaxis avanzada (V.9.1)
            self.lbl_syntax_help = tk.Label(header, text='💡 "frase exacta"  +incluir  -excluir  *wildcard (Ej: "recurso reposicion"+extraordinario*)', 
                                         font=("Segoe UI", 8, "italic"))
            self.lbl_syntax_help.pack(anchor='w', pady=(0, 5))
        
        entry_cnt = tk.Frame(header)
        entry_cnt.pack(fill='x')
        
        # Variables locales para este componente
        query_var = tk.StringVar()
        entry = tk.Entry(entry_cnt, textvariable=query_var, font=("Segoe UI", 11), relief='solid', bd=1)
        entry.pack(side='left', fill='x', expand=True, ipady=8, padx=(0, 10))
        
        # Guardar referencia para foco global (V.10.0)
        if search_type == "content":
            self.search_entry_content = entry
        else:
            self.search_entry_files = entry
        
        # Helper para disparar la búsqueda
        def trigger_search(): self._do_search(query_var.get(), search_type, tree)

        entry.bind("<Return>", lambda e: trigger_search())
        if search_type == "content": entry.focus_set()
        
        btn_go = tk.Button(entry_cnt, text="🔍 Buscar", command=trigger_search, font=("Segoe UI", 10, "bold"), relief='flat', padx=20, pady=8, cursor="hand2")
        btn_go.pack(side='left', padx=(0, 5))
        
        btn_clear = tk.Button(entry_cnt, text="🧹 Limpiar", command=lambda: [query_var.set(""), tree.delete(*tree.get_children())], font=("Segoe UI", 9), relief='flat', padx=12, pady=8, cursor="hand2")
        btn_clear.pack(side='left')

        # --- FILTROS POR EXTENSIÓN (Chips V.10.0) ---
        if search_type == "content":
            filter_frame = tk.Frame(header)
            filter_frame.pack(fill='x', pady=(10, 0))
            
            tk.Label(filter_frame, text="Filtrar por:", font=("Segoe UI", 8, "bold"), fg="#888888").pack(side='left', padx=(0, 10))
            
            extensions = [
                ("Todos", "all"),
                ("PDF", ".pdf"),
                ("Word", ".docx"),
                ("Excel", ".xlsx")
            ]
            
            for label, ext in extensions:
                btn = tk.Button(filter_frame, text=label, 
                              command=lambda e=ext, t=tree, v=query_var, s=search_type: self._set_filter(e, t, v, s),
                              font=("Segoe UI", 8), relief='flat', padx=10, pady=2, cursor="hand2")
                btn.pack(side='left', padx=2)
                self.filter_buttons[ext] = btn
            
            self._update_filter_ui_styles()

        # (TreeView ya creado arriba)
        
        tree.bind("<Button-3>", lambda e: self._show_results_context_menu(e, tree))
        tree.bind("<Button-2>", lambda e: self._show_results_context_menu(e, tree))
        tree.bind("<Double-1>", lambda e: self._open_selected_result(tree))
        
        # --- NUEVAS BINDINGS (V.9.3 - Interactive Preview) ---
        tree.bind("<KeyPress-space>", lambda e: self._show_preview(tree))
        tree.bind("<KeyRelease-space>", lambda e: self._hide_preview())
        tree.bind("<F7>", lambda e: self._open_folder_selected_result(tree))
        
        # Redirigir flechas a la vista previa si está activa
        tree.bind("<Up>", lambda e: self._handle_nav_keys(e, tree, -1, "units"))
        tree.bind("<Down>", lambda e: self._handle_nav_keys(e, tree, 1, "units"))
        tree.bind("<Prior>", lambda e: self._handle_nav_keys(e, tree, -1, "pages"))
        tree.bind("<Next>", lambda e: self._handle_nav_keys(e, tree, 1, "pages"))
        
        # Ordenamiento por columna al hacer clic en el encabezado
        tree._sort_reverse = {"file": False, "path": False}
        tree.heading("file", text="Archivo", anchor='w',
                     command=lambda: self._sort_tree(tree, "file", 0))
        tree.heading("path", text="Ubicación Relativa", anchor='w',
                     command=lambda: self._sort_tree(tree, "path", 1))
        # Guardar referencias para coloreado
        if not hasattr(self, '_search_buttons'): self._search_buttons = []
        self._search_buttons.append((btn_go, btn_clear))
        
        return tree

    def _sort_tree(self, tree, col, col_index):
        """Ordena las filas del árbol por la columna indicada, alternando asc/desc"""
        reverse = tree._sort_reverse.get(col, False)
        rows = [(tree.item(k)["values"], k) for k in tree.get_children("")]
        rows.sort(key=lambda x: str(x[0][col_index]).lower(), reverse=reverse)
        for i, (_, k) in enumerate(rows):
            tree.move(k, "", i)
        # Actualizar indicador en el encabezado
        labels = {"file": "Archivo", "path": "Ubicación Relativa"}
        arrow = " ▼" if reverse else " ▲"
        other = "path" if col == "file" else "file"
        tree.heading(col, text=labels[col] + arrow)
        tree.heading(other, text=labels[other])  # Limpiar indicador de la otra columna
        tree._sort_reverse[col] = not reverse

    def _create_config_tab(self):
        main = tk.Frame(self.tab_config, padx=20, pady=20)
        main.pack(fill='both', expand=True)
        btn_f = tk.Frame(main)
        btn_f.pack(fill='x', pady=(0, 8))
        self.btn_add_folder = tk.Button(btn_f, text="➕ Agregar Carpeta", command=self._add_folder, font=("Segoe UI", 9), relief='flat', padx=12, pady=6)
        self.btn_add_folder.pack(side='left', padx=(0, 5))
        
        self.btn_import_txt = tk.Button(btn_f, text="📄 Importar TXT", command=self._import_locations_from_txt, font=("Segoe UI", 9), relief='flat', padx=12, pady=6)
        self.btn_import_txt.pack(side='left', padx=(0, 5))

        self.btn_remove_folder = tk.Button(btn_f, text="❌ Quitar", command=self._remove_folder, font=("Segoe UI", 9), relief='flat', padx=12, pady=6)
        self.btn_remove_folder.pack(side='left', padx=(0, 5))
        
        self.btn_clear_index = tk.Button(btn_f, text="🗑️ Borrar Índice", command=self._handle_clear_all_index, font=("Segoe UI", 9), relief='flat', padx=12, pady=6)
        self.btn_clear_index.pack(side='left', padx=(0, 5))
        
        self.btn_index = tk.Button(btn_f, text="⚡ Iniciar Indexación", command=self._handle_indexing_click, font=("Segoe UI", 9, "bold"), relief='flat', padx=15, pady=6)
        self.btn_index.pack(side='right')

        # --- Etiqueta de ruta base común ---
        base_f = tk.Frame(main)
        base_f.pack(fill='x', pady=(0, 4))
        tk.Label(base_f, text="📂 Base:", font=("Segoe UI", 8, "bold"), fg="#555").pack(side='left')
        self.lbl_base_path = tk.Label(
            base_f, textvariable=self.common_base_var,
            font=("Segoe UI", 8), fg="#1565c0",
            anchor='w', wraplength=750, justify='left'
        )
        self.lbl_base_path.pack(side='left', fill='x', expand=True, padx=(4, 0))

        tree_cnt = tk.Frame(main)
        tree_cnt.pack(fill='both', expand=True)
        self.config_tree = ttk.Treeview(tree_cnt, columns=("name", "mode", "status", "last", "duration", "full_path"), show="headings", style="Treeview")
        self.config_tree.heading("name", text="Carpeta", anchor='w')
        self.config_tree.heading("mode", text="Modo", anchor='center')
        self.config_tree.heading("status", text="Estado", anchor='center')
        self.config_tree.heading("last", text="Última Indexación", anchor='center')
        self.config_tree.heading("duration", text="⏳ Duración", anchor='center')
        self.config_tree.heading("full_path", text="Ruta Completa", anchor='w')
        
        self.config_tree.column("name",      width=180, stretch=True)
        self.config_tree.column("mode",      width=100, stretch=False)
        self.config_tree.column("status",    width=110, stretch=False)
        self.config_tree.column("last",      width=140, stretch=False)
        self.config_tree.column("duration",  width=80,  stretch=False)
        self.config_tree.column("full_path", width=400, stretch=True)
        
        # Ocultar la columna de ruta completa por defecto
        self.config_tree["displaycolumns"] = ("name", "mode", "status", "last", "duration")
        self.config_tree.pack(fill='both', expand=True)
        
        # Tooltip: mostrar ruta completa en la barra de estado al seleccionar
        self.config_tree.bind("<<TreeviewSelect>>", self._on_config_tree_select)
        
        # El menú se creará dinámicamente en _show_context_menu para mayor robustez
        self.config_tree.bind("<Button-3>", self._show_context_menu, add="+")
        self.config_tree.bind("<Button-2>", self._show_context_menu, add="+")

        prog_f = tk.Frame(main, pady=15, padx=10)
        prog_f.pack(fill='x', pady=(15, 0))
        self.pbar = ttk.Progressbar(prog_f, variable=self.percent_var, maximum=100)
        self.pbar.pack(fill='x', pady=(0, 5))
        self.lbl_progress = tk.Label(prog_f, textvariable=self.progress_var, font=("Segoe UI", 9))
        self.lbl_progress.pack()

    def _show_context_menu(self, event):
        """Muestra el menú contextual de configuración de forma ultra-robusta"""
        # Confirmar que recibimos el evento (Depuración visual para el usuario)
        self.status_var.set("📂 Configuración: Menú de opciones...")
        
        item = self.config_tree.identify_row(event.y)
        # Crear el menú vinculado directamente al árbol
        context_menu = tk.Menu(self.config_tree, tearoff=0)
        
        context_menu.add_command(label="➕ Agregar Carpeta", command=self._add_folder)
        context_menu.add_separator()
        
        state = "normal" if item else "disabled"
        if item:
            self.config_tree.selection_set(item)
            
        context_menu.add_command(
            label="🔄 Actualizar índice de esta carpeta", 
            command=self._index_single_selected,
            state=state
        )
        
        if item:
            loc = next((l for l in self.loc_manager.locations if l['path'] == self._get_selected_full_path()), None)
            if loc:
                label_toggle = "📑 Cambiar a: Indexar Todo" if not loc.get('index_content', True) else "🖼️ Cambiar a: Solo Nombres (Escaneado)"
                context_menu.add_command(label=label_toggle, command=self._toggle_content_indexing)
        
        context_menu.add_separator()
        
        # Opción para mostrar/ocultar rutas
        is_showing_paths = "full_path" in list(self.config_tree["displaycolumns"])
        label_paths = "🙈 Ocultar Rutas Completas" if is_showing_paths else "👁️ Mostrar Rutas Completas"
        context_menu.add_command(label=label_paths, command=self._toggle_path_column)
        
        context_menu.add_separator()
        context_menu.add_command(label="📂 Abrir en explorador", command=self._open_folder_selected, state=state)
        context_menu.add_command(
            label="❌ Quitar de la lista", 
            command=self._remove_folder,
            state=state
        )
        
        # Pequeño retraso para asegurar que el evento de clic se procese antes que el popup
        def do_popup():
            try:
                context_menu.post(event.x_root, event.y_root)
            except:
                pass
                
        self.modal.after(10, do_popup)
        return "break"

    def _show_results_context_menu(self, event, tree):
        item_id = tree.identify_row(event.y)
        if not item_id: return
        tree.selection_set(item_id)
        
        tags = tree.item(item_id).get('tags', [])
        if not tags: return
        
        path = tags[0]
        snippet = tags[1] if len(tags) > 1 else "Contexto no disponible"
        
        # LIMPIAR SNIPPET DE CARACTERES EXTRAÑOS
        snippet = snippet.replace('\n', ' ').replace('\r', ' ')
        
        self.results_context_menu.delete(0, tk.END)
        self.results_context_menu.add_command(label=f"📝 Contexto: {snippet}", command=lambda: self._open_selected_result(tree))
        self.results_context_menu.add_separator()
        self.results_context_menu.add_command(label="📂 Abrir Archivo", command=lambda: self._open_selected_result(tree))
        try:
            self.results_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.results_context_menu.grab_release()

    def _open_selected_result(self, tree):
        sel = tree.selection()
        if not sel: return
        path = tree.item(sel[0]).get('tags', [None])[0]
        if path and os.path.exists(path): os.startfile(path)

    def _open_folder_selected_result(self, tree):
        """Abre la carpeta contenedora del archivo seleccionado (F7)"""
        sel = tree.selection()
        if not sel: return
        path = tree.item(sel[0]).get('tags', [None])[0]
        if path and os.path.exists(path):
            folder = os.path.dirname(path)
            if os.path.exists(folder):
                os.startfile(folder)
                
    def _show_preview(self, tree):
        """Muestra una ventana flotante de vista previa (Quick Look)"""
        if self.preview_window: return
        sel = tree.selection()
        if not sel: return
        
        path = tree.item(sel[0]).get('tags', [None])[0]
        if not path or not os.path.exists(path): return
        
        # Crear ventana minimalista
        self.preview_window = tk.Toplevel(self.modal)
        self.preview_window.overrideredirect(True)
        self.preview_window.attributes("-topmost", True)
        
        # Forzar un tamaño inicial para el cálculo de posición
        self.preview_window.geometry("700x500")
        
        c = self.app.theme_manager.colores
        bg_color = c.get("bg", "#ffffff")
        accent = c.get("accent_primary", "#007acc")
        
        self.preview_window.configure(bg=accent, padx=2, pady=2) # Borde de color acento
        
        # Contenedor interno para el contenido
        f_main = tk.Frame(self.preview_window, bg=bg_color)
        f_main.pack(fill='both', expand=True)
        
        # Header con info del archivo
        f_header = tk.Frame(f_main, bg=c.get("button_active_bg", "#f0f0f0"), padx=12, pady=8)
        f_header.pack(fill='x')
        tk.Label(f_header, text=f"📄 {os.path.basename(path)}", font=("Segoe UI", 10, "bold"), 
                 bg=c.get("button_active_bg", "#f0f0f0"), fg=accent).pack(side='left')
        
        # Cuerpo con texto
        f_body = tk.Frame(f_main, bg=bg_color, padx=15, pady=15)
        f_body.pack(fill='both', expand=True)
        
        text_preview = tk.Text(f_body, font=("Consolas", 10), bg=c.get("entry_bg", "#ffffff"), 
                               fg=c.get("entry_fg", "#000000"), relief='flat', wrap='word')
        text_preview.pack(fill='both', expand=True)
        self.preview_text_widget = text_preview
        
        # Footer con instrucciones de navegación
        f_footer = tk.Frame(f_main, bg=bg_color, padx=10, pady=2)
        f_footer.pack(fill='x')
        tk.Label(f_footer, text="🖱️ Mantén Espacio  |  ⌨️ Navegar: ↑ ↓  RePág AvPág", 
                 font=("Segoe UI", 8, "italic"), bg=bg_color, fg=c.get("fg_alt", "#888888")).pack(side='right')
        
        # Cargar contenido: snippet o lectura directa (LÍMITE AUMENTADO V.9.3)
        tags = tree.item(sel[0]).get('tags', [])
        snippet = tags[1] if len(tags) > 1 else None
        
        has_content = False
        if snippet and snippet != "Contexto no disponible":
            # Limpiar etiquetas HTML del snippet para el widget Text
            clean_text = snippet.replace('<b>', '').replace('</b>', '').strip()
            if clean_text:
                text_preview.insert('1.0', clean_text + "\n" + "-"*50 + "\n\n")
                # Intentar cargar más texto después del snippet
                has_content = False # Forzamos carga adicional
        
        # Intento de lectura rápida de los primeros 10000 chars
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext in ('.pdf', '.docx', '.xlsx'):
                if not has_content: text_preview.insert('end', "[Cargando extracto extendido...]\n\n")
                text_preview.insert('end', self.indexer._extract_text(path))
            else:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_preview.insert('end', f.read(10000))
        except Exception as e:
            if not text_preview.get('1.0', 'end').strip():
                text_preview.insert('1.0', f"[Vista previa no disponible: {str(e)}]")
        
        text_preview.configure(state='disabled')
        
        # Posicionar centrada usando rootx/y para evitar desfases de monitores
        self.preview_window.update_idletasks()
        w = self.preview_window.winfo_reqwidth()
        h = self.preview_window.winfo_reqheight()
        
        # Centrar respecto a la ventana modal
        mx = self.modal.winfo_rootx() + (self.modal.winfo_width() - w) // 2
        my = self.modal.winfo_rooty() + (self.modal.winfo_height() - h) // 2
        
        # Asegurarse de que no se salga de la pantalla
        mx = max(0, mx)
        my = max(0, my)
        
        self.preview_window.geometry(f"{w}x{h}+{mx}+{my}")

    def _handle_nav_keys(self, event, tree, amount, unit):
        """Maneja las teclas de navegación: desplaza la vista previa si está activa, o la lista si no."""
        if self.preview_window and self.preview_text_widget:
            self.preview_text_widget.yview_scroll(amount, unit)
            return "break"
        return None # Dejar que el evento siga su curso normal en la lista

    def _hide_preview(self):
        """Cierra la ventana de vista previa"""
        if self.preview_window:
            try:
                self.preview_window.destroy()
            except:
                pass
            self.preview_window = None
            self.preview_text_widget = None

    def aplicar_tema(self):
        if not self.modal or not self.modal.winfo_exists(): return
        tm = self.app.theme_manager
        c = tm.colores
        self.modal.configure(bg=c["bg"])
        style = ttk.Style()
        style.configure("TNotebook", background=c["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                        background=c.get("bg_alt", "#252526"), 
                        foreground=c.get("fg", "#ffffff"),
                        padding=[15, 5],
                        font=("Segoe UI", 9))
        style.map("TNotebook.Tab",
                  background=[("selected", c.get("accent_primary", "#3498db"))],
                  foreground=[("selected", "#ffffff")])
        
        self._colorear_recursivo(self.modal, c)
        
        # Actualizar estilos de los filtros (V.10.0)
        self._update_filter_ui_styles()
        
        if hasattr(self, 'status_bar_frame'):
            self.status_bar_frame.configure(bg=c.get("status_bg", "#007acc"))
            self.lbl_status_bar.configure(bg=c.get("status_bg", "#007acc"), fg=c.get("status_fg", "#ffffff"))
            self.lbl_timer.configure(bg=c.get("status_bg", "#007acc"), fg=c.get("status_fg", "#ffffff"))
        
        # Colorear botones de búsqueda (reutilizables)
        if hasattr(self, '_search_buttons'):
            for btn_go, btn_clear in self._search_buttons:
                btn_go.configure(bg=c.get("accent_primary", "#3498db"), fg="white")
                btn_clear.configure(bg=c.get("button_bg", "#e0e0e0"), fg=c.get("button_fg", "#000000"))
        
        if hasattr(self, 'btn_clear_index'):
            self.btn_clear_index.configure(bg="#e74c3c", fg="white")
        
        if hasattr(self, 'btn_index') and not self.is_indexing: 
            self.btn_index.configure(bg=c.get("success", "#10b981"), fg="white")
        
        if self.results_tree: tm._apply_theme_to_tree(self.results_tree, "ResultsContent", {'fg': c["tree_fg"], 'bg': c["tree_bg"]})
        if self.files_results_tree: tm._apply_theme_to_tree(self.files_results_tree, "ResultsFiles", {'fg': c["tree_fg"], 'bg': c["tree_bg"]})
        if self.config_tree: tm._apply_theme_to_tree(self.config_tree, "Config", {'fg': c["tree_fg"], 'bg': c["tree_bg"]})

    def _colorear_recursivo(self, widget, c):
        try:
            wclass = widget.winfo_class()
            if wclass in ("Frame", "TFrame"):
                if hasattr(self, 'status_bar_frame') and widget == self.status_bar_frame: pass
                else: widget.configure(bg=c["bg"])
            elif wclass in ("Label", "TLabel"):
                if hasattr(self, 'status_bar_frame') and widget.master == self.status_bar_frame: pass
                else: 
                    widget.configure(bg=c["bg"], fg=c["fg"])
                    if hasattr(self, 'lbl_ocr_warning') and widget == self.lbl_ocr_warning: widget.configure(fg=c.get("fg_alt", "#888888"))
                    if hasattr(self, 'lbl_syntax_help') and widget == self.lbl_syntax_help: widget.configure(fg=c.get("fg_alt", "#888888"))
            elif wclass == "Entry": widget.configure(bg=c["entry_bg"], fg=c["entry_fg"], insertbackground=c["entry_fg"])
            elif wclass == "Button": widget.configure(bg=c["button_bg"], fg=c["button_fg"], activebackground=c["button_active_bg"])
            for child in widget.winfo_children(): self._colorear_recursivo(child, c)
        except: pass

    def _clear_search(self):
        self.search_query_var.set("")
        self.results_tree.delete(*self.results_tree.get_children())
        self.search_entry.focus_set()

    def _handle_clear_all_index(self):
        if self.is_indexing:
            messagebox.showwarning("Acción bloqueada", "No puedes borrar el índice mientras hay una indexación en curso. Detenla primero.", parent=self.modal)
            return

        if messagebox.askyesno("Confirmar Borrado Total", "¿Estás seguro de que deseas borrar ABSOLUTAMENTE TODO el índice de contenido?\n\nEsta acción no se puede deshacer y también limpiará todos los tiempos registrados.", parent=self.modal):
            self.btn_clear_index.config(text="🗑️ Borrando...", state='disabled')
            self.btn_index.config(state='disabled') # Evitar iniciar mientras se borra
            self.modal.update()
            
            def run():
                success = self.indexer.clear_all_index()
                if self.modal and self.modal.winfo_exists():
                    self.modal.after(0, lambda: self._post_clear(success))
                    
            threading.Thread(target=run, daemon=True).start()

    def _post_clear(self, success):
        self.btn_clear_index.config(text="🗑️ Borrar Todo el Índice", state='normal')
        self.btn_index.config(state='normal')
        if success:
            # RESETEAR TIEMPOS
            for loc in self.loc_manager.locations:
                loc['last_duration'] = "-"
                loc['last_indexed'] = "Nunca"
            self.loc_manager.save()
            
            messagebox.showinfo("Éxito", "El índice y los tiempos han sido vaciados.", parent=self.modal)
            self.status_var.set("📊 Índice eliminado")
            self._populate_config_tree()
            self._update_status_from_locs()

    def _do_search(self, query, search_type, tree):
        if not query: return
        
        # Limpiar resultados anteriores
        tree.delete(*tree.get_children())
        
        def run():
            try:
                start = time.time()
                # Pasar el filtro de extensión (V.10.0)
                ext_filter = self.search_filter_ext.get()
                results = self.indexer.search(query, search_field=search_type, extension=ext_filter)
                
                # Usar after para actualizar UI (Corregido: _display_results V.10.2)
                self.modal.after(0, lambda: self._display_results(results, tree))
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.modal.after(0, lambda: messagebox.showerror("Error", f"Error en búsqueda: {e}"))
                
        threading.Thread(target=run, daemon=True).start()

    def _set_filter(self, ext, tree, query_var, search_type):
        """Establece el filtro y dispara la búsqueda si hay algo escrito"""
        self.search_filter_ext.set(ext)
        self._update_filter_ui_styles()
        
        query = query_var.get()
        if query:
            self._do_search(query, search_type, tree)

    def _update_filter_ui_styles(self):
        """Actualiza el estilo visual de los botones de filtro"""
        if not hasattr(self.app, 'theme_manager'): return
        tm = self.app.theme_manager
        # Usar .colores que es el atributo real en ThemeManager
        c = tm.colores if hasattr(tm, 'colores') else tm.TEMAS.get(tm.tema_actual, tm.TEMAS["claro"])
        
        active_ext = self.search_filter_ext.get()
        
        for ext, btn in self.filter_buttons.items():
            try:
                if ext == active_ext:
                    # Usar accent o accent_primary según disponibilidad
                    bg_color = c.get("accent", c.get("accent_primary", "#0078d7"))
                    btn.configure(bg=bg_color, fg="#ffffff")
                else:
                    btn.configure(bg=c.get("button_bg", "#f0f0f0"), fg=c.get("button_fg", "#000000"))
            except: pass

    def _display_results(self, results, tree):
        if not results:
            tree.insert("", "end", values=("Sin resultados", "Intenta con otra palabra"))
            return
            
        # Ocultamos el árbol temporalmente para acelerar el renderizado (hack de Tkinter)
        
        max_limit = 10000
        count = 0
        
        for r in results:
            if count >= max_limit:
                item = tree.insert("", "end", values=("⚠️ Demasiados resultados", f"Mostrando los primeros {max_limit}. Por favor, sé más específico o añade más palabras."))
                # Aplicamos un color distinto si fuera posible o simplemente lo insertamos
                self.app.theme_manager.apply_theme_to_item(tree, item)
                break
                
            item = tree.insert("", "end", values=(r['name'], r['path']), tags=(r['abs_path'], r['snippet']))
            self.app.theme_manager.apply_theme_to_item(tree, item)
            count += 1

    def _on_config_tree_select(self, event):
        """Muestra la ruta completa en la barra de estado al seleccionar una fila"""
        full_path = self._get_selected_full_path()
        if full_path:
            self.status_var.set(f"📂 {full_path}")

    def _get_selected_full_path(self):
        """Obtiene la ruta COMPLETA del item seleccionado (guardada en tags[1])"""
        sel = self.config_tree.selection()
        if not sel:
            return None
        tags = self.config_tree.item(sel[0]).get('tags', [])
        # tags = (color_tag, full_path)
        return tags[1] if len(tags) >= 2 else None

    def _populate_config_tree(self):
        self.config_tree.delete(*self.config_tree.get_children())
        
        # --- Calcular ruta base común (normalizando separadores primero) ---
        norm_paths = [os.path.normpath(loc['path']) for loc in self.loc_manager.locations]
        common_base = ""
        if len(norm_paths) > 1:
            try:
                cb = os.path.commonpath(norm_paths)
                # Solo usar la base si es útil (incluso si es solo la unidad "D:\")
                if len(cb) >= 3:
                    common_base = cb
            except ValueError:
                common_base = ""   # paths en unidades distintas
        elif len(norm_paths) == 1:
            common_base = os.path.dirname(norm_paths[0])
        
        # Mostrar la base en la etiqueta
        if hasattr(self, 'common_base_var'):
            self.common_base_var.set(common_base if common_base else "(rutas en distintas unidades)")
        
        # Configurar tags de colores
        self.config_tree.tag_configure('indexed',     background='#e8f5e9', foreground='#1b5e20')
        self.config_tree.tag_configure('not_indexed', background='#fff8e1', foreground='#e65100')
        self.config_tree.tag_configure('disabled',    background='#f5f5f5', foreground='#9e9e9e')
        
        for loc in self.loc_manager.locations:
            full_path = loc['path']
            norm_full = os.path.normpath(full_path)
            enabled   = loc.get('enabled', True)
            idx_cont  = loc.get('index_content', True)
            last_idx  = loc.get('last_indexed') or 'Nunca'
            last_dur  = loc.get('last_duration') or '-'
            
            mode_text = "Completo" if idx_cont else "🖼️ Escaneado"
            
            # Mostrar SOLO el nombre de la carpeta
            display_name = os.path.basename(norm_full) or norm_full
            
            has_index = last_idx not in ('Nunca', None, '')
            
            if not enabled:
                status = "⛔ Deshabilitado"
                tag    = 'disabled'
            elif has_index:
                status = "✅ Indexado"
                tag    = 'indexed'
            else:
                status = "⚠️ Sin índice"
                tag    = 'not_indexed'
            
            # tags = (color_tag, ruta_completa) — la ruta completa se usa en operaciones
            self.config_tree.insert(
                "", "end",
                values=(display_name, mode_text, status, last_idx, last_dur, full_path),
                tags=(tag, full_path)
            )

    def _handle_indexing_click(self):
        if self.is_indexing:
            self.indexer.stop_indexing()
            self.btn_index.config(text="🛑 Deteniendo...")
            # Limpiar progreso visual inmediatamente
            self.progress_var.set("Indexación detenida")
            self.percent_var.set(0)
            self.modal.update()
        else: self._start_indexing()

    def _update_timer(self):
        if not self.is_indexing: return
        elapsed = int(time.time() - self.start_time)
        m, s = divmod(elapsed, 60)
        self.timer_str_var.set(f"{m:02d}:{s:02d}")
        self.modal.after(500, self._update_timer)

    def _start_indexing(self, single_path=None):
        if single_path: locations = [l for l in self.loc_manager.locations if l['path'] == single_path]
        else: locations = self.loc_manager.get_enabled_locations()
        if not locations: return
        self.is_indexing = True
        self.indexer.stop_requested = False # ¡RESETEO CRUCIAL! Para que pueda volver a arrancar
        self.start_time = time.time()
        self.btn_index.config(text="🛑 Detener Indexación", bg="#ef4444", state='normal')
        self._update_timer()
        def upd(msg, val):
            if self.modal and self.modal.winfo_exists(): self.modal.after(0, lambda: [self.progress_var.set(msg), self.percent_var.set(val)])
        def run():
            try:
                for loc in locations:
                    if self.indexer.stop_requested: break
                    t0 = time.time()
                    skip_content = not loc.get('index_content', True)
                    self.indexer.index_folder(loc['path'], progress_callback=upd, skip_content=skip_content)
                    dur = time.time() - t0
                    loc['last_duration'] = f"{int(dur)}s" if dur < 60 else f"{int(dur//60)}m {int(dur%60)}s"
                    loc['last_indexed'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    if self.modal and self.modal.winfo_exists():
                        self.modal.after(0, self._populate_config_tree)
                        
                self.loc_manager.save()
                self.modal.after(0, self._update_status_from_locs)
            finally:
                self.is_indexing = False
                if self.modal and self.modal.winfo_exists():
                    self.modal.after(0, lambda: [self._populate_config_tree(), 
                        self.btn_index.config(text="⚡ Iniciar Indexación", bg=self.app.theme_manager.colores.get("success", "#10b981"), state='normal')])
        threading.Thread(target=run, daemon=True).start()

    def _add_folder(self):
        """Selección múltiple: repite el diálogo hasta que el usuario cancele"""
        added = 0
        initial_dir = None  # Recordar directorio padre para abrirse en el nivel correcto
        while True:
            title = f"Agregar carpeta  ({added} añadida{'s' if added != 1 else ''} — Cancelar para terminar)" if added else "Seleccionar carpeta(s) para indexar"
            p = filedialog.askdirectory(parent=self.modal, title=title, initialdir=initial_dir)
            if not p:
                break
            # Guardar el PADRE para que el siguiente diálogo abra al mismo nivel
            initial_dir = os.path.dirname(p)
            if self.loc_manager.add_location(p, os.path.basename(p)):
                added += 1
                self._populate_config_tree()  # Refresca en tiempo real
        if added > 0:
            self.status_var.set(f"✅ {added} carpeta{'s' if added != 1 else ''} añadida{'s' if added != 1 else ''} al índice")

    def _remove_folder(self):
        sel = self.config_tree.selection()
        if not sel: return
        path = self._get_selected_full_path()
        if not path:
            # fallback por si los tags cambiaron
            path = self.config_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Quitar y limpiar índice?\n{path}", parent=self.modal):
            self.indexer.purge_location(path)
            self.loc_manager.remove_location(path)
            self._populate_config_tree()

    def _index_single_selected(self):
        """Indexa únicamente la carpeta seleccionada en la tabla de configuración"""
        path = self._get_selected_full_path()
        if not path: return
        self._start_indexing(single_path=path)

    def _toggle_content_indexing(self):
        """Cambia el modo entre indexación completa e indexación de solo nombres"""
        path = self._get_selected_full_path()
        if not path: return
        for loc in self.loc_manager.locations:
            if loc['path'] == path:
                loc['index_content'] = not loc.get('index_content', True)
                break
        self.loc_manager.save()
        self._populate_config_tree()

    def _toggle_path_column(self):
        """Muestra u oculta la columna de ruta completa"""
        cols = list(self.config_tree["displaycolumns"])
        if "full_path" in cols:
            cols.remove("full_path")
        else:
            cols.append("full_path")
        self.config_tree["displaycolumns"] = tuple(cols)

    def _open_folder_selected(self):
        """Abre la carpeta seleccionada en el explorador de Windows"""
        path = self._get_selected_full_path()
        if not path: return
        if os.path.exists(path): os.startfile(path)

    def _import_locations_from_txt(self):
        """Importa múltiples rutas desde un archivo TXT (una ruta por línea)"""
        p = filedialog.askopenfilename(parent=self.modal, title="Seleccionar archivo TXT con rutas", filetypes=[("Archivos de Texto", "*.txt")])
        if not p: return
        
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            added = 0
            for line in lines:
                # Limpiar comillas y espacios (Windows suele poner comillas al 'Copiar como ruta')
                path = line.strip().replace('"', '').replace("'", "")
                if path and os.path.isdir(path):
                    if self.loc_manager.add_location(path, os.path.basename(path)):
                        added += 1
            
            if added > 0:
                self._populate_config_tree()
                messagebox.showinfo("Éxito", f"Se han importado {added} ubicaciones correctamente.", parent=self.modal)
            else:
                messagebox.showwarning("Aviso", "No se encontraron rutas válidas en el archivo.", parent=self.modal)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {e}", parent=self.modal)
