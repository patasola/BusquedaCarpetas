# Guía para corregir TreeView - Aplicar directamente desde theme_manager

## Problema
Los TreeViews no cambian de color porque:
1. `Colors.TREE_BG` está hardcodeado
2. Los estilos ttk no se aplican correctamente en Windows

## Solución Simple
Modificar `theme_manager.py._actualizar_treeviews()` para aplicar colores DIRECTAMENTE:

```python
def _actualizar_treeviews(self):
    """Actualiza DIRECTAMENTE todos los TreeViews forzando colores"""
    try:
        import tkinter as tk
        
        # TreeView principal
        if hasattr(self.app, 'tree') and self.app.tree:
            tree = self.app.tree
            
            # Forzar colores directamente en el widget
            tree.configure(
                background=self.colores["tree_bg"],
                foreground=self.colores["tree_fg"]
            )
            
            # Tags para filas
            tree.tag_configure('oddrow', background=self.colores["tree_bg"])
            tree.tag_configure('evenrow', background=self.colores["tree_field_bg"])
            
            # Actualizar frame contenedor
            if tree.master:
                tree.master.configure(bg=self.colores["tree_bg"])
        
        # Historial
        if hasattr(self.app, 'historial_manager') and self.app.historial_manager:
            if hasattr(self.app.historial_manager, 'tree') and self.app.historial_manager.tree:
                htree = self.app.historial_manager.tree
                htree.configure(
                    background=self.colores["tree_bg"],
                    foreground=self.colores["tree_fg"]
                )
                htree.tag_configure('oddrow', background=self.colores["tree_bg"])
                htree.tag_configure('evenrow', background=self.colores["tree_field_bg"])
                if htree.master:
                    htree.master.configure(bg=self.colores["tree_bg"])
                    
    except Exception as e:
        print(f"[ThemeManager] Error: {e}")
```

Añadir esto en línea 147 de theme_manager.py, reemplazando el método actual.
