# Walkthrough: V.6.3 - PARADISO

Esta versión marca la culminación del proceso de optimización del buscador, logrando un equilibrio perfecto entre velocidad extrema (Índice Nitro) y precisión de resultados.

## 🚀 Mejoras Principales

### 1. Motor de Búsqueda Unificado (Nitro Engine)
- Se ha integrado el índice **SQLite FTS5** como motor principal de la aplicación.
- Las búsquedas de nombres de carpetas y archivos ahora son instantáneas, independientemente de la profundidad de los discos.
- Se ha separado la lógica: el sistema siempre busca nombres/rutas en el índice, y opcionalmente busca **contenido de texto** (PDF, Word, Excel) si se marca la casilla.

### 2. Importación Masiva Inteligente (Smart TXT Import)
- Nuevo botón **📄 Importar TXT** en la configuración.
- Permite cargar múltiples ubicaciones de red o locales de una sola vez.
- **Limpieza Automática:** El sistema detecta y elimina comillas (`"`) y espacios adicionales que Windows añade al usar "Copiar como ruta".

### 3. Normalización de Rutas (Deduplicación)
- Se corrigió el problema de resultados duplicados mediante la normalización de rutas (`os.path.normpath`).
- El sistema ahora reconoce que `D:/Carpeta` y `D:\Carpeta` son el mismo elemento, manteniendo la lista de resultados limpia.

### 4. Metadatos de Precisión (Anti-Ghosts)
- Se refinó la lógica de enriquecimiento de datos.
- Los nombres de Demandante/Demandado solo se asignan a las filas que coinciden **exactamente** con el radicado buscado, evitando la propagación de datos incorrectos en la lista.

## 🛠️ Instrucciones de Mantenimiento
Para asegurar que el sistema vea nuevas carpetas creadas en Windows:
1. Ir a **Configuración e Índice** (Botón ⚡).
2. Si se han añadido nuevas rutas, darle a **⚡ Iniciar Indexación**.
3. El proceso es incremental: solo escaneará lo nuevo o modificado.

## 📦 Archivos Modificados
- `src/core/content_indexer.py`: Lógica de indexación de carpetas y búsqueda literal.
- `src/ui/content_search_modal.py`: Nueva interfaz de importación y gestión masiva.
- `src/managers/search_coordinator.py`: Coordinación de fases de búsqueda (Caché -> Nitro -> Contenido -> Disco).
- `src/ui/results_renderer.py`: Renderizado deduplicado y normalizado.
- `src/managers/app.py`: Sincronización de versiones y estados globales.

---
*V.6.3 - "E quindi uscimmo a riveder le stelle"*
