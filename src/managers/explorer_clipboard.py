# src/managers/explorer_clipboard.py - Portapapeles del Explorador (Ctrl+X/C/V)
# Extraído de file_explorer_manager.py (refactor incremental, pieza 2/7)
import os
import shutil
from tkinter import messagebox

class ExplorerClipboard:
    """Copiar/cortar/pegar de archivos y carpetas en el explorador"""

    def __init__(self, manager):
        self.manager = manager
        self._paths = []
        self._mode = None

    def copy(self):
        """Copia los items seleccionados al portapapeles"""
        m = self.manager
        selection = m.ui.tree.selection()
        if not selection:
            print('[FileExplorer] No hay selección para copiar')
            return

        paths = [m.item_to_path.get(item) for item in selection if m.item_to_path.get(item)]

        if paths:
            self._paths = paths
            self._mode = 'copy'
            print(f'[FileExplorer] Copiados {len(paths)} items')
        else:
            print('[FileExplorer] Error: no se pudo obtener rutas')

    def cut(self):
        """Corta los items seleccionados al portapapeles (para mover)"""
        m = self.manager
        selection = m.ui.tree.selection()
        if not selection:
            print('[FileExplorer] No hay selección para cortar')
            return

        paths = [m.item_to_path.get(item) for item in selection if m.item_to_path.get(item)]

        if paths:
            self._paths = paths
            self._mode = 'cut'
            print(f'[FileExplorer] Cortados {len(paths)} items')
        else:
            print('[FileExplorer] Error: no se pudo obtener rutas')

    def paste(self):
        """Pega los items del portapapeles en la ubicación seleccionada"""
        m = self.manager

        if not self._paths:
            print('[FileExplorer] Portapapeles vacío')
            return

        # Obtener destino
        selection = m.ui.tree.selection()
        if selection:
            dest_path = m.item_to_path.get(selection[0])
        else:
            dest_path = m.current_path

        if not dest_path or not os.path.isdir(dest_path):
            messagebox.showerror("Error", "Destino debe ser una carpeta")
            return

        source_paths = self._paths
        mode = self._mode

        try:
            successful = 0
            for source_path in source_paths:
                if not os.path.exists(source_path):
                    continue

                item_name = os.path.basename(source_path)
                new_path = os.path.join(dest_path, item_name)

                # Auto-renombrar si existe
                if os.path.exists(new_path):
                    base, ext = os.path.splitext(item_name)
                    counter = 1
                    while os.path.exists(new_path):
                        new_name = f"{base}_{counter}{ext}" if ext else f"{item_name}_{counter}"
                        new_path = os.path.join(dest_path, new_name)
                        counter += 1

                # Copiar o mover
                if mode == 'copy':
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, new_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_path, new_path)
                    successful += 1
                elif mode == 'cut':
                    shutil.move(source_path, new_path)
                    successful += 1

            if mode == 'cut':
                self._paths = []
                self._mode = None

            # Refresh en background para no congelar UI
            m.ui.tree.after(100, m.refresh_tree)
            print(f'[FileExplorer] {successful} items procesados')

            # Notificar al TreeView principal
            if m.on_file_change_callback:
                operation = 'move' if mode == 'cut' else 'copy'
                m.on_file_change_callback(operation, source_paths)

        except PermissionError:
            messagebox.showerror("Error", "Sin permisos para realizar la operación")
        except OSError as e:
            messagebox.showerror("Error", f"Error:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado:\n{str(e)}")
            import traceback
            traceback.print_exc()
