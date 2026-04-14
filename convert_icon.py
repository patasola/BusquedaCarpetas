from PIL import Image
import os
import glob

def convert_to_ico():
    # Buscar la imagen generada (la más reciente que empiece por app_icon_empireo)
    pattern = r"C:\Users\edperezp\.gemini\antigravity\brain\5cb7e51c-c1bf-4e5c-a146-783f4de6d45f\app_icon_empireo_*.png"
    files = glob.glob(pattern)
    if not files:
        print("No se encontró la imagen PNG")
        return
    
    # Tomar la más reciente
    latest_file = max(files, key=os.path.getctime)
    print(f"Usando imagen: {latest_file}")
    
    img = Image.open(latest_file)
    
    # Redimensionar y guardar como ICO con múltiples tamaños para Windows
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save('app_icon.ico', sizes=icon_sizes)
    print("Icono app_icon.ico creado exitosamente")

if __name__ == "__main__":
    convert_to_ico()
