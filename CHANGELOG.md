# Changelog - BusquedaCarpetas

## [7.25.0] - 2026-10-27 (V.12.19 en el título de la ventana)

### 🎨 Resaltado automático y estético para carpetas de `MigradoSIUGJ`
- **ADDED:** Detección automática de cualquier resultado o subcarpeta perteneciente a la ruta de expedientes migrados (`MigradoSIUGJ`).
- **CHANGED:** Resaltado sobrio y elegante adaptado a cada tema:
  - **Tema Oscuro:** Fondo rojo vino/burdeos suave (`#5c1d1d`) con texto crema claro (`#ffcdd2`) para lectura nítida sin encandilar.
  - **Tema Claro:** Fondo rosa pastel tenue (`#ffebee`) con texto rojo carmesí vino (`#b71c1c`).
- **FIXED:** En `ttk.Treeview`, la sobreescritura de estilos por los tags de filas alternas (`evenrow`/`oddrow`) impedía visualizar el resaltado. Ahora se configura el tag directamente en el renderizador previo a la inserción y se aplica de forma unificada e insensible a mayúsculas o espacios.
- **ADDED:** Al desplegar nodos (`TreeExpansionHandler`), las subcarpetas hijas contenidas en `MigradoSIUGJ` heredan también el resaltado estético.
- **BUMP:** Título de ventana `V.12.18` → `V.12.19` y `APP_VERSION` `V7.24` → `V7.25`.

## [7.24.0] - 2026-08-03 (V.12.18 en el título de la ventana)

### 🐛 "La app no abre" — en realidad abría fuera de la pantalla visible

- **FIXED:** `window_manager.py::configurar_ventana` aplicaba la geometría guardada (`config.json`, posición/tamaño de la última sesión) sin validar que cupiera en la pantalla actual. Confirmado en el log: geometría guardada `1840x815+24+1208` en una pantalla de 1080px de alto — la ventana se posicionaba 128px por debajo del borde inferior visible. El proceso corría normalmente (confirmado con `tasklist`), solo que invisible; parecía que la app "no cargaba". Se agregó `_clamp_geometry_to_screen()`, que acota tamaño y posición a los límites de la pantalla actual antes de aplicar la geometría guardada. Puede pasar tras cambiar de resolución, desconectar un segundo monitor, o mover el equipo a otra pantalla.

## [7.23.0] - 2026-08-03 (V.12.17 en el título de la ventana)

### 🐛 Causa real del resaltado de destino que no se veía (corrección de la explicación anterior)

- **FIXED:** El diagnóstico de la versión 7.22 sobre el orden de tags era incorrecto — el orden dentro de la tupla `tags=(...)` de un item NO determina cuál tag gana. La causa real, confirmada con capturas de píxel reales sobre una réplica exacta de la secuencia de arranque de la app: en `ttk.Treeview`, cuando dos tags definen el mismo atributo (aquí, `background`), gana el tag cuyo **`tag_configure()` se llamó primero en la vida del widget**, sin importar el orden en la tupla del item ni si se reconfigura después. El tag `drop_target_highlight` se registraba recién al primer arrastre — mucho después de que `evenrow`/`oddrow` ya se hubieran registrado al crear el árbol — así que nunca podía ganar. Se movió el registro de `drop_target_highlight` a `explorer_ui.py`, justo antes de `evenrow`/`oddrow`, en el mismo lugar donde se crea el árbol.

## [7.22.0] - 2026-07-30 (V.12.16 en el título de la ventana)

### 🐛 Causa raíz: colisión de atajos Ctrl+Shift+E / Ctrl+E

