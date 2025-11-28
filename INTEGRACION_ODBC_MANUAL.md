# Guía de Integración ODBC - Pasos Manuales

## ✅ Ya Completado
- `src/database_manager.py` creado y funcional
- Probado exitosamente con radicado real

## 📝 Pendiente - 4 Archivos a Modificar

### 1️⃣ src/app.py

Busca la línea 109 que dice:
```python
self.results_display = ResultsDisplay(self)
```

Inmediatamente DESPUÉS de esa línea, añade este bloque:

```python
        
        # ODBC Database Manager
        try:
            from .database_manager import DatabaseManager
            self.database_manager = DatabaseManager(self)
        except ImportError:
            self.database_manager = None
```

---

### 2️⃣ src/ui_components.py

**Paso A** - Busca la línea ~332 que dice:
```python
columns=("Método", "Ruta"),
```

Cámbiala a:
```python
columns=("Método", "Ruta", "Demandante", "Demandado"),
```

**Paso B** - Busca las líneas ~344-347 que dicen:
```python
tree.heading("#0", text="Carpeta", anchor=tk.CENTER)
tree.heading("Método", text="M", anchor=tk.CENTER)
tree.heading("Ruta", text="Ruta Relativa", anchor=tk.W)
```

Añade DESPUÉS de la línea de "Ruta":
```python
tree.heading("Demandante", text="Demandante", anchor=tk.W)
tree.heading("Demandado", text="Demandado", anchor=tk.W)
```

**Paso C** - Busca las líneas ~349-351 que dicen:
```python
tree.column("#0", width=200, anchor=tk.W, minwidth=120, stretch=False)
tree.column("Método", width=35, anchor=tk.CENTER, minwidth=30, stretch=False)
tree.column("Ruta", width=300, anchor=tk.W, minwidth=150, stretch=True)
```

Añade DESPUÉS de la línea de "Ruta":
```python
tree.column("Demandante", width=200, anchor=tk.W, minwidth=100, stretch=False)
tree.column("Demandado", width=200, anchor=tk.W, minwidth=100, stretch=False)
```

---

### 3️⃣ src/search_methods.py

**Añadir al final de la clase SearchMethods** (antes del último método), estos dos métodos nuevos:

```python
    def _convertir_a_radicado(self, criterio):
        """Convierte formato AAAA-EXP a radicado de 23 dígitos"""
        import re
        # Detectar si es formato AAAA-EXP
        match = re.match(r'(\d{4})-(\d{3,4})$', criterio)
        if not match:
            return None
        
        año = match.group(1)
        exp = match.group(2).zfill(5)  # Pad a 5 dígitos
        
        # Formato: 110013105017 + AAAA + EXP(5) + 00
        radicado = f"110013105017{año}{exp}00"
        return radicado if len(radicado) == 23 else None
    
    def _enriquecer_con_bd(self, resultados, criterio):
        """Enriquece resultados con datos de la base de datos"""
        if not hasattr(self.app, 'database_manager') or not self.app.database_manager:
            # Sin database manager, retornar con valores vacíos
            return [(r[0], r[1], r[2], "", "") if len(r) == 3 else r for r in resultados]
        
        # Intentar convertir criterio a radicado
        radicado = self._convertir_a_radicado(criterio)
        if not radicado:
            # Si no es formato AAAA-EXP, retornar con valores vacíos
            return [(r[0], r[1], r[2], "", "") if len(r) == 3 else r for r in resultados]
        
        # Consultar base de datos
        demandante, demandado = self.app.database_manager.obtener_info_proceso(radicado)
        
        # Enriquecer resultados (nombre, ruta_rel, ruta_abs, demandante, demandado)
        resultados_enriquecidos = []
        for resultado in resultados:
            if len(resultado) >= 3:
                resultados_enriquecidos.append((
                    resultado[0], resultado[1], resultado[2], demandante, demandado
                ))
            else:
                resultados_enriquecidos.append(resultado)
        
        return resultados_enriquecidos
```

**Modificar método `ejecutar_busqueda`** - Busca donde dice:
```python
self.app.results_display.mostrar_instantaneos(resultados, criterio, metodo)
```

ANTES de esa línea, añade:
```python
resultados = self._enriquecer_con_bd(resultados, criterio)
```

---

### 4️⃣ src/results_display.py

Busca el método `_agregar_por_lotes` y dentro de él, la sección donde se hace `self.app.tree.insert`.

Justo ANTES del `self.app.tree.insert`, añade estas líneas para extraer demandante/demandado:

```python
                    # Extraer demandante/demandado si están disponibles
                    demandante = resultado[3] if len(resultado) > 3 else ""
                    demandado = resultado[4] if len(resultado) > 4 else ""
```

Luego en el `tree.insert`, donde dice `values=(letra_metodo, ruta_rel)`, cámbialo a:
```python
values=(letra_metodo, ruta_rel, demandante, demandado)
```

---

## 🧪 Probar

Ejecuta la app y busca: `2025-226`

Deberías ver las columnas "Demandante" y "Demandado" populadas con los datos de la BD.

---

## 💡 Notas Importantes

- El formato de búsqueda es: `AAAA-EXP` (ej: 2025-226)
- Se convierte automáticamente a: `110013105017` + `AAAA` + `EXP (5 dígitos)` + `00`
- Ejemplo: `2025-226` → `11001310501720250022600` (23 dígitos)
- Si no encuentra en BD, mostrará columnas vacías (sin errores)
