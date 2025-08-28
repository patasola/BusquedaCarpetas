# src/manual_viewer.py - Visor de Manual Técnico V.4.2 (Refactorizado)
import tkinter as tk
from tkinter import ttk, messagebox
import re
import html

class ManualViewer:
    def __init__(self, master):
        self.master = master
        self.manual_window = None
        self.manual_structure = None
    
    def show_manual(self):
        """Muestra la ventana del manual técnico"""
        if self.manual_window and self.manual_window.winfo_exists():
            self.manual_window.lift()
            self.manual_window.focus()
            return
            
        try:
            self._crear_ventana()
            self._crear_interfaz()
            self._cargar_contenido()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear manual: {str(e)}")
            
    def _crear_ventana(self):
        """Crea y configura la ventana principal"""
        self.manual_window = tk.Toplevel(self.master)
        self.manual_window.title("Manual Técnico - Búsqueda Rápida de Carpetas V.4.2")
        self.manual_window.geometry("1000x750")
        self.manual_window.resizable(True, True)
        self.manual_window.transient(self.master)
        self.manual_window.grab_set()
    
    def _crear_interfaz(self):
        """Crea la interfaz del manual"""
        main_frame = ttk.Frame(self.manual_window)
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Título
        ttk.Label(
            main_frame,
            text="Manual Técnico - V.4.2 Purgatorio (Refactorizado)",
            font=('Segoe UI', 16, 'bold')
        ).pack(pady=(0, 20))
        
        # Frame de contenido
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Panel izquierdo - Índice
        left_frame = ttk.LabelFrame(content_frame, text="Índice", padding=5)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        
        self.index_listbox = tk.Listbox(left_frame, width=25, height=20, font=('Segoe UI', 10))
        self.index_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Panel derecho - Contenido
        right_frame = ttk.LabelFrame(content_frame, text="Contenido", padding=5)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.content_text = tk.Text(
            right_frame,
            wrap='word',
            font=('Segoe UI', 11),
            bg='white',
            relief='flat',
            padx=20, pady=20
        )
        
        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        
        self.content_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Eventos
        self.index_listbox.bind('<<ListboxSelect>>', self._seleccionar_seccion)
        self.manual_window.bind('<F1>', lambda e: self.manual_window.destroy())
        self.manual_window.bind('<Escape>', lambda e: self.manual_window.destroy())
        
    def _cargar_contenido(self):
        """Carga el contenido del manual"""
        self.manual_structure = self._obtener_estructura_manual()
        self._poblar_indice()
        self._mostrar_introduccion()
        
    def _obtener_estructura_manual(self):
        """Define la estructura completa del manual V.4.2"""
        return {
            "introduccion": {
                "title": "Introducción",
                "content": """<h2>Búsqueda Rápida de Carpetas V.4.2</h2>
<p>Sistema híbrido de búsqueda y exploración de directorios con arquitectura refactorizada.</p>

<h3>Inicio Rápido:</h3>
<ol>
<li>Ejecutar main.py desde terminal</li>
<li>Seleccionar carpeta base (menú Archivo)</li>
<li>Ingresar criterio de búsqueda</li>
<li>Presionar Enter o botón Buscar</li>
</ol>

<h3>Novedades V.4.2:</h3>
<ul>
<li>Código refactorizado: 50% menos líneas</li>
<li>Arquitectura optimizada y modular</li>
<li>Rendimiento mejorado en todas las operaciones</li>
<li>Mantenimiento completo de funcionalidad</li>
</ul>"""
            },
            "atajos": {
                "title": "Atajos de Teclado",
                "content": """<h2>Atajos de Teclado Completos</h2>

<h3>Funciones Principales:</h3>
<p><strong>F1:</strong> Mostrar este manual técnico</p>
<p><strong>F2:</strong> Enfocar campo de búsqueda (selecciona todo)</p>
<p><strong>F3:</strong> Copiar ruta de carpeta seleccionada</p>
<p><strong>F4:</strong> Abrir carpeta seleccionada en explorador</p>
<p><strong>F5:</strong> Cambiar modo numérico/alfanumérico</p>
<p><strong>F6:</strong> Limpiar cache temporal (Tree Explorer)</p>

<h3>Navegación:</h3>
<p><strong>Tab:</strong> Navegar entre elementos (circular)</p>
<p><strong>Shift+Tab:</strong> Navegar hacia atrás</p>
<p><strong>↑↓:</strong> Navegar en tabla/historial</p>
<p><strong>←→:</strong> Expandir/colapsar en Tree Explorer</p>
<p><strong>Enter:</strong> Ejecutar acción o toggle expansión</p>

<h3>Gestión de Ventana:</h3>
<p><strong>Ctrl+E:</strong> Centrar ventana en pantalla</p>
<p><strong>Ctrl+R:</strong> Restaurar ventana a tamaño normal</p>
<p><strong>F11:</strong> Maximizar ventana</p>
<p><strong>Ctrl+H:</strong> Toggle historial de búsquedas</p>"""
            },
            "busqueda": {
                "title": "Sistema de Búsqueda",
                "content": """<h2>Sistema Híbrido de Búsqueda</h2>

<h3>Métodos de Búsqueda:</h3>
<p><strong>Cache (C):</strong> Búsqueda ultrarrápida en índice preconstruido</p>
<p><strong>Tradicional (T):</strong> Escaneo completo del sistema de archivos</p>
<p><strong>Tree Explorer (E):</strong> Navegación expandible por subdirectorios</p>

<h3>Funcionamiento Automático:</h3>
<ol>
<li>Intenta búsqueda en cache primero</li>
<li>Si no hay resultados, ejecuta búsqueda tradicional</li>
<li>Resultados se muestran con indicador de método (C/T/E)</li>
</ol>

<h3>Construcción de Cache:</h3>
<ul>
<li>Automática: Al seleccionar nueva carpeta</li>
<li>Manual: Menú Archivo → Construir cache</li>
<li>Límites: 50,000 carpetas máx, 30s tiempo máx</li>
<li>Persistencia: Archivo carpetas_cache.pkl</li>
</ul>

<h3>Criterios de Búsqueda:</h3>
<p>Búsquedas por nombre de carpeta (case-insensitive)</p>
<p>No soporta wildcards ni regex en V.4.2</p>"""
            },
            "tree_explorer": {
                "title": "Tree Explorer V.4.1+",
                "content": """<h2>Explorador de Árbol Integrado</h2>

<h3>Funcionalidades:</h3>
<ul>
<li>Expansión/colapso de nodos con subdirectorios</li>
<li>Cache temporal para navegación rápida</li>
<li>Carga asíncrona de subdirectorios (threading)</li>
<li>Ajuste automático de columnas bidireccional</li>
<li>Integración completa con búsquedas</li>
</ul>

<h3>Navegación Tree Explorer:</h3>
<p><strong>→:</strong> Expandir nodo o ir al primer hijo</p>
<p><strong>←:</strong> Colapsar nodo o ir al padre</p>
<p><strong>Enter:</strong> Toggle expansión/colapso</p>
<p><strong>Doble-click:</strong> Abrir carpeta en explorador</p>

<h3>Cache Temporal:</h3>
<p><strong>F6:</strong> Limpiar cache temporal completo</p>
<p>Almacena subdirectorios expandidos en memoria</p>
<p>Límites: 100 subdirectorios por nivel, 2s carga máx</p>

<h3>Indicadores Visuales:</h3>
<p>📁 - Carpeta con subdirectorios</p>
<p>🔄 - Cargando subdirectorios</p>
<p>⛔ - Error de acceso</p>"""
            },
            "historial": {
                "title": "Historial de Búsquedas",
                "content": """<h2>Panel de Historial Integrado</h2>

<h3>Características:</h3>
<ul>
<li>Panel lateral integrado (no ventana separada)</li>
<li>Historial de sesión únicamente (máx 50 entradas)</li>
<li>Ordenamiento por hora y criterio</li>
<li>Búsqueda rápida al seleccionar</li>
<li>Navegación completa por teclado</li>
</ul>

<h3>Controles:</h3>
<p><strong>Ctrl+H:</strong> Mostrar/ocultar historial</p>
<p><strong>Click:</strong> Ejecutar búsqueda rápida desde cache</p>
<p><strong>F3:</strong> Repetir búsqueda completa</p>
<p><strong>F4:</strong> Abrir primera carpeta encontrada</p>
<p><strong>Delete:</strong> Eliminar entrada seleccionada</p>

<h3>Ordenamiento:</h3>
<p>Headers clickeables con indicadores ↑↓</p>
<p>Ordenar por hora (cronológico) o criterio (alfabético)</p>

<h3>Búsquedas Silenciosas:</h3>
<p>Al seleccionar del historial se ejecuta búsqueda rápida</p>
<p>No se duplican entradas en el historial</p>"""
            },
            "interfaz": {
                "title": "Control de Interfaz",
                "content": """<h2>Menú Ver - Control Total</h2>

<h3>Opciones Disponibles:</h3>
<p><strong>Barra de Estado:</strong> Toggle de barra inferior con atajos</p>
<p><strong>Barra de Cache:</strong> Toggle de barra azul con información</p>
<p><strong>Historial:</strong> Panel lateral de búsquedas (Ctrl+H)</p>

<h3>Layout Adaptativo:</h3>
<p>Ventana principal se ajusta automáticamente</p>
<p>Con historial: Ventana amplia (1200px)</p>
<p>Sin historial: Ventana compacta ajustada</p>

<h3>Navegación por Tab:</h3>
<p>Orden: Campo → Buscar → Cancelar → Tabla → Copiar → Abrir → Historial</p>
<p>Inclusión dinámica del historial según visibilidad</p>
<p>Navegación circular automática</p>

<h3>Gestión de Ventana:</h3>
<p>Centrado automático al iniciar</p>
<p>Controles de maximizar/restaurar/centrar</p>
<p>Tamaño mínimo: 800x500px</p>"""
            },
            "arquitectura": {
                "title": "Arquitectura V.4.2",
                "content": """<h2>Arquitectura Refactorizada</h2>

<h3>Módulos Principales:</h3>
<p><strong>app.py:</strong> Coordinación principal (200 líneas)</p>
<p><strong>cache_manager.py:</strong> Gestión de cache optimizada</p>
<p><strong>search_coordinator.py:</strong> Coordinación de búsquedas</p>
<p><strong>tree_explorer.py:</strong> Explorador de árbol</p>
<p><strong>historial_manager.py:</strong> Panel de historial</p>

<h3>Managers de UI:</h3>
<p><strong>ui_manager.py:</strong> Control de elementos de interfaz</p>
<p><strong>window_manager.py:</strong> Gestión de ventana</p>
<p><strong>navigation_manager.py:</strong> Navegación por Tab</p>
<p><strong>event_manager.py:</strong> Gestión de eventos</p>

<h3>Optimizaciones V.4.2:</h3>
<ul>
<li>Reducción promedio 30% líneas de código</li>
<li>Eliminación de redundancias y duplicación</li>
<li>Configuraciones por diccionario vs if-elif</li>
<li>Manejo de errores unificado</li>
<li>Métodos más enfocados y específicos</li>
</ul>

<h3>Threading:</h3>
<p>Búsquedas asíncronas para evitar bloqueo UI</p>
<p>Carga de subdirectorios en background</p>
<p>Construcción de cache sin bloquear interfaz</p>"""
            },
            "troubleshooting": {
                "title": "Solución de Problemas",
                "content": """<h2>Diagnóstico y Soluciones</h2>

<h3>Problemas Comunes:</h3>

<h4>Cache no se construye:</h4>
<ul>
<li>Verificar permisos de lectura/escritura</li>
<li>Menú Archivo → Verificar problemas</li>
<li>Seleccionar ruta diferente si hay restricciones</li>
</ul>

<h4>Búsquedas lentas:</h4>
<ul>
<li>Construir/reconstruir cache manualmente</li>
<li>Carpetas con >50k subdirectorios requieren límites</li>
<li>Verificar disponibilidad de espacio en disco</li>
</ul>

<h4>Tree Explorer no responde:</h4>
<ul>
<li>Presionar F6 para limpiar cache temporal</li>
<li>Evitar expandir carpetas con miles de subdirectorios</li>
<li>Reiniciar aplicación si es necesario</li>
</ul>

<h3>Comandos de Diagnóstico:</h3>
<p><strong>Menú Archivo → Verificar problemas:</strong> Diagnóstico completo</p>
<p><strong>Menú Archivo → Limpiar cache:</strong> Resetear cache corrupto</p>

<h3>Archivos del Sistema:</h3>
<p><strong>config.json:</strong> Configuración de rutas</p>
<p><strong>carpetas_cache.pkl:</strong> Cache de directorios</p>
<p>Eliminar estos archivos resetea la configuración</p>"""
            }
        }
    
    def _poblar_indice(self):
        """Puebla el índice con secciones del manual"""
        self.index_listbox.delete(0, tk.END)
        for section in self.manual_structure.values():
            self.index_listbox.insert(tk.END, section['title'])
    
    def _mostrar_introduccion(self):
        """Muestra la introducción por defecto"""
        self._mostrar_contenido(self.manual_structure['introduccion']['content'])
        self.index_listbox.selection_set(0)
    
    def _seleccionar_seccion(self, event=None):
        """Maneja selección de sección en el índice"""
        selection = self.index_listbox.curselection()
        if not selection:
            return
        
        section_keys = list(self.manual_structure.keys())
        section_key = section_keys[selection[0]]
        content = self.manual_structure[section_key]['content']
        self._mostrar_contenido(content)
    
    def _mostrar_contenido(self, html_content):
        """Muestra contenido convertido de HTML a texto"""
        self.content_text.configure(state='normal')
        self.content_text.delete('1.0', tk.END)
        
        text_content = self._convertir_html_a_texto(html_content)
        self.content_text.insert('1.0', text_content)
        self.content_text.configure(state='disabled')
    
    def _convertir_html_a_texto(self, html_content):
        """Convierte HTML a texto plano formateado"""
        # Reemplazos de HTML a texto
        replacements = {
            '<h2>': '\n=== ', '</h2>': ' ===\n',
            '<h3>': '\n--- ', '</h3>': ' ---\n',
            '<h4>': '\n* ', '</h4>': '\n',
            '<strong>': '**', '</strong>': '**',
            '<code>': '`', '</code>': '`',
            '<li>': '• ', '</li>': '\n',
            '<ul>': '\n', '</ul>': '\n',
            '<ol>': '\n', '</ol>': '\n',
            '<p>': '\n', '</p>': '\n'
        }
        
        content = html_content
        for html_tag, replacement in replacements.items():
            content = content.replace(html_tag, replacement)
        
        # Limpiar tags restantes y formatear
        content = re.sub(r'<[^>]+>', '', content)
        content = html.unescape(content)
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
    
    def close_manual(self):
        """Cierra la ventana del manual"""
        if self.manual_window and self.manual_window.winfo_exists():
            self.manual_window.destroy()
        self.manual_window = None