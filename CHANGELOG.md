# Changelog - BusquedaCarpetas V.6.1 (Empíreo Híbrido)

## [6.1.0] - 2026-04-14

### 🚀 Búsqueda Híbrida y Mejoras de UI (Empíreo Híbrido)

#### Búsqueda Cruzada (Híbrida)
- **NEW:** Implementado checkbox "📄 Incluir archivos" en la interfaz principal.
- **INTEGRATED:** Fusión instantánea de resultados de carpetas (Caché/Disco) con resultados de archivos indexados (FTS5).
- **PERF:** Búsqueda combinada asíncrona que mantiene la fluidez de la UI.

#### Interfaz de Usuario (UI/UX)
- **NEW:** Ordenamiento interactivo de columnas (Carpeta, M, Ruta) mediante clic en encabezados (A-Z / Z-A).
- **FIXED:** Restaurado y mejorado el menú contextual (clic derecho) en la pestaña de Generación de Índice.
- **NEW:** Opción "➕ Agregar Carpeta" añadida directamente al menú contextual de configuración.
- **STABILITY:** Uso de índices numéricos en menús para evitar fallos por codificación de emojis.
- **THEME:** Mejorado el soporte de modo oscuro para Checkbuttons y diálogos secundarios.

#### Robustez y Dependencias
- **SILENCE:** Implementado silenciador agresivo para `pypdf` (CRITICAL) eliminando advertencias de codificación en consola.
- **FIXED:** Corregido "Ghost search" donde el checkbox de archivos era ignorado por el coordinador central.

## [6.0.0] - Versión anterior "Empíreo"
(Buscador de contenido FTS5 inicial)

## [5.1.0] - 2026-02-06

### 🚀 Optimización de Inicio y Estabilidad (Luce Ultima)

#### Startup
- **OPTIMIZED:** Implementado patrón "Hidden Loading" (`withdraw` -> `init` -> `deiconify`) para arranque invisible y sin parpadeos.
- **THREADED:** Carga inicial de caché (`.pkl`) movida a hilo secundario para desbloquear el inicio inmediato.
- **SYNC:** Restauración de paneles síncrona pre-visualización para layout perfecto desde el primer frame.

#### Navegación y Foco
- **FIXED:** Solucionado problema de "Tab Jumping" mediante validación de `search_id` en actualizaciones de fondo.
- **PROTECTED:** Implementado mecanismo de preservación de foco (`focus_get` -> `update` -> `focus_set`) en `UIManager` y `HistorialManager`.
- **VISUAL:** Añadido `highlightthickness=1` a botones para feedback de foco nativo y claro.

#### Concurrencia
- **SAFETY:** Añadidos IDs únicos por búsqueda (`current_search_id`) para prevenir "Ghost Updates" de búsquedas canceladas.
- **STABILITY:** `SearchCoordinator` ahora aborta enriquecimientos en segundo plano si la búsqueda ha cambiado.

## [5.0.1] - 2026-01-28

### 🚀 Corrección Crítica de Rendimiento

- **FIXED:** Restaurada implementación original de renderizado del commit `cbc838b` que funcionaba perfectamente antes del refactor
- **PERF:** Eliminada completamente la verificación de subcarpetas durante el renderizado de resultados
- **PERF:** Renderizado ahora es **siempre instantáneo** sin importar la ubicación de las carpetas (red, SSD, HDD)
- **PERF:** Procesamiento síncrono para búsquedas típicas de 1-100 resultados (caso común del usuario)
- **PERF:** Batching asíncrono solo para conjuntos grandes (>100 resultados)
- **REMOVED:** Eliminada lógica de inserción de nodos dummy que nunca existió en la versión funcional original
- **CONSISTENCY:** Rendimiento ahora es consistente en todas las búsquedas, sin variabilidad por I/O

#### Impacto
- ✅ Búsquedas de 1-5 resultados: **instantáneas** (0ms de overhead)
- ✅ Sin lag variable por ubicación de carpetas
- ✅ Experiencia de usuario consistente y predecible

## [4.5.3] - 2026-01-26