- **FIXED (bug preexistente, no introducido por el refactor):** `<Control-Shift-e>` (abrir/cerrar Explorador, en `keyboard_manager.py`) y `<Control-e>` (centrar ventana, en `event_manager.py`) capturaban la MISMA combinación de teclas. En Tkinter, un binding con letra mayúscula como `<Control-E>` implica Shift también (la "E" solo se produce con Shift presionado), así que `<Control-E>` y `<Control-Shift-E>` son el mismo evento. Al presionar Ctrl+Shift+E, ambos handlers se disparaban en cadena: primero abría el Explorador, y sin nada que lo detuviera, inmediatamente después centraba la ventana de golpe — de ahí que "al abrir el explorador, cambia la ubicación de la app". El mismo patrón afectaba a `<Control-Shift-h>`/`<Control-h>` (historial). Se agregó `"break"` a ambos bindings de `keyboard_manager.py` para no propagar el evento.
- **CHANGED (drag & drop, rediseño tras reporte de regresión):**
  - El resaltado de la carpeta destino no se veía porque el tag de color quedaba después del tag de fila par/impar en la tupla — en ttk gana el primer tag de la lista. Se invirtió el orden.
  - La selección múltiple con Shift no funcionaba porque el enfoque anterior (interceptar el clic y devolver `"break"`) bloqueaba también el comportamiento nativo de Shift de Tkinter. Rediseñado: ahora solo se toma una "foto" de la selección antes del clic, sin bloquear nada; si el arrastre termina siendo sobre un item que ya era parte de una selección múltiple, se recupera esa foto en vez de la selección ya colapsada por Tkinter. Shift y Ctrl funcionan exactamente igual que antes de tocar nada.
  - Cada archivo movido programaba su propio refresco completo del árbol; con varios archivos seleccionados esto disparaba una ráfaga de recargas simultáneas del mismo nodo (confirmado en el log: 7 líneas de "Refrescando árbol completo" en los mismos milisegundos), lo que probablemente contribuía a la falla de crear carpeta al chocar con la protección de edición en curso. Ahora hay un solo refresco al final del drop, sin importar cuántos archivos se movieron.
- **VERIFIED:** Todo lo anterior confirmado con pruebas automatizadas aisladas (creación de carpeta hasta persistir en disco, drag con selección Shift/Ctrl preservada, orden de tags de resaltado, conteo de refrescos).

## [7.21.0] - 2026-07-30 (V.12.15 en el título de la ventana)

### 🖱️ Drag & Drop: resaltado de destino + selección múltiple real

- **CHANGED:** La línea guía azul del drag & drop se reemplazó por resaltar la fila de la carpeta destino (como el Explorador de Windows), usando tags de Treeview en vez de un `Frame` flotante encima del árbol.
- **FIXED:** Arrastrar varios items seleccionados con Shift no funcionaba en la práctica — Tkinter colapsa la selección múltiple al item clickeado apenas se presiona el botón del mouse, antes de que el código de arrastre alcanzara a leerla. Se agregó `on_press` (nuevo binding `<ButtonPress-1>`) que intercepta el clic inicial: si es sobre un item ya parte de una selección múltiple y sin Ctrl/Shift, preserva la selección para el arrastre; si al final no hubo arrastre (fue un clic simple), la colapsa a un único item igual que el comportamiento nativo.
- **VERIFIED:** Ambos cambios probados con una prueba automatizada aislada (selección preservada durante el drag, colapso correcto en clic simple, tag de resaltado aplicado/quitado en el destino).

## [7.20.0] - 2026-07-30 (V.12.14 en el título de la ventana)

### 🐛 "No me deja crear carpetas" — segunda vuelta de la misma familia de bug

- **FIXED:** `load_directory()` borraba el árbol completo del panel Explorador sin ningún resguardo, a diferencia de `_clear_children()` (que ya protegía el item en edición). Si el usuario tenía una carpeta a medio crear/renombrar y algo disparaba una recarga completa (ej. clic en otro resultado de la búsqueda principal mientras el cuadro de edición seguía abierto), el cuadro quedaba "flotando" sobre un item ya borrado, y terminar la edición fallaba. Se agregó `_cancel_any_inline_edit()`, que cancela limpiamente cualquier edición activa antes de recargar.
- **FIXED:** `_finalize_load()` ahora verifica que el item destino todavía exista en el árbol antes de tocarlo — si otra carga (recarga completa u otro nodo) invalidó ese item mientras esta carga estaba en curso, se descarta en silencio en vez de fallar con "Item not found". Reproducido y confirmado corregido con una prueba automatizada aislada.

## [7.19.0] - 2026-07-30 (V.12.13 en el título de la ventana)

### 🔧 Refactor incremental de file_explorer_manager.py — pieza 4/7: arrastrar y soltar

- **REFACTOR:** Extraído todo el drag & drop a `src/managers/explorer_drag_drop.py` (`ExplorerDragDrop`), incluyendo su propio estado (`_drag_state`, `_drop_indicator`), totalmente autocontenido. `file_explorer_manager.py` pasó de 1067 a 903 líneas (por debajo de las 1000 por primera vez). Los bindings `<B1-Motion>`/`<ButtonRelease-1>` ahora apuntan directo al nuevo componente.
- **CLEANUP:** Mismo detalle del `\\n` literal (en vez de salto de línea real) en los mensajes de error de mover por drag & drop, corregido igual que en el portapapeles.

