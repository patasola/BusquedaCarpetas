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