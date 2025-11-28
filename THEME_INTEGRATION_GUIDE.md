# Guía para integrar Theme Manager en app.py

## 1. Añadir import (línea ~27, después de otros imports)
```python
from .theme_manager import ThemeManager
```

## 2. Inicializar en _init_managers (después de crear ui_state_manager, línea ~207)
```python
        self.ui_state_manager = UIStateManager(self)
        
        # Inicializar gestor de temas
        self.theme_manager = ThemeManager(self, tema_inicial="claro")
        self.theme_manager.aplicar_tema()
```

## 3. Añadir atajo F12 en keyboard_manager.py (buscar la sección de atajos globales)
```python
        # F12: Toggle tema
        self.app.master.bind('<F12>', lambda e: self._toggle_tema())
```

## 4. Añadir método en keyboard_manager.py (al final de la clase)
```python
    def _toggle_tema(self):
        """Toggle entre modo claro y oscuro"""
        if hasattr(self.app, 'theme_manager'):
            self.app.theme_manager.toggle_tema()
            return "break"
```

## 5. Opcional: Añadir en menú Ver (menu_manager.py)
```python
view_menu.add_separator()
view_menu.add_command(label="🌓 Cambiar Tema (F12)",
                      command=lambda: self.app.theme_manager.toggle_tema())
```
