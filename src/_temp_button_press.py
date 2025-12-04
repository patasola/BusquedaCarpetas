    def _on_button_press(self, event):
        """Preserva selección múltiple al iniciar drag"""
        # Obtener item clickeado
        item = self.ui.tree.identify_row(event.y)
        if not item:
            return
        
        # Si ya hay múltiples items seleccionados y clickeamos uno de ellos, 
        # NO dejar que tkinter deseleccione (preservar selección para drag)
        selection = self.ui.tree.selection()
        if len(selection) > 1 and item in selection:
            # Prevenir deselección por defecto
            return 'break'
