import os

file_path = r'c:\Users\edperezp\OneDrive - Consejo Superior de la Judicatura (1)\Abrir archivos\BusquedaCarpetas4.5\BusquedaCarpetas4.5\src\app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Nuevo método simple (líneas 348-357)
new_method_lines = [
    '    def _on_explorer_file_change(self, operation, paths):\n',
    '        """Maneja cambios de archivos del explorador"""\n',
    '        print(f\'[App] Cambio en explorador: {operation}\')\n',
    '        \n',
   '        # Mostrar warning de resultados desactualizados\n',
    '        if hasattr(self, \'label_estado\'):\n',
    '            self.label_estado.config(\n',
    '                text="⚠️ Resultados de búsqueda pueden estar desactualizados - Presiona F5 para actualizar",\n',
    '                fg=\'#ff6b00\'  # Naranja\n',
    '            )\n',
    '\n'
]

# Reemplazar líneas 347-403 (índices 347-403 en base 0)
new_lines = lines[:347] + new_method_lines + lines[403:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f'✓ Editado: eliminadas {403-347} líneas, agregadas {len(new_method_lines)} líneas')
print(f'✓ Total reducción: {(403-347) - len(new_method_lines)} líneas')
