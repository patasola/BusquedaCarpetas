# src/file_monitor.py
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMonitor:
    """Monitorea cambios en el sistema de archivos"""
    
    def __init__(self, explorer_manager):
        self.explorer_manager = explorer_manager
        self.observer = None
        self.event_handler = None
    
    def start(self, path):
        """Inicia el monitoreo de un directorio"""
        self.stop()
        
        try:
            self.event_handler = FileChangeHandler(self.explorer_manager)
            self.observer = Observer()
            self.observer.schedule(self.event_handler, path, recursive=False)
            self.observer.start()
            print(f"[DEBUG] Monitoreo iniciado en: {path}")
        except Exception as e:
            print(f"[ERROR] No se pudo iniciar monitoreo: {e}")
            # El explorador funcionará sin monitoreo automático
    
    def stop(self):
        """Detiene el monitoreo"""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=1)
            self.observer = None
            print("[DEBUG] Monitoreo detenido")

class FileChangeHandler(FileSystemEventHandler):
    """Maneja eventos de cambios en archivos"""
    
    def __init__(self, explorer_manager):
        self.explorer_manager = explorer_manager
    
    def on_created(self, event):
        """Archivo o carpeta creado"""
        print(f"[DEBUG] Creado: {event.src_path}")
        self.explorer_manager.refresh_current_node()
    
    def on_deleted(self, event):
        """Archivo o carpeta eliminado"""
        print(f"[DEBUG] Eliminado: {event.src_path}")
        self.explorer_manager.refresh_current_node()
    
    def on_modified(self, event):
        """Archivo o carpeta modificado"""
        if not event.is_directory:
            print(f"[DEBUG] Modificado: {event.src_path}")
    
    def on_moved(self, event):
        """Archivo o carpeta movido/renombrado"""
        print(f"[DEBUG] Movido: {event.src_path} -> {event.dest_path}")
        self.explorer_manager.refresh_current_node()