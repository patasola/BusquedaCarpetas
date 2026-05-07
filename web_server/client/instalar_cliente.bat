@echo off
chcp 65001 >nul
title Instalador BusquedaCarpetas - Acceso Directo

echo.
echo  ============================================================
echo   BusquedaCarpetas - Instalador de Acceso Directo
echo  ============================================================
echo.
echo  Este instalador configura tu equipo para abrir archivos
echo  directamente desde el buscador web de BusquedaCarpetas.
echo.
echo  Solo necesitas hacer esto UNA VEZ.
echo.
echo  Presiona cualquier tecla para continuar o cierra esta
echo  ventana para cancelar...
pause >nul

echo.
echo  [1/3] Creando directorio de instalacion...
set "INSTALL_DIR=%LOCALAPPDATA%\BusquedaCarpetasClient"
mkdir "%INSTALL_DIR%" 2>nul

echo  [2/3] Copiando manejador de protocolo...
REM Descargar el handler.vbs desde el servidor
powershell -NoProfile -Command "Invoke-WebRequest -Uri 'http://%SERVIDOR_IP%:%SERVIDOR_PUERTO%/client/handler.vbs' -OutFile '%INSTALL_DIR%\handler.vbs'" 2>nul

REM Si no se pudo descargar, intentar desde la misma red
if not exist "%INSTALL_DIR%\handler.vbs" (
    echo  ADVERTENCIA: No se pudo descargar automaticamente.
    echo  Copia manualmente handler.vbs a: %INSTALL_DIR%\
    echo.
    pause
    goto :eof
)

echo  [3/3] Registrando protocolo busqueda:// en Windows...

REG ADD "HKCU\Software\Classes\busqueda" /ve /d "URL:BusquedaCarpetas Protocol" /f >nul
REG ADD "HKCU\Software\Classes\busqueda" /v "URL Protocol" /d "" /f >nul
REG ADD "HKCU\Software\Classes\busqueda\shell" /f >nul
REG ADD "HKCU\Software\Classes\busqueda\shell\open" /f >nul
REG ADD "HKCU\Software\Classes\busqueda\shell\open\command" /ve /d "wscript.exe \"%INSTALL_DIR%\handler.vbs\" \"%%1\"" /f >nul

echo.
echo  ============================================================
echo   INSTALACION COMPLETADA
echo  ============================================================
echo.
echo  Ahora puedes abrir archivos y carpetas directamente
echo  desde el buscador web de BusquedaCarpetas.
echo.
echo  Presiona cualquier tecla para cerrar...
pause >nul
