# test_ambiente.py - Ejecuta esto para verificar tu setup
import sys
print("=== VERIFICACIÓN DE AMBIENTE ===")

# Verificar librerías necesarias
librerias_necesarias = {
    'pywin32': 'Comunicación con Outlook',
    'PyPDF2': 'Manipulación de PDFs', 
    'openpyxl': 'Para logs en Excel',
    'python-docx': 'Conversión de Word a PDF'
}

for lib, uso in librerias_necesarias.items():
    try:
        __import__(lib.replace('-','_'))
        print(f"✅ {lib}: Instalado ({uso})")
    except ImportError:
        print(f"❌ {lib}: NO instalado - Instalar con: pip install {lib}")

# Verificar acceso a Outlook
try:
    import win32com.client
    outlook = win32com.client.Dispatch("Outlook.Application")
    print(f"✅ Outlook: Conectado - Versión {outlook.Version}")
except:
    print("❌ Outlook: No se pudo conectar")

# Verificar tu ruta de OneDrive
from pathlib import Path
ruta_base = Path(r"C:\Users\edperezp\OneDrive - Consejo Superior de la Judicatura\Juzgado 17\Procesos")
if ruta_base.exists():
    print(f"✅ OneDrive: Ruta encontrada")
    print(f"   Expedientes 2024: {len(list(ruta_base.glob('2024/*/*')))}")
    print(f"   Expedientes 2023: {len(list(ruta_base.glob('2023/*/*')))}")
else:
    print("❌ OneDrive: Ruta no encontrada")