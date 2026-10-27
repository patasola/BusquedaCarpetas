# src/managers/explorer_context_menu.py - Menú contextual del Explorador de Archivos
# Extraído de file_explorer_manager.py (refactor incremental, pieza 1/7)
import tkinter as tk
import os

class ExplorerContextMenu:
    """Construye y muestra el menú contextual (clic derecho) del explorador de archivos"""

    def __init__(self, manager):
        self.manager = manager

    def show(self, event):
        """Muestra menú contextual"""
        m = self.manager
        region = m.tree.identify('region', event.x, event.y)
        context_menu = tk.Menu(m.tree, tearoff=0)

        if region == 'tree':
            item = m.tree.identify_row(event.y)
            if not item:
                return

            m.tree.selection_set(item)
            path = m.item_to_path.get(item)
            if path and path != m.current_path:
                self._add_item_specific(context_menu, path)
                context_menu.add_separator()

        self._add_footer(context_menu)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _add_footer(self, menu):
        """Ítems comunes al final del menú, sin importar dónde se hizo clic"""
        m = self.manager
        menu.add_command(
            label="Nueva carpeta",
            command=m.create_new_folder_inline,
            accelerator="Ctrl+N"
        )
        menu.add_command(
            label="Pegar",
            command=m.paste_item,
            accelerator="Ctrl+V"
        )
        menu.add_separator()
        menu.add_command(
            label="Actualizar árbol",
            command=m.refresh_tree
        )
        menu.add_command(
            label="Ir a Home",
            command=m.go_home
        )

    def _add_item_specific(self, menu, path):
        """Agrega items específicos del archivo/carpeta bajo el cursor"""
        m = self.manager
        if os.path.isdir(path):
            menu.add_command(
                label="Expandir/Colapsar",
                command=m.toggle_expand_collapse
            )
            menu.add_command(
                label="Abrir en Windows",
                command=lambda: m.file_ops.open_item(path)
            )
            menu.add_command(
                label="Renombrar carpeta",
                command=m.handle_f2,
                accelerator="F2"
            )
        elif os.path.isfile(path):
            menu.add_command(
                label="Abrir archivo",
                command=lambda: m.on_double_click(None)
            )
            menu.add_command(
                label="Renombrar archivo",
                command=m.handle_f2,
                accelerator="F2"
            )

        menu.add_separator()
        menu.add_command(
            label="Copiar",
            command=m.copy_item,
            accelerator="Ctrl+C"
        )
        menu.add_command(
            label="Cortar",
            command=m.cut_item,
            accelerator="Ctrl+X"
        )
        menu.add_separator()
        menu.add_command(
            label="Eliminar",
            command=m.delete_selected_item,
            accelerator="Supr"
        )
        menu.add_command(
            label="Copiar ruta",
            command=m.copy_selected_path
        )
