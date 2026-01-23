# src/menu_manager.py - Gestión de Menús V.4.5 - OPTIMIZADO SIN REDUNDANCIAS
from tkinter import Menu, messagebox

class MenuManager:
    """Gestiona la creación y manejo de menús - SIN opciones redundantes del caché"""
    
    def __init__(self, app):
        self.app = app
        self.menubar = None
    
    def create_menu_bar(self):
        """Crea la barra de menú completa - OPTIMIZADA"""
        self.menubar = Menu(self.app.master)
        self.app.master.config(menu=self.menubar)
        
        self._create_archivo_menu(self.menubar)
        self._create_ver_menu(self.menubar)
        self._create_ayuda_menu(self.menubar)
    
    def _create_archivo_menu(self, menubar):
        """Crea menú Archivo - Con nomenclatura clara"""
        archivo = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo)
        
        # Carpeta PRINCIPAL (ruta_carpeta) - Base del sistema
        archivo.add_command(
            label="Carpeta Principal...", 
            command=self._seleccionar_carpeta,
            accelerator="Ctrl+O"
        )
        
        # Ubicaciones ADICIONALES (multi_location_search)
        archivo.add_command(
            label="Ubicaciones Adicionales...", 
            command=self._show_locations_config,
            accelerator="Ctrl+U"
        )
        
        archivo.add_separator()
        archivo.add_command(label="Verificar problemas", command=self.app.search_coordinator.verificar_problemas_cache)
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.app.master.quit)
    
    def _create_ver_menu(self, menubar):
        """Crea menú Ver para paneles duales"""
        ver_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=ver_menu)
        
        # Historial y explorador con checkbuttons - ATAJOS ACTUALIZADOS
        ver_menu.add_checkbutton(
            label="Historial de Búsquedas",
            variable=self.app.mostrar_historial,
            command=self.app.toggle_historial,
            accelerator="Ctrl+Shift+H"
        )
        
        ver_menu.add_checkbutton(
            label="Explorador de Archivos", 
            variable=self.app.mostrar_explorador,
            command=self.app.toggle_explorador,
            accelerator="Ctrl+Shift+E"
        )
        
        ver_menu.add_separator()
        
        # Barras de información
        ver_menu.add_checkbutton(
            label="Barra de Información de Cache",
            variable=self.app.mostrar_barra_cache,
            command=self.app.toggle_barra_cache
        )
        
        ver_menu.add_checkbutton(
            label="Barra de Estado",
            variable=self.app.mostrar_barra_estado,
            command=self.app.toggle_barra_estado
        )
       
        ver_menu.add_separator()
        ver_menu.add_command(
            label="🌓 Cambiar Tema",
            command=lambda: self.app.theme_manager.toggle_tema(),
            accelerator="F12"
        )
    
    def _create_ayuda_menu(self, menubar):
        """Crea menú Ayuda"""
        ayuda = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda)
        
        ayuda.add_command(label="Manual de Usuario", command=self.mostrar_manual)
        ayuda.add_command(label="Registro de Cambios", command=self.mostrar_changelog)
        ayuda.add_separator()
        ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)
    
    def _seleccionar_carpeta(self):
        """Wrapper para seleccionar carpeta - MEJORADO para reconstruir cache automáticamente"""
        try:
            nueva_ruta = self.app.file_manager.seleccionar_ruta(self.app.ruta_carpeta)
            if nueva_ruta:
                self.app.ruta_carpeta = nueva_ruta
                
                # Actualizar componentes con nueva ruta
                self.app.cache_manager.ruta_base = nueva_ruta
                self.app.search_engine.actualizar_ruta_base(nueva_ruta)
                
                # Limpiar resultados y actualizar UI
                self.app.ui_callbacks.limpiar_resultados()
                self.app.actualizar_info_carpeta()
                
                # Habilitar búsqueda
                if self.app.entry.get().strip():
                    self.app.btn_buscar.config(state='normal')
                
                # CAMBIO PRINCIPAL: Construir cache automáticamente SIEMPRE al cambiar ruta
                self.app.ui_callbacks.actualizar_estado("Construyendo caché para nueva ubicación...")
                
                # Construir cache en background
                import threading
                def construir_nuevo_cache():
                    try:
                        # Invalidar cache anterior
                        self.app.cache_manager.invalidar_cache()
                        
                        # Construir nuevo cache
                        if self.app.cache_manager.construir_cache():
                            self.app.master.after(0, lambda: [
                                self.app.actualizar_info_carpeta(),
                                self.app.ui_callbacks.actualizar_estado("Nueva carpeta configurada - Caché listo")
                            ])
                            print(f"[CACHE] Cache construido para nueva ruta: {nueva_ruta}")
                        else:
                            self.app.master.after(0, lambda: 
                                self.app.ui_callbacks.actualizar_estado("Nueva carpeta configurada - Use búsqueda directa"))
                    except Exception as e:
                        print(f"[CACHE] Error construyendo cache para nueva ruta: {e}")
                        self.app.master.after(0, lambda: 
                            self.app.ui_callbacks.actualizar_estado("Nueva carpeta configurada - Error en caché"))
                
                threading.Thread(target=construir_nuevo_cache, daemon=True).start()
                
        except Exception as e:
            print(f"Error seleccionando carpeta: {e}")
            messagebox.showerror("Error", f"Error al seleccionar carpeta: {str(e)}")
    
    def _show_locations_config(self):
        """Muestra modal de configuración de ubicaciones"""
        try:
            from .locations_config_modal import LocationsConfigModal
            modal = LocationsConfigModal(self.app.master, self.app)
            modal.show_modal()
        except Exception as e:
            print(f"Error abriendo configuración de ubicaciones: {e}")
            messagebox.showerror("Error", f"No se pudo abrir la configuración: {str(e)}")
    
    def mostrar_manual(self):
        """Abre el manual renderizado como HTML"""
        try:
            import os
            base_dir = os.path.dirname(os.path.dirname(__file__))
            readme_path = os.path.join(base_dir, 'README.md')
            
            if os.path.exists(readme_path):
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self._abrir_como_html(content, "Manual de Usuario")
            else:
                messagebox.showinfo("Manual", "Manual no encontrado (README.md)")
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo manual: {e}")
    
    def mostrar_changelog(self):
        """Abre el changelog renderizado como HTML"""
        try:
            import os
            changelog_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'CHANGELOG.md')
            
            if os.path.exists(changelog_path):
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self._abrir_como_html(content, "Registro de Cambios")
            else:
                messagebox.showinfo("Changelog", "No hay registro de cambios disponible")
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo changelog: {e}")

    def _abrir_como_html(self, markdown_text, title):
        """Convierte Markdown a HTML temporal y lo abre"""
        import tempfile
        import webbrowser
        import re
        import html
        import os
        
        # 1. Escapar HTML base
        # No escapamos todo porque queremos insertar tags, pero sí caracteres especiales si fuera necesario
        # En este caso simple, asumimos que el markdown es seguro y confiable
        
        # 2. Estilos CSS (Estilo GitHub Clean)
        css = """
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; 
                   line-height: 1.6; color: #24292e; max-width: 900px; margin: 0 auto; padding: 40px 20px; background: #ffffff; }
            h1, h2, h3 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; color: #1b1f23; }
            h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
            h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
            h3 { font-size: 1.25em; }
            code { padding: .2em .4em; margin: 0; font-size: 85%; background-color: #f6f8fa; border-radius: 6px; font-family: Consolas, monospace; }
            pre { padding: 16px; overflow: auto; font-size: 85%; line-height: 1.45; background-color: #f6f8fa; border-radius: 6px; }
            ul { padding-left: 2em; margin-bottom: 16px; }
            li { margin: 0.25em 0; }
            p { margin-bottom: 16px; }
            hr { height: .25em; padding: 0; margin: 24px 0; background-color: #e1e4e8; border: 0; }
            strong { font-weight: 600; color: #24292e; }
            blockquote { padding: 0 1em; color: #6a737d; border-left: 0.25em solid #dfe2e5; margin: 0 0 16px 0; }
            .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eaecef; color: #586069; font-size: 12px; text-align: center; }
        </style>
        """
        
        # 3. Parser "Trucado" (Regex Simple)
        html_content = markdown_text
        
        # Headers
        html_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        
        # Horizontal Rules
        html_content = re.sub(r'^---$', r'<hr>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^={3,}$', r'<hr>', html_content, flags=re.MULTILINE)
        
        # Bold
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        
        # Lists (Naive: - item -> <li>item</li>)
        # Primero detectamos bloques de lista para envolverlos en <ul>
        lines = html_content.split('\n')
        processed_lines = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detectar item de lista
            if stripped.startswith('- ') or stripped.startswith('• '):
                content = stripped[2:]
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                processed_lines.append(f'<li>{content}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                
                # Párrafos simples (si no es tag HTML ya procesado)
                if stripped and not stripped.startswith('<') and not stripped.startswith('='):
                    processed_lines.append(f'<p>{stripped}</p>')
                else:
                    processed_lines.append(stripped)
        
        if in_list:
            processed_lines.append('</ul>')
            
        body_content = '\n'.join(processed_lines)
        
        # 4. Armar HTML Final
        full_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            {css}
        </head>
        <body>
            {body_content}
            <div class="footer">
                Generado automáticamente por Búsqueda Rápida de Carpetas V.4.5<br>
                {title}
            </div>
        </body>
        </html>
        """
        
        # 5. Guardar y Abrir
        try:
            fd, path = tempfile.mkstemp(suffix='.html')
            with os.fdopen(fd, 'w', encoding='utf-8') as tmp:
                tmp.write(full_html)
            
            webbrowser.open(f'file:///{path}')
        except Exception as e:
            print(f"Error generando HTML temporal: {e}")
            # Fallback a abrir el archivo original si falla la conversión
            pass
    
    def mostrar_acerca_de(self):
        """Muestra información sobre la aplicación con messagebox nativo"""
        try:
            version_info = f"Versión {self.app.version}" if hasattr(self.app, 'version') else "Versión desconocida"
            messagebox.showinfo(
                "Búsqueda de Carpetas",
                f"Búsqueda Rápida de Carpetas\n\n"
                f"{version_info}\n\n"
                f"Desarrollado por: Elkin Darío Pérez Puyana\n"
                f"© 2025\n\n"
                f"Una herramienta para búsqueda eficiente de carpetas."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
    
    def get_menu_state(self):
        """Obtiene el estado actual de las opciones del menú"""
        return {
            'historial_visible': self.app.mostrar_historial.get(),
            'explorador_visible': self.app.mostrar_explorador.get(),
            'barra_cache_visible': self.app.mostrar_barra_cache.get(),
            'barra_estado_visible': self.app.mostrar_barra_estado.get()
        }
    
    def update_menu_variables(self):
        """Actualiza las variables del menú según el estado actual"""
        try:
            # Actualizar historial
            if hasattr(self.app, 'historial_manager') and self.app.historial_manager:
                self.app.mostrar_historial.set(self.app.historial_manager.visible)
            
            # Actualizar explorador
            if hasattr(self.app, 'file_explorer_manager') and self.app.file_explorer_manager:
                self.app.mostrar_explorador.set(self.app.file_explorer_manager.is_visible())
                
        except Exception as e:
            print(f"Error actualizando variables del menú: {e}")
    
    def reset_menu_state(self):
        """Resetea el estado del menú a valores por defecto"""
        self.app.mostrar_historial.set(False)
        self.app.mostrar_explorador.set(False)
        self.app.mostrar_barra_cache.set(True)
        self.app.mostrar_barra_estado.set(True)