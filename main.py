# main.py - VERSIÓN CORREGIDA (sin el método suelto)
import tkinter as tk
from src.app import BusquedaCarpetaApp

def main():
    root = tk.Tk()
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
    root.mainloop()

if __name__ == "__main__":
    main()