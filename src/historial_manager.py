# src/historial_manager.py - Gestor del Historial de Búsquedas - Con paneles duales V.4.4
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json
import os
from .column_manager import ColumnManager
from .managers.base_tree_manager import BaseTreeManager

class HistorialManager(BaseTreeManager):
    """Gestiona el historial de búsquedas con registro automático y posicionamiento dual"""
    
    def __init__(self, app):
        # Configuración para BaseTreeManager
        config = {
            'title': 'Historial de Búsquedas',
            'columns': [
                ('Criterio', 150),
                ('Método', 80),
                ('Resultados', 70),
                ('Tiempo', 80),
                ('Fecha', 100)
            ]
        }
        super().__init__(app, config)
        
        # Atributos específicos del historial
        self.historial_data = []
        self.historial_file = "historial_busquedas.json"
        
        # Variables para redimensionamiento
        self.resize_start_x = 0
        self.resize_start_width = 0
        
        # Cargar historial existente
        self.cargar_historial()
  
    def show(self):
        """Muestra el panel de historial con posicionamiento dual"""
        if not self.frame:
            self.create_historial()
        
        if self.frame:
            # Obtener columna asignada del sistema de paneles duales
            self.assigned_column = self.app.assign_panel_position('historial')
            
            # Mostrar en la columna asignada
            self.frame.grid(row=0, column=self.assigned_column, sticky='ns', padx=(0, 0))
            self.visible = True
            
            # Actualizar la variable del menú
            if hasattr(self.app, 'mostrar_historial'):
                self.app.mostrar_historial.set(True)
            
            print(f"[DEBUG] Historial mostrado en columna {self.assigned_column}")
    
    def hide(self):
        """Oculta el panel de historial y libera su posición"""
        if self.frame:
            self.frame.grid_forget()
            self.visible = False
            
            # Liberar posición en el sistema dual
            if self.assigned_column is not None:
                self.app.release_panel_position('historial')
                print(f"[DEBUG] Historial liberado de columna {self.assigned_column}")
                self.assigned_column = None
            
            # Actualizar la variable del menú
            if hasattr(self.app, 'mostrar_historial'):
                self.app.mostrar_historial.set(False)
    
    def create_historial(self):
        """Crea el widget del historial con estilo consistente - ANCHO 8CM"""
        try:
            # Calcular ancho del panel (8cm)
            panel_width = 300  # Fallback
            if hasattr(self.app, 'window_manager') and hasattr(self.app.window_manager, 'get_panel_width'):
                panel_width = self.app.window_manager.get_panel_width()
            
            print(f"[DEBUG] Historial usando ancho: {panel_width}px (8cm)")
            
            # Frame contenedor principal - hijo del app_frame
            if hasattr(self.app, 'app_frame'):
                parent_frame = self.app.app_frame
            else:
                parent_frame = self.app.master
            
            self.frame = tk.Frame(parent_frame, width=panel_width, relief=tk.RIDGE, borderwidth=1)
            self.frame.pack_propagate(False)
            
            # Grip de redimensionamiento en el borde izquierdo
            self.grip_frame = tk.Frame(self.frame, width=5, bg='#d0d0d0', cursor='sb_h_double_arrow')
            self.grip_frame.pack(side='left', fill='y')
            self.grip_frame.pack_propagate(False)
            
            # Eventos para el grip
            self.grip_frame.bind('<Button-1>', self.start_resize)
            self.grip_frame.bind('<B1-Motion>', self.do_resize)
            self.grip_frame.bind('<Enter>', lambda e: self.grip_frame.config(bg='#b0b0b0'))
            self.grip_frame.bind('<Leave>', lambda e: self.grip_frame.config(bg='#d0d0d0'))
            
            # Frame de contenido
            self.content_frame = tk.Frame(self.frame)
            self.content_frame.pack(side='right', fill='both', expand=True)
            
            # Título
            title_frame = tk.Frame(self.content_frame, bg='#2c3e50')
            title_frame.pack(fill='x')
            
            title_label = tk.Label(
                title_frame,
                text="Historial de Busquedas",
                bg='#2c3e50',
                fg='white',
                font=('Segoe UI', 10, 'bold'),
                pady=8
            )
            title_label.pack(side='left', expand=True)
            
            # Botón cerrar
            close_btn = tk.Button(
                title_frame,
                text="X",
                command=self.hide,
                bg='#2c3e50',
                fg='white',
                font=('Segoe UI', 10, 'bold'),
                bd=0,
                padx=8,
                pady=4
            )
            close_btn.pack(side='right')
            
            # Botones de control
            control_frame = tk.Frame(self.content_frame)
            control_frame.pack(fill='x', padx=5, pady=5)
            
            btn_limpiar = tk.Button(
                control_frame,
                text="Limpiar",
                command=self.limpiar_historial,
                font=('Segoe UI', 9),
                bg='#ffebee',
                fg='#c62828',
                relief='flat',
                padx=10,
                pady=4
            )
            btn_limpiar.pack(side='left', padx=(0, 5))
            
            btn_exportar = tk.Button(
                control_frame,
                text="Exportar",
                command=self.exportar_historial,
                font=('Segoe UI', 9),
                bg='#e8f5e8',
                fg='#2e7d32',
                relief='flat',
                padx=10,
                pady=4
            )
            btn_exportar.pack(side='left')
            
            # TreeView con scrollbar
            tree_frame = tk.Frame(self.content_frame)
            tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Scrollbars
            vsb = ttk.Scrollbar(tree_frame, orient="vertical")
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
            
            # TreeView con el MISMO estilo que el principal
            self.tree = ttk.Treeview(
                tree_frame,
                columns=("Criterio", "Metodo", "Resultados", "Tiempo", "Fecha"),
                show="tree headings",
                style="Custom.Treeview"  # MISMO ESTILO
            )
            
            # Aplicar exactamente el mismo estilo que el TreeView principal
            style = ttk.Style()
            
            # Asegurar que el estilo existe (puede que ya esté configurado)
            style.configure('Custom.Treeview',
                          rowheight=28,
                          background="#ffffff",
                          fieldbackground="#ffffff", 
                          foreground="#2c3e50",
                          selectbackground="#e3f2fd",
                          selectforeground="#0d47a1",
                          borderwidth=1,
                          relief="solid",
                          font=('Segoe UI', 10))  # MISMA FUENTE
            
            style.configure('Custom.Treeview.Heading', 
                          font=('Segoe UI', 10, 'bold'),
                          background="#f8f9fa",
                          foreground="#2c3e50",
                          relief="flat",
                          borderwidth=1)
            
            # Configurar encabezados (busca esta sección)
            self.tree.heading("#0", text="#", anchor=tk.CENTER)
            self.tree.heading("Criterio", text="Criterio", anchor=tk.W)
            self.tree.heading("Metodo", text="M", anchor=tk.CENTER)
            self.tree.heading("Resultados", text="Res.", anchor=tk.CENTER)  # Texto más corto
            self.tree.heading("Tiempo", text="Tiempo", anchor=tk.CENTER)
            self.tree.heading("Fecha", text="Hora", anchor=tk.CENTER)  # Texto más corto

            
            # Configurar columnas con anchos similares al TreeView principal
            self.tree.column("#0", width=35, anchor=tk.CENTER, minwidth=30, stretch=False)  # Reducido de 40
            self.tree.column("Criterio", width=100, anchor=tk.W, minwidth=80, stretch=False)  # Reducido de 120 a 100
            self.tree.column("Metodo", width=30, anchor=tk.CENTER, minwidth=25, stretch=False)  # Reducido de 35
            self.tree.column("Resultados", width=50, anchor=tk.CENTER, minwidth=45, stretch=False)  # Reducido de 70
            self.tree.column("Tiempo", width=55, anchor=tk.CENTER, minwidth=50, stretch=False)  # Reducido de 60
            self.tree.column("Fecha", width=55, anchor=tk.CENTER, minwidth=50, stretch=False)  # Reducido de 80
            
            # Definicion de columnas para ColumnManager
            column_definitions = {
                "Criterio": {"title": "Criterio", "width": 100, "anchor": "w", "minwidth": 80, "stretch": False, "default_visible": True},
                "Metodo": {"title": "M", "width": 30, "anchor": "center", "minwidth": 25, "stretch": False, "default_visible": True},
                "Resultados": {"title": "Res.", "width": 50, "anchor": "center", "minwidth": 45, "stretch": False, "default_visible": True},
                "Tiempo": {"title": "Tiempo", "width": 55, "anchor": "center", "minwidth": 50, "stretch": False, "default_visible": True},
                "Fecha": {"title": "Hora", "width": 55, "anchor": "center", "minwidth": 50, "stretch": False, "default_visible": True},
                "Demandante": {"title": "Demandante", "width": 150, "anchor": "w", "minwidth": 100, "stretch": False, "default_visible": False},
                "Demandado": {"title": "Demandado", "width": 150, "anchor": "w", "minwidth": 100, "stretch": False, "default_visible": False},
                "Ruta": {"title": "Ruta", "width": 200, "anchor": "w", "minwidth": 150, "stretch": False, "default_visible": False}
            }
            
            # Inicializar ColumnManager
            self.column_manager = ColumnManager(self.tree, "historial_tree", column_definitions)
            # Configurar scrollbars
            self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            vsb.configure(command=self.tree.yview)
            hsb.configure(command=self.tree.xview)
            
            # Configurar tags para filas alternadas (MISMO QUE TreeView principal)
            self.tree.tag_configure('evenrow', background='#ffffff')
            self.tree.tag_configure('oddrow', background='#f8f9fa')
            
            # Tags para métodos (MISMOS COLORES que TreeView principal)
            self.tree.tag_configure('cache_method', 
                                  foreground='#1b5e20', 
                                  background='#e8f5e8',
                                  font=('Segoe UI', 10, 'bold'))
            self.tree.tag_configure('tradicional_method', 
                                  foreground='#0d47a1', 
                                  background='#e3f2fd',
                                  font=('Segoe UI', 10, 'bold'))
            self.actualizar_vista()
            
        except Exception as e:
            print(f"Error creando historial: {e}")
            self.frame = None
    
    def start_resize(self, event):
        """Inicia el redimensionamiento"""
        self.resize_start_x = event.x_root
        self.resize_start_width = self.frame.winfo_width()
    
    def do_resize(self, event):
        """Realiza el redimensionamiento"""
        if not self.frame:
            return
        
        # Calcular nuevo ancho
        diff = self.resize_start_x - event.x_root
        new_width = self.resize_start_width + diff
        
        # Limitar ancho entre 250 y 500 píxeles
        new_width = max(250, min(500, new_width))
        
        # Aplicar nuevo ancho
        self.frame.configure(width=new_width)
    
    def agregar_busqueda(self, criterio, metodo, num_resultados, tiempo_total):
        """Agrega una búsqueda al historial - SIEMPRE registra, sin importar si está visible"""
        try:
            # Crear entrada del historial
            entrada = {
                'criterio': criterio,
                'metodo': metodo,
                'resultados': num_resultados,
                'tiempo': f"{tiempo_total:.2f}s",
                'fecha': datetime.now().strftime("%H:%M:%S"),
                'timestamp': datetime.now().isoformat()
            }
            
            # Agregar al inicio de la lista (más reciente primero)
            self.historial_data.insert(0, entrada)
            
            # Limitar a los últimos 100 registros
            if len(self.historial_data) > 100:
                self.historial_data = self.historial_data[:100]
            
            # Guardar en archivo
            self.guardar_historial()
            
            # Actualizar vista solo si está visible
            if self.visible and self.tree:
                self.actualizar_vista()
                
            print(f"[DEBUG] Búsqueda registrada en historial: {criterio} ({metodo}) - {num_resultados} resultados")
            
        except Exception as e:
            print(f"Error agregando búsqueda al historial: {e}")
    
    def actualizar_vista(self):
        """Actualiza la vista del TreeView con los datos del historial"""
        if not self.tree:
            return
        
        try:
            # Limpiar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Agregar entradas del historial
            for i, entrada in enumerate(self.historial_data):
                # Determinar tags según el método y fila alternada
                row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                
                # Tag del método
                metodo = entrada['metodo'].upper()
                if metodo == 'C':
                    method_tag = 'cache_method'
                elif metodo == 'T':
                    method_tag = 'tradicional_method'
                elif metodo == 'A' or metodo == 'E':
                    method_tag = 'tree_method'
                else:
                    method_tag = row_tag
                
                # Combinar tags
                tags = (row_tag, method_tag)
                
                # Insertar en TreeView
                self.tree.insert('', 'end', 
                               text=str(i + 1),
                               values=(
                                   entrada['criterio'],
                                   entrada['metodo'],
                                   entrada['resultados'],
                                   entrada['tiempo'],
                                   entrada['fecha']
                               ),
                               tags=tags)
            
            # Actualizar scrollbars
            if hasattr(self, 'update_scrollbars'):
                self.tree.after_idle(self.update_scrollbars)
                
        except Exception as e:
            print(f"Error actualizando vista historial: {e}")
    
    def cargar_historial(self):
        """Carga el historial desde archivo"""
        try:
            if os.path.exists(self.historial_file):
                with open(self.historial_file, 'r', encoding='utf-8') as f:
                    self.historial_data = json.load(f)
                print(f"[DEBUG] Historial cargado: {len(self.historial_data)} entradas")
            else:
                self.historial_data = []
        except Exception as e:
            print(f"Error cargando historial: {e}")
            self.historial_data = []
    
    def guardar_historial(self):
        """Guarda el historial en archivo"""
        try:
            with open(self.historial_file, 'w', encoding='utf-8') as f:
                json.dump(self.historial_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando historial: {e}")
    
    def limpiar_historial(self):
        """Limpia todo el historial"""
        from tkinter import messagebox
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea limpiar todo el historial?"):
            self.historial_data = []
            self.guardar_historial()
            if self.tree:
                self.actualizar_vista()
            if hasattr(self.app, 'label_estado'):
                self.app.label_estado.config(text="Historial limpiado")
    
    def exportar_historial(self):
        """Exporta el historial a archivo CSV"""
        try:
            from tkinter import filedialog
            import csv
            
            filename = filedialog.asksaveasfilename(
                title="Exportar historial",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Criterio', 'Método', 'Resultados', 'Tiempo', 'Fecha', 'Timestamp'])
                    
                    for entrada in self.historial_data:
                        writer.writerow([
                            entrada['criterio'],
                            entrada['metodo'],
                            entrada['resultados'],
                            entrada['tiempo'],
                            entrada['fecha'],
                            entrada['timestamp']
                        ])
                
                if hasattr(self.app, 'label_estado'):
                    self.app.label_estado.config(text=f"Historial exportado: {filename}")
                    
        except Exception as e:
            print(f"Error exportando historial: {e}")
    
    def on_double_click(self, event):
        """Maneja doble clic en el historial"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item.get('values')
        if not values:
            return
            
        criterio = values[0]  # Primera columna es el criterio
        
        # Realizar nueva búsqueda con el criterio del historial
        if hasattr(self.app, 'entry'):
            self.app.entry.delete(0, tk.END)
            self.app.entry.insert(0, criterio)
            if hasattr(self.app, 'buscar_carpeta'):
                self.app.buscar_carpeta()
    
    def on_enter_key(self, event):
        """Maneja tecla Enter"""
        self.on_double_click(event)
        return "break"
    
    def show_context_menu(self, event):
        """Muestra menú contextual"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Seleccionar el item
        self.tree.selection_set(item)
        
        # Crear menú contextual
        context_menu = tk.Menu(self.tree, tearoff=0)
        context_menu.add_command(label="Buscar de nuevo", command=self.on_double_click)
        context_menu.add_separator()
        context_menu.add_command(label="Copiar criterio", command=self.copy_criterio)
        context_menu.add_separator()
        context_menu.add_command(label="Eliminar entrada", command=self.delete_entry)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def copy_criterio(self):
        """Copia el criterio seleccionado al portapapeles"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item.get('values')
        if not values:
            return
            
        criterio = values[0]
        
        try:
            self.app.master.clipboard_clear()
            self.app.master.clipboard_append(criterio)
            
            if hasattr(self.app, 'label_estado'):
                self.app.label_estado.config(text=f"Criterio copiado: {criterio}")
        except Exception as e:
            print(f"Error copiando criterio: {e}")
    
    def delete_entry(self):
        """Elimina la entrada seleccionada del historial"""
        selection = self.tree.selection()
        if not selection:
            return
        
        try:
            # Obtener índice de la entrada
            item = self.tree.item(selection[0])
            index_text = item.get('text', '0')
            index = int(index_text) - 1  # El texto es el número de fila
            
            # Eliminar de los datos
            if 0 <= index < len(self.historial_data):
                criterio_eliminado = self.historial_data[index]['criterio']
                del self.historial_data[index]
                self.guardar_historial()
                self.actualizar_vista()
                
                if hasattr(self.app, 'label_estado'):
                    self.app.label_estado.config(text=f"Entrada eliminada: {criterio_eliminado}")
        except (ValueError, IndexError) as e:
            print(f"Error eliminando entrada del historial: {e}")
    
    def get_stats(self):
        """Obtiene estadísticas del historial"""
        try:
            total = len(self.historial_data)
            if total == 0:
                return {'total': 0}
            
            # Contar por método
            metodos = {}
            for entrada in self.historial_data:
                metodo = entrada.get('metodo', 'Desconocido')
                metodos[metodo] = metodos.get(metodo, 0) + 1
            
            return {
                'total': total,
                'por_metodo': metodos,
                'mas_reciente': self.historial_data[0]['fecha'] if total > 0 else None
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {'total': 0}