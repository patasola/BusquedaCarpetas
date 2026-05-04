import os
import subprocess
import sys

def build(with_console=False):
    type_str = "con CONSOLA" if with_console else "SIN CONSOLA"
    print(f"Iniciando proceso de construcción del ejecutable ({type_str})...")
    
    # Nombre del archivo principal
    main_script = "main.py"
    app_name = "BusquedaRápidaCarpetas"
    if with_console:
        app_name += "_Debug"
    
    if not os.path.exists(main_script):
        print(f"Error: No se encontró {main_script}")
        return

    # Comando de PyInstaller (usando el ejecutable actual de python para evitar problemas de PATH)
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        f"--name={app_name}",
        "--add-data=src;src",
        "--clean",
        main_script
    ]
    
    # Si NO queremos consola, añadimos el flag
    if not with_console:
        command.append("--noconsole")
    
    print(f"Ejecutando: {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
        print(f"\n¡Éxito! El ejecutable '{app_name}.exe' se encuentra en la carpeta 'dist'.")
    except subprocess.CalledProcessError as e:
        print(f"\nError durante la construcción: {e}")

if __name__ == "__main__":
    # Por defecto hacemos ambos o preguntamos? Vamos a hacer que el .bat elija.
    import sys
    console_mode = "--console" in sys.argv
    build(with_console=console_mode)
