# src/components/tree_tooltip.py - Tooltip reutilizable para TreeViews
import tkinter as tk

class TreeViewTooltip:
    """Tooltip simple con ruta truncada - Componente reutilizable"""
    
    def __init__(self, treeview):
        self.treeview = treeview
        self.tooltip_window = None
        self.current_item = None
        self.after_id = None
        
        # Configurar eventos
        self.treeview.bind("<Motion>", self._on_motion)
        self.treeview.bind("<Leave>", self._on_leave)
        self.treeview.bind("<Button-1>", self._hide_tooltip)
        
    def _on_motion(self, event):
        """Maneja movimiento del mouse"""
        item = self.treeview.identify_row(event.y)
        
        if item != self.current_item:
            self.current_item = item
            self._hide_tooltip()
            
            if item:
                self.after_id = self.treeview.after(500, 
                    lambda: self._show_tooltip(event.x_root, event.y_root, item))
    
    def _on_leave(self, event):
        """Mouse salió del TreeView"""
        self._hide_tooltip()
        self.current_item = None
    
    def _show_tooltip(self, x, y, item):
        """Muestra tooltip simple con texto inteligentemente cortado"""
        if self.current_item != item:
            return
            
        # Obtener ruta completa
        ruta_completa = self._get_full_path(item)
        if not ruta_completa:
            return
        
        # Cortar ruta inteligentemente
        texto_tooltip = self._format_path_smart(ruta_completa)
        
        # Crear tooltip simple
        self.tooltip_window = tk.Toplevel(self.treeview)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.configure(bg="#ffffe0", relief="solid", bd=1)
        
        label = tk.Label(
            self.tooltip_window,
            text=texto_tooltip,
            bg="#ffffe0",
            fg="#000000",
            font=("Segoe UI", 9),
            padx=6,
            pady=4,
            wraplength=300,
            justify='left'
        )
        label.pack()
        
        # Posicionar tooltip
        self._position_tooltip(x, y)
    
    def _format_path_smart(self, ruta):
        """Formatea ruta dividida por niveles/carpetas"""
        if len(ruta) <= 50:
            return ruta
        
        # Si tiene "->", procesar por separado
        if " -> " in ruta:
            partes = ruta.split(" -> ", 1)
            nombre = partes[0]
            path = partes[1]
            
            niveles_path = self._dividir_por_niveles(path)
            if len(niveles_path) > 1:
                resultado = [nombre] + [f"→ {niveles_path[0]}"]
                for nivel in niveles_path[1:]:
                    resultado.append(f"  {nivel}")
                return "\n".join(resultado)
            else:
                return f"{nombre}\n→ {path}"
        
        # Ruta normal - dividir por niveles
        niveles = self._dividir_por_niveles(ruta)
        if len(niveles) > 1:
            return "\n".join(niveles)
        else:
            return ruta
    
    def _dividir_por_niveles(self, ruta):
        """Divide ruta en niveles (una carpeta por línea)"""
        if "\\" in ruta:
            separador = "\\"
        elif "/" in ruta:
            separador = "/"
        else:
            return [ruta]
        
        partes = ruta.split(separador)
        niveles = []
        
        if partes[0]:
            niveles.append(partes[0])
        else:
            niveles.append(separador)
        
        for parte in partes[1:]:
            if parte:
                if len(niveles) == 1:
                    niveles.append(f"{separador}{parte}")
                else:
                    niveles.append(f"{separador}{parte}")
        
        return niveles
    
    def _get_full_path(self, item):
        """Obtiene ruta completa del item"""
        try:
            values = self.treeview.item(item, 'values')
            if values and len(values) >= 2:
                ruta = values[1] if len(values) > 1 else values[0]
                nombre = self.treeview.item(item, 'text')
                
                if ruta and not ruta.startswith(('C:', 'D:', '/', '\\\\')):
                    return f"{nombre} -> {ruta}"
                elif ruta:
                    return ruta
                else:
                    return nombre
            
            return self.treeview.item(item, 'text')
        except:
            return None
    
    def _position_tooltip(self, x, y):
        """Posiciona tooltip evitando bordes"""
        if not self.tooltip_window:
            return
            
        self.tooltip_window.update_idletasks()
        tooltip_width = self.tooltip_window.winfo_reqwidth()
        tooltip_height = self.tooltip_window.winfo_reqheight()
        
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()
        
        tooltip_x = x + 15
        tooltip_y = y + 10
        
        if tooltip_x + tooltip_width > screen_width:
            tooltip_x = x - tooltip_width - 15
            
        if tooltip_y + tooltip_height > screen_height:
            tooltip_y = y - tooltip_height - 10
            
        tooltip_x = max(0, min(tooltip_x, screen_width - tooltip_width))
        tooltip_y = max(0, min(tooltip_y, screen_height - tooltip_height))
        
        self.tooltip_window.geometry(f"+{tooltip_x}+{tooltip_y}")
    
    def _hide_tooltip(self, event=None):
        """Oculta tooltip"""
        if self.after_id:
            self.treeview.after_cancel(self.after_id)
            self.after_id = None
            
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
