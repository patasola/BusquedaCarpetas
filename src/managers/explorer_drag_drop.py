# src/managers/explorer_drag_drop.py - Arrastrar y soltar en el Explorador de Archivos (OLE Nativo)
"""
Arrastrar y soltar (mover/abrir/recibir) archivos y carpetas con soporte OLE nativo de Windows:
- Permite arrastrar desde el Explorador hacia Windows Explorer (para mover o copiar).
- Permite arrastrar hacia aplicaciones externas como Nitro PDF, Word, Excel, Chrome (para abrir).
- Permite arrastrar y soltar entre carpetas dentro del mismo árbol del panel.
- Permite recibir archivos arrastrados desde Windows Explorer hacia cualquier carpeta del árbol.
"""
import os
import shutil
from tkinter import messagebox
from ..core.ole_drag_drop import (
    do_drag_drop,
    register_drop_target,
    revoke_drop_target,
    DROPEFFECT_MOVE,
    DROPEFFECT_COPY,
    DROPEFFECT_NONE
)

DROP_HIGHLIGHT_TAG = 'drop_target_highlight'

class ExplorerDragDrop:
    """Arrastrar y soltar con integración OLE nativa de Windows en el panel Explorador"""

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
        # Foto de la selección justo antes del clic para soportar arrastre de multi-selección
        self._press_item = None
        self._press_time_selection = ()
        self._ole_drop_target = None

    def setup_drop_target(self):
        """Registra el Treeview del explorador como receptor de soltado (IDropTarget) de Windows"""
        m = self.manager
        tree = getattr(getattr(m, 'ui', None), 'tree', None) or getattr(m, 'tree', None)
        if tree:
            self._ole_drop_target = register_drop_target(
                tree,
                on_drag_over=self.on_ole_drag_over,
                on_drag_leave=self.on_ole_drag_leave,
                on_drop=self.on_ole_drop
            )
            print("[FileExplorer] IDropTarget nativo de Windows registrado en el TreeView")

    def on_press(self, event):
        """Registra qué item y selección había antes del clic sin interferir con Tkinter"""
        m = self.manager
        tree = getattr(getattr(m, 'ui', None), 'tree', None) or getattr(m, 'tree', None)
        if not tree:
            return
        self._press_item = tree.identify_row(event.y)
        self._press_time_selection = tree.selection()
        self._state['start_x'] = event.x
        self._state['start_y'] = event.y

    def on_motion(self, event):
        """Detecta movimiento mayor a 8px e inicia DoDragDrop nativo de Windows"""
        m = self.manager
        tree = getattr(getattr(m, 'ui', None), 'tree', None) or getattr(m, 'tree', None)
        if not tree:
            return

        if not self._state.get('start_x'):
            self._state['start_x'] = event.x
            self._state['start_y'] = event.y
            return

        if not self._state['active']:
            dx = abs(event.x - self._state['start_x'])
            dy = abs(event.y - self._state['start_y'])

            if dx > 8 or dy > 8:
                selection = tree.selection()

                # Si el clic cayó sobre un item que ya era parte de una multi-selección,
                # recuperamos la foto de selección previa antes del colapso de Tkinter
                if (self._press_item and len(self._press_time_selection) > 1
                        and self._press_item in self._press_time_selection):
                    selection = self._press_time_selection
                elif not selection and self._press_item:
                    selection = [self._press_item]

                if selection:
                    paths = [
                        m.item_to_path.get(item) for item in selection
                        if m.item_to_path.get(item) and os.path.exists(m.item_to_path.get(item))
                    ]
                    if paths:
                        self._state['active'] = True
                        self._state['source_items'] = list(selection)
                        self._state['source_paths'] = paths
                        print(f'[FileExplorer] Iniciando OLE DoDragDrop con {len(paths)} elemento(s)')

                        try:
                            # Iniciar bucle modal nativo de Windows DoDragDrop
                            hr, effect, performed = do_drag_drop(paths, preferred_effect=DROPEFFECT_MOVE)
                            print(f'[FileExplorer] DoDragDrop finalizado: hr={hex(hr)}, effect={effect}, performed={performed}')

                            # Si Windows Explorer movió los archivos externamente,
                            # alguno de los archivos originales ya no existirá en su ruta de origen
                            any_moved = any(not os.path.exists(p) for p in paths)
                            if any_moved or (performed & DROPEFFECT_MOVE):
                                tree.after(100, m.refresh_tree)
                        finally:
                            self._state['active'] = False
                            self._state['start_x'] = 0
                            self._state['start_y'] = 0
                            self._hide_drop_indicator()
                            try:
                                tree.config(cursor='')
                            except Exception:
                                pass

    def on_release(self, event):
        """Limpia estado al soltar el botón"""
        m = self.manager
        tree = getattr(getattr(m, 'ui', None), 'tree', None) or getattr(m, 'tree', None)
        self._state['start_x'] = 0
        self._state['start_y'] = 0
        if not self._state['active'] and tree:
            try:
                tree.config(cursor='')
            except Exception:
                pass
            self._hide_drop_indicator()

    # ─── Callbacks de IDropTarget (Soltado sobre nuestro TreeView) ──────────────

    def on_ole_drag_over(self, local_x, local_y, grfKeyState):
        """Llamado continuamente por Windows mientras se arrastra sobre nuestro Treeview"""
        m = self.manager
        tree = getattr(getattr(m, 'ui', None), 'tree', None) or getattr(m, 'tree', None)
        if not tree:
            return DROPEFFECT_NONE

        target_item = tree.identify_row(local_y)
        if target_item:
            # Si es arrastre interno y el destino es uno de los mismos items arrastrados, rechazar
            if self._state['active'] and target_item in self._state['source_items']:
                self._hide_drop_indicator()
                return DROPEFFECT_NONE

            self._show_drop_indicator(target_item)
            return DROPEFFECT_MOVE | DROPEFFECT_COPY
        else:
            self._hide_drop_indicator()
            # Si no está sobre una fila pero sí sobre el área del explorador, permitir en carpeta raíz
            if getattr(m, 'current_path', None) and os.path.isdir(m.current_path):
                return DROPEFFECT_MOVE | DROPEFFECT_COPY
            return DROPEFFECT_NONE

    def on_ole_drag_leave(self):
        """Llamado por Windows cuando el mouse sale de nuestro Treeview"""
        self._hide_drop_indicator()

    def on_ole_drop(self, local_x, local_y, files, grfKeyState):
        """Llamado por Windows cuando se sueltan archivos sobre nuestro Treeview"""
        m = self.manager
        tree = getattr(getattr(m, 'ui', None), 'tree', None) or getattr(m, 'tree', None)
        self._hide_drop_indicator()
        if not files or not tree:
            return DROPEFFECT_NONE

        target_item = tree.identify_row(local_y)
        dest_path = None
        if target_item:
            dest_path = m.item_to_path.get(target_item)
        if not dest_path:
            dest_path = getattr(m, 'current_path', None)

        # Si el destino es un archivo, usar su carpeta padre contenedora
        if dest_path and os.path.isfile(dest_path):
            dest_path = os.path.dirname(dest_path)

        if not dest_path or not os.path.isdir(dest_path):
            print("[FileExplorer] Drop rechazado: destino no es una carpeta válida")
            return DROPEFFECT_NONE

        moved_any = False
        dest_norm = os.path.normcase(os.path.abspath(dest_path))

        for source_path in files:
            if not os.path.exists(source_path):
                continue

            src_norm = os.path.normcase(os.path.abspath(source_path))
            src_dir_norm = os.path.normcase(os.path.abspath(os.path.dirname(source_path)))

            # Evitar mover a la misma carpeta o dentro de sí misma
            if dest_norm == src_dir_norm:
                print(f"[FileExplorer] Saltando (mismo directorio): {source_path}")
                continue
            if dest_norm == src_norm or dest_norm.startswith(src_norm + os.sep):
                print(f"[FileExplorer] Saltando subcarpeta: {source_path}")
                continue

            # Si es arrastre interno: mover
            if self._state['active'] and source_path in self._state['source_paths']:
                if self._move(source_path, dest_path):
                    moved_any = True
            else:
                # Arrastre externo (ej. desde Windows Explorer hacia el explorador de la app): copiar
                try:
                    name = os.path.basename(source_path)
                    new_path = os.path.join(dest_path, name)
                    if os.path.exists(new_path):
                        base, ext = os.path.splitext(name)
                        counter = 1
                        while os.path.exists(new_path):
                            new_path = os.path.join(dest_path, f"{base}_{counter}{ext}" if ext else f"{name}_{counter}")
                            counter += 1

                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, new_path)
                    else:
                        shutil.copy2(source_path, new_path)
                    moved_any = True
                    print(f"[FileExplorer] Copiado (drop externo): {source_path} -> {new_path}")
                except Exception as ex:
                    print(f"[FileExplorer] Error en drop externo: {ex}")

        if moved_any:
            tree.after(100, m.refresh_tree)

        return DROPEFFECT_MOVE

    def _move(self, source_path, dest_path):
        """Ejecuta el movimiento de un item (drag & drop interno mueve)"""
        try:
            item_name = os.path.basename(source_path)
            new_path = os.path.join(dest_path, item_name)

            # Auto-renombrar si existe colisión de nombre
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
        """Resalta la carpeta destino (con el tag drop_target_highlight)"""
        m = self.manager
        tree = getattr(getattr(m, 'ui', None), 'tree', None) or getattr(m, 'tree', None)
        if not tree:
            return
        if self._drop_target_item == target_item:
            return
        self._hide_drop_indicator()
        try:
            self._drop_target_original_tags = tree.item(target_item, 'tags')
            new_tags = tuple(self._drop_target_original_tags or ()) + (DROP_HIGHLIGHT_TAG,)
            tree.item(target_item, tags=new_tags)
            self._drop_target_item = target_item
        except Exception:
            pass

    def _hide_drop_indicator(self):
        """Quita el resaltado de la carpeta destino"""
        m = self.manager
        tree = getattr(getattr(m, 'ui', None), 'tree', None) or getattr(m, 'tree', None)
        if not tree or self._drop_target_item is None:
            return
        try:
            if tree.exists(self._drop_target_item):
                tree.item(self._drop_target_item, tags=self._drop_target_original_tags or ())
        except Exception:
            pass
        self._drop_target_item = None
        self._drop_target_original_tags = None

    def destroy(self):
        """Revoca registro OLE al destruirse el panel"""
        m = self.manager
        tree = getattr(getattr(m, 'ui', None), 'tree', None) or getattr(m, 'tree', None)
        if tree:
            revoke_drop_target(tree)
