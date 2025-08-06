import tkinter as tk
from tkinter import messagebox

class UICallbacks:
    """
    Interface optimizada entre managers y UI para minimizar movimientos.
    Responsabilidades:
    - Actualizar elementos UI con mínimo impacto visual
    - Manejar callbacks async de forma suave
    - Evitar redimensionamientos innecesarios
    """
    
    def __init__(self, app_instance):
        self.app = app_instance
        print("DEBUG: UICallbacks inicializado con optimizaciones de estabilidad")
    
    # ===== GESTIÓN DE RESULTADOS OPTIMIZADA =====
    
    def limpiar_resultados(self):
        """Limpia resultados sin afectar layout de tabla"""
        try:
            for item in self.app.tree.get_children():
                self.app.tree.delete(item)
            print("DEBUG: Resultados limpiados")
        except Exception as e:
            print(f"ERROR limpiando resultados: {e}")
    
    def mostrar_resultados(self, resultados, metodo, tiempo_total):
        """
        Muestra resultados MINIMIZANDO cambios de layout
        """
        print(f"DEBUG: Mostrando {len(resultados)} resultados ({metodo}) - modo estable")
        
        self.limpiar_resultados()
        
        if not resultados:
            # Mensaje específico según el método
            if metodo == "Cache":
                mensaje = f"No se encontraron resultados en cache ({tiempo_total:.3f}s)"
            elif metodo == "Tradicional":
                mensaje = f"No se encontraron resultados en la búsqueda tradicional ({tiempo_total:.3f}s)"
            else:
                mensaje = f"No se encontraron resultados ({metodo}, {tiempo_total:.3f}s)"
            
            self.actualizar_estado(mensaje)
            print(f"DEBUG: {mensaje}")
            
            # Para búsqueda tradicional, ocultar progreso gradualmente
            if metodo == "Tradicional":
                self.app.master.after(1500, self.app.progress_manager.ocultar)
            
            return
        
        # Insertar resultados SIN autoajustes agresivos
        try:
            for nombre, ruta_rel, ruta_abs in resultados:
                self.app.tree.insert("", "end", values=(metodo, nombre, ruta_rel))
            
            # Actualización MÍNIMA de UI
            self._actualizar_ui_minimal()
            
            # Mensaje de estado
            mensaje = f"Encontrados {len(resultados)} resultados en {tiempo_total:.3f}s ({metodo})"
            self.actualizar_estado(mensaje)
            print(f"DEBUG: {mensaje}")
            
        except Exception as e:
            print(f"ERROR mostrando resultados: {e}")
            self.actualizar_estado(f"Error mostrando resultados: {str(e)}")
    
    def mostrar_resultados_async(self, resultados, metodo, tiempo_total):
        """Versión async optimizada"""
        self.app.master.after(0, lambda: self.mostrar_resultados(resultados, metodo, tiempo_total))
    
    # ===== GESTIÓN DE ESTADO =====
    
    def actualizar_estado(self, mensaje):
        """Actualiza estado sin afectar layout"""
        try:
            self.app.label_estado.config(text=mensaje)
            # Actualización mínima, sin update_idletasks excesivo
            print(f"DEBUG: Estado: {mensaje}")
        except Exception as e:
            print(f"ERROR actualizando estado: {e}")
    
    def actualizar_estado_async(self, mensaje):
        """Versión async"""
        self.app.master.after(0, lambda: self.actualizar_estado(mensaje))
    
    # ===== GESTIÓN DE PROGRESO =====
    
    def actualizar_progreso(self, procesados, total):
        """Actualiza progreso de forma suave"""
        try:
            self.app.progress_manager.actualizar(procesados, total)
        except Exception as e:
            print(f"ERROR actualizando progreso: {e}")
    
    def actualizar_progreso_async(self, procesados, total):
        """Versión async con actualización garantizada"""
        # Actualizar SIEMPRE, sin throttling para evitar inconsistencias
        self.app.master.after(0, lambda: self.actualizar_progreso(procesados, total))
    
    # ===== GESTIÓN DE BOTONES =====
    
    def habilitar_busqueda(self):
        """Habilita botones sin efectos visuales"""
        try:
            self.app.btn_buscar.config(state=tk.NORMAL)
            self.app.btn_cancelar.config(state=tk.DISABLED)
            print("DEBUG: Botones habilitados")
        except Exception as e:
            print(f"ERROR habilitando botones: {e}")
    
    def deshabilitar_busqueda(self):
        """Deshabilita botones sin efectos visuales"""
        try:
            self.app.btn_buscar.config(state=tk.DISABLED)
            self.app.btn_cancelar.config(state=tk.NORMAL)
            print("DEBUG: Botones deshabilitados")
        except Exception as e:
            print(f"ERROR deshabilitando botones: {e}")
    
    def finalizar_busqueda_inmediata(self):
        """Finaliza búsqueda cache (inmediata)"""
        self.habilitar_busqueda()
    
    def finalizar_busqueda_async(self):
        """Finaliza búsqueda tradicional con transición suave"""
        def finalizar():
            self.habilitar_busqueda()
            # Ocultar progreso con delay más largo para estabilidad
            self.app.master.after(2000, self.app.progress_manager.ocultar)
        
        self.app.master.after(0, finalizar)
    
    # ===== DIÁLOGOS DE USUARIO =====
    
    def mostrar_advertencia(self, mensaje):
        """Muestra advertencia"""
        try:
            print(f"DEBUG: Advertencia: {mensaje}")
            messagebox.showwarning("Advertencia", mensaje)
        except Exception as e:
            print(f"ERROR mostrando advertencia: {e}")
    
    def mostrar_error(self, mensaje):
        """Muestra error"""
        try:
            print(f"DEBUG: Error: {mensaje}")
            messagebox.showerror("Error", mensaje)
        except Exception as e:
            print(f"ERROR mostrando error: {e}")
    
    def mostrar_info(self, titulo, mensaje):
        """Muestra información"""
        try:
            print(f"DEBUG: Info: {titulo}")
            messagebox.showinfo(titulo, mensaje)
        except Exception as e:
            print(f"ERROR mostrando info: {e}")
    
    # ===== OPERACIONES DELEGADAS =====
    
    def construir_cache(self):
        """Inicia construcción de cache"""
        try:
            print("DEBUG: Iniciando construcción de cache")
            self.app.construir_cache_automatico()
        except Exception as e:
            print(f"ERROR iniciando construcción cache: {e}")
    
    # ===== UTILIDADES OPTIMIZADAS =====
    
    def _actualizar_ui_minimal(self):
        """Actualización mínima de UI para evitar movimientos"""
        try:
            # Solo actualizar scrollbars si realmente es necesario
            children_count = len(self.app.tree.get_children())
            
            # Actualización con delay para evitar "saltos"
            if children_count > 0:
                self.app.tree.after(300, self.app.tree.update_scrollbars)
            
            print("DEBUG: UI actualizada de forma minimal")
        except Exception as e:
            print(f"ERROR en actualización minimal: {e}")
    
    # ===== INFORMACIÓN DE ESTADO =====
    
    def obtener_seleccion_tabla(self):
        """Obtiene selección de tabla"""
        try:
            selection = self.app.tree.selection()
            if not selection:
                return None
            
            item = self.app.tree.item(selection[0])
            values = item['values']
            
            if len(values) >= 3:
                return {
                    'metodo': values[0],
                    'nombre': values[1],
                    'ruta_rel': values[2]
                }
            return None
            
        except Exception as e:
            print(f"ERROR obteniendo selección: {e}")
            return None
    
    def hay_seleccion(self):
        """Verifica si hay selección en tabla"""
        try:
            return len(self.app.tree.selection()) > 0
        except:
            return False