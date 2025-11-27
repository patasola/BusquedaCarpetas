# procesador_directo.py
import win32com.client
import re
from pathlib import Path
from datetime import datetime
import PyPDF2

class ProcesadorDirecto:
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application")
        self.namespace = self.outlook.GetNamespace("MAPI")
        self.inbox = self.namespace.GetDefaultFolder(6)
        self.ruta_base = Path(r"C:\Users\edperezp\OneDrive - Consejo Superior de la Judicatura\Juzgado 17\Procesos")
    
    def procesar_simple(self):
        """Versión simplificada que solo guarda los adjuntos"""
        correo = self.inbox.Items.Item(1)
        
        print("\n🔥 PROCESAMIENTO DIRECTO SIMPLE")
        print(f"Correo: {correo.Subject[:60]}")
        
        # Extraer expediente (simplificado)
        match = re.search(r'RADICADO:\s*(\d{4})\s*[–\-—]\s*(\d{3,4})', correo.Subject, re.IGNORECASE)
        if not match:
            print("❌ No se encontró expediente")
            return
        
        expediente = f"{match.group(1)}-{match.group(2).lstrip('0')}"
        print(f"✅ Expediente: {expediente}")
        
        # Construir ruta
        año = match.group(1)
        num = match.group(2).zfill(5)
        ruta_final = self.ruta_base / año / "Ordinario" / expediente / f"110013105017{año}{num}00"
        
        # Crear carpeta
        ruta_final.mkdir(parents=True, exist_ok=True)
        print(f"✅ Carpeta: {ruta_final}")
        
        # Contar archivos existentes para consecutivo
        archivos_existentes = list(ruta_final.glob("*.pdf"))
        consecutivo = len(archivos_existentes) + 1
        
        # Guardar adjuntos directamente
        fecha = datetime.now().strftime("%d-%m-%y")
        
        if correo.Attachments.Count > 0:
            print(f"\n📎 Guardando {correo.Attachments.Count} adjuntos:")
            
            for i, adj in enumerate(correo.Attachments, 1):
                # Determinar nombre según tipo
                if adj.FileName.endswith('.pdf'):
                    # PDF principal con consecutivo
                    if i == 1:  # Primer PDF es el memorial principal
                        nombre_guardar = f"{consecutivo:02d}Memorial{fecha}.pdf"
                    else:
                        nombre_guardar = f"{consecutivo:02d}_anexo_{i}_{adj.FileName}"
                else:
                    # Otros archivos (imágenes, etc)
                    nombre_guardar = f"{consecutivo:02d}_imagen_{i}_{adj.FileName}"
                
                ruta_archivo = ruta_final / nombre_guardar
                
                try:
                    # Guardar con ruta absoluta completa
                    adj.SaveAsFile(str(ruta_archivo.absolute()))
                    print(f"   ✅ {adj.FileName} → {nombre_guardar}")
                except Exception as e:
                    print(f"   ❌ Error con {adj.FileName}: {e}")
        
        # Marcar correo
        correo.Categories = f"Procesado_{expediente}"
        correo.Save()
        
        print(f"\n✅ COMPLETADO - Expediente {expediente}")
        print(f"   Archivos guardados en: {ruta_final}")
        
        # Preguntar si mover
        mover = input("\n¿Mover correo a carpeta 'Procesados'? (s/n): ")
        if mover.lower() == 's':
            try:
                carpeta_procesados = self.inbox.Folders("Procesados")
            except:
                carpeta_procesados = self.inbox.Folders.Add("Procesados")
            
            correo.Move(carpeta_procesados)
            print("✅ Correo movido a 'Procesados'")

# Ejecutar
if __name__ == "__main__":
    procesador = ProcesadorDirecto()
    procesador.procesar_simple()