# src/tree_explorer.py - Explorador de Árbol V.4.1 (Debug y Correcciones)
import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import time
from datetime import datetime

class TreeExplorer:
    def __init__(self, master, app_reference):
        self.master = master
        self.app = app_reference
        self.temp_cache = {}  # Cache temporal para subdirectorios expandidos
        self.loading_nodes = set()  # Nodos que están cargando
        self.expanded_nodes = set()  # Nodos que ya fueron expandidos
        
        # Configurar el TreeView existente para modo explorador
        self.setup_explorer_mode()
        
    def setup_explorer_mode(self):
        """Configura el TreeView existente para modo explorador"""
        tree = self.app.tree
        
        # Configurar para mostrar estructura de árbol
        tree.configure(show="tree headings")
        
        # Bind eventos para expansión
        tree.bind("<<TreeviewOpen>>", self.on_node_expand)
        tree.bind("<<TreeviewClose>>", self.on_node_collapse)
        
        # Navegación con flechas
        tree.bind('<Right>', self.on_arrow_right)
        tree.bind('<Left>', self.on_arrow_left)
        tree.bind('<Return>', self.on_enter_key)
        
        # Doble click para abrir carpeta
        tree.bind('<Double-1>', self.on_double_click)
        
    def populate_search_results(self, resultados):
        """Popula el TreeView con resultados de búsqueda como nodos expandibles"""
        tree = self.app.tree
        
        # Limpiar resultados anteriores y cache
        tree.delete(*tree.get_children())
        self.temp_cache.clear()
        self.loading_nodes.clear()
        self.expanded_nodes.clear()  # NUEVO: Limpiar nodos expandidos
        
        # Si no hay resultados, mantener TreeView vacío
        if not resultados:
            return
        
        # Insertar cada resultado como nodo expandible
        for i, carpeta in enumerate(resultados):
            try:
                # Determinar formato de datos
                if isinstance(carpeta, dict):
                    # Formato V.4.1
                    nombre = carpeta.get('name', 'Sin nombre')
                    path = carpeta.get('path', '')
                else:
                    # Formato V.4.0: (nombre, ruta_rel, ruta_abs)
                    if len(carpeta) >= 3:
                        nombre, ruta_rel, ruta_abs = carpeta[:3]
                        path = ruta_abs
                    else:
                        continue
                
                # Determinar tag para filas alternadas
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                
                # Insertar nodo
                node_id = tree.insert("", "end", 
                                    text=f"📁 {nombre}", 
                                    values=("Tree", path if isinstance(carpeta, dict) else ruta_rel),
                                    open=False,
                                    tags=(tag,))
                
                # Verificar si tiene subdirectorios para mostrar triángulo
                if self.has_subdirectories(path):
                    # Insertar placeholder para mostrar triángulo
                    tree.insert(node_id, "end", text="Cargando...", values=("", ""))
                    
            except Exception as e:
                continue  # Saltar elementos con errores
        
        # Configurar scrollbars después de poblar
        if hasattr(self.app, 'configurar_scrollbars'):
            self.app.configurar_scrollbars()
        
    def has_subdirectories(self, path):
        """Verifica rápidamente si una carpeta tiene subdirectorios"""
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return False
                
            # Verificación rápida: buscar primer subdirectorio
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    return True
            return False
        except (PermissionError, OSError):
            return False
            
    def on_node_expand(self, event):
        """Maneja la expansión de un nodo"""
        tree = self.app.tree
        selected_items = tree.selection()
        
        if not selected_items:
            return
            
        node_id = selected_items[0]
        self.expand_node_async(node_id)
        
    def on_node_collapse(self, event):
        """Maneja el colapso de un nodo"""
        tree = self.app.tree
        selected_items = tree.selection()
        
        if not selected_items:
            return
            
        node_id = selected_items[0]
        
        # NUEVO: Marcar que este nodo ya no está expandido
        if node_id in self.expanded_nodes:
            self.expanded_nodes.remove(node_id)
        
    def expand_node_async(self, node_id):
        """Expande un nodo cargando subdirectorios de forma asíncrona"""
        # NUEVO: Verificar si ya fue expandido antes
        if node_id in self.expanded_nodes:
            return  # Ya fue expandido, no hacer nada
            
        if node_id in self.loading_nodes:
            return  # Ya está cargando
            
        tree = self.app.tree
        values = tree.item(node_id, 'values')
        
        if not values or len(values) < 2:
            return
        
        # Obtener path según el formato
        if values[0] == "Tree":  # Formato tree explorer
            path = values[1]  # La ruta está en la columna 1
        else:
            # Formato V.4.0: construir ruta absoluta
            ruta_rel = values[1]
            path = self.app.file_manager.obtener_ruta_absoluta(self.app.ruta_carpeta, ruta_rel)
        
        # Marcar como expandido ANTES de cargar
        self.expanded_nodes.add(node_id)
        
        # Verificar si ya está en cache temporal
        if path in self.temp_cache:
            self.populate_children_from_cache(node_id, path)
            return
            
        # Marcar como cargando
        self.loading_nodes.add(node_id)
        
        # Mostrar indicador de carga
        children = tree.get_children(node_id)
        if children and tree.item(children[0], 'text') == "Cargando...":
            tree.item(children[0], text="🔄 Cargando subdirectorios...")
            
        # Cargar en thread separado
        def load_subdirectories():
            try:
                subdirs = self.scan_subdirectories(path)
                # Actualizar en thread principal
                self.master.after(0, self.on_subdirectories_loaded, node_id, path, subdirs)
            except Exception as e:
                self.master.after(0, self.on_subdirectories_error, node_id, str(e))
                
        thread = threading.Thread(target=load_subdirectories, daemon=True)
        thread.start()
        
    def scan_subdirectories(self, path):
        """Escanea subdirectorios de una carpeta"""
        subdirs = []
        
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return subdirs
                
            start_time = time.time()
            
            for item in os.listdir(path):
                # Límite de tiempo para evitar bloqueos
                if time.time() - start_time > 2.0:  # Máximo 2 segundos
                    break
                    
                item_path = os.path.join(path, item)
                
                if os.path.isdir(item_path):
                    try:
                        # Obtener información básica
                        file_count = len([f for f in os.listdir(item_path) 
                                        if os.path.isfile(os.path.join(item_path, f))])
                        
                        # Calcular tamaño (limitado para rendimiento)
                        size = self.calculate_folder_size_quick(item_path)
                        
                        subdirs.append({
                            'name': item,
                            'path': item_path,
                            'files': file_count,
                            'size': self.format_size(size)
                        })
                        
                    except (PermissionError, OSError):
                        # Agregar carpeta sin acceso
                        subdirs.append({
                            'name': f"{item} (Sin acceso)",
                            'path': item_path,
                            'files': 0,
                            'size': "N/A"
                        })
                        
                # Límite de subdirectorios por rendimiento
                if len(subdirs) >= 100:
                    subdirs.append({
                        'name': f"... y más carpetas ({len(os.listdir(path)) - len(subdirs)} adicionales)",
                        'path': "",
                        'files': 0,
                        'size': ""
                    })
                    break
                    
        except (PermissionError, OSError) as e:
            pass  # Error silencioso
            
        return subdirs
        
    def calculate_folder_size_quick(self, path):
        """Calcula tamaño de carpeta de forma rápida"""
        try:
            total_size = 0
            count = 0
            
            for item in os.listdir(path):
                if count >= 50:  # Límite para rendimiento
                    break
                    
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    total_size += os.path.getsize(item_path)
                    count += 1
                    
            return total_size
        except (PermissionError, OSError):
            return 0
            
    def format_size(self, size_bytes):
        """Formatea tamaño en bytes a formato legible"""
        if size_bytes == 0:
            return "0 B"
            
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
            
        return f"{size_bytes:.1f} TB"
        
    def on_subdirectories_loaded(self, node_id, path, subdirs):
        """Callback cuando se cargan los subdirectorios"""
        tree = self.app.tree
        
        # SIEMPRE limpiar hijos existentes antes de poblar
        children = tree.get_children(node_id)
        for child in children:
            tree.delete(child)
            
        # Guardar en cache temporal
        self.temp_cache[path] = subdirs
        
        # Poblar hijos
        self.populate_children_from_cache(node_id, path)
        
        # Remover de loading
        self.loading_nodes.discard(node_id)
        
    def populate_children_from_cache(self, node_id, path):
        """Popla hijos desde cache temporal"""
        tree = self.app.tree
        subdirs = self.temp_cache.get(path, [])
        
        # SIEMPRE limpiar hijos existentes antes de poblar
        children = tree.get_children(node_id)
        for child in children:
            tree.delete(child)
        
        for i, subdir in enumerate(subdirs):
            # Tag para filas alternadas
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            if not subdir['path']:  # Entrada especial "... y más"
                child_id = tree.insert(node_id, "end",
                                     text=f"📂 {subdir['name']}",
                                     values=("Info", ""),
                                     tags=(tag,))
            else:
                child_id = tree.insert(node_id, "end",
                                     text=f"📁 {subdir['name']}",
                                     values=("Tree", subdir['path']),
                                     tags=(tag,))
                
                # Si este subdirectorio también tiene hijos, agregar placeholder
                if self.has_subdirectories(subdir['path']):
                    tree.insert(child_id, "end", text="Cargando...", values=("", ""))
                    
    def on_subdirectories_error(self, node_id, error_msg):
        """Callback cuando hay error cargando subdirectorios"""
        tree = self.app.tree
        
        # Remover indicador de carga
        children = tree.get_children(node_id)
        for child in children:
            tree.delete(child)
            
        # Mostrar error
        tree.insert(node_id, "end", 
                   text=f"❌ Error: {error_msg}",
                   values=("Error", ""))
                   
        # Remover de loading
        self.loading_nodes.discard(node_id)
        
    def on_arrow_right(self, event):
        """Maneja flecha derecha: expandir o navegar a hijo"""
        tree = self.app.tree
        selected = tree.selection()
        
        if not selected:
            return "break"
            
        node_id = selected[0]
        
        # Si está cerrado, expandir
        if not tree.item(node_id, 'open'):
            tree.item(node_id, open=True)
            self.expand_node_async(node_id)
        else:
            # Si está abierto, ir al primer hijo
            children = tree.get_children(node_id)
            if children:
                tree.selection_set(children[0])
                tree.focus(children[0])
                tree.see(children[0])
        
        return "break"
                
    def on_arrow_left(self, event):
        """Maneja flecha izquierda: colapsar o ir al padre"""
        tree = self.app.tree
        selected = tree.selection()
        
        if not selected:
            return "break"
            
        node_id = selected[0]
        
        # Si está abierto, colapsar
        if tree.item(node_id, 'open'):
            tree.item(node_id, open=False)
            # NUEVO: Remover de nodos expandidos al colapsar manualmente
            if node_id in self.expanded_nodes:
                self.expanded_nodes.remove(node_id)
        else:
            # Si está cerrado, ir al padre
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
            # NUEVO: Remover de nodos expandidos al colapsar
            if node_id in self.expanded_nodes:
                self.expanded_nodes.remove(node_id)
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
            # Verificar que tiene ruta válida
            if values[0] == "Tree" and values[1]:  # Formato tree explorer
                # Delegar a la funcionalidad V.4.0 existente
                self.app.event_manager.abrir_carpeta_seleccionada()
            elif values[0] != "Tree" and values[1]:  # Formato V.4.0
                # Delegar a la funcionalidad V.4.0 existente
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
            
        if values[0] == "Tree":  # Formato tree explorer
            return values[1] if values[1] else None
        else:  # Formato V.4.0
            # Construir ruta absoluta
            ruta_rel = values[1]
            if ruta_rel and hasattr(self.app, 'file_manager'):
                return self.app.file_manager.obtener_ruta_absoluta(self.app.ruta_carpeta, ruta_rel)
            return None
        
    def clear_temp_cache(self):
        """Limpia el cache temporal"""
        self.temp_cache.clear()
        self.loading_nodes.clear()
        self.expanded_nodes.clear()  # NUEVO: Limpiar nodos expandidos
        
        # Actualizar barra de información
        if hasattr(self.app, 'actualizar_info_carpeta'):
            self.app.actualizar_info_carpeta()
        
    def get_cache_stats(self):
        """Obtiene estadísticas del cache temporal"""
        return {
            'cached_paths': len(self.temp_cache),
            'loading_nodes': len(self.loading_nodes),
            'memory_usage': sum(len(subdirs) for subdirs in self.temp_cache.values())
        }
    
    def _get_file_count_quick(self, path):
        """Obtiene conteo rápido de archivos"""
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return 0
            return len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
        except (PermissionError, OSError):
            return 0
            
    def _get_folder_size_quick(self, path):
        """Obtiene tamaño rápido de carpeta"""
        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return "0 B"
                
            total_size = 0
            count = 0
            
            for item in os.listdir(path):
                if count >= 20:  # Límite para velocidad
                    break
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    total_size += os.path.getsize(item_path)
                    count += 1
                    
            return self.format_size(total_size)
        except (PermissionError, OSError):
            return "N/A"