# manual_viewer.py
# Búsqueda Rápida de Carpetas - Visor de Manual Técnico (CORREGIDO)

import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import re

# IMPORTACIÓN CORREGIDA - prueba estas opciones:
try:
    from .manual_data import get_manual_structure
except ImportError:
    try:
        from manual_data import get_manual_structure
    except ImportError:
        # Fallback: manual embebido
        def get_manual_structure():
            return {
                "introduccion": {
                    "title": "🏠 Introducción",
                    "content": """
<h2>🏠 Introducción</h2>
<p><strong>Búsqueda Rápida de Carpetas V.4.0 Purgatorio</strong> - Herramienta para localizar directorios en Windows.</p>

<h3>🚀 Inicio Rápido</h3>
<ol>
<li>Ejecutar app.py</li>
<li>Ingresar criterio de búsqueda</li>
<li>Presionar Enter</li>
</ol>
                    """
                },
                "atajos": {
                    "title": "⌨️ Atajos de Teclado",
                    "content": """
<h2>⌨️ Atajos de Teclado</h2>
<p><strong>F1:</strong> Manual técnico</p>
<p><strong>F2:</strong> Enfocar búsqueda</p>
<p><strong>F3:</strong> Copiar ruta</p>
<p><strong>F4:</strong> Abrir carpeta</p>
<p><strong>Ctrl+H:</strong> Toggle historial</p>
                    """
                }
            }

class ManualViewer:
    def __init__(self, master):
        self.master = master
        self.manual_window = None
        self.manual_structure = None
        self.current_search_thread = None
        
    def show_manual(self):
        """Muestra la ventana del manual técnico"""
        print("🔍 DEBUG: show_manual() llamado")  # DEBUG
        
        if self.manual_window and self.manual_window.winfo_exists():
            self.manual_window.lift()
            self.manual_window.focus()
            return
            
        try:
            self._create_manual_window()
            self._setup_manual_interface()
            self._load_manual_content()
            print("✅ DEBUG: Manual creado exitosamente")  # DEBUG
        except Exception as e:
            print(f"❌ DEBUG: Error creando manual: {e}")  # DEBUG
            messagebox.showerror("Error", f"Error al crear manual: {str(e)}")
            
    def _create_manual_window(self):
        """Crea la ventana principal del manual"""
        print("🔍 DEBUG: Creando ventana del manual")  # DEBUG
        
        self.manual_window = tk.Toplevel(self.master)
        self.manual_window.title("Manual Técnico - Búsqueda Rápida de Carpetas V.4.0")
        self.manual_window.geometry("1000x700")
        self.manual_window.resizable(True, True)
        
        # Centrar ventana
        self.manual_window.transient(self.master)
        self.manual_window.grab_set()
        
    def _setup_manual_interface(self):
        """Configura la interfaz del manual"""
        print("🔍 DEBUG: Configurando interfaz")  # DEBUG
        
        # Frame principal
        main_frame = ttk.Frame(self.manual_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título principal
        title_label = ttk.Label(
            main_frame,
            text="📚 Manual Técnico - V.4.0 Purgatorio",
            font=('Segoe UI', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de contenido principal
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # Panel izquierdo - Índice (más simple)
        left_frame = ttk.LabelFrame(content_frame, text="📋 Índice", padding=5)
        left_frame.pack(side='left', fill='y', padx=(0, 5))
        
        # Lista simple en lugar de TreeView
        self.index_listbox = tk.Listbox(left_frame, width=25, height=15)
        self.index_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Panel derecho - Contenido
        right_frame = ttk.LabelFrame(content_frame, text="📖 Contenido", padding=5)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Text widget para mostrar contenido
        self.content_text = tk.Text(
            right_frame,
            wrap='word',
            font=('Segoe UI', 11),
            bg='white',
            relief='flat',
            padx=15,
            pady=15
        )
        
        # Scrollbar para el contenido
        content_scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=content_scrollbar.set)
        
        self.content_text.pack(side='left', fill='both', expand=True)
        content_scrollbar.pack(side='right', fill='y')
        
        # Eventos
        self.index_listbox.bind('<<ListboxSelect>>', self._on_section_select)
        self.manual_window.bind('<F1>', lambda e: self.manual_window.destroy())
        self.manual_window.bind('<Escape>', lambda e: self.manual_window.destroy())
        
    def _load_manual_content(self):
        """Carga el contenido del manual"""
        print("🔍 DEBUG: Cargando contenido del manual")  # DEBUG
        
        try:
            self.manual_structure = get_manual_structure()
            print(f"✅ DEBUG: Manual structure cargado: {list(self.manual_structure.keys())}")  # DEBUG
            self._populate_index()
            self._show_introduction()
        except Exception as e:
            print(f"❌ DEBUG: Error cargando contenido: {e}")  # DEBUG
            messagebox.showerror("Error", f"Error al cargar el manual: {str(e)}")
            
    def _populate_index(self):
        """Popula el índice con las secciones del manual"""
        if not self.manual_structure:
            return
            
        # Limpiar índice
        self.index_listbox.delete(0, tk.END)
            
        # Agregar secciones
        for key, section in self.manual_structure.items():
            self.index_listbox.insert(tk.END, section['title'])
            
    def _show_introduction(self):
        """Muestra la introducción por defecto"""
        if self.manual_structure and 'introduccion' in self.manual_structure:
            self._display_content(self.manual_structure['introduccion']['content'])
            # Seleccionar introducción en el índice
            self.index_listbox.selection_set(0)
            
    def _on_section_select(self, event=None):
        """Maneja la selección de una sección en el índice"""
        selection = self.index_listbox.curselection()
        if not selection or not self.manual_structure:
            return
            
        section_index = selection[0]
        section_keys = list(self.manual_structure.keys())
        
        if section_index < len(section_keys):
            section_key = section_keys[section_index]
            content = self.manual_structure[section_key]['content']
            self._display_content(content)
            
    def _display_content(self, html_content):
        """Convierte HTML a texto y lo muestra"""
        self.content_text.configure(state='normal')
        self.content_text.delete('1.0', tk.END)
        
        # Conversión básica de HTML a texto
        text_content = self._convert_html_to_text(html_content)
        self.content_text.insert('1.0', text_content)
        
        # Hacer el texto de solo lectura
        self.content_text.configure(state='disabled')
        
    def _convert_html_to_text(self, html_content):
        """Convierte contenido HTML a texto plano simple"""
        import html
        
        # Reemplazos básicos de HTML
        content = html_content.replace('<h2>', '\n=== ').replace('</h2>', ' ===\n')
        content = content.replace('<h3>', '\n--- ').replace('</h3>', ' ---\n')
        content = content.replace('<h4>', '\n* ').replace('</h4>', '\n')
        content = content.replace('<strong>', '**').replace('</strong>', '**')
        content = content.replace('<code>', '`').replace('</code>', '`')
        content = content.replace('<li>', '• ').replace('</li>', '\n')
        content = content.replace('<ul>', '\n').replace('</ul>', '\n')
        content = content.replace('<ol>', '\n').replace('</ol>', '\n')
        content = content.replace('<p>', '\n').replace('</p>', '\n')
        
        # Limpiar tags restantes
        content = re.sub(r'<[^>]+>', '', content)
        
        # Decodificar entidades HTML
        content = html.unescape(content)
        
        # Limpiar espacios múltiples y líneas vacías excesivas
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
        
    def close_manual(self):
        """Cierra la ventana del manual"""
        if self.manual_window and self.manual_window.winfo_exists():
            self.manual_window.destroy()
        self.manual_window = None