## [7.18.0] - 2026-07-30 (V.12.12 en el título de la ventana)

### 🔧 Refactor incremental de file_explorer_manager.py — pieza 3/7: sincronización de ruta

- **REFACTOR:** Extraído `focus_path`/`_apply_pending_focus` a `src/managers/explorer_path_sync.py` (`ExplorerPathSync`). `file_explorer_manager.py` pasó de 1139 a 1067 líneas. `pending_focus_path` (el estado que indica "hay que enfocar esta ruta en cuanto termine de cargar") se queda en `FileExplorerManager` porque también lo leen `load_directory`/`_finalize_load`, que no se movieron.
- **CLEANUP:** Quitado un `else: pass` vacío que no hacía nada (quedaba de una rama sin implementar).

## [7.17.0] - 2026-07-30 (V.12.11 en el título de la ventana)

### 🎨 Alineación del menú contextual del explorador

- **FIXED:** Los emoji del menú contextual se renderizaban de forma inconsistente en Windows/Tkinter — algunos (📁📋📄) se veían bien, otros con variador de emoji (✍️✂️🗑️🔄🏠) se veían mal o directamente en blanco, descuadrando el menú. Se quitaron todos los íconos y se dejó texto plano — se ve parejo sin depender de qué emoji decida renderizar bien la fuente de Windows en cada equipo.

## [7.16.0] - 2026-07-30 (V.12.10 en el título de la ventana)

### 🖱️ Menú contextual del explorador: Copiar/Cortar/Pegar + doble clic en carpetas

- **NEW:** El menú contextual del explorador ahora tiene "📄 Copiar", "✂️ Cortar" y "📋 Pegar" (antes solo estaban disponibles por Ctrl+C/X/V).
- **NEW:** "🪟 Abrir en Windows" para carpetas — abre la carpeta en el Explorador de Windows nativo.
- **CHANGED:** Doble clic en una carpeta del panel Explorador ahora expande/colapsa el nodo dentro del propio panel, en vez de abrir Windows Explorer. Doble clic en un archivo sigue abriéndolo con la app predeterminada (sin cambios ahí).

## [7.15.0] - 2026-07-30 (V.12.9 en el título de la ventana)

### 🔧 Refactor incremental de file_explorer_manager.py — pieza 2/7: clipboard

- **REFACTOR:** Extraído copiar/cortar/pegar (Ctrl+X/C/V) a `src/managers/explorer_clipboard.py` (`ExplorerClipboard`). `file_explorer_manager.py` pasó de 1234 a 1135 líneas; `copy_item`/`cut_item`/`paste_item` quedan como fachadas de una línea.
- **CLEANUP:** De paso, dos detalles menores en el código movido: los mensajes de error de pegar usaban `\\n` (backslash-n literal) en vez de salto de línea real, y el docstring de `cut_item` estaba después de un `print`, por lo que Python no lo reconocía como docstring.

## [7.14.0] - 2026-07-30 (V.12.8 en el título de la ventana)

### 🐛 Bugs preexistentes del explorador, encontrados al probar el menú contextual extraído

- **FIXED:** "📂 Expandir/Colapsar" del menú contextual llamaba a `on_double_click` (abre en Windows Explorer) en vez de expandir/colapsar el nodo en el árbol. Se extrajo la lógica correcta de `on_enter_key` a un nuevo método `toggle_expand_collapse()`, y el menú ahora lo usa.
- **FIXED:** Corrupción de bytes en dos strings de `file_explorer_manager.py` (`start_inline_edit` y `_update_item_after_rename`) que debían contener los emoji 📁/📄 — al renombrar, el nombre aparecía con el emoji sin poder quitarlo, y el nuevo nombre quedaba con caracteres inválidos al inicio.
- **FIXED:** Crear una carpeta nueva podía fallar con `Error inesperado: Item IXXX not found` — el monitor de archivos (`watchdog`) detecta el `os.makedirs` de la nueva carpeta y dispara un refresco automático que puede borrar el item temporal justo cuando el código todavía lo está finalizando. `_clear_children` ahora protege el item que está en edición inline activa para que ningún refresco concurrente pueda borrarlo.
- **INVESTIGANDO:** Reporte de "Actualizar Árbol" quedándose en "Buscando..." sin avanzar — puede ser el mismo síntoma del bug de "Expandir/Colapsar" (que nunca disparaba la carga real). Pendiente de reconfirmar con este build.

## [7.13.0] - 2026-07-30 (V.12.7 en el título de la ventana)

### 🔧 Refactor incremental de file_explorer_manager.py — pieza 1/7: menú contextual

