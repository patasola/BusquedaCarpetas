# src/ui_callbacks.py - Callbacks de UI V.4.1 (Compatible)
import tkinter as tk
from tkinter import messagebox

class UICallbacks:
    def __init__(self, app_instance):
        self.app = app_instance
    
    def limpiar_resultados(self):
        """Limpia resultados del TreeView"""
        try:
            for item in self.app.tree.get_children():
                self.app.tree.delete(item)
        except Exception as e:
            print(f"ERROR limpiando resultados: {e}")
    
    def mostrar_resultados(self, resultados, metodo, tiempo_total):
        """Muestra resultados en TreeView V.4.0 (fallback)"""
        self.limpiar_resultados()
        
        # CORREGIDO: Solo agregar al historial si NO es búsqueda silenciosa
        if not getattr(self.app.search_coordinator, 'busqueda_silenciosa', False):
            num_resultados = len(resultados) if resultados else 0
            self.app._finalizar_busqueda_con_historial(metodo, num_resultados)
        
        if not resultados:
            if metodo == "Cache":
                mensaje = f"No se encontraron resultados en cache ({tiempo_total:.3f}s)"
            elif metodo == "Tradicional":
                mensaje = f"No se encontraron resultados en la búsqueda tradicional ({tiempo_total:.3f}s)"
            else:
                mensaje = f"No se encontraron resultados ({metodo}, {tiempo_total:.3f}s)"
            
            self.actualizar_estado(mensaje)
            return
        
        try:
            # CORREGIDO: Verificar si tree explorer está activo
            if hasattr(self.app, 'tree_explorer') and self.app.tree_explorer:
                # Usar tree explorer para mostrar resultados
                formatted_results = []
                for resultado in resultados:
                    if isinstance(resultado, tuple) and len(resultado) >= 3:
                        nombre, ruta_rel, ruta_abs = resultado[:3]
                        formatted_results.append({
                            'name': nombre,
                            'path': ruta_abs,
                            'files': 0,
                            'size': '0 B'
                        })
                    elif isinstance(resultado, dict):
                        formatted_results.append(resultado)
                
                # Mostrar usando tree explorer
                self.app.tree_explorer.populate_search_results(formatted_results)
            else:
                # FALLBACK: Insertar resultados sin columna "Nombre" en TreeView normal
                for i, resultado in enumerate(resultados):
                    # Determinar el tag para filas alternadas
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                    
                    # Extraer datos según formato
                    if isinstance(resultado, tuple) and len(resultado) >= 3:
                        nombre, ruta_rel, ruta_abs = resultado[:3]
                    elif isinstance(resultado, dict):
                        nombre = resultado.get('name', 'Sin nombre')
                        ruta_rel = resultado.get('path', '')
                        ruta_abs = resultado.get('path', '')
                    else:
                        continue
                    
                    # CORREGIDO: Solo 2 columnas (Método, Ruta) - el nombre va en la columna del árbol (#0)
                    item_id = self.app.tree.insert("", "end", 
                                                  text=f"📁 {nombre}",  # Nombre en columna del árbol
                                                  values=(metodo, ruta_rel),  # Solo 2 columnas
                                                  tags=(tag,))
            
            mensaje = f"✅ Encontrados {len(resultados)} resultados en {tiempo_total:.3f}s ({metodo})"
            self.actualizar_estado(mensaje)
            
            # Configurar scrollbars después de insertar datos
            self.app.configurar_scrollbars()
            
        except Exception as e:
            self.actualizar_estado(f"Error mostrando resultados: {str(e)}")
    
    def mostrar_resultados_async(self, resultados, metodo, tiempo_total):
        """Versión asíncrona de mostrar_resultados"""
        self.app.master.after(0, lambda: self.mostrar_resultados(resultados, metodo, tiempo_total))
    
    # Gestión de estado
    def actualizar_estado(self, mensaje):
        """Actualiza mensaje en barra de estado"""
        try:
            self.app.label_estado.config(text=mensaje)
        except Exception as e:
            print(f"ERROR actualizando estado: {e}")
    
    def actualizar_estado_async(self, mensaje):
        """Versión asíncrona de actualizar_estado"""
        self.app.master.after(0, lambda: self.actualizar_estado(mensaje))
    
    # Gestión de botones
    def habilitar_busqueda(self):
        """Habilita botones de búsqueda"""
        try:
            self.app.btn_buscar.config(state=tk.NORMAL)
            self.app.btn_cancelar.config(state=tk.DISABLED)
        except Exception as e:
            print(f"ERROR habilitando botones: {e}")
    
    def deshabilitar_busqueda(self):
        """Deshabilita botones de búsqueda"""
        try:
            self.app.btn_buscar.config(state=tk.DISABLED)
            self.app.btn_cancelar.config(state=tk.NORMAL)
        except Exception as e:
            print(f"ERROR deshabilitando botones: {e}")
    
    def finalizar_busqueda_inmediata(self):
        """Finaliza búsqueda inmediatamente"""
        self.habilitar_busqueda()
    
    def finalizar_busqueda_async(self):
        """Versión asíncrona de finalizar_busqueda"""
        def finalizar():
            self.habilitar_busqueda()
        
        self.app.master.after(0, finalizar)
    
    # Diálogos de usuario
    def mostrar_advertencia(self, mensaje):
        """Muestra diálogo de advertencia"""
        try:
            messagebox.showwarning("Advertencia", mensaje)
        except Exception as e:
            print(f"ERROR mostrando advertencia: {e}")
    
    def mostrar_error(self, mensaje):
        """Muestra diálogo de error"""
        try:
            messagebox.showerror("Error", mensaje)
        except Exception as e:
            print(f"ERROR mostrando error: {e}")
    
    def mostrar_info(self, titulo, mensaje):
        """Muestra diálogo informativo"""
        try:
            messagebox.showinfo(titulo, mensaje)
        except Exception as e:
            print(f"ERROR mostrando info: {e}")
    
    # Operaciones delegadas
    def construir_cache(self):
        """Inicia construcción de cache"""
        try:
            self.app.search_coordinator.construir_cache_automatico()
        except Exception as e:
            print(f"ERROR iniciando construcción cache: {e}")
    
    # Información de estado
    def obtener_seleccion_tabla(self):
        """Obtiene información del elemento seleccionado"""
        try:
            selection = self.app.tree.selection()
            if not selection:
                return None
            
            item = self.app.tree.item(selection[0])
            values = item['values']
            text = item['text']
            
            # CORREGIDO: Extraer nombre del texto del árbol y ajustar para nueva estructura
            nombre = text.replace("📁 ", "").replace("📂 ", "")
            
            if len(values) >= 2:
                return {
                    'metodo': values[0],
                    'nombre': nombre,
                    'ruta_rel': values[1]  # Ajustado para nueva estructura sin columna Nombre
                }
            return None
            
        except Exception as e:
            print(f"ERROR obteniendo selección: {e}")
            return None
    
    def hay_seleccion(self):
        """Verifica si hay algún elemento seleccionado"""
        try:
            return len(self.app.tree.selection()) > 0
        except:
            return False