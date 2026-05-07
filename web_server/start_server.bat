@echo off
title BusquedaCarpetas Web Server
cd /d "%~dp0.."
echo.
echo  ============================================
echo   BusquedaCarpetas Web Server V7
echo  ============================================
echo   Iniciando servidor en puerto 8080...
echo   Abre tu navegador en: http://localhost:8080
echo  ============================================
echo.
python web_server/server.py
pause
