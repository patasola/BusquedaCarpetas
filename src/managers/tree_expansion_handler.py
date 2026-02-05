# src/tree_expansion_handler.py - Manejador de expansión de subcarpetas en resultados
import os
from datetime import datetime

class TreeExpansionHandler:
    """Maneja la expansión de subcarpetas en el TreeView de resultados"""
    
    def __init__(self, app):
        self.app = app
        self.loaded_items = set()  # Items ya cargados
        self.loading_items = set()  # Items en proceso de carga
    
    def configure_tree_expansion(self):
        """Configura el evento de expansión en el TreeView"""
        if hasattr(self.app, 'tree') and self.app.tree:
            # Bind del evento de expansión
            self.app.tree.bind('<<TreeviewOpen>>', self.on_tree_expand)
            self.app.tree.bind('\u003c\u003cTreeviewClose\u003e\u003e', self.on_tree_collapse)
            print("[DEBUG] Evento de expansión configurado en TreeView")
    
    def on_tree_expand(self, event):
        """Maneja el evento cuando se expande un nodo"""
        try:
            tree = event.widget
            item = tree.focus()
            
            if not item or item in self.loaded_items or item in self.loading_items:
                return
            
            self.loading_items.add(item)
            
            # Obtener ruta del item
            values = tree.item(item, 'values')
            if not values or len(values) < 2:
                self.loading_items.discard(item)
                return
            
            # DETERMINAR RUTA ABSOLUTA (Prioridad values[2] -> Metadata oculta)
            if len(values) >= 3 and os.path.isabs(values[2]):
                ruta = values[2]
            else:
                # Fallback: Resolver desde la segunda columna (values[1])
                ruta_info = values[1]
                if os.path.isabs(ruta_info):
                    ruta = ruta_info
                else:
                    ruta_base = getattr(self.app, 'ruta_carpeta', '')
                    ruta = os.path.join(ruta_base, ruta_info) if ruta_base else ruta_info
            
            if not os.path.exists(ruta) or not os.path.isdir(ruta):
                print(f"[DEBUG] Ruta inválida para expansión: {ruta}")
                self.loading_items.discard(item)
                return
            
            # Eliminar todos los nodos hijos existentes (dummies o espacios)
            children = tree.get_children(item)
            for child in children:
                tree.delete(child)
            
            # VERIFICACIÓN REAL POST-CLIC (Lazy Detection)
            if not self._tiene_subcarpetas(ruta):
                # No tiene subcarpetas - quitar el triangulito (dummy) y salir
                self.loaded_items.add(item)
                self.loading_items.discard(item)
                return
            
            # Cargar subcarpetas
            self.load_subdirectories(item, ruta)
            
            self.loaded_items.add(item)
            self.loading_items.discard(item)
            
        except Exception as e:
            print(f"[ERROR] Error en expansión: {e}")
            if item in self.loading_items:
                self.loading_items.discard(item)
    
    def load_subdirectories(self, parent_item, parent_path):
        """Carga las subcarpetas de un directorio"""
        try:
            items = []
            
            # Listar contenido del directorio
            for entry in os.scandir(parent_path):
                try:
                    if entry.is_dir():
                        nombre = entry.name
                        ruta_completa = entry.path
                        
                        try:
                            fecha_mod = datetime.fromtimestamp(
                                entry.stat().st_mtime
                            ).strftime("%d/%m/%Y %H:%M")
                        except:
                            fecha_mod = "N/A"
                        
                        items.append((nombre, ruta_completa, fecha_mod))
                except PermissionError:
                    continue
                except Exception:
                    continue
            
            # Ordenar alfabéticamente
            items.sort(key=lambda x: x[0].lower())
            
            # Insertar en el TreeView
            for i, (nombre, ruta, fecha) in enumerate(items):
                # Determinar método (mantener el del padre)
                parent_values = self.app.tree.item(parent_item, 'values')
                metodo = parent_values[0] if parent_values else "E"
                
                # Determinar tag para filas alternadas
                existing_children = len(self.app.tree.get_children(parent_item))
                tag = 'evenrow' if (existing_children + i) % 2 == 0 else 'oddrow'
                
                # Insertar subcarpeta
                child_item = self.app.tree.insert(
                    parent_item,
                    'end',
                    text=f"📂 {nombre}",
                    values=(metodo, ruta),
                    tags=(tag,)
                )
                
                # Agregar nodo dummy si tiene subcarpetas (Verificación real para subniveles)
                if self._tiene_subcarpetas(ruta):
                    self.app.tree.insert(child_item, 'end', text='Cargando...', values=('', ''))
            
            print(f"[DEBUG] Cargadas {len(items)} subcarpetas de: {parent_path}")
            
        except PermissionError:
            print(f"[WARN] Sin permisos para: {parent_path}")
        except Exception as e:
            print(f"[ERROR] Error cargando subcarpetas: {e}")
    
    def _tiene_subcarpetas(self, ruta):
        """Verifica si una carpeta tiene subcarpetas"""
        try:
            if not os.path.exists(ruta) or not os.path.isdir(ruta):
                return False
            
            for entry in os.scandir(ruta):
                if entry.is_dir():
                    return True
            return False
        except:
            return False
    
    def clear_cache(self):
        """Limpia el caché de items cargados"""
        self.loaded_items.clear()
        self.loading_items.clear()
        print("[DEBUG] Caché de expansión limpiado")
    
    def on_tree_collapse(self, event):
        """Maneja el evento cuando se colapsa un nodo"""
        try:
            if hasattr(self.app, 'ui_manager'):
                self.app.ui_manager._ajustar_columnas_inmediato()
        except Exception as e:
            print(f"[ERROR] Error en collapse: {e}")