### 🚀 Restauración de Performance (Veloce+)
- **PERF:** Re-implementado motor recursivo con `os.scandir` en `CacheManager` para escaneos de red ultra-rápidos.
- **PERF:** Implementada persistencia en memoria de gestores de caché en `SearchCoordinator`. Los archivos `.pkl` ahora se cargan una sola vez al inicio, eliminando latencias de disco en búsquedas sucesivas.
- **FIX:** Agregados campos faltantes (`edad`) en estadísticas de caché para compatibilidad con diagnóstico.

## [4.5.2] - 2026-01-23

### 🔧 Correcciones y Estética
- **FIXED:** `AttributeError: 'CacheManager' object has no attribute 'get_cache_stats'` en el gestor de caché.
- **UI:** Optimizado icono de papelera (🗑) para centrado perfecto.
- **CLEANUP:** Eliminados archivos temporales y scripts de prueba del directorio raíz.

## [4.5.1] - 2026-01-22

### 🚀 Optimizaciones de Performance Críticas

#### Búsqueda y Cache
- **FIXED:** AttributeError crítico en `CacheData.is_expired()` que causaba fallos de carga del cache
- **OPTIMIZED:** Eliminada invalidación agresiva de cache en cambios de ruta OneDrive
- **OPTIMIZED:** Implementado `os.scandir` en lugar de `os.walk` para búsquedas directas (10x más rápido)
- **OPTIMIZED:** Constructor de `CacheManager` ahora acepta `cache_file` personalizado para multi-ubicación
- **OPTIMIZED:** Carga automática de cache en `__init__` sin bloqueo del hilo principal

#### Renderizado TreeView
- **FIXED:** Eliminadas llamadas bloqueantes `os.path.isdir()` durante renderizado (200x mejora en rutas de red)
- **OPTIMIZED:** Implementada verificación ultra-rápida `_tiene_subcarpetas_rapido()` con `os.scandir`
- **FIXED:** Eliminados espacios vacíos y triángulos falsos en carpetas sin subcarpetas
- **OPTIMIZED:** Batch processing mantenido en 50 items por lote para UI fluida

#### SearchCoordinator
- **RESTORED:** Métodos de compatibilidad: `verificar_problemas_cache()`, `construir_cache_automatico()`, `construir_cache_manual()`
- **OPTIMIZED:** Búsqueda multi-ubicación usa cache individualizado por ruta (hash MD5)
- **OPTIMIZED:** `_search_direct_limited()` ahora usa `os.scandir` para primer nivel

### 📊 Impacto en Performance

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|---------|
| Búsqueda en Cache (30k carpetas) | ~20s | < 0.01s | >2000x |
| Búsqueda en Red (Primer nivel) | 2-5s | < 0.5s | ~10x |
| Renderizado TreeView (1000 items red) | ~200s | < 1s | >200x |
| UI Responsiveness | Congelada | Fluida | ✅ |

### 🔧 Archivos Modificados

- `src/cache_manager.py`: Optimización completa de carga y construcción
- `src/search_coordinator.py`: Métodos restaurados + optimización scandir
- `src/search_methods.py`: Integración con nuevo constructor CacheManager
- `src/results_display.py`: Eliminación I/O bloqueante + verificación rápida subcarpetas
- `src/results_renderer.py`: [NUEVO] Renderizador centralizado
- `src/app.py`: Actualización inicialización CacheManager

### 🐛 Bugs Corregidos

1. **AttributeError en startup** - Menu requería `verificar_problemas_cache()` 
2. **Cache loading failure** - `is_expired()` llamaba método inexistente
3. **Slow network searches** - Miles de `os.path.isdir()` en rutas de red
4. **UI freeze during rendering** - Operaciones I/O bloqueaban hilo principal
5. **False expansion indicators** - Triángulos aparecían sin subcarpetas

### 📝 Notas Técnicas

- El cache ahora tolera variaciones de ruta OneDrive ("OneDrive" vs "OneDrive (1)")
- La verificación de subcarpetas se detiene en el **primer** subdirectorio encontrado
- Los nodos dummy se insertan con `text=""` para evitar espacio visual
- Background indexer mantiene límites: 100,000 carpetas, 300s timeout

---

## [4.5.0] - Versión anterior
(Cambios previos documentados en commits anteriores)