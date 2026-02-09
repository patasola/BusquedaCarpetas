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
    
    root.title("Búsqueda Rápida de Carpetas")
    
    # Configurar tamaño y posición inicial
    root.geometry("900x600")
    
    # Centrar la ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    app = BusquedaCarpetaApp(root)
    
    # MOSTRAR VENTANA FINALMENTE (Todo cargado)
    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()