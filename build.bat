@echo off
echo ============================================
echo   Constructor de Ejecutable - Busqueda Rapida
echo ============================================
echo 1. Crear EXE Limpio (Sin Consola - Recomendado)
echo 2. Crear EXE Debug (Con Consola - Para ver errores)
echo 3. Solo ejecutar app (Sin IDE - Ahorra RAM)
echo ============================================
set /p opt="Elija una opcion: "

if "%opt%"=="1" python scripts\build_exe.py
if "%opt%"=="2" python scripts\build_exe.py --console
if "%opt%"=="3" start /b python main.py

pause

