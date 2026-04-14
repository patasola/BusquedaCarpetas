# MANUAL DE USUARIO - BÚSQUEDA RÁPIDA DE CARPETAS V.6.2 (Empíreo Sincro)

## CÓMO USAR LA APLICACIÓN

### PASO 1: CONFIGURACIÓN INICIAL

1. **Al abrir la aplicación por primera vez:**
   - Ve al menú "Archivo" → "Seleccionar carpeta"
   - Elige la carpeta raíz donde quieres buscar (ejemplo: `C:\Users\tu_nombre`)
   - La aplicación escaneará automáticamente y creará un índice

2. **Espera a que aparezca el mensaje "Caché construido exitosamente"**
   - Esto solo ocurre la primera vez
   - Siguientes usos serán instantáneos

---

### PASO 2: REALIZAR TU PRIMERA BÚSQUEDA

1. **En el campo de búsqueda (arriba), escribe el nombre de la carpeta:**
   - Ejemplo: "Documents"
   - Ejemplo: "proyecto"
   - Ejemplo: "fotos"

2. **Presiona ENTER o haz clic en el botón "Buscar"**

3. **Los resultados aparecerán en la tabla:**
   - Primera columna: Nombre de la carpeta
   - Segunda columna: Ruta completa
   - Tercera columna: Fecha de modificación

4. **Navega los resultados con las flechas ↑↓ del teclado**

---

### PASO 3: ABRIR UNA CARPETA

Tienes 3 maneras de abrir una carpeta encontrada:

1. **DOBLE CLIC** sobre el resultado
2. Seleccionar el resultado y presionar **ENTER**
3. Seleccionar el resultado y hacer clic en "Abrir"

La carpeta se abrirá en el Explorador de Windows.

---

### PASO 4: COPIAR RUTAS DE CARPETAS

Para copiar la ruta de una carpeta:

1. Selecciona el resultado que te interesa
2. Haz clic en "Copiar" o presiona **F6**
3. La ruta completa se copiará al portapapeles
4. Pégala donde necesites (Ctrl+V)

---

### PASO 5: USANDO EL HISTORIAL (MODIFICADO V.5.0)

1. Presiona **Ctrl+Shift+H** o ve a "Ver" → "Historial de Búsquedas"
2. Se abrirá un panel lateral con tus búsquedas anteriores
3. Haz clic en cualquier búsqueda anterior para repetirla
4. Para cerrar el historial, usa el mismo atajo

> **NOVEDAD V.5.0:** El historial aparece al LADO de la ventana principal.

---

### PASO 6: USANDO EL EXPLORADOR DE ARCHIVOS (MODIFICADO V.5.0)

1. Presiona **Ctrl+Shift+E** o ve a "Ver" → "Explorador de Archivos"
2. Se abrirá otro panel lateral con un navegador de carpetas
3. Puedes navegar carpetas haciendo clic en las flechas
4. Para cerrar el explorador, usa el mismo atajo

> **NOVEDAD V.6.2:** Al seleccionar un resultado en la tabla principal, el explorador se sincroniza automáticamente con esa carpeta o archivo.

---

### PASO 7: MÉTODOS DE BÚSQUEDA DISPONIBLES

Tienes 3 métodos para buscar:

1. **CACHÉ (recomendado):**
   - Es el más rápido (milisegundos)
   - Usa un índice pre-construido
   - Ideal para uso diario

2. **BÚSQUEDA DIRECTA:**
   - Busca en tiempo real en el disco
   - Más lento pero siempre actualizado
   - Útil si acabas de crear carpetas nuevas

3. **WINDOWS SEARCH:**
   - Usa el índice de Windows
   - Solo funciona si tienes Windows Search habilitado

Para cambiar método: Selecciona el botón correspondiente antes de buscar.

### PASO 8: BÚSQUEDA CRUZADA DE ARCHIVOS Y CARPETAS (V.6.2)

1. En la parte superior, marca la casilla **"📄 Incluir archivos"**.
2. Al realizar una búsqueda, verás tanto carpetas (📂) como archivos indexados (📄).
3. Si un archivo y una carpeta tienen el mismo nombre, el sistema mostrará ambos de forma independiente.

### PASO 9: ACTUALIZAR EL ÍNDICE DE CONTENIDO

Si trabajas con archivos (.pdf, .docx, .xlsx, .txt) y quieres buscarlos por su contenido:

1. Ve a "Archivo" → "Búsqueda por Contenido".
2. En la pestaña **Configuración e Índice**, agrega las carpetas que quieres indexar.
3. Haz clic derecho sobre una carpeta en la lista y selecciona **"🔄 Actualizar índice de esta carpeta"**.
4. Una vez terminado, podrás buscar palabras dentro de esos archivos.

