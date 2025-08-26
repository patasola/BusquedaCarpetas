# src/search_engine.py - Motor de Búsqueda V.4.1 (Búsqueda Tradicional Corregida)
import os
import time

class SearchEngine:
    """Motor de búsqueda tradicional de carpetas"""
    
    def __init__(self, ruta_base):
        self.ruta_base = ruta_base
        self.busqueda_cancelada = False
        self.busqueda_activa = False
        self.callback_progreso = None
    
    def actualizar_ruta_base(self, nueva_ruta):
        """Actualiza la ruta base de búsqueda"""
        self.ruta_base = nueva_ruta
        self.busqueda_cancelada = False
    
    def buscar_tradicional(self, criterio):
        """Realiza búsqueda tradicional en el sistema de archivos"""
        print(f"🔍 SEARCH_ENGINE: Iniciando búsqueda tradicional para '{criterio}'")
        
        if not self.ruta_base or not os.path.exists(self.ruta_base):
            print(f"❌ SEARCH_ENGINE: Ruta base inválida: {self.ruta_base}")
            return []
        
        self.busqueda_cancelada = False
        self.busqueda_activa = True
        
        resultados = []
        criterio_lower = criterio.lower()
        procesados = 0
        
        try:
            print(f"🔍 SEARCH_ENGINE: Escaneando desde {self.ruta_base}")
            
            # Obtener estimación inicial de carpetas para progreso
            total_estimado = self._estimar_carpetas_rapido()
            
            for root, dirs, files in os.walk(self.ruta_base):
                # Verificar si la búsqueda fue cancelada
                if self.busqueda_cancelada:
                    print("🔍 SEARCH_ENGINE: Búsqueda cancelada")
                    break
                
                # Procesar cada directorio en el nivel actual
                for dirname in dirs[:]:  # Usar slice para permitir modificación
                    if self.busqueda_cancelada:
                        break
                        
                    # Verificar si coincide con el criterio
                    if criterio_lower in dirname.lower():
                        ruta_completa = os.path.join(root, dirname)
                        ruta_relativa = os.path.relpath(ruta_completa, self.ruta_base)
                        
                        resultado = (dirname, ruta_relativa, ruta_completa)
                        resultados.append(resultado)
                        
                        print(f"✅ SEARCH_ENGINE: Encontrado: {dirname}")
                        
                        # Limitar resultados para evitar lentitud extrema
                        if len(resultados) >= 1000:
                            print(f"🔍 SEARCH_ENGINE: Límite de 1000 resultados alcanzado")
                            break
                    
                    procesados += 1
                    
                    # Callback de progreso si existe
                    if self.callback_progreso and procesados % 25 == 0:
                        try:
                            porcentaje = min(int((procesados / total_estimado) * 100), 99) if total_estimado > 0 else 0
                            self.callback_progreso(porcentaje, 100, f"Búsqueda tradicional... {len(resultados)} encontradas")
                        except Exception as e:
                            print(f"⚠️ Error en callback progreso: {e}")
                
                # Limitar profundidad para evitar búsquedas extremadamente largas
                depth = root.replace(self.ruta_base, '').count(os.sep)
                if depth >= 8:  # Máximo 8 niveles de profundidad
                    dirs.clear()  # No continuar más profundo en esta rama
                    
                # Si ya tenemos muchos resultados, detener la búsqueda
                if len(resultados) >= 1000:
                    break
                    
        except (PermissionError, OSError) as e:
            print(f"⚠️ SEARCH_ENGINE: Error de permisos: {e}")
        except Exception as e:
            print(f"❌ SEARCH_ENGINE: Error inesperado: {e}")
        finally:
            self.busqueda_activa = False
            if self.callback_progreso:
                try:
                    self.callback_progreso(100, 100, f"Búsqueda completada: {len(resultados)} resultados")
                except:
                    pass
        
        print(f"🔍 SEARCH_ENGINE: Búsqueda tradicional completada. {len(resultados)} resultados encontrados")
        return resultados
    
    def _estimar_carpetas_rapido(self):
        """Hace una estimación rápida del número total de carpetas"""
        try:
            if not self.ruta_base or not os.path.exists(self.ruta_base):
                return 1000  # Estimación por defecto
            
            # Contar carpetas solo en el primer nivel para estimación
            primer_nivel = 0
            for item in os.listdir(self.ruta_base):
                item_path = os.path.join(self.ruta_base, item)
                if os.path.isdir(item_path):
                    primer_nivel += 1
            
            # Estimación basada en primer nivel (multiplicador conservador)
            estimacion = max(primer_nivel * 50, 100)  # Mínimo 100, escalado por 50
            print(f"🔍 SEARCH_ENGINE: Estimación de carpetas: {estimacion}")
            return estimacion
            
        except Exception as e:
            print(f"⚠️ Error en estimación: {e}")
            return 1000  # Valor por defecto seguro
    
    def cancelar_busqueda(self):
        """Cancela la búsqueda en curso"""
        print("🔍 SEARCH_ENGINE: Cancelando búsqueda...")
        self.busqueda_cancelada = True
        self.busqueda_activa = False
    
    def verificar_ruta_valida(self, ruta):
        """Verifica si una ruta es válida y accesible"""
        try:
            return os.path.exists(ruta) and os.path.isdir(ruta)
        except Exception:
            return False
    
    def get_estado_busqueda(self):
        """Obtiene el estado actual de la búsqueda"""
        return {
            'activa': self.busqueda_activa,
            'cancelada': self.busqueda_cancelada,
            'ruta_base': self.ruta_base
        }