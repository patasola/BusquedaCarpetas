import os
import sys
import tkinter as tk
from src.managers.app import BusquedaCarpetaApp

def setup_logging():
    """Redirige stdout y stderr a un archivo si es un ejecutable congelado"""
    if getattr(sys, 'frozen', False):
        log_path = os.path.join(os.path.dirname(sys.executable), "app_log.txt")
        log_file = open(log_path, "w", encoding="utf-8", buffering=1)
        sys.stdout = log_file
        sys.stderr = log_file
        print(f"--- Log iniciado: {os.path.basename(sys.executable)} ---")

def main():
    setup_logging()
    root = tk.Tk()
    root.withdraw() # OCULTAR VENTANA INICIALMENTE (Evitar "baile")
    
    root.title("Búsqueda Avanzada por Contenido V.7.8 - ULTIMATE FIX")
    
    # El tamaño y posición se manejan dentro de BusquedaCarpetaApp -> WindowManager
    app = BusquedaCarpetaApp(root)
    
    # MOSTRAR VENTANA FINALMENTE (Todo cargado)
    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()