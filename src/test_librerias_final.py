# test_librerias_final.py
import sys

print("=== VERIFICACIÓN FINAL DE LIBRERÍAS ===")
libs = ['win32com.client', 'PyPDF2', 'openpyxl', 'PIL', 'reportlab']

for lib in libs:
    try:
        if lib == 'PIL':
            import PIL
            print(f"✅ Pillow (PIL): {PIL.__version__}")
        else:
            mod = __import__(lib)
            print(f"✅ {lib}: Instalado")
    except ImportError:
        print(f"❌ {lib}: Falta")

print("\n✅ Todo listo para continuar!" if all else "⚠️ Instala las faltantes con pip")