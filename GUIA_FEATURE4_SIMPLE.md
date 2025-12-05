# Feature #4: Indicador TreeView Desactualizado - Guía Final

## Solución: Warning Visual Simple

En lugar de actualizar TreeView/caché, mostrar indicador "⚠️ Resultados desactualizados" cuando hay cambios.

---

## Implementación

### Archivo: `src/app.py`

#### 1. Simplificar `_on_explorer_file_change` (línea ~348)

**REEMPLAZAR TODO el método** con:

```python
    def _on_explorer_file_change(self, operation, paths):
        """Maneja cambios de archivos del explorador"""
        print(f'[App] Cambio en explorador: {operation}')
        
        # Mostrar warning de resultados desactualizados
        self._show_stale_results_warning()
```

#### 2. Agregar método `_show_stale_results_warning` (después línea ~350)

```python
    def _show_stale_results_warning(self):
        """Muestra advertencia de resultados desactualizados"""
        if hasattr(self, 'label_estado'):
            self.label_estado.config(
                text="⚠️ Resultados de búsqueda pueden estar desactualizados - Presiona F5 para actualizar",
                fg='#ff6b00'  # Naranja
            )
```

#### 3. Limpiar warning al buscar

Buscar método que ejecuta búsquedas (probablemente en `search_methods.py` o similar) y agregar:

```python
# Limpiar warning de resultados desactualizados
if hasattr(self.app, 'label_estado'):
    self.app.label_estado.config(text="", fg='black')
```

#### 4. ELIMINAR métodos no necesarios

**ELIMINAR** estos métodos que ya no sirven:
- `_remove_paths_from_tree`
- `_refresh_last_search`

---

## Testing

1. Hacer búsqueda
2. Abrir explorador
3. Eliminar/crear carpeta
4. **Verificar**: Barra de estado muestra "⚠️ Resultados desactualizados" en naranja
5. Presionar F5 o nueva búsqueda
6. **Verificar**: Warning desaparece

---

## Ventajas

✅ Súper simple
✅ No requiere actualizar caché
✅ Usuario sabe que debe refrescar
✅ No bugs de sincronización
