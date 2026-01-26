# src/tree_column_config.py - V2.1 - Bugs corregidos
"""
Módulo V2.1 para gestión avanzada de columnas en TreeView.
Añade columnas dinámicamente y se vincula a TreeViews existentes.
"""

import tkinter as tk
from tkinter import ttk
import json
import os

class TreeColumnConfig:
    """Configura columnas de TreeView con capacidad de añadir columnas dinámicamente"""
    
    # Definiciones de columnas disponibles para cada tipo de TreeView
    COLUMN_DEFINITIONS = {
        "results": {
            "Método": {"title": "M", "width": 35, "anchor": "center", "default_visible": True},
            "Ruta": {"title": "Ruta Relativa", "width": 300, "anchor": "w", "default_visible": True},
            "Demandante": {"title": "Demandante", "width": 200, "anchor": "w", "default_visible": False},
            "Demandado": {"title": "Demandado", "width": 200, "anchor": "w", "default_visible": False},
            "Resultados": {"title": "Res.", "width": 60, "anchor": "center", "default_visible": False},
            "Hora": {"title": "Hora", "width": 80, "anchor": "center", "default_visible": False},
            "Tiempo": {"title": "Tiempo", "width": 70, "anchor": "center", "default_visible": False}
        },
        "historial": {
            "Criterio": {"title": "Criterio", "width": 100, "anchor": "w", "default_visible": True},
            "Metodo": {"title": "M", "width": 30, "anchor": "center", "default_visible": True},
            "Resultados": {"title": "Res.", "width": 50, "anchor": "center", "default_visible": True},
            "Tiempo": {"title": "Tiempo", "width": 55, "anchor": "center", "default_visible": True},
            "Fecha": {"title": "Hora", "width": 55, "anchor": "center", "default_visible": True},
            "Demandante": {"title": "Demandante", "width": 150, "anchor": "w", "default_visible": False},
            "Demandado": {"title": "Demandado", "width": 150, "anchor": "w", "default_visible": False},
            "Ruta": {"title": "Ruta", "width": 200, "anchor": "w", "default_visible": False}
        }
    }
    
    def __init__(self, tree, config_id, app=None):
        """
        Args:
            tree: TreeView instance existente (puede ser None si aún no existe)
            config_id: ID único para persistencia ('results' o 'historial')
            app: Instancia de la app principal para acceder a la configuración global
        """
        self.tree = tree
        self.app = app
        # Track de anchos originales para toggle
        self._original_widths = {}
        self.config_id = config_id
        # Mapear IDs de TreeColumnConfig a claves de ConfigManager
        self.config_keys = {
            "results": "main_column_widths",
            "historial": "history_column_widths"
        }
        
        # Obtener definiciones de columnas para este TreeView
        self.column_defs = self.COLUMN_DEFINITIONS.get(config_id, {})
        
        # Solo inicializar si el tree existe
        if self.tree:
            self._initialize_columns()
            self.load_config()
            self._reconfigure_all_headings()  # Asegurar headings visibles al inicio
            self.bind_context_menu()
        else:
            print(f"[TreeColumnConfig] Tree no existe aún para {config_id}")
    
    def initialize_when_ready(self, tree):
        """Inicializa cuando el TreeView esté listo (para historial)"""
        self.tree = tree
        # Track de anchos originales para toggle
        self._original_widths = {}
        if self.tree:
            self._initialize_columns()
            self.load_config()
            self.bind_context_menu()
            
    def _get_saved_widths(self):
        """Obtiene anchos guardados desde la configuración global"""
        if self.app and hasattr(self.app, 'config'):
            key = self.config_keys.get(self.config_id)
            if key:
                config = self.app.config.get(key, {})
                # Puede ser un dict con 'widths': {...} o un dict directo de anchos
                if isinstance(config, dict):
                    return config.get('widths', config)
        return {}
    
    def _initialize_columns(self):
        """Inicializa todas las columnas definidas en el TreeView"""
        # Configurar heading de columna #0 (Carpeta)
        self.tree.heading("#0", text="Carpeta", anchor="center")
        
        # Obtener columnas actuales (Método, Ruta)
        current_columns = list(self.tree["columns"])
        
        # all_available: todas las definidas en COLUMN_DEFINITIONS
        all_available_columns = list(self.column_defs.keys())
        
        # CRÍTICO: Crear lista de TODAS las columnas manteniendo orden
        # Primero las que ya están, luego las adicionales
        all_columns_ordered = current_columns.copy()
        for col in all_available_columns:
            if col not in all_columns_ordered:
                all_columns_ordered.append(col)
        
        # Configurar TODAS las columnas en el tree (para que existan)
        self.tree.configure(columns=tuple(all_columns_ordered))
        
        # Obtener anchos guardados para no sobreescribirlos con defaults
        saved_widths = self._get_saved_widths()
        
        # Configurar headings y propiedades de TODAS las columnas
        for col_id in all_columns_ordered:
            col_def = self.column_defs.get(col_id, {
                "title": col_id,
                "width": 100,
                "anchor": "w",
                "default_visible": True
            })
            
            # PRIORIDAD: 1. Guardado, 2. ColDef, 3. Hardcoded default
            w = saved_widths.get(col_id, col_def.get("width", 100))
            
            self.tree.heading(col_id, text=col_def.get("title", col_id), anchor=col_def.get("anchor", "center" if col_id == "Método" else "w"))
            self.tree.column(
                col_id,
                width=w,
                anchor=col_def.get("anchor", "w"),
                minwidth=col_def.get("minwidth", 50),
                stretch=True if col_id == "Ruta" else False
            )
        
        # Guardar todas las columnas disponibles
        self.all_columns = all_columns_ordered
    
    def bind_context_menu(self):
        """Vincula menú contextual a las cabeceras del TreeView"""
        if self.tree:
            self.tree.bind("<Button-3>", self._on_right_click)
            self.configure_drag_drop()
        self.setup_doubleclick_autofit()
    
    def configure_drag_drop(self):
        """Configura drag & drop para reordenar columnas"""
        if not self.tree:
            return
        
        # Variables para tracking de drag
        self._drag_data = {
            "dragging": False,
            "column": None,
            "start_x": 0
        }
        
        # Bindings para drag & drop
        self.tree.bind("<ButtonPress-1>", self._on_drag_start, add="+")
        self.tree.bind("<B1-Motion>", self._on_drag_motion, add="+")
        self.tree.bind("<ButtonRelease-1>", self._on_drag_release, add="+")
    
    def _on_drag_start(self, event):
        """Detecta inicio de arrastre en heading"""
        try:
            region = self.tree.identify_region(event.x, event.y)
            if region == "heading":
                source_col_id = self.tree.identify_column(event.x)
                self._drag_data["dragging"] = True
                self._drag_data["source_col"] = source_col_id
                self._drag_data["target_idx"] = None
                self.tree.config(cursor="hand2")
                
                # Crear línea guía visual
                self._create_drop_indicator()
        except:
            pass
    
    def _create_drop_indicator(self):
        """Crea línea vertical guía para drag & drop"""
        try:
            # Determinar color según tema
            line_color = "#3498db"  # Azul base
            if self.app and hasattr(self.app, 'theme_manager'):
                if self.app.theme_manager.tema_actual == "oscuro":
                    line_color = "#00d2ff"  # Cian vibrante para oscuro
                else:
                    line_color = "#2980b9"  # Azul fuerte para claro

            # Frame delgado para línea vertical
            # USAR EL TREE DIRECTAMENTE como parent para que place sea relativo a él
            self._drop_line = tk.Frame(
                self.tree,
                bg=line_color,
                width=3,
                height=self.tree.winfo_height()
            )
            # Inicialmente oculto
            self._drop_line.place_forget()
        except Exception as e:
            print(f"[TreeColumnConfig] Error creando indicador: {e}")
            self._drop_line = None
    
    def _on_drag_motion(self, event):
        """Maneja el dibujo de la guía visual basado en límites calculados por anclaje visual"""
        if not self._drag_data["dragging"]: return
        self.tree.config(cursor="exchange")
        
        try:
            # 1. Obtener orden visual actualizado
            is_tree = ("tree" in self.tree.cget("show"))
            display_cols = list(self.tree["displaycolumns"])
            if display_cols == ["#all"]:
                display_cols = list(self.tree["columns"])
            all_visible = (["#0"] + display_cols) if is_tree else display_cols
            
            # 2. ANCLAJE VISUAL: Encontrar la primera columna visible para anclar coordenadas
            # Insertar item temporal para medición (invisible para el usuario)
            dummy = self.tree.insert("", "end")
            first_vis_idx = -1
            first_vis_x = 0
            
            for i, col in enumerate(all_visible):
                bbox = self.tree.bbox(dummy, col)
                if bbox:
                    first_vis_idx = i
                    first_vis_x = bbox[0]
                    break
            
            # Limpiar dummy
            self.tree.delete(dummy)
            
            if first_vis_idx == -1: return # Nada visible
            
            # 3. Calcular TODOS los bordes (boundaries) relativos al anclaje
            boundaries = []
            curr_x = first_vis_x
            
            # Ir hacia atrás desde el anclaje para encontrar el inicio absoluto (pueda ser negativo)
            for i in range(first_vis_idx - 1, -1, -1):
                curr_x -= self.tree.column(all_visible[i], "width")
            
            boundaries.append(curr_x) # Lado izquierdo de la Col 0
            for col in all_visible:
                curr_x += self.tree.column(col, "width")
                boundaries.append(curr_x) # Lado derecho de cada columna
                
            # 4. Encontrar el hueco (gap) más cercano al ratón
            # En un Tree, el primer gap (índice 0, antes de #0) está prohibido
            valid_boundaries = boundaries[1:] if is_tree else boundaries
            closest_x = min(valid_boundaries, key=lambda b: abs(b - event.x))
            
            # Guardamos el índice real del borde en la lista 'boundaries'
            self._drag_data["target_idx"] = boundaries.index(closest_x)
            
            # 5. Dibujar guía
            if self._drop_line:
                self._drop_line.place(x=closest_x, y=0, height=self.tree.winfo_height())
                    
        except Exception as e:
            print(f"[TreeColumnConfig] Error crítico en motion: {e}")
    
    def _on_drag_release(self, event):
        """Maneja soltar columna para reordenar"""
        try:
            if not self._drag_data["dragging"]:
                return
            
            source_col = self._drag_data.get("source_col")
            target_idx = self._drag_data.get("target_idx")
            
            if source_col and target_idx is not None:
                # La columna #0 (Carpeta) no se puede mover por limitaciones de Tkinter
                if source_col == "#0":
                    print("[TreeColumnConfig] La columna principal '#0' no puede ser movida.")
                else:
                    self._reorder_columns_by_index(source_col, target_idx)
            
        finally:
            # Reset drag state
            self._drag_data["dragging"] = False
            self.tree.config(cursor="")
            
            if hasattr(self, '_drop_line') and self._drop_line:
                try:
                    self._drop_line.destroy()
                    self._drop_line = None
                except: pass

    def _reorder_columns_by_index(self, source_col_id, target_pos_idx):
        """Reordena usando el ID lógico de la fuente y el índice del 'hueco' de destino final"""
        try:
            display_cols = list(self.tree["displaycolumns"])
            if display_cols == ["#all"]:
                display_cols = list(self.tree["columns"])
            
            # Identificar nombre real de la columna arrastrada
            col_name = str(self.tree.column(source_col_id, "id"))
            
            if col_name in display_cols:
                # Quitar de su sitio
                display_cols.remove(col_name)
                
                # Calcular nueva posición:
                # target_pos_idx es el índice del borde en [ #0, C1, C2... ]
                # Gap 1 (después de #0) -> Índice 0 en display_cols
                # Gap 2 (después de C1) -> Índice 1 en display_cols
                is_tree = ("tree" in self.tree.cget("show"))
                adj_idx = target_pos_idx - (1 if is_tree else 0)
                
                # Ajuste de seguridad: no permitir insertar antes de #0 si es un tree
                adj_idx = max(0, min(adj_idx, len(display_cols)))
                
                # Insertar
                display_cols.insert(adj_idx, col_name)
                
                # Aplicar
                self.tree.configure(displaycolumns=tuple(display_cols))
                self.save_config()
                print(f"[TreeColumnConfig] Reordenado: '{col_name}' al hueco visual {target_pos_idx}")
        except Exception as e:
            print(f"[TreeColumnConfig] Error final en reordenamiento: {e}")
    
    def _on_right_click(self, event):
        """Maneja clic derecho - muestra menú si es en cabecera"""
        region = self.tree.identify_region(event.x, event.y)
        
        if region == "heading":
            self._show_column_menu(event)
            return "break"  # Prevenir propagación
    
    def _show_column_menu(self, event):
        """Muestra menú de configuración de columnas"""
        menu = tk.Menu(self.tree, tearoff=0)
        
        # Título
        menu.add_command(label="📋 Configurar Columnas", state="disabled",
                        font=('Segoe UI', 9, 'bold'))
        menu.add_separator()
        
        # Obtener columnas visibles actualmente
        current_display = list(self.tree["displaycolumns"])
        if current_display == ['#all']:
            current_display = list(self.tree["columns"])
        
        # Crear variables para cada columna (para persistir estado)
        self._menu_vars = {}
        
        # Checkbuttons para cada columna disponible
        for col_id in self.all_columns:
            is_visible = col_id in current_display
            col_def = self.column_defs.get(col_id, {})
            col_title = col_def.get("title", col_id)
            
            # Crear variable booleana para esta columna
            var = tk.BooleanVar(value=is_visible)
            self._menu_vars[col_id] = var
            
            # CRÍTICO: indicatoron=True muestra checkbox visual
            menu.add_checkbutton(
                label=f"  {col_title}",
                command=lambda c=col_id: self._toggle_column_safe(c),
                variable=var,
                indicatoron=True
            )
        
        menu.add_separator()
        menu.add_command(label="↩️ Restaurar por defecto", 
                        command=self._reset_to_defaults)
        
        # Mostrar menú
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _toggle_column_safe(self, column_id):
        """Toggle seguro de columna con verificación"""
        try:
            # CRÍTICO: Usar displaycolumns en lugar de columns
            # Esto oculta columnas sin cambiar el mapeo de datos
            all_columns = list(self.tree["columns"])
            current_display = list(self.tree["displaycolumns"])
            
            # Si displaycolumns es '#all', obtener lista real
            if current_display == ['#all']:
                current_display = all_columns.copy()
            
            if column_id in current_display:
                # Ocultar - pero mantener al menos 1 columna
                if len(current_display) > 1:
                    current_display.remove(column_id)
                    self.tree.configure(displaycolumns=tuple(current_display))
                    self.tree.update_idletasks()
                    # NO necesitamos reconfigure headings aquí
                    self.save_config()
                else:
                    print(f"[TreeColumnConfig] No se puede ocultar la última columna")
            else:
                # Mostrar - añadir en posición original
                # Encontrar posición correcta para mantener orden
                insert_pos = len(current_display)
                for col in all_columns:
                    if col == column_id:
                        break
                    if col in current_display:
                        insert_pos = current_display.index(col) + 1
                
                current_display.insert(insert_pos, column_id)
                self.tree.configure(displaycolumns=tuple(current_display))
                self.tree.update_idletasks()
                # NO necesitamos reconfigure headings aquí
                self.save_config()
                
        except Exception as e:
            print(f"[TreeColumnConfig] Error en toggle: {e}")
    
    def load_config(self):
        """Carga configuración guardada desde el config central"""
        try:
            if self.app and hasattr(self.app, 'config'):
                key = self.config_keys.get(self.config_id)
                if not key: return
                
                config = self.app.config.get(key, {})
                visible_columns = config.get('visible_columns')
                
                if visible_columns:
                    # Filtrar solo columnas que existen
                    valid_columns = [c for c in visible_columns if c in self.all_columns]
                    if valid_columns:
                        self.tree.configure(displaycolumns=tuple(valid_columns))
                        
                # Aplicar anchos si están en el config (aunque ya se hace en _initialize_columns)
                # Esto es útil si load_config se llama después
                widths = config.get('widths', {})
                for col_id, w in widths.items():
                    try:
                        self.tree.column(col_id, width=w)
                    except: pass
                return
            
            # Fallback a defaults si no hay app/config
            self._apply_defaults()
            
        except Exception as e:
            print(f"[TreeColumnConfig] Error cargando config central: {e}")
            self._apply_defaults()
    
    def _apply_defaults(self):
        """Aplica columnas visibles por defecto"""
        try:
            default_visible = []
            for col_id in self.all_columns:
                col_def = self.column_defs.get(col_id, {})
                if col_def.get("default_visible", False):
                    default_visible.append(col_id)
            
            if default_visible:
                self.tree.configure(displaycolumns=tuple(default_visible))
            elif self.all_columns:
                # Si no hay defaults, mostrar primeras 3
                self.tree.configure(displaycolumns=tuple(self.all_columns[:3]))
            
            # NO necesitamos reconfigure headings aquí
                
        except Exception as e:
            print(f"[TreeColumnConfig] Error aplicando defaults: {e}")
    
    def save_config(self):
        """Guarda configuración actual en el config central"""
        try:
            if not self.app or not hasattr(self.app, 'config'):
                return
                
            # Obtener displaycolumns actual
            current_display = list(self.tree["displaycolumns"])
            if current_display == ['#all']:
                current_display = list(self.tree["columns"])
            
            # Obtener anchos actuales
            cols = ["#0"] + list(self.tree["columns"])
            widths = {str(col): self.tree.column(col, 'width') for col in cols}
            
            # Preparar datos de configuración
            config_data = {
                'visible_columns': current_display,
                'all_columns': self.all_columns,
                'widths': widths
            }
            
            # Guardar en el config manager
            key = self.config_keys.get(self.config_id)
            if key:
                self.app.config.set(key, config_data)
                # Ojo: ConfigManager.set ya llama a _save_config()
                
            print(f"[TreeColumnConfig] Configuración guardada para {self.config_id}")
                
        except Exception as e:
            print(f"[TreeColumnConfig] Error guardando config central: {e}")
    
    def _reconfigure_all_headings(self):
        """Re-configura todos los headings (útil después de tree.configure)"""
        try:
            # Configurar heading #0
            self.tree.heading("#0", text="Carpeta", anchor="center")
            
            # Configurar headings de todas las columnas visibles
            current_columns = list(self.tree["columns"])
            for col_id in current_columns:
                col_def = self.column_defs.get(col_id, {})
                self.tree.heading(
                    col_id, 
                    text=col_def.get("title", col_id), 
                    anchor=col_def.get("anchor", "w")
                )
        except Exception as e:
            print(f"[TreeColumnConfig] Error reconfigurando headings: {e}")
    
    def _reset_to_defaults(self):
        """Restaura columnas a configuración por defecto"""
        try:
            self._apply_defaults()
            self.save_config()
            print(f"[TreeColumnConfig] Columnas restauradas a defaults para {self.config_id}")
        except Exception as e:
            print(f"[TreeColumnConfig] Error en reset: {e}")


    def configure_doubleclick_resize(self):
        """Configura doble click en headings para autoajustar ancho"""
        if not self.tree:
            return
        
    
    def _autofit_column(self, column_id):
        """Ajusta ancho de columna al contenido mas ancho"""
        try:
            items = self.tree.get_children()
            if not items:
                return
            
            max_width = 100
            
            # Ancho del heading
            heading_text = self.tree.heading(column_id, 'text')
            if heading_text:
                max_width = max(max_width, len(str(heading_text)) * 8)
            
            # Ancho del contenido
            if column_id == '#0':
                for item in items:
                    text = self.tree.item(item, 'text')
                    if text:
                        max_width = max(max_width, len(str(text)) * 7)
                    values = self.tree.item(item, 'values')
                    # identify_column devuelve #N, necesitamos convertir a indice
                    col_num = int(column_id.replace('#', '')) - 1
                    if col_num < len(values):
                        text = str(values[col_num])
                    else:
                        text = ''
            
            new_width = min(max_width + 20, 600)
            self.tree.column(column_id, width=new_width)
            print(f'[TreeColumnConfig] Columna {column_id} ajustada a {new_width}px')
            
        except Exception as e:
            print(f'[TreeColumnConfig] Error autoajustando: {e}')

    
    def setup_doubleclick_autofit(self):
        print('[TreeColumnConfig] Setting up doubleclick autofit...')
        """Setup double click to autofit column width"""
        if self.tree:
            self.tree.bind('<Double-Button-1>', self._handle_doubleclick_autofit, add='+')
    
    def _handle_doubleclick_autofit(self, event):
        
        """Handle double click on heading to autofit column"""
        try:
            region = self.tree.identify_region(event.x, event.y)
            
            if region == 'separator':
                column_id = self.tree.identify_column(event.x)
                if column_id:
                    self._autofit_column_width(column_id)
                    return 'break'
        except:
            pass
    
    def _autofit_column_width(self, column_id):
        """Auto-fit column width to content (toggle entre autofit y restore)"""
        try:
            # Obtener ancho actual
            current_width = self.tree.column(column_id, 'width')
            
            # Si ya guardamos el ancho original, restaurarlo (toggle)
            if column_id in self._original_widths:
                original = self._original_widths[column_id]
                self.tree.column(column_id, width=original)
                del self._original_widths[column_id]
                print(f'[TreeColumnConfig] Column {column_id} restored to {original}px')
                return
            
            # Guardar ancho actual para poder restaurar
            self._original_widths[column_id] = current_width
            
            items = self.tree.get_children()
            if not items:
                return
            
            # Obtener fuente del treeview para medicion real
            try:
                import tkinter.font as tkfont
                font = tkfont.Font(font=self.tree.cget("font"))
            except:
                # Fallback: usar fuente por defecto
                font = None
            
            max_width = 50
            
            # Medir heading
            heading = str(self.tree.heading(column_id, 'text'))
            if font:
                max_width = max(max_width, font.measure(heading) + 50)
            else:
                max_width = max(max_width, len(heading) * 10 + 20)
            
            # Medir contenido
            for item in items:
                if column_id == '#0':
                    text = str(self.tree.item(item, 'text'))
                else:
                    col_num = int(column_id.replace('#', '')) - 1
                    values = self.tree.item(item, 'values')
                    text = str(values[col_num]) if col_num < len(values) else ''
                
                if font:
                    text_width = font.measure(text) + 50
                else:
                    text_width = len(text) * 8 + 40
                    
                max_width = max(max_width, text_width)
            
            # Aplicar con 10% margen (max 800px)
            new_width = int(min(max_width * 1.1, 800))
            self.tree.column(column_id, width=new_width)
            print(f'[TreeColumnConfig] Column {column_id} autofitted: {new_width}px (was {current_width}px)')
            
        except Exception as e:
            print(f'[TreeColumnConfig] Autofit error: {e}')
            import traceback
            traceback.print_exc()
            
            # Calcular ancho máximo del contenido
            for item in items:
                if column_id == '#0':
                    text = str(self.tree.item(item, 'text'))
                else:
                    values = self.tree.item(item, 'values')
                    if col_index < len(values):
                        text = str(values[col_index])
                    else:
                        text = ''
                
                # Calcular ancho en píxeles (aproximado: 1 carácter = 8px)
                text_width = len(text) * 8 + 40  # +40 para padding
                max_width = max(max_width, text_width)
            
            # Aplicar nuevo ancho (máximo 800px para evitar columnas demasiado anchas)
            new_width = min(max_width, 800)
            self.tree.column(column_id, width=new_width)
            print(f'[TreeColumnConfig] Column {column_id} autofitted: {new_width}px (content: {max_width}px)')
            
        except Exception as e:
            print(f'[TreeColumnConfig] Autofit error: {e}')
            import traceback
            traceback.print_exc()
