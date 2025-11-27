# src/tree_explorer.py - Explorador de Árbol V.4.2 (Con Tooltips Corregidos)
import tkinter as tk
from tkinter import ttk
import os
import threading
import time

class TreeExplorerTooltip:
    """Tooltip para explorador de árbol con error corregido"""
    
    def __init__(self, treeview, tree_explorer_instance):
        self.treeview = treeview
        self.tree_explorer = tree_explorer_instance
        self.tooltip_window = None
        self.current_item = None
        self.after_id = None
        
        # Configurar eventos
        self.treeview.bind("<Motion>", self._on_motion)
        self.treeview.bind("<Leave>", self._on_leave)
        self.treeview.bind("<Button-1>", self._hide_tooltip)
        
    def _on_motion(self, event):
        """Maneja movimiento del mouse"""
        item = self.treeview.identify_row(event.y)
        
        if item != self.current_item:
            self.current_item = item
            self._hide_tooltip()
            
            if item:
                self.after_id = self.treeview.after(500, 
                    lambda: self._show_tooltip(event.x_root, event.y_root, item))
    
    def _on_leave(self, event):
        """Mouse salió del TreeView"""
        self._hide_tooltip()
        self.current_item = None
    
    def _show_tooltip(self, x, y, item):
        """Muestra tooltip simple con wraplength"""
        if self.current_item != item:
            return
            
        # Obtener ruta completa
        ruta_completa = self._get_full_path(item)
        if not ruta_completa:
            return
        
        # Formatear ruta
        texto_tooltip = self._format_path_smart(ruta_completa)
        
        # Crear tooltip
        self.tooltip_window = tk.Toplevel(self.treeview)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.configure(bg="#ffffe0", relief="solid", bd=1)
        
        label = tk.Label(
            self.tooltip_window,
            text=texto_tooltip,
            bg="#ffffe0",
            fg="#000000",
            font=("Segoe UI", 9),
            padx=6,
            pady=4,
            wraplength=300,  # FORZAR WRAP A 300 PIXELS
            justify='left'
        )
        label.pack()
        
        # Posicionar tooltip
        self._position_tooltip(x, y)
    
    def _format_path_smart(self, ruta):
        """Formatea ruta dividida por niveles/carpetas"""
        if len(ruta) <= 50:
            return ruta
        
        # Dividir por niveles
        niveles = self._dividir_por_niveles(ruta)
        if len(niveles) > 1:
            return "\n".join(niveles)
        else:
            return ruta
    
    def _dividir_por_niveles(self, ruta):
        """Divide ruta en niveles (una carpeta por línea)"""
        if "\\" in ruta:
            separador = "\\"
        elif "/" in ruta:
            separador = "/"
        else:
            return [ruta]  # Sin separadores
        
        partes = ruta.split(separador)
        niveles = []
        
        # Primer nivel (raíz)
        if partes[0]:
            niveles.append(partes[0])
        else:
            niveles.append(separador)  # Para rutas que empiezan con /
        
        # Niveles siguientes
        for parte in partes[1:]:
            if parte:  # Ignorar partes vacías
                if len(niveles) == 1:
                    # Segundo nivel: agregar directamente
                    niveles.append(f"{separador}{parte}")
                else:
                    # Niveles siguientes: solo el nombre de la carpeta
                    niveles.append(f"{separador}{parte}")
        
        return niveles
    
    def _get_full_path(self, item):
        """Obtiene ruta completa del explorador de árbol"""
        try:
            values = self.treeview.item(item, 'values')
            if values and len(values) >= 2:
                metodo = values[0]
                ruta = values[1]
                
                # Si es método directo (C, T, E) y tiene ruta
                if metodo in ["C", "T", "E"] and ruta:
                    return ruta
                
                # Para rutas relativas, intentar construir ruta absoluta
                if ruta and hasattr(self.tree_explorer.app, 'file_manager'):
                    try:
                        ruta_base = getattr(self.tree_explorer.app, 'ruta_carpeta', '')
                        if ruta_base:
                            full_path = self.tree_explorer.app.file_manager.obtener_ruta_absoluta(ruta_base, ruta)
                            return full_path if full_path else ruta
                    except:
                        pass
                
                return ruta if ruta else self._build_path_from_hierarchy(item)
            
            # Fallback: construir desde jerarquía
            return self._build_path_from_hierarchy(item)
            
        except:
            return None
    
    def _build_path_from_hierarchy(self, item):
        """Construye ruta desde la jerarquía del árbol"""
        try:
            path_parts = []
            current = item
            
            while current:
                text = self.treeview.item(current, 'text')
                if text and not text.startswith(('🔄', '⛔', 'Cargando')):
                    # Limpiar emojis y texto extra
                    clean_text = text.replace('📁 ', '').replace('📂 ', '').replace('🗂 ', '')
                    if clean_text and clean_text != '':
                        path_parts.append(clean_text)
                current = self.treeview.parent(current)
            
            if path_parts:
                path_parts.reverse()
                # Si hay una ruta base conocida, usarla
                if hasattr(self.tree_explorer.app, 'ruta_carpeta') and self.tree_explorer.app.ruta_carpeta:
                    base_path = self.tree_explorer.app.ruta_carpeta
                    for part in path_parts[1:]:  # Saltar el primer elemento si es la raíz
                        base_path = os.path.join(base_path, part)
                    return base_path
                else:
                    return os.path.join(*path_parts)
            
            return None
        except:
            return None
    
    def _position_tooltip(self, x, y):
        """Posiciona tooltip evitando bordes"""
        if not self.tooltip_window:
            return
            
        self.tooltip_window.update_idletasks()
        tooltip_width = self.tooltip_window.winfo_reqwidth()
        tooltip_height = self.tooltip_window.winfo_reqheight()
        
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()
        
        tooltip_x = x + 15
        tooltip_y = y + 10
        
        if tooltip_x + tooltip_width > screen_width:
            tooltip_x = x - tooltip_width - 15
            
        if tooltip_y + tooltip_height > screen_height:
            tooltip_y = y - tooltip_height - 10
            
        tooltip_x = max(0, min(tooltip_x, screen_width - tooltip_width))
        tooltip_y = max(0, min(tooltip_y, screen_height - tooltip_height))
        
        self.tooltip_window.geometry(f"+{tooltip_x}+{tooltip_y}")
    
    def _hide_tooltip(self, event=None):  # CORREGIDO: agregado event=None
        """Oculta tooltip"""
        if self.after_id:
            self.treeview.after_cancel(self.after_id)
            self.after_id = None
            
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class TreeExplorer:
    def __init__(self, master, app_reference):
        self.master = master
        self.app = app_reference
        self.temp_cache = {}
        self.loading_nodes = set()
        self.expanded_nodes = set()
        self.tooltip = None  # Referencia al tooltip
        
        self.setup_explorer_mode()
        
    def setup_explorer_mode(self):
        """Configura el TreeView existente para modo explorador"""
        tree = self.app.tree
        
        tree.configure(show="tree headings")
        
        # AGREGAR TOOLTIP AL TREE EXPLORER
        self.tooltip = TreeExplorerTooltip(tree, self)
        
        # Eventos principales
        tree.bind("<<TreeviewOpen>>", self.on_node_expand)
        tree.bind("<<TreeviewClose>>", self.on_node_collapse)
        tree.bind('<Right>', self.on_arrow_right)
        tree.bind('<Left>', self.on_arrow_left)
        tree.bind('<Return>', self.on_enter_key)
        tree.bind('<Double-1>', self.on_double_click)
    
    def populate_search_results(self, resultados):
        """Popula el TreeView con resultados de búsqueda"""
        tree = self.app.tree
        
        tree.delete(*tree.get_children())
        self.temp_cache.clear()
        self.loading_nodes.clear()
        self.expanded_nodes.clear()
        
        if not resultados:
            return
        
        for i, carpeta in enumerate(resultados):
            try:
                if isinstance(carpeta, dict):
                    nombre = carpeta.get('name', 'Sin nombre')
                    path = carpeta.get('path', '')
                else:
                    if len(carpeta) >= 3:
                        nombre, ruta_rel, ruta_abs = carpeta[:3]
                        path = ruta_abs
                    else:
                        continue
                
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                icono_metodo = "C"  # Cache por defecto
                
                node_id = tree.insert("", "end", 
                                    text=f"📁 {nombre}", 
                                    values=(icono_metodo, path if isinstance(carpeta, dict) else ruta_rel),
                                    open=False,
                                    tags=(tag,))
                
                if self.has_subdirectories(path):
                    tree.insert(node_id, "end", text="Cargando...", values=("", ""))
                    
            except Exception:
                continue
        
        if hasattr(self.app, 'configurar_scrollbars'):
            self.app.configurar_scrollbars()
        
        if hasattr(self.app, 'ui_callbacks') and hasattr(self.app.ui_callbacks, '_ajustar_columnas_inmediato'):
            self.app.ui_callbacks._ajustar_columnas_inmediato()
    
    def has_subdirectories(self, path):
        """Verifica si una carpeta tiene subdirectorios"""
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return False
                
            for item in os.listdir(path):
                if os.path.isdir(os.path.join(path, item)):
                    return True
            return False
        except (PermissionError, OSError):
            return False
            
    def on_node_expand(self, event):
        """Maneja expansión de nodo"""
        tree = self.app.tree
        selected_items = tree.selection()
        
        if selected_items:
            self.expand_node_async(selected_items[0])
        
    def on_node_collapse(self, event):
        """Maneja colapso de nodo"""
        tree = self.app.tree
        selected_items = tree.selection()
        
        if selected_items:
            node_id = selected_items[0]
            if node_id in self.expanded_nodes:
                self.expanded_nodes.remove(node_id)
            
            if hasattr(self.app, 'ui_callbacks') and hasattr(self.app.ui_callbacks, '_ajustar_columnas_inmediato'):
                self.app.ui_callbacks._ajustar_columnas_inmediato()
        
    def expand_node_async(self, node_id):
        """Expande nodo cargando subdirectorios"""
        if node_id in self.loading_nodes:
            return
            
        tree = self.app.tree
        values = tree.item(node_id, 'values')
        
        if not values or len(values) < 2:
            return
        
        # Obtener path
        if values[0] in ["C", "T", "E"]:
            path = values[1]
        else:
            if values[0] == "Tree":
                path = values[1]
            else:
                ruta_rel = values[1]
                path = self.app.file_manager.obtener_ruta_absoluta(self.app.ruta_carpeta, ruta_rel)
        
        self.expanded_nodes.add(node_id)
        
        if path in self.temp_cache:
            self.populate_children_from_cache(node_id, path)
            
            if hasattr(self.app, 'ui_callbacks') and hasattr(self.app.ui_callbacks, '_ajustar_columnas_inmediato'):
                self.app.ui_callbacks._ajustar_columnas_inmediato()
            return
            
        self.loading_nodes.add(node_id)
        
        children = tree.get_children(node_id)
        if children and tree.item(children[0], 'text') == "Cargando...":
            tree.item(children[0], text="🔄 Cargando subdirectorios...")
            
        def load_subdirectories():
            try:
                subdirs = self.scan_subdirectories(path)
                self.master.after(0, self.on_subdirectories_loaded, node_id, path, subdirs)
            except Exception as e:
                self.master.after(0, self.on_subdirectories_error, node_id, str(e))
                
        threading.Thread(target=load_subdirectories, daemon=True).start()
        
    def scan_subdirectories(self, path):
        """Escanea subdirectorios de una carpeta"""
        subdirs = []
        
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return subdirs
                
            start_time = time.time()
            
            for item in os.listdir(path):
                if time.time() - start_time > 2.0:  # Máximo 2 segundos
                    break
                    
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    try:
                        file_count = len([f for f in os.listdir(item_path) 
                                        if os.path.isfile(os.path.join(item_path, f))])
                        
                        size = self.calculate_folder_size_quick(item_path)
                        
                        subdirs.append({
                            'name': item,
                            'path': item_path,
                            'files': file_count,
                            'size': self.format_size(size)
                        })
                        
                    except (PermissionError, OSError):
                        subdirs.append({
                            'name': f"{item} (Sin acceso)",
                            'path': item_path,
                            'files': 0,
                            'size': "N/A"
                        })
                        
                if len(subdirs) >= 100:
                    subdirs.append({
                        'name': f"... y más carpetas ({len(os.listdir(path)) - len(subdirs)} adicionales)",
                        'path': "",
                        'files': 0,
                        'size': ""
                    })
                    break
                    
        except (PermissionError, OSError):
            pass
            
        return subdirs
        
    def calculate_folder_size_quick(self, path):
        """Calcula tamaño de carpeta de forma rápida"""
        try:
            total_size = 0
            count = 0
            
            for item in os.listdir(path):
                if count >= 50:
                    break
                    
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    total_size += os.path.getsize(item_path)
                    count += 1
                    
            return total_size
        except (PermissionError, OSError):
            return 0
            
    def format_size(self, size_bytes):
        """Formatea tamaño en bytes"""
        if size_bytes == 0:
            return "0 B"
            
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
            
        return f"{size_bytes:.1f} TB"
        
    def on_subdirectories_loaded(self, node_id, path, subdirs):
        """Callback cuando se cargan subdirectorios"""
        tree = self.app.tree
        
        children = tree.get_children(node_id)
        for child in children:
            tree.delete(child)
            
        self.temp_cache[path] = subdirs
        self.populate_children_from_cache(node_id, path)
        self.loading_nodes.discard(node_id)
        
        if hasattr(self.app, 'ui_callbacks') and hasattr(self.app.ui_callbacks, '_ajustar_columnas_inmediato'):
            self.app.ui_callbacks._ajustar_columnas_inmediato()
        
    def populate_children_from_cache(self, node_id, path):
        """Pobla hijos desde cache temporal"""
        tree = self.app.tree
        subdirs = self.temp_cache.get(path, [])
        
        children = tree.get_children(node_id)
        for child in children:
            tree.delete(child)
        
        for i, subdir in enumerate(subdirs):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            if not subdir['path']:
                child_id = tree.insert(node_id, "end",
                                     text=f"📂 {subdir['name']}",
                                     values=("i", ""),
                                     tags=(tag,))
            else:
                child_id = tree.insert(node_id, "end",
                                     text=f"📁 {subdir['name']}",
                                     values=("E", subdir['path']),
                                     tags=(tag,))
                
                if self.has_subdirectories(subdir['path']):
                    tree.insert(child_id, "end", text="Cargando...", values=("", ""))
                    
    def on_subdirectories_error(self, node_id, error_msg):
        """Callback cuando hay error cargando subdirectorios"""
        tree = self.app.tree
        
        children = tree.get_children(node_id)
        for child in children:
            tree.delete(child)
            
        tree.insert(node_id, "end", 
                   text=f"⛔ Error: {error_msg}",
                   values=("X", ""))
                   
        self.loading_nodes.discard(node_id)
        
    def on_arrow_right(self, event):
        """Maneja flecha derecha"""
        tree = self.app.tree
        selected = tree.selection()
        
        if not selected:
            return "break"
            
        node_id = selected[0]
        
        if not tree.item(node_id, 'open'):
            tree.item(node_id, open=True)
            self.expand_node_async(node_id)
        else:
            children = tree.get_children(node_id)
            if children:
                tree.selection_set(children[0])
                tree.focus(children[0])
                tree.see(children[0])
        
        return "break"
                
    def on_arrow_left(self, event):
        """Maneja flecha izquierda"""
        tree = self.app.tree
        selected = tree.selection()
        
        if not selected:
            return "break"
            
        node_id = selected[0]
        
        if tree.item(node_id, 'open'):
            tree.item(node_id, open=False)
            if node_id in self.expanded_nodes:
                self.expanded_nodes.remove(node_id)
            
            if hasattr(self.app, 'ui_callbacks') and hasattr(self.app.ui_callbacks, '_ajustar_columnas_inmediato'):
                self.app.ui_callbacks._ajustar_columnas_inmediato()
        else:
            parent = tree.parent(node_id)
            if parent:
                tree.selection_set(parent)
                tree.focus(parent)
                tree.see(parent)
        
        return "break"
                
    def on_enter_key(self, event):
        """Maneja Enter: toggle expand/collapse"""
        tree = self.app.tree
        selected = tree.selection()
        
        if not selected:
            return "break"
            
        node_id = selected[0]
        
        if tree.item(node_id, 'open'):
            tree.item(node_id, open=False)
            if node_id in self.expanded_nodes:
                self.expanded_nodes.remove(node_id)
            
            if hasattr(self.app, 'ui_callbacks') and hasattr(self.app.ui_callbacks, '_ajustar_columnas_inmediato'):
                self.app.ui_callbacks._ajustar_columnas_inmediato()
        else:
            tree.item(node_id, open=True)
            self.expand_node_async(node_id)
        
        return "break"
            
    def on_double_click(self, event):
        """Maneja doble click: abrir carpeta en explorador"""
        tree = self.app.tree
        selected = tree.selection()
        
        if not selected:
            return
            
        node_id = selected[0]
        values = tree.item(node_id, 'values')
        
        if values and len(values) >= 2:
            if values[0] in ["C", "T", "E"] and values[1]:
                self.app.event_manager.abrir_carpeta_seleccionada()
            elif values[0] not in ["C", "T", "E", "i", "X"] and values[1]:
                self.app.event_manager.abrir_carpeta_seleccionada()
            
    def get_selected_path(self):
        """Obtiene la ruta de la carpeta seleccionada"""
        tree = self.app.tree
        selected = tree.selection()
        
        if not selected:
            return None
            
        node_id = selected[0]
        values = tree.item(node_id, 'values')
        
        if not values or len(values) < 2:
            return None
            
        if values[0] in ["C", "T", "E"]:
            return values[1] if values[1] else None
        else:
            if values[0] == "Tree":
                return values[1] if values[1] else None
            else:
                ruta_rel = values[1]
                if ruta_rel and hasattr(self.app, 'file_manager'):
                    return self.app.file_manager.obtener_ruta_absoluta(self.app.ruta_carpeta, ruta_rel)
                return None
        
    def clear_temp_cache(self):
        """Limpia el cache temporal"""
        self.temp_cache.clear()
        self.loading_nodes.clear()
        self.expanded_nodes.clear()
        
        if hasattr(self.app, 'actualizar_info_carpeta'):
            self.app.actualizar_info_carpeta()
        
    def get_cache_stats(self):
        """Obtiene estadísticas del cache temporal"""
        return {
            'cached_paths': len(self.temp_cache),
            'loading_nodes': len(self.loading_nodes),
            'memory_usage': sum(len(subdirs) for subdirs in self.temp_cache.values())
        }