# Feature #4: Sincronizar TreeView Principal - Guía Manual

## Problema
Cuando borras/mueves/creas archivos en el explorador, el TreeView principal no se actualiza.

**Estrategia acordada**:
- Delete/Move → remover del TreeView
- Create/Copy → re-ejecutar búsqueda

---

## PARTE 1: Agregar Callback en FileExplorerManager

### Archivo: `src/file_explorer_manager.py`

#### 1.1 Agregar callback en `__init__` (línea ~54)

**Buscar** (después de `self._drop_indicator = None`):
```python
        self._drop_indicator = None
    
    @property
```

**Insertar ENTRE línea 54 y 55**:
```python
        self._drop_indicator = None
        
        # Callback para notificar cambios al TreeView principal
        self.on_file_change_callback = None
    
    @property
```

#### 1.2 Llamar callback después de `delete_selected_item()` (línea ~871)

**Buscar**:
```python
            print(f"[DEBUG] Eliminado exitosamente: {path}")
        else:
            # El error ya fue mostrado por file_ops.delete_item
            pass
    
    def update_shortcuts_context(self):
```

**Reemplazar con**:
```python
            print(f"[DEBUG] Eliminado exitosamente: {path}")
            
            # Notificar al TreeView principal
            if self.on_file_change_callback:
                self.on_file_change_callback('delete', path)
        else:
            # El error ya fue mostrado por file_ops.delete_item
            pass
    
    def update_shortcuts_context(self):
```

#### 1.3 Llamar callback después de `paste_item()` (línea ~985)

**Buscar**:
```python
            # Refresh en background para no congelar UI
            self.ui.tree.after(100, self.refresh_tree)
            print(f'[FileExplorer] {successful} items procesados')
            
        except PermissionError:
```

**Reemplazar con**:
```python
            # Refresh en background para no congelar UI
            self.ui.tree.after(100, self.refresh_tree)
            print(f'[FileExplorer] {successful} items procesados')
            
            # Notificar al TreeView principal
            if self.on_file_change_callback:
                operation = 'move' if mode == 'cut' else 'copy'
                self.on_file_change_callback(operation, source_paths)
            
        except PermissionError:
```

#### 1.4 Llamar callback después de `create_new_folder_inline()` (línea ~360)

**Buscar** (en `_finish_create_folder`):
```python
            # Mensaje de éxito
            if hasattr(self.app, 'label_estado'):
                self.app.label_estado.config(text=f"Carpeta creada: {new_name}")
            
            print(f"[DEBUG] Carpeta creada exitosamente: {nueva_ruta}")
            
        except PermissionError:
```

**Reemplazar con**:
```python
            # Mensaje de éxito
            if hasattr(self.app, 'label_estado'):
                self.app.label_estado.config(text=f"Carpeta creada: {new_name}")
            
            print(f"[DEBUG] Carpeta creada exitosamente: {nueva_ruta}")
            
            # Notificar al TreeView principal
            if self.on_file_change_callback:
                self.on_file_change_callback('create', nueva_ruta)
            
        except PermissionError:
```

---

## PARTE 2: Configurar Callback desde app.py

### Archivo: `src/app.py`

#### 2.1 Agregar método para manejar cambios (insertar después de `update_search_locations`, línea ~343)

```python
    def _on_explorer_file_change(self, operation, paths):
        """Maneja cambios de archivos del explorador"""
        print(f'[App] Cambio en explorador: {operation} - {paths}')
        
        if not hasattr(self, 'tree') or not self.tree:
            return
        
        # Solo procesar si hay resultados en TreeView
        if not self.tree.get_children():
            return
        
        if operation in ['delete', 'move']:
            # Remover items del TreeView
            self._remove_paths_from_tree(paths if isinstance(paths, list) else [paths])
        elif operation in ['create', 'copy']:
            # Re-ejecutar última búsqueda
            self._refresh_last_search()
    
    def _remove_paths_from_tree(self, paths):
        """Remueve rutas específicas del TreeView"""
        for path in paths:
            # Buscar item en TreeView que contenga esta ruta
            for item in self.tree.get_children():
                item_values = self.tree.item(item, 'values')
                if item_values and path in str(item_values[1]):  # Columna 'Ruta Relativa'
                    self.tree.delete(item)
                    print(f'[App] Removido del TreeView: {path}')
                    break
    
    def _refresh_last_search(self):
        """Re-ejecuta la última búsqueda"""
        # TODO: guardar último criterio de búsqueda
        print('[App] Re-ejecutando última búsqueda...')
        # Por ahora solo mensaje, implementar según necesidad
```

#### 2.2 Configurar callback en `_init_managers` (línea ~213)

**Buscar**:
```python
        self.file_explorer_manager = FileExplorerManager(self)
        self.keyboard_manager = KeyboardManager(self)
```

**Insertar DESPUÉS de FileExplorerManager**:
```python
        self.file_explorer_manager = FileExplorerManager(self)
        
        # Configurar callback para sincronizar TreeView
        self.file_explorer_manager.on_file_change_callback = self._on_explorer_file_change
        
        self.keyboard_manager = KeyboardManager(self)
```

---

## Testing

1. Hacer búsqueda → obtener resultados
2. Abrir explorador  
3. Eliminar carpeta que esté en resultados → debería desaparecer del TreeView
4. Crear carpeta nueva → debería mostrar mensaje de re-búsqueda

---

## Rollback si falla
```bash
git checkout src/file_explorer_manager.py src/app.py
```
