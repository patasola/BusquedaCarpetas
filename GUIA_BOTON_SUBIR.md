# GUÍA MANUAL: Agregar botón ⬆ Subir nivel

## Archivo: src/explorer_ui.py

### Buscar (línea ~90):
```python
        self.btn_home.pack(side='left', padx=2)
        
        # Botón refresh
        self.btn_refresh = tk.Button(
```

### Insertar DESPUÉS de btn_home.pack y ANTES de btn_refresh:
```python
        self.btn_home.pack(side='left', padx=2)
        
        # Botón subir nivel
        self.btn_up = tk.Button(
            nav_frame, 
            text="⬆", 
            bg='#fff9c4', 
            fg='#f57f17',
            command=self.explorer_manager.go_up,
            **btn_config
        )
        self.btn_up.pack(side='left', padx=2)
        
        # Botón refresh
        self.btn_refresh = tk.Button(
```

### Buscar tooltips (línea ~136):
```python
        self._create_tooltip(self.btn_home, "Ir a carpeta personal")
        self._create_tooltip(self.btn_refresh, "Actualizar árbol")
```

### Insertar tooltip para up ENTRE home y refresh:
```python
        self._create_tooltip(self.btn_home, "Ir a carpeta personal")
        self._create_tooltip(self.btn_up, "Subir un nivel")
        self._create_tooltip(self.btn_refresh, "Actualizar árbol")
```

## Método go_up() YA EXISTE en file_explorer_manager.py (línea 532)
