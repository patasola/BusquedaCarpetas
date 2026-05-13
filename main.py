import os
import sys
import tkinter as tk
import socket
import threading
from src.managers.app import BusquedaCarpetaApp

# Puerto para comunicación de instancia única
SINGLE_INSTANCE_PORT = 54321

def setup_logging():
    """Redirige stdout y stderr a un archivo si es un ejecutable congelado"""
    if getattr(sys, 'frozen', False):
        log_path = os.path.join(os.path.dirname(sys.executable), "app_log.txt")
        log_file = open(log_path, "w", encoding="utf-8", buffering=1)
        sys.stdout = log_file
        sys.stderr = log_file
        print(f"--- Log iniciado: {os.path.basename(sys.executable)} ---")

def send_wakeup_signal():
    """Intenta enviar una señal a una instancia ya abierta"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(('127.0.0.1', SINGLE_INSTANCE_PORT))
        s.sendall(b'WAKE_UP')
        s.close()
        return True
    except:
        return False

def listen_for_wakeup(app):
    """Escucha señales de otras instancias para traer la app al frente"""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', SINGLE_INSTANCE_PORT))
        server.listen(5)
        while True:
            conn, addr = server.accept()
            data = conn.recv(1024)
            if data == b'WAKE_UP':
                # Ejecutar en el hilo principal de Tkinter
                app.root.after(0, lambda: app.keyboard_manager._bring_to_front_and_focus())
            conn.close()
    except Exception as e:
        print(f"Error en servidor de instancia única: {e}")

def main():
    # 0. Si se pide modo servidor, arrancar Flask y salir
    if "--server" in sys.argv:
        try:
            # Configurar consola nativa para que pueda ser invocada
            import ctypes
            import time
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            # Asegurar que tiene consola (importante en modo --noconsole)
            kernel32.AllocConsole()
            time.sleep(0.2)
            
            # Ponerle un título único para encontrarla luego
            # Usamos un título muy específico
            unique_title = "BusquedaServer_Console_V75_Live"
            kernel32.SetConsoleTitleW(unique_title)
            time.sleep(0.2)
            
            # Ocultarla por defecto
            hwnd = kernel32.GetConsoleWindow()
            if hwnd:
                user32.ShowWindow(hwnd, 0) # SW_HIDE
            
            # Redirigir log de servidor si es frozen
            if getattr(sys, 'frozen', False):
                log_path = os.path.join(os.path.dirname(sys.executable), "app_log_server.txt")
                log_file = open(log_path, "w", encoding="utf-8", buffering=1)
                sys.stdout = log_file
                sys.stderr = log_file
                print(f"--- Servidor Web V.7.5 (Consola Nativa) iniciado ---")
            
            # Asegurar que el path esté correcto para importar web_server
            sys.path.append(os.getcwd())
            from web_server.server import app as flask_app
            print(f"Iniciando modo servidor Flask en {unique_title}...")
            flask_app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
        except Exception as e:
            print(f"Error fatal en modo servidor: {e}")
        sys.exit(0)

    setup_logging()
    
    # 1. Verificar si ya hay una instancia corriendo
    if send_wakeup_signal():
        print("Instancia ya detectada. Enviando señal de despertar y cerrando.")
        sys.exit(0)
        
    root = tk.Tk()
    root.withdraw() # OCULTAR VENTANA INICIALMENTE
    
    root.title("Búsqueda Rápida de Carpetas - V.12.0")
    
    app = BusquedaCarpetaApp(root)
    
    # 2. Iniciar servidor para escuchar a futuras instancias
    instance_thread = threading.Thread(target=listen_for_wakeup, args=(app,), daemon=True)
    instance_thread.start()
    
    # MOSTRAR VENTANA FINALMENTE
    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()