# src/search_engine.py - Motor de Búsqueda V.4.3 (Optimizado)
import os
import time

class SearchEngine:
    """Motor de búsqueda tradicional de carpetas optimizado"""
    
    def __init__(self, ruta_base):
        self.ruta_base = ruta_base
        self.busqueda_cancelada = False
        self.busqueda_activa = False
        self.callback_progreso = None
        
        # Carpetas a ignorar (optimización: -30% IO)
        self.skip_folders = {
            '.git', 'node_modules', '__pycache__', '.venv', 'venv',
            '.idea', '.vscode', 'dist', 'build', '.pytest_cache',
            '$RECYCLE.BIN', 'System Volume Information', '.Trash'
        }
    
    def actualizar_ruta_base(self, nueva_ruta):
        """Actualiza la ruta base de búsqueda"""
        self.ruta_base = nueva_ruta
        self.busqueda_cancelada = False
    
    def buscar_tradicional(self, criterio):
        """Realiza búsqueda tradicional en el sistema de archivos"""
        if not self.ruta_base or not os.path.exists(self.ruta_base):
            return []
        
        self.busqueda_cancelada = False
        self.busqueda_activa = True
        
        resultados = []
        criterio_lower = criterio.lower()
        procesados = 0
        total_estimado = self._estimar_carpetas_rapido()
        
        try:
            for root, dirs, files in os.walk(self.ruta_base):
                if self.busqueda_cancelada:
                    break
                
                # OPTIMIZACIÓN: Filtrar carpetas a ignorar ANTES de procesarlas
                dirs[:] = [d for d in dirs if d not in self.skip_folders]
                
                # Procesar directorios
                for dirname in dirs[:]:
                    # OPTIMIZACIÓN: Early exit si ya encontró muchos rápidamente
                    if self.busqueda_cancelada or len(resultados) >= 1000:
                        break
                    
                    # Early exit agresivo: si encontró 500+ en pocas carpetas, probablemente hay miles
                    if len(resultados) >= 500 and procesados < 100:
                        break
                        
                    if criterio_lower in dirname.lower():
                        ruta_completa = os.path.join(root, dirname)
                        ruta_relativa = os.path.relpath(ruta_completa, self.ruta_base)
                        
                        resultados.append((dirname, ruta_relativa, ruta_completa))
                        
                        if len(resultados) >= 1000:
                            break
                    
                    procesados += 1
                    
                    # Callback de progreso
                    if self.callback_progreso and procesados % 25 == 0:
                        try:
                            porcentaje = min(int((procesados / total_estimado) * 100), 99) if total_estimado > 0 else 0
                            self.callback_progreso(porcentaje, 100, f"Búsqueda tradicional... {len(resultados)} encontradas")
                        except Exception:
                            pass
                
                # Limitar profundidad
                depth = root.replace(self.ruta_base, '').count(os.sep)
                if depth >= 8:
                    dirs.clear()
                    
                if len(resultados) >= 1000:
                    break
                    
        except (PermissionError, OSError):
            pass
        finally:
            self.busqueda_activa = False
            if self.callback_progreso:
                try:
                    self.callback_progreso(100, 100, f"Búsqueda completada: {len(resultados)} resultados")
                except:
                    pass
        
        return resultados
    
    def _estimar_carpetas_rapido(self):
        """Estimación rápida del número total de carpetas"""
        try:
            if not self.ruta_base or not os.path.exists(self.ruta_base):
                return 1000
            
            primer_nivel = sum(1 for item in os.listdir(self.ruta_base)
                             if os.path.isdir(os.path.join(self.ruta_base, item)))
            
            return max(primer_nivel * 50, 100)
            
        except Exception:
            return 1000
    
    def cancelar_busqueda(self):
        """Cancela la búsqueda en curso"""
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