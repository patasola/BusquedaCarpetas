# MANUAL DE USUARIO - BÚSQUEDA RÁPIDA DE CARPETAS V.5.0 (Luce Intellettual)

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
2. Haz clic en "Copiar" o presiona **F3**
3. La ruta completa se copiará al portapapeles
4. Pégala donde necesites (Ctrl+V)

---

### PASO 5: USANDO EL HISTORIAL (NUEVA FUNCIONALIDAD V.4.5)

1. Presiona **F2** o ve a "Ver" → "Historial de Búsquedas"
2. Se abrirá un panel lateral con tus búsquedas anteriores
3. Haz clic en cualquier búsqueda anterior para repetirla
4. Para cerrar el historial, presiona F2 nuevamente

> **NOVEDAD V.4.5:** El historial aparece al LADO de la ventana principal, no encima. La ventana se agranda automáticamente.

---

### PASO 6: USANDO EL EXPLORADOR DE ARCHIVOS (NUEVA FUNCIONALIDAD V.4.5)

1. Presiona **F3** o ve a "Ver" → "Explorador de Archivos"
2. Se abrirá otro panel lateral con un navegador de carpetas
3. Puedes navegar carpetas haciendo clic en las flechas
4. Para cerrar el explorador, presiona F3 nuevamente

> **NOVEDAD V.4.5:** Puedes tener AMBOS paneles abiertos al mismo tiempo. La primera que abras aparecerá pegada a la aplicación principal. La segunda aparecerá a la derecha de la primera.

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

---

### PASO 8: ACTUALIZAR EL ÍNDICE

Si has creado carpetas nuevas y no aparecen en las búsquedas:

1. Presiona **F5** o ve a "Archivo" → "Construir cache"
2. Espera a que termine la actualización
3. Ahora las carpetas nuevas aparecerán en futuras búsquedas

> El índice se actualiza automáticamente cada 24 horas.

---

### PASO 9: ATAJOS DE TECLADO ÚTILES

**BÁSICOS:**
- `Ctrl+L` - Ir al campo de búsqueda
- `Enter` - Ejecutar búsqueda
- `Esc` - Limpiar campo de búsqueda
- `↑↓` - Navegar resultados

**PANELES (NOVEDAD V.4.5):**
- `F2` - Abrir/cerrar Historial
- `F3` - Abrir/cerrar Explorador
- `Tab` - Navegar entre todos los elementos

**ACCIONES:**
- `Enter` - Abrir carpeta seleccionada
- `F3` - Copiar ruta de carpeta seleccionada
- `F5` - Actualizar índice

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
1. Presiona F5 para actualizar el índice
2. Si sigue sin aparecer, usa "Búsqueda Directa" como método

**PROBLEMA: "La búsqueda está muy lenta"**
**SOLUCIÓN:**
1. Asegúrate de usar el método "Caché"
2. Si es la primera vez, espera que termine de construir el índice

**PROBLEMA: "Los paneles se superponen"**
**SOLUCIÓN:**
- Esto ya no ocurre en V.4.5. Los paneles aparecen lado a lado.
- La ventana se redimensiona automáticamente.

**PROBLEMA: "La aplicación se ve muy pequeña/grande"**
**SOLUCIÓN:**
- En V.4.5 esto es automático según los paneles que tengas abiertos
- App sola: 15cm de ancho
- Con 1 panel: 23cm de ancho
- Con 2 paneles: 31cm de ancho

---

### PASO 12: FLUJO DE TRABAJO RECOMENDADO

**PARA USO DIARIO:**
1. Abre la aplicación
2. Presiona F2 y F3 para abrir ambos paneles
3. Escribe tu búsqueda y presiona Enter
4. Usa el historial para búsquedas repetitivas
5. Usa el explorador para navegar dentro de carpetas encontradas

**PARA DESARROLLADORES:**
1. Busca por tecnología: "node", "python", "react"
2. Usa el historial para proyectos frecuentes
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
5. Abre carpetas con Enter o doble clic
6. Usa F2 para historial, F3 para explorador
7. Ambos paneles pueden estar abiertos al mismo tiempo (V.4.5)

**¡Con estos pasos básicos ya puedes usar la aplicación efectivamente!**

Para funciones avanzadas, experimenta con los diferentes métodos de búsqueda y los atajos de teclado mencionados en este manual.

---

© 2025 - Búsqueda Rápida de Carpetas V.5.0 (Luce Intellettual)
¡Encuentra tus carpetas más rápido que nunca!
