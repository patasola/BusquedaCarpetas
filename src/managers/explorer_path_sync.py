# src/managers/explorer_path_sync.py - Sincronización del Explorador con una ruta
# Extraído de file_explorer_manager.py (refactor incremental, pieza 3/7)
import os

class ExplorerPathSync:
    """Sincroniza el panel Explorador con una ruta específica: expande la jerarquía y selecciona el elemento"""

    def __init__(self, manager):
        self.manager = manager

    def focus_path(self, target_path):
        """
        Sincroniza el explorador con una ruta específica:
        Expande la jerarquía y resalta el elemento.
        """
        m = self.manager
        if not target_path or not os.path.exists(target_path):
            return

        print(f"[DEBUG] Sincronizando explorador con: {target_path}")

        # Asegurar que el explorador esté visible
        if not m.is_visible():
            m.show()

        target_path = os.path.normpath(target_path)

        # 1. Verificar si la ruta está dentro de la raíz actual
        if not target_path.lower().startswith(m.current_path.lower()):
            # Si no está en la raíz actual, cargamos la carpeta contenedora como nueva raíz
            # y establecemos un "enfoque pendiente"
            parent_dir = os.path.dirname(target_path)
            if os.path.exists(parent_dir):
                print(f"[DEBUG] Cambiando raíz y estableciendo enfoque pendiente: {target_path}")
                m.pending_focus_path = target_path
                m.load_directory(parent_dir)
            return

        # Limpiar enfoque pendiente si ya estamos en la raíz correcta
        if m.pending_focus_path == target_path:
            m.pending_focus_path = None

        # 2. Descomponer la ruta en partes relativas a la raíz
        try:
            rel_path = os.path.relpath(target_path, m.current_path)
        except ValueError:
            return

        if rel_path == ".":
            # Es la propia raíz
            root_item = m.path_to_item.get(m.current_path)
            if root_item:
                m.tree.selection_set(root_item)
                m.tree.see(root_item)
            return

        parts = rel_path.split(os.sep)
        current_traversal = m.current_path

        # 3. Recorrer y expandir
        for part in parts:
            current_traversal = os.path.join(current_traversal, part)

            # Buscar el item en el árbol
            item = m.path_to_item.get(current_traversal)

            if item:
                # Si es un directorio, expandir y forzar carga de hijos si hace falta
                if os.path.isdir(current_traversal):
                    m.tree.item(item, open=True)
                    if item not in m.loaded_items:
                        m.handle_node_expansion_immediate(item)
                        # CRÍTICO: Permitir que la UI procese la inserción de hijos antes de seleccionar
                        m.tree.update_idletasks()

                # Seleccionar y desplazar a la vista (sin robar foco de teclado)
                m.tree.selection_set(item)
                m.tree.see(item)
            # Si el item no está en el mapa todavía, puede estar cargando: se ignora este tramo

    def apply_pending_focus(self):
        """Aplica el enfoque que quedó pendiente tras una carga asíncrona"""
        m = self.manager
        if not m.pending_focus_path:
            return

        target = m.pending_focus_path
        m.pending_focus_path = None  # Limpiar para evitar bucles
        self.focus_path(target)
