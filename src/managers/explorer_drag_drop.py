# src/managers/explorer_drag_drop.py - Arrastrar y soltar en el Explorador de Archivos
# Extraído de file_explorer_manager.py (refactor incremental, pieza 4/7)
import os
import shutil
from tkinter import messagebox

DROP_HIGHLIGHT_TAG = 'drop_target_highlight'

class ExplorerDragDrop:
    """Arrastrar y soltar (mover) archivos/carpetas dentro del panel Explorador"""

    def __init__(self, manager):
        self.manager = manager
        self._state = {
            'active': False,
            'source_items': [],
            'source_paths': [],
            'start_x': 0,
            'start_y': 0
        }
        self._drop_target_item = None
        self._drop_target_original_tags = None
        # Foto de la selección justo antes del clic, tomada SIN interferir con el
        # comportamiento normal de Tkinter (que puede colapsarla a un solo item si
        # no se usó Ctrl/Shift). Sirve para arrastrar varios items ya seleccionados.
        self._press_item = None
        self._press_time_selection = ()

    def on_press(self, event):
        """
        Registra qué item y qué selección había justo antes del clic. No modifica
        nada ni bloquea el evento: Tkinter sigue procesando el clic con su
        comportamiento normal (Ctrl/Shift para selección múltiple funcionan igual
        que siempre). Solo guardamos esta foto por si el clic termina siendo el
        inicio de un arrastre de varios items ya seleccionados.
        """
        m = self.manager
        self._press_item = m.ui.tree.identify_row(event.y)
        self._press_time_selection = m.ui.tree.selection()

    def on_motion(self, event):
        """Detecta movimiento y activa drag si threshold > 30px"""
        m = self.manager
        # Inicializar start position en primer motion
        if not self._state.get('start_x'):
            self._state['start_x'] = event.x
            self._state['start_y'] = event.y
            return

        # Activar drag solo si movimiento > 30px
        if not self._state['active']:
            dx = abs(event.x - self._state['start_x'])
            dy = abs(event.y - self._state['start_y'])

            if dx > 10 or dy > 10:
                selection = m.ui.tree.selection()

                # Si el clic que inició el arrastre cayó sobre un item que YA era
                # parte de una selección múltiple antes de ese clic, Tkinter la
                # habría colapsado a un solo item; usamos la foto de antes del
                # clic para poder arrastrar todos los items originalmente
                # seleccionados (con Ctrl o con Shift).
                if (self._press_item and len(self._press_time_selection) > 1
                        and self._press_item in self._press_time_selection):
                    selection = self._press_time_selection

                if selection:
                    self._state['active'] = True
                    self._state['source_items'] = list(selection)
                    self._state['source_paths'] = [
                        m.item_to_path.get(item) for item in selection
                        if m.item_to_path.get(item)
                    ]
                    print(f'[FileExplorer] Drag iniciado: {len(self._state["source_paths"])} items')

        # Si drag activo, resaltar la carpeta destino (validación al soltar)
        if self._state['active']:
            target_item = m.ui.tree.identify_row(event.y)
            if target_item and target_item not in self._state['source_items']:
                # Siempre mostrar como válido, validar al soltar
                self._show_drop_indicator(target_item)
                m.ui.tree.config(cursor='exchange')
            else:
                self._hide_drop_indicator()
                m.ui.tree.config(cursor='')

    def on_release(self, event):
        """Ejecuta drop al soltar"""
        m = self.manager
        moved_any = False
        try:
            # Reset start position
            self._state['start_x'] = 0
            self._state['start_y'] = 0

            # Limpiar UI
            m.ui.tree.config(cursor='')
            self._hide_drop_indicator()

            if not self._state['active']:
                return

            # Obtener destino
            target_item = m.ui.tree.identify_row(event.y)

            if target_item and target_item not in self._state['source_items']:
                dest_path = m.item_to_path.get(target_item)

                # Si destino es archivo, usar su carpeta padre
                if dest_path and os.path.isfile(dest_path):
                    dest_path = os.path.dirname(dest_path)

                # Validar carpeta válida
                if dest_path and os.path.isdir(dest_path):
                    # Mover cada item válido
                    for source_path in self._state['source_paths']:
                        source_dir = os.path.dirname(source_path)

                        # Rechazar si: misma carpeta O subcarpeta del origen
                        if dest_path == source_dir:
                            print(f'[FileExplorer] Saltando: {source_path}')
                            continue

                        if dest_path.startswith(source_path + os.sep):
                            print(f'[FileExplorer] Saltando subcarpeta: {source_path}')
                            continue

                        # Drop válido: ejecutar movimiento
                        if self._move(source_path, dest_path):
                            moved_any = True
                else:
                    print('[FileExplorer] Drop rechazado: destino no es carpeta válida')

        finally:
            # Reset drag state
            self._state = {
                'active': False,
                'source_items': [],
                'source_paths': [],
                'start_x': 0,
                'start_y': 0
            }
            # Un solo refresco al final, sin importar cuántos items se movieron
            # (antes cada item programaba su propio refresco por separado, lo
            # que con varios items disparaba una ráfaga de recargas completas
            # del árbol casi simultáneas).
            if moved_any:
                m.ui.tree.after(100, m.refresh_tree)

    def _move(self, source_path, dest_path):
        """Ejecuta el movimiento de un item (drag & drop siempre mueve, nunca copia).
        Retorna True si el movimiento se realizó."""
        m = self.manager
        try:
            item_name = os.path.basename(source_path)
            new_path = os.path.join(dest_path, item_name)

            # Auto-renombrar si existe
            if os.path.exists(new_path):
                base, ext = os.path.splitext(item_name)
                counter = 1
                while os.path.exists(new_path):
                    if ext:
                        new_name = f"{base}_{counter}{ext}"
                    else:
                        new_name = f"{item_name}_{counter}"
                    new_path = os.path.join(dest_path, new_name)
                    counter += 1
                print(f'[FileExplorer] Auto-renombrado a: {os.path.basename(new_path)}')

            # Drag & Drop siempre mueve
            shutil.move(source_path, new_path)
            print(f'[FileExplorer] Movido (drag): {source_path} -> {new_path}')
            return True

        except PermissionError:
            messagebox.showerror("Error", "Sin permisos para mover")
        except OSError as e:
            messagebox.showerror("Error", f"Error moviendo:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")
            import traceback
            traceback.print_exc()
        return False

    def _show_drop_indicator(self, target_item):
        """Resalta la carpeta destino (como el Explorador de Windows) en vez de una línea guía.
        El tag 'drop_target_highlight' ya está registrado en explorer_ui.py, ANTES que
        'evenrow'/'oddrow' — en ttk.Treeview gana el tag registrado primero, así que ese
        orden es lo que determina que el resaltado sea visible por encima del rayado."""
        m = self.manager
        if self._drop_target_item == target_item:
            return
        self._hide_drop_indicator()
        try:
            self._drop_target_original_tags = m.tree.item(target_item, 'tags')
            new_tags = tuple(self._drop_target_original_tags or ()) + (DROP_HIGHLIGHT_TAG,)
            m.tree.item(target_item, tags=new_tags)
            self._drop_target_item = target_item
        except Exception:
            pass

    def _hide_drop_indicator(self):
        """Quita el resaltado de la carpeta destino"""
        m = self.manager
        if self._drop_target_item is None:
            return
        try:
            if m.tree.exists(self._drop_target_item):
                m.tree.item(self._drop_target_item, tags=self._drop_target_original_tags or ())
        except Exception:
            pass
        self._drop_target_item = None
        self._drop_target_original_tags = None
