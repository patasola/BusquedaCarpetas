# main.py - VERSIÓN CORREGIDA (sin el método suelto)
import tkinter as tk
from src.managers.app import BusquedaCarpetaApp

def main():
    root = tk.Tk()
    root.withdraw() # OCULTAR VENTANA INICIALMENTE (Evitar "baile")
    
    root.title("Búsqueda Rápida de Carpetas V.5.1 (Luce Ultima)")
    
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