import threading
import time

class SearchManager:
    """
    Gestiona toda la lógica de búsqueda de la aplicación.
    Responsabilidades:
    - Coordinar búsquedas en cache y tradicionales
    - Manejar progreso y callbacks
    - Gestionar threads de búsqueda
    - Validar criterios de búsqueda
    """
    
    def __init__(self, cache_manager, search_engine, progress_manager, ui_callbacks):
        self.cache_manager = cache_manager
        self.search_engine = search_engine
        self.progress_manager = progress_manager
        self.ui_callbacks = ui_callbacks
        
        # Variables de estado
        self.tiempo_inicio = 0
        self.ultimo_criterio = ""
        self.resultados = []
        self.busqueda_activa = False
    
    def buscar(self, criterio):
        """Método principal de búsqueda con estrategia híbrida"""
        print(f"DEBUG: Iniciando búsqueda para: '{criterio}'")
        
        if not self._validar_busqueda(criterio):
            return False
            
        self._preparar_busqueda(criterio)
        
        # Estrategia 1: Intentar búsqueda en cache primero
        if self._buscar_en_cache(criterio):
            return True
            
        # Estrategia 2: Fallback a búsqueda tradicional
        return self._iniciar_busqueda_tradicional(criterio)
    
    def _validar_busqueda(self, criterio):
        """Valida que se pueda realizar la búsqueda"""
        if not criterio:
            self.ui_callbacks.mostrar_advertencia("Ingrese un criterio de búsqueda")
            return False
            
        if not self.cache_manager.ruta_base:
            self.ui_callbacks.mostrar_advertencia("Seleccione una ruta de búsqueda primero")
            return False
            
        return True
    
    def _preparar_busqueda(self, criterio):
        """Prepara el estado para una nueva búsqueda"""
        self.ultimo_criterio = criterio
        self.tiempo_inicio = time.time()
        self.busqueda_activa = True
        
        # Limpiar resultados anteriores
        self.ui_callbacks.limpiar_resultados()
        self.ui_callbacks.actualizar_estado("Buscando...")
        
        print(f"DEBUG: Búsqueda preparada para: '{criterio}'")
    
    def _buscar_en_cache(self, criterio):
        """Intenta búsqueda en cache (método preferido)"""
        print("DEBUG: Intentando búsqueda en cache...")
        
        if not self.cache_manager.cache.valido:
            print("DEBUG: Cache no válido, requiere construcción")
            self.ui_callbacks.actualizar_estado("Cache no disponible. Construyendo cache...")
            self.ui_callbacks.construir_cache()
            return True  # Terminar aquí, la construcción manejará la continuación
            
        # Buscar en cache
        resultados = self.cache_manager.buscar_en_cache(criterio)
        
        if resultados is not None:
            print(f"DEBUG: Cache procesó búsqueda - {len(resultados)} resultados")
            
            if len(resultados) > 0:
                print(f"DEBUG: Cache encontró {len(resultados)} resultados")
                self._finalizar_busqueda_exitosa(resultados, "Cache")
                return True
            else:
                print("DEBUG: Cache no encontró resultados, pero búsqueda válida")
                # Mostrar que cache no encontró nada antes de ir a tradicional
                tiempo_cache = time.time() - self.tiempo_inicio
                self.ui_callbacks.actualizar_estado(f"Cache sin resultados ({tiempo_cache:.3f}s), buscando tradicionalmente...")
                return False
        
        print("DEBUG: Error en cache, fallback a búsqueda tradicional")
        self.ui_callbacks.actualizar_estado("Error en cache, buscando en directorios...")
        return False
    
    def _iniciar_busqueda_tradicional(self, criterio):
        """Inicia búsqueda tradicional con progreso SIMPLIFICADO (solo porcentaje)"""
        print("DEBUG: Iniciando búsqueda tradicional SIMPLIFICADA")
        
        # INICIO SIMPLIFICADO: Mostrar solo porcentaje 0%
        self.progress_manager.mostrar()
        self.progress_manager.actualizar(0, 100)
        
        # Configurar callback SIMPLIFICADO
        def callback_progreso(procesados, total):
            self.ui_callbacks.actualizar_progreso_async(procesados, total)
        
        self.search_engine.callback_progreso = callback_progreso
        
        # Ejecutar en thread separado
        threading.Thread(
            target=self._ejecutar_busqueda_tradicional,
            args=(criterio,),
            daemon=True
        ).start()
        
        return True
    
    def _ejecutar_busqueda_tradicional(self, criterio):
        """Ejecuta búsqueda tradicional con progreso SIMPLIFICADO (solo porcentaje)"""
        print("DEBUG: Ejecutando búsqueda tradicional SIMPLIFICADA en thread")
        
        try:
            self.ui_callbacks.actualizar_estado_async("Búsqueda tradicional en progreso...")
            
            # Ejecutar búsqueda
            resultados = self.search_engine.buscar_tradicional(criterio)
            
            if resultados is not None:
                print(f"DEBUG: Búsqueda tradicional encontró {len(resultados)} resultados")
                self.resultados = resultados
                
                # FINALIZACIÓN SIMPLIFICADA: 100% antes de mostrar resultados
                self.ui_callbacks.actualizar_progreso_async(100, 100)
                tiempo_total = time.time() - self.tiempo_inicio
                
                # Programar ocultación de progreso y mostrar resultados
                def finalizar_busqueda():
                    if len(resultados) > 0:
                        self.ui_callbacks.mostrar_resultados_async(
                            resultados, "Tradicional", tiempo_total
                        )
                    else:
                        print("DEBUG: Búsqueda tradicional sin resultados")
                        self.ui_callbacks.mostrar_resultados_async(
                            [], "Tradicional", tiempo_total
                        )
                    # Ocultar progreso después de 1.5 segundos
                    self.ui_callbacks.app.master.after(1500, self.progress_manager.ocultar)
                
                self.ui_callbacks.app.master.after(0, finalizar_busqueda)
                
            else:
                print("DEBUG: Error en búsqueda tradicional")
                self.ui_callbacks.actualizar_estado_async("Error en la búsqueda tradicional")
                self.ui_callbacks.app.master.after(0, self.progress_manager.ocultar)
                
        except Exception as e:
            print(f"ERROR en búsqueda tradicional: {e}")
            self.ui_callbacks.actualizar_estado_async(f"Error en búsqueda tradicional: {str(e)}")
            self.ui_callbacks.app.master.after(0, self.progress_manager.ocultar)
            
        finally:
            # Finalizar búsqueda
            self.ui_callbacks.finalizar_busqueda_async()
            self.busqueda_activa = False
    
    def _finalizar_busqueda_exitosa(self, resultados, metodo):
        """Finaliza una búsqueda exitosa (cache)"""
        tiempo_total = time.time() - self.tiempo_inicio
        self.resultados = resultados
        self.busqueda_activa = False
        
        # Mostrar resultados
        self.ui_callbacks.mostrar_resultados(resultados, metodo, tiempo_total)
        
        # Habilitar botones
        self.ui_callbacks.finalizar_busqueda_inmediata()
    
    def cancelar(self):
        """Cancela la búsqueda en curso"""
        print("DEBUG: Cancelando búsqueda")
        
        if self.busqueda_activa:
            # Cancelar en el search engine
            self.search_engine.cancelar_busqueda()
            
            # Ocultar barra de progreso
            self.progress_manager.ocultar()
            
            # Actualizar estado
            self.ui_callbacks.actualizar_estado("Búsqueda cancelada")
            
            self.busqueda_activa = False
            
            print("DEBUG: Búsqueda cancelada exitosamente")
    
    def actualizar_componentes(self, cache_manager, search_engine):
        """Actualiza los componentes cuando cambia la ruta"""
        print("DEBUG: Actualizando componentes del SearchManager")
        self.cache_manager = cache_manager
        self.search_engine = search_engine
    
    def get_estado(self):
        """Retorna el estado actual de la búsqueda"""
        return {
            "activa": self.busqueda_activa,
            "ultimo_criterio": self.ultimo_criterio,
            "resultados_count": len(self.resultados) if self.resultados else 0,
            "tiempo_inicio": self.tiempo_inicio
        }