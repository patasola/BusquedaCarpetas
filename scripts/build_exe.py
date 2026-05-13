import os
import subprocess
import sys
import shutil
import tempfile

def build(with_console=False):
    type_str = "con CONSOLA" if with_console else "SIN CONSOLA"
    print(f"Iniciando proceso de construcción V7.6 TOTAL CONTROL ({type_str})...")
    
    app_name = "BusquedaRápidaCarpetas"
    if with_console:
        app_name += "_Debug"
    
    # 1. Directorios
    current_project_dir = os.getcwd()
    temp_root = os.path.join(tempfile.gettempdir(), f"build_purgatorio_{int(os.getpid())}")
    
    try:
        # 2. Crear entorno de construcción limpio en C:
        print(f"Copiando proyecto a entorno temporal: {temp_root}")
        os.makedirs(temp_root, exist_ok=True)
        
        # Copiar solo lo necesario para el build
        for item in os.listdir(current_project_dir):
            if item in ['.git', '.venv', 'build', 'dist', 'dist-v7', 'dist-v7.5', '__pycache__']:
                continue
            s = os.path.join(current_project_dir, item)
            d = os.path.join(temp_root, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        
        # 3. Ejecutar PyInstaller en el entorno temporal
        print("Iniciando PyInstaller...")
        command = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            f"--name={app_name}",
            "--add-data=src;src",
            "--add-data=web_server;web_server",
            "--add-data=README.md;.",
            "--add-data=CHANGELOG.md;.",
            "--clean",
            "main.py"
        ]
        
        if not with_console:
            command.append("--noconsole")
            
        subprocess.run(command, check=True, cwd=temp_root)
        
        # 4. Copiar resultado de vuelta
        dist_dir = os.path.join(current_project_dir, "dist")
        os.makedirs(dist_dir, exist_ok=True)
        
        exe_source = os.path.join(temp_root, "dist", f"{app_name}.exe")
        exe_dest = os.path.join(dist_dir, f"{app_name}.exe")
        
        print(f"Copiando ejecutable final a: {exe_dest}")
        shutil.copy2(exe_source, exe_dest)
        
        print(f"\nSUCCESS: Versión V7.6 generada correctamente en 'dist'.")
        
    except PermissionError:
        print(f"\nERROR DE PERMISO: No se pudo sobrescribir el archivo en 'dist'.")
        print("Asegúrate de CERRAR la aplicación 'BusquedaRápidaCarpetas' antes de construir.")
    except Exception as e:
        print(f"\nERROR: Error durante la construcción aislada: {e}")
    finally:
        # 5. Limpieza (opcional, pero recomendada)
        print("Limpiando archivos temporales...")
        try:
            shutil.rmtree(temp_root)
        except: pass

if __name__ == "__main__":
    console_mode = "--console" in sys.argv
    build(with_console=console_mode)
