# src/file_explorer_manager.py - Gestor del Explorador V.4.5 - Crear carpeta inline
import tkinter as tk
from tkinter import ttk, messagebox
import os
from datetime import datetime

# Importar componentes separados
from .explorer_ui import ExplorerUI
from .file_monitor import FileMonitor
from .file_operations import FileOperations

class FileExplorerManager:
    """Gestor principal del explorador de archivos - Con crear carpeta inline"""
    
    def __init__(self, app):
        self.app = app
        self.current_path = os.path.expanduser("~")
        self.assigned_column = None
        
        # Componentes del explorador
        self.ui = None
        self.file_monitor = FileMonitor(self)
        self.file_ops = FileOperations(self)
        
        # Variables de estado
        self.resize_start_x = 0
        self.resize_start_width = 0
        self.edit_entry = None
        self.editing_item = None
        self.original_name = None
        self.is_creating_new = False  # Flag para distinguir crear vs renombrar
        self.new_folder_parent = None  # Directorio padre para nueva carpeta
        
        # Mapeo de rutas a items del árbol
        self.path_to_item = {}
        self.item_to_path = {}
        
        # Control de carga de nodos
        self.loading_items = set()
        self.loaded_items = set()
        self.expanding_items = set()
    
    @property
    def frame(self):
        return self.ui.frame if self.ui else None
    
    @property
    def tree(self):
        return self.ui.tree if self.ui else None
    
    @property
    def path_label(self):
        return self.ui.path_label if self.ui else None
    
    def is_visible(self):
        """Verifica si el explorador está visible"""
        if not self.frame:
            return False
        try:
            return bool(self.frame.grid_info())
        except:
            return False
    
    def toggle_visibility(self):
        """Alterna la visibilidad del explorador"""
        if self.is_visible():
            self.hide()
        else:
            self.show()
    
    def show(self):
        """Muestra el explorador de archivos con posicionamiento dual"""
        if not self.ui:
            self.create_explorer()
        
        if self.frame:
            self.assigned_column = self.app.assign_panel_position('explorador')
            self.frame.grid(row=0, column=self.assigned_column, sticky='ns', padx=(0, 0))
            
            if hasattr(self.app, 'mostrar_explorador'):
                self.app.mostrar_explorador.set(True)
            
            if hasattr(self.ui, 'update_scrollbars'):
                self.frame.after(100, self.ui.update_scrollbars)
                self.frame.after(300, self.ui.update_scrollbars)
            
            print(f"[DEBUG] Explorador mostrado en columna {self.assigned_column}")
    
    def hide(self):
        """Oculta el explorador de archivos y libera su posición"""
        if self.frame:
            self.frame.grid_forget()
            self.file_monitor.stop()
            
            if self.assigned_column is not None:
                self.app.release_panel_position('explorador')
                print(f"[DEBUG] Explorador liberado de columna {self.assigned_column}")
                self.assigned_column = None
            
            if hasattr(self.app, 'mostrar_explorador'):
                self.app.mostrar_explorador.set(False)
    
    def create_explorer(self):
        """Crea el widget del explorador"""
        panel_width = 300
        if hasattr(self.app, 'window_manager') and hasattr(self.app.window_manager, 'get_panel_width'):
            panel_width = self.app.window_manager.get_panel_width()
        
        print(f"[DEBUG] Explorador usando ancho: {panel_width}px (8cm)")
        
        parent_frame = getattr(self.app, 'app_frame', self.app.master)
        self.ui = ExplorerUI(parent_frame, self)
        
        if self.ui.create(panel_width):
            self._configure_keyboard_shortcuts()
            self.load_directory(self.current_path)
            return True
        return False
    
    def _configure_keyboard_shortcuts(self):
        """Configura atajos de teclado para el explorador"""
        if self.tree:
            # Ctrl+N para crear nueva carpeta
            self.tree.bind('<Control-n>', lambda e: self.create_new_folder_inline())
            self.tree.bind('<Control-N>', lambda e: self.create_new_folder_inline())
            
            print("[DEBUG] Atajo Ctrl+N configurado para crear carpetas inline")
    
    def create_new_folder_inline(self):
        """Crea una nueva carpeta con edición inline (como F2)"""
        try:
            # Determinar el directorio donde crear la carpeta
            target_dir = None
            parent_item = None
            selection = self.tree.selection()
            
            if selection:
                # Si hay algo seleccionado, verificar si es una carpeta
                selected_item = selection[0]
                selected_path = self.item_to_path.get(selected_item)
                
                if selected_path and os.path.isdir(selected_path):
                    # Crear dentro de la carpeta seleccionada
                    target_dir = selected_path
                    parent_item = selected_item
                    
                    # Expandir la carpeta si no está expandida
                    if not self.tree.item(selected_item, 'open'):
                        self.tree.item(selected_item, open=True)
                        self.handle_node_expansion_immediate(selected_item)
                elif selected_path:
                    # Si es un archivo, usar el directorio padre
                    target_dir = os.path.dirname(selected_path)
                    # Encontrar el parent_item del directorio
                    parent_item = self.tree.parent(selected_item)
            
            # Si no hay selección o no se pudo determinar, usar directorio raíz
            if not target_dir or not parent_item:
                target_dir = self.current_path
                # El primer item es siempre la raíz
                root_items = self.tree.get_children()
                if root_items:
                    parent_item = root_items[0]
                else:
                    messagebox.showerror("Error", "No se encontró el directorio raíz")
                    return
            
            # Validar permisos de escritura
            if not os.access(target_dir, os.W_OK):
                messagebox.showerror(
                    "Error de permisos",
                    f"No tiene permisos de escritura en:\n{target_dir}"
                )
                return
            
            # Generar nombre único temporal
            base_name = "Nueva carpeta"
            temp_name = base_name
            counter = 1
            temp_path = os.path.join(target_dir, temp_name)
            
            while os.path.exists(temp_path):
                temp_name = f"{base_name} ({counter})"
                temp_path = os.path.join(target_dir, temp_name)
                counter += 1
            
            # Contar items para el tag
            existing_items = len(self.tree.get_children(parent_item))
            tag = 'evenrow' if existing_items % 2 == 0 else 'oddrow'
            
            # Crear item temporal en el árbol (sin crear carpeta física aún)
            temp_item = self.tree.insert(
                parent_item,
                'end',
                text=f"📁 {temp_name}",
                values=(datetime.now().strftime("%d/%m/%Y %H:%M"),),
                tags=(tag,)
            )
            
            # Hacer visible y seleccionar
            self.tree.selection_set(temp_item)
            self.tree.focus(temp_item)
            self.tree.see(temp_item)
            
            # Guardar información para la creación
            self.new_folder_parent = target_dir
            self.editing_item = temp_item
            self.original_name = temp_name
            self.is_creating_new = True
            
            # Iniciar edición inline
            self._start_inline_edit_for_creation(temp_item, temp_name)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error preparando creación de carpeta:\n{str(e)}")
            print(f"[ERROR] Error en create_new_folder_inline: {e}")
    
    def _start_inline_edit_for_creation(self, item, initial_name):
        """Inicia edición inline para creación de carpeta"""
        bbox = self.tree.bbox(item, column='#0')
        if not bbox:
            # Si no hay bbox, cancelar
            self.tree.delete(item)
            self.is_creating_new = False
            return
        
        x, y, width, height = bbox
        
        self.edit_entry = tk.Entry(self.tree, font=('Segoe UI', 10))
        self.edit_entry.place(x=x + 20, y=y, width=width-25, height=height)
        self.edit_entry.insert(0, initial_name)
        self.edit_entry.select_range(0, len(initial_name))
        self.edit_entry.focus_set()
        
        # Bindings específicos
        self.edit_entry.bind('<Return>', self._finish_create_folder)
        self.edit_entry.bind('<Escape>', self._cancel_create_folder)
        self.edit_entry.bind('<FocusOut>', self._finish_create_folder)
    
    def _finish_create_folder(self, event=None):
        """Finaliza creación de carpeta (crea físicamente)"""
        if not self.edit_entry or not self.is_creating_new:
            return
        
        new_name = self.edit_entry.get().strip()
        self.edit_entry.destroy()
        self.edit_entry = None
        
        # Si está vacío o es igual al nombre temporal, cancelar
        if not new_name:
            self._cancel_create_folder_cleanup()
            return
        
        # Validar caracteres inválidos
        caracteres_invalidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        if any(char in new_name for char in caracteres_invalidos):
            messagebox.showwarning(
                "Nombre inválido",
                f"El nombre no puede contener: {' '.join(caracteres_invalidos)}"
            )
            self._cancel_create_folder_cleanup()
            return
        
        # Construir ruta completa
        nueva_ruta = os.path.join(self.new_folder_parent, new_name)
        
        # Verificar si ya existe
        if os.path.exists(nueva_ruta):
            messagebox.showwarning(
                "Carpeta existente",
                f"Ya existe una carpeta o archivo con el nombre:\n{new_name}"
            )
            self._cancel_create_folder_cleanup()
            return
        
        try:
            # CREAR LA CARPETA FÍSICAMENTE
            os.makedirs(nueva_ruta, exist_ok=False)
            
            # Actualizar el item temporal con la información real
            self.tree.item(self.editing_item, text=f"📁 {new_name}")
            
            # Agregar al mapeo
            self.path_to_item[nueva_ruta] = self.editing_item
            self.item_to_path[self.editing_item] = nueva_ruta
            
            # Agregar dummy si es necesario (para que muestre flecha de expansión)
            # Aunque esté vacía, dejamos que el usuario pueda crear subcarpetas
            
            # Mensaje de éxito
            if hasattr(self.app, 'label_estado'):
                self.app.label_estado.config(text=f"Carpeta creada: {new_name}")
            
            print(f"[DEBUG] Carpeta creada exitosamente: {nueva_ruta}")
            
        except PermissionError:
            messagebox.showerror(
                "Error de permisos",
                "No tiene permisos para crear carpetas en esta ubicación"
            )
            self._cancel_create_folder_cleanup()
        except OSError as e:
            messagebox.showerror(
                "Error al crear carpeta",
                f"No se pudo crear la carpeta:\n{str(e)}"
            )
            self._cancel_create_folder_cleanup()
        except Exception as e:
            messagebox.showerror(
                "Error inesperado",
                f"Error al crear carpeta:\n{str(e)}"
            )
            self._cancel_create_folder_cleanup()
        finally:
            self.is_creating_new = False
            self.new_folder_parent = None
            self.editing_item = None
    
    def _cancel_create_folder(self, event=None):
        """Cancela creación de carpeta (ESC)"""
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
        
        self._cancel_create_folder_cleanup()
    
    def _cancel_create_folder_cleanup(self):
        """Limpia después de cancelar creación"""
        if self.is_creating_new and self.editing_item:
            # Eliminar el item temporal del árbol
            try:
                self.tree.delete(self.editing_item)
            except:
                pass
        
        self.is_creating_new = False
        self.new_folder_parent = None
        self.editing_item = None
        self.original_name = None
        
        if hasattr(self.app, 'label_estado'):
            self.app.label_estado.config(text="Creación de carpeta cancelada")
    
    def load_directory(self, path):
        """Carga el contenido de un directorio en estructura de árbol"""
        if not os.path.exists(path) or not os.path.isdir(path):
            return
        
        self.current_path = os.path.normpath(path)
        self.path_label.configure(text=f"Raíz: {self.current_path}")
        
        print(f"[DEBUG] Cargando directorio: {self.current_path}")
        
        # Limpiar árbol y mapeos
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._clear_state()
        
        # Crear nodo raíz
        root_name = os.path.basename(self.current_path) or self.current_path
        try:
            root_fecha = datetime.fromtimestamp(os.path.getmtime(self.current_path)).strftime("%d/%m/%Y %H:%M")
        except:
            root_fecha = "N/A"
            
        root_item = self.tree.insert('', 'end', text=f"📁 {root_name}", 
                                    values=(root_fecha,),
                                    open=True, tags=('evenrow',))
        
        self.path_to_item[self.current_path] = root_item
        self.item_to_path[root_item] = self.current_path
        
        # Cargar contenido del directorio raíz
        self._load_directory_children_sync(root_item, self.current_path)
        
        # Iniciar monitoreo
        if self.is_visible():
            self.file_monitor.start(self.current_path)
        
        # Actualizar scrollbars
        if hasattr(self.ui, 'update_scrollbars'):
            self.tree.after_idle(self.ui.update_scrollbars)
    
    def _clear_state(self):
        """Limpia el estado interno"""
        self.path_to_item.clear()
        self.item_to_path.clear()
        self.loading_items.clear()
        self.loaded_items.clear()
        self.expanding_items.clear()
    
    def _load_directory_children_sync(self, parent_item, directory_path):
        """Carga los hijos de un directorio sincronizadamente"""
        print(f"[DEBUG] Cargando hijos para: {directory_path}")
        
        if parent_item in self.loading_items or parent_item in self.loaded_items:
            return
        
        self.loading_items.add(parent_item)
        
        try:
            self._clear_children(parent_item)
            
            items = self.file_ops.get_directory_contents(directory_path)
            if items is None:
                self._add_error_node(parent_item, "⚠ Acceso denegado")
                return
            
            if not items:
                print(f"[DEBUG] Directorio vacío: {directory_path}")
                return
            
            self._add_directory_items(parent_item, items)
            self.loaded_items.add(parent_item)
                    
        except Exception as e:
            print(f"[ERROR] Error cargando directorio {directory_path}: {e}")
            self._add_error_node(parent_item, f'❌ Error: {str(e)}')
        finally:
            self.loading_items.discard(parent_item)
    
    def _clear_children(self, parent_item):
        """Limpia los hijos de un item"""
        children = self.tree.get_children(parent_item)
        for child in children:
            if child in self.item_to_path:
                path_to_remove = self.item_to_path[child]
                if path_to_remove in self.path_to_item:
                    del self.path_to_item[path_to_remove]
                del self.item_to_path[child]
            self.tree.delete(child)
    
    def _add_error_node(self, parent_item, text):
        """Agrega un nodo de error"""
        error_item = self.tree.insert(parent_item, 'end', text=text, 
                                    values=('',), tags=('evenrow',))
    
    def _add_directory_items(self, parent_item, items):
        """Agrega items del directorio al árbol"""
        for i, (name, is_dir, fecha_mod, full_path) in enumerate(items):
            row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            if is_dir:
                display_name = f"📁 {name}"
                item_id = self.tree.insert(parent_item, 'end', text=display_name,
                                         values=(fecha_mod,), tags=(row_tag,))
                
                self.path_to_item[full_path] = item_id
                self.item_to_path[item_id] = full_path
                
                if self.file_ops.has_subdirectories(full_path):
                    dummy = self.tree.insert(item_id, 'end', text='Cargando...', values=('',))
            else:
                display_name = f"📄 {name}"
                item_id = self.tree.insert(parent_item, 'end', text=display_name,
                                         values=(fecha_mod,), tags=(row_tag,))
                
                self.path_to_item[full_path] = item_id
                self.item_to_path[item_id] = full_path
    
    def handle_node_expansion_immediate(self, item):
        """Maneja expansión de nodo inmediatamente"""
        if item in self.expanding_items or item in self.loaded_items:
            return
        
        self.expanding_items.add(item)
        path = self.item_to_path.get(item)
        
        if not path or not os.path.isdir(path):
            self.expanding_items.discard(item)
            return
        
        children = self.tree.get_children(item)
        for child in children:
            if self.tree.item(child, 'text') == 'Cargando...':
                self.tree.delete(child)
                break
        
        try:
            self._load_directory_children_sync(item, path)
        except Exception as e:
            print(f"[ERROR] Error expandiendo nodo: {e}")
        finally:
            self.expanding_items.discard(item)
    
    def refresh_tree(self):
        """Refresca todo el árbol"""
        print("[DEBUG] Refrescando árbol completo")
        self._clear_state()
        self.load_directory(self.current_path)
    
    def refresh_current_node(self):
        """Refresca el nodo actual"""
        if self.current_path in self.path_to_item:
            item = self.path_to_item[self.current_path]
            if self.tree.item(item, 'open'):
                self.loaded_items.discard(item)
                self._load_directory_children_sync(item, self.current_path)
    
    def go_home(self):
        """Va al directorio home"""
        home_path = os.path.expanduser("~")
        self.load_directory(home_path)
    
    def on_double_click(self, event):
        """Maneja doble clic"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        path = self.item_to_path.get(item)
        
        if path:
            if os.path.isdir(path):
                is_open = self.tree.item(item, 'open')
                self.tree.item(item, open=not is_open)
                
                if not is_open:
                    self.handle_node_expansion_immediate(item)
            else:
                self.file_ops.open_item(path)
    
    def on_enter_key(self, event):
        """Maneja tecla Enter"""
        selection = self.tree.selection()
        if not selection:
            return "break"
        
        item = selection[0]
        path = self.item_to_path.get(item)
        
        if path and os.path.isdir(path):
            is_open = self.tree.item(item, 'open')
            self.tree.item(item, open=not is_open)
            
            if not is_open:
                self.handle_node_expansion_immediate(item)
        
        return "break"
    
    def on_f2_key(self, event):
        """Maneja F2 para renombrar"""
        self.handle_f2()
        return "break"
    
    def handle_f2(self):
        """Inicia edición para renombrar"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        path = self.item_to_path.get(item)
        
        if path and path != self.current_path:
            self.start_inline_edit(item)
    
    def start_inline_edit(self, item):
        """Inicia edición inline del nombre (SOLO para renombrar existentes)"""
        name = self.tree.item(item, 'text')
        clean_name = name.replace('📁 ', '').replace('📄 ', '')
        
        bbox = self.tree.bbox(item, column='#0')
        if not bbox:
            return
        
        x, y, width, height = bbox
        
        self.edit_entry = tk.Entry(self.tree, font=('Segoe UI', 10))
        self.edit_entry.place(x=x + 20, y=y, width=width-25, height=height)
        self.edit_entry.insert(0, clean_name)
        self.edit_entry.select_range(0, len(clean_name))
        self.edit_entry.focus_set()
        
        self.editing_item = item
        self.original_name = clean_name
        self.is_creating_new = False  # Esto es RENOMBRAR, no crear
        
        self.edit_entry.bind('<Return>', self.finish_inline_edit)
        self.edit_entry.bind('<Escape>', self.cancel_inline_edit)
        self.edit_entry.bind('<FocusOut>', self.finish_inline_edit)
    
    def finish_inline_edit(self, event=None):
        """Finaliza edición y renombra (SOLO para archivos existentes)"""
        if not self.edit_entry or self.is_creating_new:
            return
        
        new_name = self.edit_entry.get().strip()
        self.edit_entry.destroy()
        self.edit_entry = None
        
        if new_name and new_name != self.original_name:
            old_path = self.item_to_path.get(self.editing_item)
            if old_path and self._rename_item(old_path, new_name):
                self._update_item_after_rename(old_path, new_name)
    
    def _rename_item(self, old_path, new_name):
        """Renombra un item"""
        old_dir = os.path.dirname(old_path)
        new_path = os.path.join(old_dir, new_name)
        return self.file_ops.rename_item(old_path, new_name)
    
    def _update_item_after_rename(self, old_path, new_name):
        """Actualiza el item después del renombrado"""
        old_dir = os.path.dirname(old_path)
        new_path = os.path.join(old_dir, new_name)
        
        del self.path_to_item[old_path]
        del self.item_to_path[self.editing_item]
        self.path_to_item[new_path] = self.editing_item
        self.item_to_path[self.editing_item] = new_path
        
        is_dir = os.path.isdir(new_path)
        prefix = "📁 " if is_dir else "📄 "
        self.tree.item(self.editing_item, text=f"{prefix}{new_name}")
        
        if hasattr(self.app, 'label_estado'):
            self.app.label_estado.config(text=f"Renombrado: {new_name}")
    
    def cancel_inline_edit(self, event=None):
        """Cancela edición inline (SOLO para renombrar)"""
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
    
    def show_context_menu(self, event):
        """Muestra menú contextual"""
        region = self.tree.identify('region', event.x, event.y)
        
        if region != 'tree':
            context_menu = tk.Menu(self.tree, tearoff=0)
            context_menu.add_command(
                label="📁 Nueva carpeta", 
                command=self.create_new_folder_inline,
                accelerator="Ctrl+N"
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="🔄 Actualizar árbol", 
                command=self.refresh_tree
            )
            context_menu.add_command(
                label="🏠 Ir a Home", 
                command=self.go_home
            )
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
            return
        
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        self.tree.selection_set(item)
        context_menu = tk.Menu(self.tree, tearoff=0)
        
        path = self.item_to_path.get(item)
        if path and path != self.current_path:
            self._add_context_menu_items(context_menu, path)
        
        context_menu.add_separator()
        context_menu.add_command(
            label="📁 Nueva carpeta", 
            command=self.create_new_folder_inline,
            accelerator="Ctrl+N"
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="🔄 Actualizar árbol", 
            command=self.refresh_tree
        )
        context_menu.add_command(
            label="🏠 Ir a Home", 
            command=self.go_home
        )
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _add_context_menu_items(self, menu, path):
        """Agrega items específicos al menú contextual"""
        if os.path.isdir(path):
            menu.add_command(
                label="📂 Expandir/Colapsar", 
                command=lambda: self.on_double_click(None)
            )
            menu.add_command(
                label="✏️ Renombrar carpeta", 
                command=self.handle_f2,
                accelerator="F2"
            )
        elif os.path.isfile(path):
            menu.add_command(
                label="📄 Abrir archivo", 
                command=lambda: self.on_double_click(None)
            )
            menu.add_command(
                label="✏️ Renombrar archivo", 
                command=self.handle_f2,
                accelerator="F2"
            )
        
        menu.add_separator()
        # ELIMINAR sin espacios extra
        menu.add_command(
            label="🗑 Eliminar",  # Sin variante de emoji
            command=self.delete_selected_item,
            accelerator="Supr"
        )
        menu.add_command(
            label="📋 Copiar ruta", 
            command=self.copy_selected_path
        )
    
    def copy_selected_path(self):
        """Copia ruta del elemento seleccionado"""
        selection = self.tree.selection()
        if not selection:
            return
        
        path = self.item_to_path.get(selection[0])
        if path:
            self.app.master.clipboard_clear()
            self.app.master.clipboard_append(path)
            
            if hasattr(self.app, 'label_estado'):
                self.app.label_estado.config(text=f"Ruta copiada: {os.path.basename(path)}")
    
    def open_selected_item(self):
        """Abre el elemento seleccionado con F7"""
        selection = self.tree.selection()
        if not selection:
            return
        
        path = self.item_to_path.get(selection[0])
        if path:
            self.file_ops.open_item(path)
    
    def start_resize(self, event):
        """Inicia redimensionamiento"""
        self.resize_start_x = event.x_root
        self.resize_start_width = self.frame.winfo_width()
    
    def do_resize(self, event):
        """Realiza redimensionamiento"""
        if not self.frame:
            return
        
        diff = self.resize_start_x - event.x_root
        new_width = self.resize_start_width + diff
        new_width = max(200, min(600, new_width))
        self.frame.configure(width=new_width)
    
    def cleanup(self):
        """Limpia recursos"""
        self.file_monitor.stop()
    
    def delete_selected_item(self):
        """Elimina el elemento seleccionado (archivo o carpeta)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(
                "Sin selección",
                "Por favor selecciona un archivo o carpeta para eliminar"
            )
            return
        
        item = selection[0]
        path = self.item_to_path.get(item)
        
        # No permitir eliminar la raíz
        if not path or path == self.current_path:
            messagebox.showwarning(
                "Operación no permitida",
                "No se puede eliminar el directorio raíz"
            )
            return
        
        # Obtener información del elemento
        item_name = os.path.basename(path)
        is_dir = os.path.isdir(path)
        item_type = "carpeta" if is_dir else "archivo"
        
        # Confirmar eliminación
        if is_dir:
            # Contar elementos dentro
            try:
                contents_count = len(os.listdir(path))
                warning_msg = f"¿Estás seguro de eliminar la carpeta '{item_name}'?\n\n"
                if contents_count > 0:
                    warning_msg += f"⚠️ Contiene {contents_count} elemento(s)\n"
                    warning_msg += "Todo su contenido será eliminado."
                else:
                    warning_msg += "La carpeta está vacía."
            except:
                warning_msg = f"¿Estás seguro de eliminar la carpeta '{item_name}'?"
        else:
            warning_msg = f"¿Estás seguro de eliminar el archivo '{item_name}'?"
        
        response = messagebox.askyesno(
            f"Confirmar eliminación de {item_type}",
            warning_msg,
            icon='warning'
        )
        
        if not response:
            return
        
        # Intentar eliminar
        success = self.file_ops.delete_item(path)
        
        if success:
            # Eliminar del árbol
            self.tree.delete(item)
            
            # Limpiar mapeos
            if path in self.path_to_item:
                del self.path_to_item[path]
            if item in self.item_to_path:
                del self.item_to_path[item]
            
            # Actualizar estado
            if hasattr(self.app, 'label_estado'):
                self.app.label_estado.config(
                    text=f"{item_type.capitalize()} eliminado: {item_name}"
                )
            
            print(f"[DEBUG] Eliminado exitosamente: {path}")
        else:
            # El error ya fue mostrado por file_ops.delete_item
            pass

    def update_shortcuts_context(self):
        """Actualiza la barra de atajos según la selección actual"""
        if not self.ui or not hasattr(self.ui, 'update_shortcuts_bar'):
            return
        
        selection = self.tree.selection()
        if not selection:
            self.ui.update_shortcuts_bar('none')
            return
        
        item = selection[0]
        path = self.item_to_path.get(item)
        
        if path:
            if os.path.isdir(path):
                self.ui.update_shortcuts_bar('folder')
            elif os.path.isfile(path):
                self.ui.update_shortcuts_bar('file')
            else:
                self.ui.update_shortcuts_bar('none')
        else:
            self.ui.update_shortcuts_bar('none')