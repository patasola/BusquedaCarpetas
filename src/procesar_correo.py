# procesar_correo.py
import sys
import json
import win32com.client
from datetime import datetime
from pathlib import Path
import subprocess
import shutil

class ProcesadorCorreoJudicial:
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application")
        self.namespace = self.outlook.GetNamespace("MAPI")
        self.extractor = ExtractorExpediente()
        self.base_path = Path(r"C:\Users\edperezp\OneDrive - Consejo Superior de la Judicatura\Juzgado 17\Procesos")
        
    def procesar_correo(self, message_id):
        """Procesa un correo completo"""
        
        # 1. Obtener el correo
        mail = self.obtener_correo_por_id(message_id)
        if not mail:
            return {"error": "Correo no encontrado"}
        
        # 2. Extraer expediente
        expediente = self.extractor.buscar_expediente_completo(mail)
        
        if not expediente:
            # Solicitar intervención manual
            return {
                "status": "manual_required",
                "asunto": mail.Subject,
                "remitente": mail.SenderEmailAddress
            }
        
        # 3. Determinar ruta y consecutivo
        año = expediente.split('-')[0]
        ruta_expediente = self.base_path / año / "Ordinario" / expediente
        
        # Crear carpeta si no existe
        ruta_expediente.mkdir(parents=True, exist_ok=True)
        
        # 4. Obtener consecutivo
        consecutivo = self.obtener_siguiente_consecutivo(ruta_expediente)
        
        # 5. Generar nombre del archivo
        fecha = mail.ReceivedTime.strftime("%d-%m-%y")
        descripcion = self.limpiar_descripcion(mail.Subject)
        nombre_archivo = f"{consecutivo:02d}{descripcion}{fecha}.pdf"
        
        # 6. Procesar adjuntos
        adjuntos_paths = self.guardar_adjuntos(mail, ruta_expediente / "temp")
        
        # 7. Crear PDF del correo
        pdf_correo = self.correo_a_pdf(mail, ruta_expediente / "temp" / "correo.pdf")
        
        # 8. Combinar PDFs
        pdf_final = ruta_expediente / nombre_archivo
        self.combinar_pdfs([pdf_correo] + adjuntos_paths, pdf_final)
        
        # 9. Limpiar temporales
        shutil.rmtree(ruta_expediente / "temp")
        
        # 10. Marcar correo como procesado
        mail.Categories = "Procesado"
        mail.Save()
        
        return {
            "status": "success",
            "expediente": expediente,
            "archivo": str(pdf_final),
            "consecutivo": consecutivo
        }
    
    def obtener_siguiente_consecutivo(self, ruta):
        """Obtiene el siguiente consecutivo disponible"""
        archivos = list(ruta.glob("*.pdf"))
        if not archivos:
            return 1
        
        consecutivos = []
        for archivo in archivos:
            try:
                # Extraer los primeros 2 dígitos
                cons = int(archivo.name[:2])
                consecutivos.append(cons)
            except:
                continue
        
        return max(consecutivos, default=0) + 1
    
    def correo_a_pdf(self, mail, output_path):
        """Convierte correo a PDF usando Nitro"""
        # Guardar como HTML temporal
        html_path = output_path.with_suffix('.html')
        mail.SaveAs(str(html_path), 5)  # 5 = HTML format
        
        # Convertir HTML a PDF con Nitro
        subprocess.run([
            r"C:\Program Files\Nitro\Pro\13\NitroPDF.exe",
            "/PrintTo",
            str(html_path),
            "Nitro PDF Creator"
        ])
        
        return output_path
    
    def combinar_pdfs(self, pdfs, output):
        """Combina PDFs usando PyPDF2"""
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        for pdf in pdfs:
            if pdf.exists():
                merger.append(str(pdf))
        
        merger.write(str(output))
        merger.close()
    
    def limpiar_descripcion(self, texto):
        """Limpia el texto para nombre de archivo"""
        # Remover caracteres no válidos
        import re
        texto = re.sub(r'[^\w\s-]', '', texto)
        texto = re.sub(r'[-\s]+', '', texto)
        
        # Convertir a CamelCase
        palabras = texto.split()[:3]  # Máximo 3 palabras
        return ''.join(word.capitalize() for word in palabras)

if __name__ == "__main__":
    message_id = sys.argv[1] if len(sys.argv) > 1 else None
    procesador = ProcesadorCorreoJudicial()
    resultado = procesador.procesar_correo(message_id)
    print(json.dumps(resultado))