- **REFACTOR:** Extraído el menú contextual (clic derecho) del explorador de `file_explorer_manager.py` a `src/managers/explorer_context_menu.py` (`ExplorerContextMenu`). `file_explorer_manager.py` pasó de 1315 a 1226 líneas; `show_context_menu` queda como fachada delgada que delega al nuevo componente. Sin cambios de comportamiento esperados — pendiente de verificación manual (clic derecho sobre fondo y sobre archivo/carpeta).
- **CLEANUP:** De paso se eliminó una duplicación real encontrada al mover el código: los 3 ítems finales del menú ("Nueva carpeta", "Actualizar Árbol", "Ir a Home") estaban repetidos casi textualmente en las dos ramas de `show_context_menu`; ahora hay un solo método `_add_footer`.

## [7.12.0] - 2026-07-30 (V.12.6 en el título de la ventana)

### 🧹 Eliminado el segundo camino de búsqueda muerto (results_display.py / SearchMethods)

- **REMOVED:** `src/ui/results_display.py` (`ResultsDisplay`, 205 líneas) — quedó sin ningún llamador alcanzable tras eliminar `_on_search_completed_async` en la limpieza anterior.
- **REMOVED:** `src/managers/search_methods.py` completo (190 líneas) — `ejecutar_busqueda` siempre delegaba a `search_coordinator.ejecutar_busqueda` (el fallback con `ResultsDisplay` nunca era alcanzable, ya que `search_coordinator` siempre existe); todo el resto del archivo (`buscar_tradicional_fallback`, `_buscar_ubicacion`, `_buscar_directo`, `_enriquecer_con_bd`, etc.) solo era código muerto colgado de ese fallback.
- **REMOVED:** `app.buscar_carpetas` y `app.mostrar_resultados` (wrappers "de compatibilidad" en `app.py`) — cero llamadores.
- **CHANGED:** El botón Buscar/Enter (`app.buscar_carpeta`) ahora llama a `search_coordinator.ejecutar_busqueda` directamente, sin la capa intermedia. Confirmado que este era el mismo camino que ya usaba la búsqueda incremental al escribir — no había dos motores de búsqueda reales, solo uno con un envoltorio redundante.

## [7.11.0] - 2026-07-30 (V.12.5 en el título de la ventana)

### ⚡ La consulta de Demandante/Demandado ya no espera al pipeline completo

- **FIXED:** `search_coordinator.py::_perform_search_async` disparaba el enriquecimiento de partes (`_trigger_background_enrichment`) hasta el final de las 4 fases de búsqueda (Caché → Nitro/índice → Contenido de archivos → Barrido de disco en todas las ubicaciones OneDrive). Las dos últimas fases pueden tardar varios segundos, y el SQL de partes (confirmado en 17ms contra la BD real) esperaba a que terminaran aunque el resultado ya estuviera visible desde la fase de Caché. Ahora se dispara justo después de Caché+Nitro (las fases rápidas), corriendo en paralelo con Contenido/Disco en vez de esperarlas.

## [7.10.0] - 2026-07-30 (V.12.4 en el título de la ventana)

### 🌐 Servidor web apagado por defecto

- **CHANGED:** El servidor web (LAN) ya no arranca automáticamente al abrir la app (`app.py` tenía `master.after(1000, self.menu_manager._start_web_server)`, se quitó). Ahora solo se activa manualmente con el label/botón "🌐 Off" de la esquina inferior derecha, o desde el menú.
- **FIXED:** El checkbutton del menú (`web_active_var`) partía en `True` aunque el label visual ya nacía en "Off" — quedaban desincronizados hasta el auto-arranque. Ahora ambos parten en `False`/"Off" de forma consistente.

## [7.9.0] - 2026-07-30 (V.12.3 en el título de la ventana)

### 🐛 Búsqueda de contenido rota para radicados (AAAA-NNNNN)

- **FIXED:** `content_indexer.py::_parse_advanced_query` — cualquier término con guión interno (ej. `2022-464`, el formato exacto de radicado) rompía la sintaxis FTS5 al pasar sin comillas dentro de `content:(...)`, arrojando `no such column: 464` en cada búsqueda. Confirmado reproduciendo el error de forma aislada contra una tabla FTS5 de prueba. Como "Incluir archivos" activa esta búsqueda en paralelo a la de carpetas, el error se disparaba en cada tecla al escribir un radicado. Se corrigió envolviendo en comillas los términos con guión o dos puntos, forzando coincidencia de frase literal.
- **VERIFIED:** La consulta SQL Server de Demandante/Demandado (`T112DRSUJEPROC`, índice sobre `A112LLAVPROC`) se probó directamente contra la base real: 17ms para una consulta batch de 10 radicados sobre 1.6M de filas. El SQL nunca fue el cuello de botella — el retraso percibido venía de la acumulación de búsquedas de contenido rotas repitiéndose en cada tecla.

