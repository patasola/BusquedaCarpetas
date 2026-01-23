# src/dynamic_column_manager.py - Callbacks de UI V.4.2 (Refactorizado)
import tkinter as tk
from .results_renderer import ResultsRenderer
from tkinter import messagebox

class UICallbacks:
    def __init__(self, app_instance):
        self.app = app_instance
    
    def _metodo_a_config(self, metodo):
        """Convierte método a letra y configuración de tags"""
        metodo_lower = metodo.lower()
        
        if 'cache' in metodo_lower:
            return "C", 'cache'
        elif 'tradicional' in metodo_lower or 'traditional' in metodo_lower:
            return "T", 'tradicional'
        elif 'tree' in metodo_lower:
            return "E", 'tree'
        else:
            return "?", 'unknown'
    
    def limpiar_resultados(self):
        """Limpia resultados - OPTIMIZADO"""
        try:
            children = self.app.tree.get_children()
            if children:
                self.app.tree.delete(*children)
        except Exception as e:
            print(f"Error limpiando: {e}")
    
    def mostrar_resultados(self, resultados, metodo, tiempo_total):
        """Muestra resultados - DELEGADO A ResultsRenderer"""
        self.limpiar_resultados()
        
        if not getattr(self.app.search_coordinator, 'busqueda_silenciosa', False):
            num_resultados = len(resultados) if resultados else 0
            self.app._finalizar_busqueda_con_historial(metodo, num_resultados)
        
        return ResultsRenderer.render_results(
            self.app, resultados, metodo, tiempo_total,
            actualizar_estado_callback=self.actualizar_estado
        )
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
        self.app.master.after(0, self.habilitar_busqueda)
    
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
            
            # Extraer nombre del texto del árbol
            nombre = text.replace("📁 ", "").replace("📂 ", "")
            
            if len(values) >= 2:
                letra = values[0]
                # Convertir letra a método
                metodo_map = {"C": "Cache", "T": "Tradicional", "E": "Tree"}
                metodo_original = metodo_map.get(letra, "Desconocido")
                
                return {
                    'metodo': metodo_original,
                    'nombre': nombre,
                    'ruta_rel': values[1]
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
