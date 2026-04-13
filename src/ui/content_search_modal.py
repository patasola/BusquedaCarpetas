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
        self.results_tree = None
        
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

    def show_modal(self):
        if self.modal and self.modal.winfo_exists():
            self.modal.lift()
            self.modal.focus_force()
            return
        self._create_modal_window()
        self._create_modal_content()
        self._populate_config_tree()
        if hasattr(self.app, 'theme_manager'):
            self.app.theme_manager.register_callback(self.aplicar_tema)
            self.aplicar_tema()
    
    def _create_modal_window(self):
        self.modal = tk.Toplevel(self.parent)
        self.modal.title("Búsqueda Avanzada por Contenido (FTS5)")
        self.modal.geometry("900x780")
        self.modal.update_idletasks()
        x = (self.modal.winfo_screenwidth() - 900) // 2
        y = (self.modal.winfo_screenheight() - 780) // 2
        self.modal.geometry(f"900x780+{x}+{y}")
        
        # BIND_ALL PARA ESCAPE - CIERRE GARANTIZADO
        self.modal.bind_all("<Escape>", lambda e: self.modal.destroy())
        
        self.modal.bind("<F12>", lambda e: self.app.theme_manager.toggle_tema())
        self.modal.bind("<Control-l>", lambda e: self._clear_search())
        self.modal.bind("<Control-L>", lambda e: self._clear_search())
        
    def _create_modal_content(self):
        self.notebook = ttk.Notebook(self.modal)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=(10, 0))
        
        self.tab_search = tk.Frame(self.notebook)
        self.notebook.add(self.tab_search, text="  🔍 Buscar Texto  ")
        self._create_search_tab()
        
        self.tab_config = tk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="  ⚙️ Configuración e Índice  ")
        self._create_config_tab()

        self.status_bar_frame = tk.Frame(self.modal, height=35, relief='flat')
        self.status_bar_frame.pack(side='bottom', fill='x')
        self.lbl_status_bar = tk.Label(self.status_bar_frame, textvariable=self.status_var, font=("Segoe UI", 9), padx=15, pady=8)
        self.lbl_status_bar.pack(side='left')
        self.lbl_timer = tk.Label(self.status_bar_frame, textvariable=self.timer_str_var, font=("Consolas", 10, "bold"), padx=15, pady=8)
        self.lbl_timer.pack(side='right')

    def _create_search_tab(self):
        header = tk.Frame(self.tab_search, padx=20, pady=20)
        header.pack(fill='x')
        tk.Label(header, text="Buscar texto en los archivos:", font=("Segoe UI", 10)).pack(anchor='w')
        self.lbl_ocr_warning = tk.Label(header, text="⚠ PDFs escaneados (imágenes) son invisibles sin OCR.", font=("Segoe UI", 8, "italic"))
        self.lbl_ocr_warning.pack(anchor='w', pady=(0, 5))
        
        entry_cnt = tk.Frame(header)
        entry_cnt.pack(fill='x')
        self.search_entry = tk.Entry(entry_cnt, textvariable=self.search_query_var, font=("Segoe UI", 11), relief='solid', bd=1)
        self.search_entry.pack(side='left', fill='x', expand=True, ipady=8, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._do_search())
        self.search_entry.focus_set()
        
        self.btn_do_search = tk.Button(entry_cnt, text="🔍 Buscar", command=self._do_search, font=("Segoe UI", 10, "bold"), relief='flat', padx=20, pady=8, cursor="hand2")
        self.btn_do_search.pack(side='left', padx=(0, 5))
        
        self.btn_clear_search = tk.Button(entry_cnt, text="🧹 Limpiar", command=self._clear_search, font=("Segoe UI", 9), relief='flat', padx=12, pady=8, cursor="hand2")
        self.btn_clear_search.pack(side='left')

        res_cnt = tk.Frame(self.tab_search, padx=20)
        res_cnt.pack(fill='both', expand=True)
        self.results_tree = ttk.Treeview(res_cnt, columns=("file", "path"), show="headings", style="Treeview")
        self.results_tree.heading("file", text="Archivo", anchor='w')
        self.results_tree.heading("path", text="Ubicación Relativa", anchor='w')
        self.results_tree.column("file", width=250, stretch=False)
        self.results_tree.column("path", width=500, stretch=False)
        
        v_scroll = ttk.Scrollbar(res_cnt, orient="vertical", command=self.results_tree.yview)
        h_scroll = ttk.Scrollbar(self.tab_search, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(fill='x', padx=20)
        
        # MENÚ CONTEXTUAL DE RESULTADOS
        self.results_context_menu = tk.Menu(self.modal, tearoff=0)
        self.results_tree.bind("<Button-3>", self._show_results_context_menu)
        self.results_tree.bind("<Button-2>", self._show_results_context_menu)
        
        self.results_tree.bind("<Double-1>", lambda e: self._open_selected_result())

    def _create_config_tab(self):
        main = tk.Frame(self.tab_config, padx=20, pady=20)
        main.pack(fill='both', expand=True)
        btn_f = tk.Frame(main)
        btn_f.pack(fill='x', pady=(0, 15))
        self.btn_add_folder = tk.Button(btn_f, text="➕ Agregar Carpeta", command=self._add_folder, font=("Segoe UI", 9), relief='flat', padx=12, pady=6)
        self.btn_add_folder.pack(side='left', padx=(0, 10))
        self.btn_remove_folder = tk.Button(btn_f, text="❌ Quitar", command=self._remove_folder, font=("Segoe UI", 9), relief='flat', padx=12, pady=6)
        self.btn_remove_folder.pack(side='left', padx=(0, 10))
        
        self.btn_clear_index = tk.Button(btn_f, text="🗑️ Borrar Todo el Índice", command=self._handle_clear_all_index, font=("Segoe UI", 9), relief='flat', padx=12, pady=6)
        self.btn_clear_index.pack(side='left', padx=(0, 10))
        
        self.btn_index = tk.Button(btn_f, text="⚡ Iniciar Indexación", command=self._handle_indexing_click, font=("Segoe UI", 9, "bold"), relief='flat', padx=15, pady=6)
        self.btn_index.pack(side='right')

        tree_cnt = tk.Frame(main)
        tree_cnt.pack(fill='both', expand=True)
        self.config_tree = ttk.Treeview(tree_cnt, columns=("path", "status", "last", "duration"), show="headings", style="Treeview")
        self.config_tree.heading("path", text="Carpeta", anchor='w')
        self.config_tree.heading("status", text="Estado", anchor='center')
        self.config_tree.heading("last", text="Última Indexación", anchor='center')
        self.config_tree.heading("duration", text="⏳ Duración", anchor='center')
        self.config_tree.column("path", width=350, stretch=False)
        self.config_tree.column("status", width=100, stretch=False)
        self.config_tree.column("last", width=150, stretch=False)
        self.config_tree.column("duration", width=100, stretch=False)
        self.config_tree.pack(fill='both', expand=True)
        
        self.context_menu = tk.Menu(self.modal, tearoff=0)
        self.context_menu.add_command(label="⚡ Indexar solo esta carpeta", command=self._index_single_selected)
        self.context_menu.add_command(label="📂 Abrir en explorador", command=self._open_folder_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Quitar de la lista", command=self._remove_folder)
        self.config_tree.bind("<Button-3>", self._show_context_menu)
        self.config_tree.bind("<Button-2>", self._show_context_menu)

        prog_f = tk.Frame(main, pady=15, padx=10)
        prog_f.pack(fill='x', pady=(15, 0))
        self.pbar = ttk.Progressbar(prog_f, variable=self.percent_var, maximum=100)
        self.pbar.pack(fill='x', pady=(0, 5))
        self.lbl_progress = tk.Label(prog_f, textvariable=self.progress_var, font=("Segoe UI", 9))
        self.lbl_progress.pack()

    def _show_context_menu(self, event):
        item = self.config_tree.identify_row(event.y)
        if item:
            self.config_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _show_results_context_menu(self, event):
        item_id = self.results_tree.identify_row(event.y)
        if not item_id: return
        self.results_tree.selection_set(item_id)
        
        tags = self.results_tree.item(item_id).get('tags', [])
        if not tags: return
        
        path = tags[0]
        snippet = tags[1] if len(tags) > 1 else "Contexto no disponible"
        
        # LIMPIAR SNIPPET DE CARACTERES EXTRAÑOS
        snippet = snippet.replace('\n', ' ').replace('\r', ' ')
        
        self.results_context_menu.delete(0, tk.END)
        self.results_context_menu.add_command(label=f"📝 Contexto: {snippet}", command=self._open_selected_result)
        self.results_context_menu.add_separator()
        self.results_context_menu.add_command(label="📂 Abrir Archivo", command=self._open_selected_result)
        self.results_context_menu.post(event.x_root, event.y_root)

    def _open_selected_result(self):
        sel = self.results_tree.selection()
        if not sel: return
        path = self.results_tree.item(sel[0]).get('tags', [None])[0]
        if path and os.path.exists(path): os.startfile(path)

    def aplicar_tema(self):
        if not self.modal or not self.modal.winfo_exists(): return
        tm = self.app.theme_manager
        c = tm.colores
        self.modal.configure(bg=c["bg"])
        style = ttk.Style()
        style.configure("TNotebook", background=c["bg"], borderwidth=0)
        self._colorear_recursivo(self.modal, c)
        if hasattr(self, 'status_bar_frame'):
            self.status_bar_frame.configure(bg=c.get("status_bg", "#007acc"))
            self.lbl_status_bar.configure(bg=c.get("status_bg", "#007acc"), fg=c.get("status_fg", "#ffffff"))
            self.lbl_timer.configure(bg=c.get("status_bg", "#007acc"), fg=c.get("status_fg", "#ffffff"))
        
        self.btn_do_search.configure(bg=c.get("accent_primary", "#3498db"), fg="white")
        self.btn_clear_search.configure(bg=c.get("button_bg", "#e0e0e0"), fg=c.get("button_fg", "#000000"))
        self.btn_clear_index.configure(bg="#e74c3c", fg="white")
        
        if not self.is_indexing: self.btn_index.configure(bg=c.get("success", "#10b981"), fg="white")
        tm._apply_theme_to_tree(self.results_tree, "Results", {'fg': c["tree_fg"], 'bg': c["tree_bg"]})
        tm._apply_theme_to_tree(self.config_tree, "Config", {'fg': c["tree_fg"], 'bg': c["tree_bg"]})

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
            elif wclass == "Entry": widget.configure(bg=c["entry_bg"], fg=c["entry_fg"], insertbackground=c["entry_fg"])
            elif wclass == "Button": widget.configure(bg=c["button_bg"], fg=c["button_fg"], activebackground=c["button_active_bg"])
            for child in widget.winfo_children(): self._colorear_recursivo(child, c)
        except: pass

    def _clear_search(self):
        self.search_query_var.set("")
        self.results_tree.delete(*self.results_tree.get_children())
        self.search_entry.focus_set()

    def _handle_clear_all_index(self):
        if messagebox.askyesno("Confirmar Borrado Total", "¿Estás seguro de que deseas borrar ABSOLUTAMENTE TODO el índice de contenido?\n\nEsta acción no se puede deshacer y también limpiará todos los tiempos registrados.", parent=self.modal):
            if self.indexer.clear_all_index():
                # RESETEAR TIEMPOS
                for loc in self.loc_manager.locations:
                    loc['last_duration'] = "-"
                    loc['last_indexed'] = "Nunca"
                self.loc_manager.save()
                
                messagebox.showinfo("Éxito", "El índice y los tiempos han sido vaciados.", parent=self.modal)
                self.status_var.set("📊 Índice eliminado")
                self._populate_config_tree()
                self._update_status_from_locs()

    def _do_search(self):
        query = self.search_query_var.get().strip()
        if not query: return
        self.results_tree.delete(*self.results_tree.get_children())
        def run():
            try:
                results = self.indexer.search(query)
                self.modal.after(0, lambda: self._display_results(results))
            except Exception as e: print(e)
        threading.Thread(target=run, daemon=True).start()

    def _display_results(self, results):
        if not results:
            self.results_tree.insert("", "end", values=("Sin resultados", "Intenta con otra palabra"))
            return
        for r in results:
            # GUARDAR SNIPPET EN TAGS
            item = self.results_tree.insert("", "end", values=(r['name'], r['path']), tags=(r['abs_path'], r['snippet']))
            self.app.theme_manager.apply_theme_to_item(self.results_tree, item)

    def _populate_config_tree(self):
        self.config_tree.delete(*self.config_tree.get_children())
        for loc in self.loc_manager.locations:
            status = "Habilitado" if loc.get('enabled', True) else "Deshabilitado"
            item = self.config_tree.insert("", "end", values=(loc['path'], status, loc.get('last_indexed', "Nunca"), loc.get('last_duration', "-")))
            self.app.theme_manager.apply_theme_to_item(self.config_tree, item)

    def _handle_indexing_click(self):
        if self.is_indexing:
            self.indexer.stop_indexing()
            self.btn_index.config(text="🛑 Deteniendo...")
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
        self.start_time = time.time()
        self.btn_index.config(text="🛑 Detener Indexación", bg="#ef4444")
        self._update_timer()
        def upd(msg, val):
            if self.modal and self.modal.winfo_exists(): self.modal.after(0, lambda: [self.progress_var.set(msg), self.percent_var.set(val)])
        def run():
            try:
                for loc in locations:
                    if self.indexer.stop_requested: break
                    t0 = time.time()
                    self.indexer.index_folder(loc['path'], progress_callback=upd)
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
        p = filedialog.askdirectory(parent=self.modal)
        if p and self.loc_manager.add_location(p, os.path.basename(p)): self._populate_config_tree()

    def _remove_folder(self):
        sel = self.config_tree.selection()
        if not sel: return
        it = self.config_tree.item(sel[0])
        path = it['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Quitar y limpiar índice?\n{path}", parent=self.modal):
            self.indexer.purge_location(path)
            self.loc_manager.remove_location(path)
            self._populate_config_tree()

    def _index_single_selected(self):
        """Indexa únicamente la carpeta seleccionada en la tabla de configuración"""
        sel = self.config_tree.selection()
        if not sel: return
        path = self.config_tree.item(sel[0])['values'][0]
        self._start_indexing(single_path=path)

    def _open_folder_selected(self):
        """Abre la carpeta seleccionada en el explorador de Windows"""
        sel = self.config_tree.selection()
        if not sel: return
        path = self.config_tree.item(sel[0])['values'][0]
        if os.path.exists(path): os.startfile(path)
