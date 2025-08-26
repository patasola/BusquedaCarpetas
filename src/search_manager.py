# src/search_manager.py - Gestión de Búsquedas V.3.6
import threading
import time

class SearchManager:
    def __init__(self, cache_manager, search_engine, progress_manager, ui_callbacks):
        self.cache_manager = cache_manager
        self.search_engine = search_engine
        self.ui_callbacks = ui_callbacks
        
        self.tiempo_inicio = 0
        self.ultimo_criterio = ""
        self.resultados = []
        self.busqueda_activa = False
    
    def buscar(self, criterio):
        if not self._validar_busqueda(criterio):
            return False
            
        self._preparar_busqueda(criterio)
        
        if self._buscar_en_cache(criterio):
            return True
            
        return self._iniciar_busqueda_tradicional(criterio)
    
    def _validar_busqueda(self, criterio):
        if not criterio:
            self.ui_callbacks.mostrar_advertencia("Ingrese un criterio de búsqueda")
            return False
            
        if not self.cache_manager.ruta_base:
            self.ui_callbacks.mostrar_advertencia("Seleccione una ruta de búsqueda primero")
            return False
            
        return True
    
    def _preparar_busqueda(self, criterio):
        self.ultimo_criterio = criterio
        self.tiempo_inicio = time.time()
        self.busqueda_activa = True
        
        self.ui_callbacks.limpiar_resultados()
        self.ui_callbacks.actualizar_estado("Buscando...")
    
    def _buscar_en_cache(self, criterio):
        if not self.cache_manager.cache.valido:
            self.ui_callbacks.actualizar_estado("Cache no disponible. Construyendo cache...")
            self.ui_callbacks.construir_cache()
            return True
            
        resultados = self.cache_manager.buscar_en_cache(criterio)
        
        if resultados is not None:
            if len(resultados) > 0:
                self._finalizar_busqueda_exitosa(resultados, "Cache")
                return True
            else:
                tiempo_cache = time.time() - self.tiempo_inicio
                self.ui_callbacks.actualizar_estado(f"Cache sin resultados ({tiempo_cache:.3f}s), buscando tradicionalmente...")
                return False
        
        self.ui_callbacks.actualizar_estado("Error en cache, buscando en directorios...")
        return False
    
    def _iniciar_busqueda_tradicional(self, criterio):
        # Progreso en barra de estado en lugar de progress_manager
        self.ui_callbacks.actualizar_estado("Búsqueda tradicional iniciada... 0%")
        
        def callback_progreso(procesados, total):
            if total > 0:
                porcentaje = int((procesados / total) * 100)
                if porcentaje % 5 == 0 or procesados >= total:
                    mensaje = f"Búsqueda tradicional... {porcentaje}%"
                    self.ui_callbacks.actualizar_estado_async(mensaje)
        
        self.search_engine.callback_progreso = callback_progreso
        
        threading.Thread(
            target=self._ejecutar_busqueda_tradicional,
            args=(criterio,),
            daemon=True
        ).start()
        
        return True
    
    def _ejecutar_busqueda_tradicional(self, criterio):
        try:
            resultados = self.search_engine.buscar_tradicional(criterio)
            
            if resultados is not None:
                self.resultados = resultados
                tiempo_total = time.time() - self.tiempo_inicio
                
                def finalizar_busqueda():
                    if len(resultados) > 0:
                        self.ui_callbacks.mostrar_resultados_async(
                            resultados, "Tradicional", tiempo_total
                        )
                    else:
                        self.ui_callbacks.mostrar_resultados_async(
                            [], "Tradicional", tiempo_total
                        )
                
                self.ui_callbacks.app.master.after(0, finalizar_busqueda)
                
            else:
                self.ui_callbacks.actualizar_estado_async("Error en la búsqueda tradicional")
                
        except Exception as e:
            self.ui_callbacks.actualizar_estado_async(f"Error en búsqueda tradicional: {str(e)}")
            
        finally:
            self.ui_callbacks.finalizar_busqueda_async()
            self.busqueda_activa = False
    
    def _finalizar_busqueda_exitosa(self, resultados, metodo):
        tiempo_total = time.time() - self.tiempo_inicio
        self.resultados = resultados
        self.busqueda_activa = False
        
        self.ui_callbacks.mostrar_resultados(resultados, metodo, tiempo_total)
        self.ui_callbacks.finalizar_busqueda_inmediata()
    
    def cancelar(self):
        if self.busqueda_activa:
            self.search_engine.cancelar_busqueda()
            self.ui_callbacks.actualizar_estado("Búsqueda cancelada")
            self.busqueda_activa = False
    
    def actualizar_componentes(self, cache_manager, search_engine):
        self.cache_manager = cache_manager
        self.search_engine = search_engine
    
    def get_estado(self):
        return {
            "activa": self.busqueda_activa,
            "ultimo_criterio": self.ultimo_criterio,
            "resultados_count": len(self.resultados) if self.resultados else 0,
            "tiempo_inicio": self.tiempo_inicio
        }