---

### PASO 9: ATAJOS DE TECLADO ÚTILES (ACTUALIZADO V.5.1)

**BÁSICOS:**
- `F4` - Cambiar Modo (Numérico/Texto)
- `F5` - Enfocar campo de búsqueda
- `Enter` - Ejecutar búsqueda / Abrir resultado
- `Esc` - Limpiar campo de búsqueda
- `↑↓` - Navegar resultados
- `Tab` - Navegar entre botones y paneles (Ahora con indicador visual)

**PANELES:**
- `Ctrl+Shift+H` - Abrir/cerrar Historial
- `Ctrl+Shift+E` - Abrir/cerrar Explorador
- `F2` - Renombrar (Solo dentro del Explorador de Archivos)

**ACCIONES:**
- `F6` - Copiar ruta de carpeta seleccionada
- `F7` - Abrir carpeta seleccionada
- `F12` - Cambiar Tema (Claro/Oscuro)

---

### PASO 10: CONSEJOS PARA BÚSQUEDAS EFECTIVAS

**BÚSQUEDAS EXITOSAS:**
- No necesitas escribir el nombre completo: "doc" encuentra "Documents"
- No importan mayúsculas/minúsculas: "PROYECTO" = "proyecto"
- Busca palabras clave: "backup" encuentra carpetas de respaldo

**EJEMPLOS PRÁCTICOS:**
- Para carpetas de proyectos: "web", "python", "react"
- Para carpetas personales: "fotos", "música", "documentos"
- Para carpetas de trabajo: "2024", "cliente", "presentación"
- Con múltiples palabras: "proyecto web" busca carpetas que tengan ambas

**BÚSQUEDAS QUE NO FUNCIONAN BIEN:**
- Símbolos especiales como *, ?, \
- Rutas completas (usa solo nombres de carpetas)

---

### PASO 11: SOLUCIÓN DE PROBLEMAS COMUNES

**PROBLEMA: "No encuentra carpetas que sé que existen"**
**SOLUCIÓN:**
1. Ve al menú Archivo > Construir caché
2. Si sigue sin aparecer, usa "Búsqueda Directa" como método

**PROBLEMA: "La búsqueda está muy lenta"**
**SOLUCIÓN:**
1. Asegúrate de usar el método "Caché"
2. La aplicación ahora tiene "Arranque Invisible", así que reiniciar es instantáneo si notas lentitud.

**PROBLEMA: "Los paneles se superponen"**
**SOLUCIÓN:**
- Esto ya no ocurre en V.5.0. Los paneles aparecen lado a lado.
- La ventana se redimensiona automáticamente.

**PROBLEMA: "Cuesta ver qué botón está seleccionado"**
**SOLUCIÓN:**
- En V.5.1, usa la tecla `Tab`. Verás un recuadro negro fino alrededor del botón seleccionado.

---

### PASO 12: FLUJO DE TRABAJO RECOMENDADO

**PARA USO DIARIO:**
1. Abre la aplicación (carga instantánea)
2. Presiona F5 para ir directo al buscador
3. Escribe tu búsqueda y presiona Enter
4. Usa F6 para copiar la ruta o F7 para abrirla

**PARA DESARROLLADORES:**
1. Busca por tecnología: "node", "python", "react"
2. Usa el historial (Ctrl+Shift+H) para proyectos frecuentes
3. Combina múltiples palabras: "api proyecto"

**PARA ADMINISTRADORES:**
1. Busca por fechas: "2024", "enero"
2. Busca por tipo: "backup", "config", "logs"
3. Usa búsqueda directa para carpetas muy recientes

---

## RESUMEN: PASOS BÁSICOS PARA EMPEZAR

1. Configura la carpeta raíz (menú Archivo → Seleccionar carpeta)
2. Escribe el nombre de la carpeta que buscas
3. Presiona Enter
4. Navega resultados con flechas ↑↓
5. Abre carpetas con Enter o F7
6. Usa Ctrl+Shift+H/E para paneles
7. **Disfruta la velocidad mejorada de la V.5.1**

**¡Con estos pasos básicos ya puedes usar la aplicación efectivamente!**

Para funciones avanzadas, experimenta con los diferentes métodos de búsqueda y los atajos de teclado mencionados en este manual.

---

© 2026 - Búsqueda Rápida de Carpetas V.6.2 (Empíreo Sincro)
¡Encuentra tus carpetas y archivos más rápido que nunca!
