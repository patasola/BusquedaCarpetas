# src/locations_config_modal.py - Modal de Configuración de Ubicaciones V.4.5 (CORREGIDO)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
from datetime import datetime

class LocationItem:
    """Representa una ubicación de búsqueda"""
    def __init__(self, path, name=None, enabled=True):
        self.path = os.path.normpath(path)
        self.name = name or os.path.basename(path) or path
        self.enabled = enabled
        self.cache_size = 0
        self.last_scanned = None
        self.is_valid = os.path.exists(path) and os.path.isdir(path)
        
    def to_dict(self):
        return {
            'path': self.path,
            'name': self.name,
            'enabled': self.enabled,
            'cache_size': self.cache_size,
            'last_scanned': self.last_scanned
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(data['path'], data['name'], data.get('enabled', True))
        item.cache_size = data.get('cache_size', 0)
        item.last_scanned = data.get('last_scanned')
        return item

class LocationsConfigModal:
    """Modal para configurar ubicaciones de búsqueda múltiple"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.modal = None
        self.locations = []
        self.tree = None
        self.config_file = "search_locations.json"
        
        # Variables de control
        self.building_cache = False
        self.progress_var = tk.StringVar()
        self.progress_bar = None
        
        self.load_locations()
    
    def show_modal(self):
        """Muestra el modal de configuración"""
        if self.modal:
            self.modal.lift()
            return
        
        self._create_modal_window()
        self._create_modal_content()
        self._populate_tree()
    
    def _create_modal_window(self):
        """Crea la ventana modal"""
        self.modal = tk.Toplevel(self.parent)
        self.modal.title("Configuración de Ubicaciones de Búsqueda")
        self.modal.geometry("700x500")
        self.modal.resizable(True, True)
        self.modal.configure(bg="#f6f5f5")
        
        # Hacer modal
        self.modal.transient(self.parent)
        self.modal.grab_set()
        
        # Centrar ventana
        self.modal.update_idletasks()
        x = (self.modal.winfo_screenwidth() - 700) // 2
        y = (self.modal.winfo_screenheight() - 500) // 2
        self.modal.geometry(f"700x500+{x}+{y}")
        
        # Protocolo de cierre
        self.modal.protocol("WM_DELETE_WINDOW", self._close_modal)
    
    def _create_modal_content(self):
        """Crea el contenido del modal"""
        # Título
        title_frame = tk.Frame(self.modal, bg="#f6f5f5")
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        tk.Label(title_frame, 
                text="📂 Ubicaciones de Búsqueda", 
                font=("Segoe UI", 14, "bold"),
                bg="#f6f5f5", fg="#424242").pack()
        
        tk.Label(title_frame,
                text="Configure las carpetas donde desea realizar búsquedas",
                font=("Segoe UI", 9),
                bg="#f6f5f5", fg="#666666").pack()
        
        # Frame principal
        main_frame = tk.Frame(self.modal, bg="#f6f5f5")
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Botones superiores
        buttons_frame = tk.Frame(main_frame, bg="#f6f5f5")
        buttons_frame.pack(fill='x', pady=(0, 10))
        
        self._create_action_buttons(buttons_frame)
        
        # TreeView con ubicaciones
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self._create_locations_tree(tree_frame)
        
        # Barra de progreso (oculta inicialmente)
        progress_frame = tk.Frame(main_frame, bg="#f6f5f5")
        progress_frame.pack(fill='x', pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=(0, 5))
        
        progress_label = tk.Label(progress_frame, 
                                textvariable=self.progress_var,
                                font=("Segoe UI", 8),
                                bg="#f6f5f5", fg="#666666")
        progress_label.pack()
        
        # Ocultar progreso inicialmente
        progress_frame.pack_forget()
        self.progress_frame = progress_frame
        
        # Botones inferiores
        bottom_frame = tk.Frame(self.modal, bg="#f6f5f5")
        bottom_frame.pack(fill='x', padx=20, pady=20)
        
        self._create_bottom_buttons(bottom_frame)
    
    def _create_action_buttons(self, parent):
        """Crea botones de acción"""
        tk.Button(parent, text="➕ Agregar Ubicación",
                 command=self._add_location,
                 bg="#e8f5e8", fg="#2e7d32",
                 font=("Segoe UI", 9),
                 relief='flat', padx=15, pady=5,
                 cursor="hand2").pack(side='left', padx=(0, 10))
        
        tk.Button(parent, text="❌ Eliminar",
                 command=self._remove_location,
                 bg="#ffebee", fg="#c62828",
                 font=("Segoe UI", 9),
                 relief='flat', padx=15, pady=5,
                 cursor="hand2").pack(side='left', padx=(0, 10))
        
        tk.Button(parent, text="🔄 Construir Todos los Caches",
                 command=self._build_all_caches,
                 bg="#e3f2fd", fg="#1565c0",
                 font=("Segoe UI", 9),
                 relief='flat', padx=15, pady=5,
                 cursor="hand2").pack(side='left')
    
    def _create_locations_tree(self, parent):
        """Crea TreeView para mostrar ubicaciones"""
        # Scrollbars
        v_scroll = ttk.Scrollbar(parent, orient="vertical")
        h_scroll = ttk.Scrollbar(parent, orient="horizontal")
        
        # TreeView
        self.tree = ttk.Treeview(parent,
                               columns=("path", "status", "cache_size", "last_scan"),
                               show="tree headings",
                               yscrollcommand=v_scroll.set,
                               xscrollcommand=h_scroll.set)
        
        # Configurar columnas
        self.tree.heading("#0", text="Nombre", anchor='w')
        self.tree.heading("path", text="Ruta", anchor='w')
        self.tree.heading("status", text="Estado", anchor='center')
        self.tree.heading("cache_size", text="Archivos", anchor='center')
        self.tree.heading("last_scan", text="Último Escaneo", anchor='center')
        
        self.tree.column("#0", width=150, minwidth=100)
        self.tree.column("path", width=250, minwidth=200)
        self.tree.column("status", width=80, minwidth=70)
        self.tree.column("cache_size", width=80, minwidth=70)
        self.tree.column("last_scan", width=120, minwidth=100)
        
        # Configurar scrollbars
        v_scroll.configure(command=self.tree.yview)
        h_scroll.configure(command=self.tree.xview)
        
        # Pack elementos
        self.tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')
        
        # Eventos
        self.tree.bind('<Double-1>', self._on_item_double_click)
        self.tree.bind('<Button-3>', self._show_context_menu)
    
    def _create_bottom_buttons(self, parent):
        """Crea botones inferiores"""
        tk.Button(parent, text="Aplicar y Cerrar",
                 command=self._apply_and_close,
                 bg="#1976D2", fg="white",
                 font=("Segoe UI", 10, "bold"),
                 relief='flat', padx=20, pady=8,
                 cursor="hand2").pack(side='right', padx=(10, 0))
        
        tk.Button(parent, text="Cancelar",
                 command=self._close_modal,
                 bg="#e0e0e0", fg="#424242",
                 font=("Segoe UI", 10),
                 relief='flat', padx=20, pady=8,
                 cursor="hand2").pack(side='right')
    
    def _populate_tree(self):
        """Puebla el TreeView con las ubicaciones"""
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar ubicaciones
        for i, location in enumerate(self.locations):
            status = "✅ Activa" if location.enabled else "⭕ Inactiva"
            cache_info = f"{location.cache_size:,}" if location.cache_size > 0 else "Sin cache"
            last_scan = location.last_scanned or "Nunca"
            
            # Color según estado
            tags = ('enabled',) if location.enabled else ('disabled',)
            if not location.is_valid:
                tags = ('invalid',)
                status = "❌ No existe"
            
            self.tree.insert("", "end",
                           text=location.name,
                           values=(location.path, status, cache_info, last_scan),
                           tags=tags)
        
        # Configurar tags de colores
        self.tree.tag_configure('enabled', background='#f1f8e9')
        self.tree.tag_configure('disabled', background='#f5f5f5', foreground='#999999')
        self.tree.tag_configure('invalid', background='#ffebee', foreground='#c62828')
    
    def _add_location(self):
        """Agrega nueva ubicación"""
        folder_path = filedialog.askdirectory(
            title="Seleccionar carpeta para búsqueda",
            initialdir=os.path.expanduser("~")
        )
        
        if folder_path:
            # Verificar si ya existe
            for location in self.locations:
                if os.path.normpath(location.path) == os.path.normpath(folder_path):
                    messagebox.showwarning("Ubicación duplicada", 
                                         f"La ubicación ya existe:\n{folder_path}")
                    return
            
            # Crear nueva ubicación
            location = LocationItem(folder_path)
            self.locations.append(location)
            self._populate_tree()
            
            # Preguntar si construir cache inmediatamente
            if messagebox.askyesno("Construir Cache", 
                                 f"¿Desea construir el cache para '{location.name}' ahora?\n\n"
                                 "Esto puede tomar unos minutos pero hará las búsquedas más rápidas."):
                self._build_cache_for_location(location)
    
    def _remove_location(self):
        """Elimina ubicación seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Selección requerida", "Seleccione una ubicación para eliminar")
            return
        
        item_index = self.tree.index(selection[0])
        if 0 <= item_index < len(self.locations):
            location = self.locations[item_index]
            
            if messagebox.askyesno("Confirmar eliminación",
                                 f"¿Eliminar la ubicación '{location.name}'?\n\n{location.path}"):
                self.locations.pop(item_index)
                self._populate_tree()
    
    def _build_all_caches(self):
        """Construye cache para todas las ubicaciones"""
        if self.building_cache:
            messagebox.showinfo("Cache en construcción", "Ya se está construyendo un cache")
            return
        
        enabled_locations = [loc for loc in self.locations if loc.enabled and loc.is_valid]
        if not enabled_locations:
            messagebox.showinfo("Sin ubicaciones", "No hay ubicaciones activas para construir cache")
            return
        
        if messagebox.askyesno("Construir Caches",
                             f"¿Construir cache para {len(enabled_locations)} ubicaciones?\n\n"
                             "Esto puede tomar varios minutos."):
            self._start_batch_cache_build(enabled_locations)
    
    def _start_batch_cache_build(self, locations):
        """Inicia construcción de cache en batch"""
        self.building_cache = True
        self.progress_frame.pack(fill='x', pady=(10, 0))
        self.progress_bar.start()
        self.progress_var.set("Preparando construcción de caches...")
        
        def build_worker():
            try:
                for i, location in enumerate(locations):
                    self.modal.after(0, lambda: self.progress_var.set(
                        f"Construyendo cache {i+1}/{len(locations)}: {location.name}"
                    ))
                    
                    # Construir cache real usando el cache_manager de la app
                    self._build_cache_sync(location)
                    
                self.modal.after(0, self._finish_batch_build)
                
            except Exception as e:
                self.modal.after(0, lambda: self._handle_build_error(str(e)))
        
        threading.Thread(target=build_worker, daemon=True).start()
    
    def _build_cache_sync(self, location):
        """Construye cache para una ubicación usando el sistema real CON NOMBRE ÚNICO"""
        try:
            # USAR EL SISTEMA REAL DE CACHE CON NOMBRES ÚNICOS
            from .cache_manager import CacheManager
            import hashlib
            
            # Generar nombre único de archivo cache basado en la ruta
            path_hash = hashlib.md5(location.path.encode()).hexdigest()[:8]
            cache_filename = f"cache_{path_hash}.pkl"
            
            # Crear cache manager temporal para esta ubicación
            temp_cache = CacheManager(location.path)
            temp_cache.cache_file = cache_filename  # Usar nombre único
            
            # Callback de progreso silencioso
            def silent_callback(progress, total, msg):
                pass  # No mostrar progreso individual
            
            temp_cache.callback_progreso = silent_callback
            
            # Construir cache
            if temp_cache.construir_cache():
                # Actualizar información de la ubicación
                stats = temp_cache.get_cache_stats()
                location.cache_size = stats.get('carpetas', 0)
                location.last_scanned = datetime.now().strftime("%H:%M:%S")
                location.is_valid = True
                print(f"[DEBUG] Cache construido para {location.name}: {location.cache_size} carpetas (archivo: {cache_filename})")
            else:
                print(f"[ERROR] Falló construcción de cache para {location.name}")
                
        except Exception as e:
            print(f"[ERROR] Error construyendo cache para {location.name}: {e}")
    
    def _finish_batch_build(self):
        """Finaliza construcción de cache en batch"""
        self.building_cache = False
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        self._populate_tree()
        messagebox.showinfo("Cache Completado", "Todos los caches han sido construidos exitosamente")
    
    def _handle_build_error(self, error_msg):
        """Maneja errores en construcción de cache"""
        self.building_cache = False
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        messagebox.showerror("Error en Cache", f"Error construyendo cache:\n{error_msg}")
    
    def _on_item_double_click(self, event):
        """Maneja doble click en item"""
        selection = self.tree.selection()
        if selection:
            item_index = self.tree.index(selection[0])
            if 0 <= item_index < len(self.locations):
                location = self.locations[item_index]
                # Toggle enabled/disabled
                location.enabled = not location.enabled
                self._populate_tree()
    
    def _show_context_menu(self, event):
        """Muestra menú contextual"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        self.tree.selection_set(item)
        item_index = self.tree.index(item)
        
        if 0 <= item_index < len(self.locations):
            location = self.locations[item_index]
            
            context_menu = tk.Menu(self.tree, tearoff=0)
            
            status_text = "Desactivar" if location.enabled else "Activar"
            context_menu.add_command(label=status_text, 
                                   command=lambda: self._toggle_location(item_index))
            
            context_menu.add_command(label="Construir cache", 
                                   command=lambda: self._build_cache_for_location(location))
            
            context_menu.add_separator()
            context_menu.add_command(label="Abrir carpeta", 
                                   command=lambda: self._open_location_folder(location.path))
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def _toggle_location(self, index):
        """Cambia estado de ubicación"""
        if 0 <= index < len(self.locations):
            self.locations[index].enabled = not self.locations[index].enabled
            self._populate_tree()
    
    def _build_cache_for_location(self, location):
        """Construye cache para una ubicación específica"""
        self._start_batch_cache_build([location])
    
    def _open_location_folder(self, path):
        """Abre carpeta de ubicación en el explorador"""
        try:
            import subprocess
            import sys
            
            if sys.platform == "win32":
                subprocess.run(['explorer', path])
            elif sys.platform == "darwin":
                subprocess.run(['open', path])
            else:
                subprocess.run(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")
    
    def _apply_and_close(self):
        """Aplica cambios y cierra modal"""
        self.save_locations()
        
        # Notificar a la app principal sobre los cambios
        if hasattr(self.app, 'update_search_locations'):
            self.app.update_search_locations(self.locations)
        
        # Recargar ubicaciones en el sistema de búsqueda múltiple
        if hasattr(self.app, 'multi_location_search'):
            self.app.multi_location_search.reload_locations()
        
        messagebox.showinfo("Configuración Guardada", 
                          f"Se han guardado {len(self.locations)} ubicaciones de búsqueda")
        self._close_modal()
    
    def _close_modal(self):
        """Cierra el modal"""
        if self.building_cache:
            if not messagebox.askyesno("Construcción en progreso", 
                                     "Se está construyendo un cache. ¿Cancelar y cerrar?"):
                return
        
        if self.modal:
            self.modal.grab_release()
            self.modal.destroy()
            self.modal = None
    
    def load_locations(self):
        """Carga ubicaciones desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.locations = [LocationItem.from_dict(item) for item in data]
                print(f"[DEBUG] Cargadas {len(self.locations)} ubicaciones")
        except Exception as e:
            print(f"Error cargando ubicaciones: {e}")
            self.locations = []
    
    def save_locations(self):
        """Guarda ubicaciones a archivo"""
        try:
            data = [location.to_dict() for location in self.locations]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Guardadas {len(self.locations)} ubicaciones")
        except Exception as e:
            print(f"Error guardando ubicaciones: {e}")
    
    def get_enabled_locations(self):
        """Obtiene ubicaciones habilitadas"""
        return [loc for loc in self.locations if loc.enabled and loc.is_valid]