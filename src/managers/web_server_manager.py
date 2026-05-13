import os
import subprocess
import sys
import socket
import webbrowser
import threading
import time

class WebServerManager:
    """Gestiona el servidor web de BusquedaCarpetas en segundo plano"""
    
    def __init__(self, app):
        self.app = app
        self.process = None
        self.port = 8080
        self.host = "0.0.0.0"
        
    def get_server_script_path(self):
        """Obtiene la ruta al script del servidor de forma robusta"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        # Opción 1: web_server está al lado del ejecutable/base (Desarrollo o portable)
        path1 = os.path.join(base_dir, "web_server", "server.py")
        if os.path.exists(path1): return path1
        
        # Opción 2: El ejecutable está en 'dist/', y web_server está en el padre (Uso común)
        path2 = os.path.join(os.path.dirname(base_dir), "web_server", "server.py")
        if os.path.exists(path2): return path2
        
        return path1 # Fallback

    def is_running(self):
        """Verifica si el servidor está respondiendo en el puerto"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                return s.connect_ex(('127.0.0.1', self.port)) == 0
        except:
            return False

    def start_server(self):
        """Inicia el servidor en segundo plano usando el propio ejecutable con el flag --server"""
        if self.is_running():
            return True, "El servidor ya está en ejecución."
            
        try:
            # Si estamos congelados, sys.executable es el EXE.
            # Si estamos en desarrollo, sys.executable es python.exe, pero necesitamos pasarle el script principal.
            if getattr(sys, 'frozen', False):
                cmd = [sys.executable, "--server"]
            else:
                # En desarrollo, el script principal es main.py (asumimos)
                # Buscamos main.py en el root
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                main_py = os.path.join(base_dir, "main.py")
                cmd = [sys.executable, main_py, "--server"]
            
            # Usar CREATE_NEW_CONSOLE (0x10) para que tenga su propia ventana (que el servidor ocultará)
            # Ya no usamos CREATE_NO_WINDOW porque queremos poder mostrarla después.
            self.process = subprocess.Popen(
                cmd, 
                creationflags=0x00000010, 
                cwd=os.getcwd() if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
            )
            
            # Esperar un momento a que inicie
            time.sleep(2.5) # Más tiempo para Flask
            if self.is_running():
                return True, "Servidor web iniciado en segundo plano."
            else:
                return False, "El servidor se inició pero no responde. Verifica que no haya otro proceso usando el puerto 8080."
                
        except Exception as e:
            return False, f"Error al iniciar servidor: {str(e)}"

    def stop_server(self):
        """Detiene el servidor matando el proceso o enviando señal"""
        if not self.is_running():
            return True, "El servidor no está corriendo."
            
        try:
            # Intentar matar procesos python que tengan el puerto 8080 (Windows)
            # Una forma más limpia es guardar el PID, pero Popen ya nos lo da.
            if self.process:
                self.process.terminate()
                self.process = None
            
            # Fallback agresivo para Windows si Popen no bastó
            subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe", "/T"], 
                          creationflags=0x08000000, capture_output=True)
            
            time.sleep(0.5)
            return True, "Servidor web detenido."
        except Exception as e:
            return False, f"Error al detener servidor: {str(e)}"

    def open_web_ui(self):
        """Abre la interfaz web en el navegador predeterminado"""
        if self.is_running():
            webbrowser.open(f"http://localhost:{self.port}")
            return True
        return False
