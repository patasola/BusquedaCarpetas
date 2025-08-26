# main.py - Punto de entrada V.4.0
from src.app import BusquedaCarpetaApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = BusquedaCarpetaApp(root)
    
    def on_closing():
        if hasattr(app, 'search_engine') and app.search_engine.busqueda_activa:
            app.search_engine.busqueda_cancelada = True
        if hasattr(app, 'cache_manager') and app.cache_manager.construyendo:
            app.cache_manager.construyendo = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()