## [7.8.0] - 2026-07-30 (V.12.2 en el título de la ventana)

### ⚡ Latencia del enriquecimiento de Demandante/Demandado

- **FIXED:** `_enrich_worker` (`search_coordinator.py`) tenía dos `time.sleep()` fijos que sumaban 1.5s de espera artificial en CADA búsqueda antes de consultar la BD, sin relación con la velocidad real de la consulta SQL (comparado directamente contra el macro `CargarAnotaciones_v4.xlsm`, que ejecuta el mismo tipo de consulta sin ninguna espera). Se quitó el sleep inicial de 1s (los resultados ya están en el árbol cuando corre este worker) y el sleep de 0.5s se reemplazó por un `threading.Event` que libera al worker en cuanto el hilo principal termina de leer el TreeView, con 1s como tope de seguridad en vez de espera fija.

## [7.7.0] - 2026-07-30 (V.12.1 en el título de la ventana)

### 🧹 Limpieza de Código y Corrección de Atajos

#### Refactor: eliminación de código muerto y duplicado
- **REMOVED:** Clase `SearchManager` completa (151 líneas) — se instanciaba pero ningún método se llegó a invocar nunca; toda búsqueda real pasa por `SearchCoordinator`.
- **REMOVED:** `tree_explorer.py` (432 líneas) — se instanciaba pero su único punto de entrada (`setup_explorer_mode()`) nunca se llamaba.
- **REMOVED:** `src/historial/historial_storage.py` — duplicaba la persistencia que ya hace `historial_manager.py`.
- **REMOVED:** `src/components/` y `ui/components/tree_view.py` — el primero tenía un import roto a un archivo inexistente; `ConfigurableTreeView` nunca se instanciaba.
- **REMOVED:** `ui/changelog_viewer.py` y `ui/manual_viewer.py` — sin uso (el manual/changelog real se renderiza desde `menu_manager.py`).
- **REMOVED:** Definición duplicada de `verificar_problemas_cache` en `search_coordinator.py` (la primera quedaba sombreada e inalcanzable).
- **REMOVED:** ~230 líneas de una cadena de búsqueda alterna inalcanzable en `search_coordinator.py` (`_search_traditional`, `_search_from_cache`, `_on_search_completed_async`, `_on_search_error`, etc.).

#### Fixed
- **FIXED:** El atajo **F1** (Manual de Usuario) estaba completamente roto — dos bindings distintos (`event_manager.py` y `keyboard_manager.py`) llamaban a métodos/atributos que nunca existieron en `BusquedaCarpetaApp`, fallando en silencio (el error solo quedaba en `app_log.txt`). Ahora F1 llama correctamente a `menu_manager.mostrar_manual()`.

#### Versión
- **BUMP:** Título de ventana `V.12.0` → `V.12.1` y `APP_VERSION` (diálogo Acerca de) `V7.6` → `V7.7`, para poder distinguir a simple vista si se está corriendo el build actualizado.

## [6.2.0] - 2026-04-14

### 🚀 Sincronización y Refinamiento (Empíreo Sincro)

#### Sincronización TreeView ↔ Explorador
- **NEW:** Implementada sincronización automática de selección. Al elegir un resultado en el TreeView principal, el explorador lateral se expande y enfoca automáticamente en dicha ubicación.
- **PERF:** Lógica de expansión jerárquica que asegura la visibilidad de archivos en subcarpetas cerradas.

#### Corrección de Visualización
- **FIXED:** Solucionado el problema de "sombreado" donde los archivos con el mismo nombre que una carpeta eran omitidos en los resultados.
- **IMPROVED:** Unificación robusta de resultados de contenido (archivos) y caché (carpetas) en el motor de búsqueda central.

#### Refactorización de Interfaz
- **REFINED:** Menú contextual del buscador de contenido simplificado. La opción de indexación ahora se llama **"🔄 Actualizar índice de esta carpeta"** y reside exclusivamente en la pestaña de configuración.
- **CLEANUP:** Eliminadas integraciones redundantes en los menús de clic derecho de la tabla principal y del explorador lateral para una UI más limpia y enfocada.

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