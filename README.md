# BusquedaCarpetas V7 "Purgatorio" 🔍 🏔️

Sistema de búsqueda de alta fidelidad para documentos locales (PDF, Word, Excel, TXT) con acceso compartido a través de red local (LAN). Esta versión unifica el motor de escritorio y el servidor web bajo la arquitectura V7.

## 🚀 Características Principales
- **Arquitectura Unificada V7**: Desktop y Web sincronizados.
- **Motor FTS5**: Búsqueda instantánea en el contenido de miles de archivos.
- **Acceso LAN**: Interfaz web moderna (Glassmorphism) accesible desde cualquier PC de la red.
- **Búsqueda Insensible**: Ignora acentos y mayúsculas automáticamente (ej: "anotación" = "ANOTACION").
- **Apertura Local**: Abre archivos y carpetas directamente en el Explorador de Windows desde el navegador (requiere instalación del cliente).
- **Manual Integrado**: Guía de usuario profesional en `/static/manual.html`.

## 🛠️ Estructura del Proyecto
- `/web_server`: Backend en Flask y Frontend SPA.
- `/src`: Motor de indexación y lógica de búsqueda.
- `/client`: Manejador de protocolo `busqueda://` para integración con Windows.

## 💻 Instalación para Usuarios
1. Acceder a `http://[IP-DEL-SERVIDOR]:8080`.
2. Hacer clic en **🔌 Configurar** para descargar e instalar el acceso directo.
3. ¡Listo! Ya puedes buscar y abrir archivos con un solo clic.

---
*Desarrollado para optimizar el flujo de trabajo en el Consejo Superior de la Judicatura.*
