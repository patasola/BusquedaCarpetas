# main.py - Archivo Principal de la Aplicación
"""
Búsqueda Rápida de Carpetas v1.5
Archivo principal de la aplicación
"""

import tkinter as tk
from src.app import BusquedaCarpetaApp

def main():
    """Función principal para iniciar la aplicación"""
    root = tk.Tk()
    app = BusquedaCarpetaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()