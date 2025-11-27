# procesador_automatico_v1.py
import win32com.client
from pathlib import Path
from datetime import datetime
import subprocess
import shutil
import PyPDF2
from extractor_expedientes_mejorado import ExtractorExpedientesMejorado

class ProcesadorAutomatico:
    def __init__(self):
        # Conectar con Outlook
        self.outlook = win32com.client.Dispatch("Outlook.Application")
        self.namespace = self.outlook.GetNamespace("MAPI")
        
        # Configurar carpetas
        self.inbox = self.namespace.GetDefaultFolder(6)  # 6 = Inbox
        self.carpeta_procesados = self.crear_carpeta_si_no_existe("Procesados")
        self.carpeta_revision = self.crear_carpeta_si_no_existe("Requiere_Revision")
        
        # Inicializar extractor
        self.extractor = ExtractorExpedientesMejorado()
        
        # Ruta base OneDrive
        self.ruta_base = Path(r"C:\Users\edperezp\OneDrive - Consejo Superior de la Judicatura\Juzgado 17\Procesos")
        
        # Crear carpeta temporal
        self.temp_dir = Path("temp_procesamiento")
        self.temp_dir.mkdir(exist_ok=True)
    
    def crear_carpeta_si_no_existe(self, nombre):
        """Crea carpeta en Outlook si no existe"""
        try:
            return self.inbox.Folders(nombre)
        except:
            return self.inbox.Folders.Add(nombre)
    
    def procesar_correos_nuevos(self, limite=10):
        """Procesa los correos más recientes"""
        mensajes = self.inbox.Items
        mensajes.Sort("[ReceivedTime]", True)  # Más recientes primero
        
        procesados = 0
        for mensaje in mensajes:
            if procesados >= limite:
                break
            
            # Solo procesar si no está categorizado
            if not mensaje.Categories:
                print(f"\n{'='*50}")
                print(f"Procesando: {mensaje.Subject[:50]}")
                resultado = self.procesar_correo_individual(mensaje)
                
                if resultado['exitoso']:
                    print(f"✅ Éxito: {resultado['expediente']} -> {resultado['archivo']}")
                    mensaje.Move(self.carpeta_procesados)
                else:
                    print(f"⚠️ Requiere revisión: {resultado['razon']}")
                    mensaje.Move(self.carpeta_revision)
                
                procesados += 1
        
        print(f"\n📊 Resumen: {procesados} correos procesados")
        print(self.extractor.generar_reporte())
    
    def procesar_correo_individual(self, mensaje):
        """Procesa un correo específico"""
        resultado = {
            'exitoso': False,
            'expediente': None,
            'archivo': None,
            'razon': None
        }
        
        try:
            # 1. Extraer expediente
            expediente, confianza, metodo = self.extractor.extraer_expediente(
                mensaje.Subject,
                mensaje.Body,
                mensaje.SenderEmailAddress
            )
            
            if not expediente or confianza < 0.6:
                resultado['razon'] = f"No se pudo identificar expediente (confianza: {confianza:.2f})"
                return resultado
            
            resultado['expediente'] = expediente
            
            # 2. Crear estructura de carpetas
            año = expediente.split('-')[0]
            ruta_expediente = self.ruta_base / año / "Ordinario" / expediente
            ruta_expediente = self.ruta_base / año / "Ordinario" / f"{año}-{expediente.split('-')[1]}" / f"110013105017{año}{expediente.split('-')[1].zfill(5)}00"
            ruta_expediente.mkdir(parents=True, exist_ok=True)
            
            # 3. Obtener consecutivo
            consecutivo = self.obtener_consecutivo(ruta_expediente)
            
            # 4. Procesar correo y adjuntos
            fecha = mensaje.ReceivedTime.strftime("%d-%m-%y")
            descripcion = self.limpiar_texto_para_nombre(mensaje.Subject)
            nombre_pdf = f"{consecutivo:02d}{descripcion}{fecha}.pdf"
            
            # 5. Crear PDF del correo
            pdf_correo = self.temp_dir / "correo_temp.pdf"
            self.correo_a_pdf(mensaje, pdf_correo)
            
            # 6. Procesar adjuntos
            pdfs_adjuntos = self.procesar_adjuntos(mensaje)
            
            # 7. Combinar todos los PDFs
            pdf_final = ruta_expediente / nombre_pdf
            self.combinar_pdfs([pdf_correo] + pdfs_adjuntos, pdf_final)
            
            # 8. Limpiar temporales
            for archivo in self.temp_dir.glob("*"):
                archivo.unlink()
            
            # 9. Marcar como procesado
            mensaje.Categories = "Procesado_Automatico"
            mensaje.Save()
            
            # 10. Aprender para futuras clasificaciones
            self.extractor.aprender_de_clasificacion(
                expediente, 
                mensaje.Subject, 
                mensaje.SenderEmailAddress
            )
            
            resultado['exitoso'] = True
            resultado['archivo'] = str(pdf_final)
            
        except Exception as e:
            resultado['razon'] = f"Error: {str(e)}"
        
        return resultado
    
    def obtener_consecutivo(self, ruta):
        """Obtiene el siguiente número consecutivo"""
        archivos_pdf = list(ruta.glob("*.pdf"))
        if not archivos_pdf:
            return 1
        
        consecutivos = []
        for archivo in archivos_pdf:
            try:
                # Intentar extraer los primeros 2 caracteres como número
                num = int(archivo.name[:2])
                consecutivos.append(num)
            except:
                continue
        
        return max(consecutivos, default=0) + 1
    
    def correo_a_pdf(self, mensaje, salida):
        """Convierte el correo a PDF"""
        # Guardar como HTML temporal
        html_path = self.temp_dir / "correo_temp.html"
        
        # Crear HTML con el contenido del correo
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 10px; margin-bottom: 20px; }}
                .field {{ margin: 5px 0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="field"><span class="label">De:</span> {mensaje.SenderName} &lt;{mensaje.SenderEmailAddress}&gt;</div>
                <div class="field"><span class="label">Fecha:</span> {mensaje.ReceivedTime}</div>
                <div class="field"><span class="label">Para:</span> {mensaje.To}</div>
                <div class="field"><span class="label">Asunto:</span> {mensaje.Subject}</div>
            </div>
            <div class="body">
                {mensaje.Body.replace(chr(10), '<br>')}
            </div>
        </body>
        </html>
        """
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Aquí usarías Nitro o wkhtmltopdf para convertir
        # Por ahora, creamos un PDF simple con PyPDF2
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(str(salida), pagesize=letter)
        # Agregar texto básico (versión simplificada)
        c.drawString(50, 750, f"De: {mensaje.SenderName}")
        c.drawString(50, 730, f"Fecha: {mensaje.ReceivedTime}")
        c.drawString(50, 710, f"Asunto: {mensaje.Subject}")
        c.save()
        
        return salida
    
    def procesar_adjuntos(self, mensaje):
        """Procesa y convierte adjuntos a PDF"""
        pdfs = []
        
        for adjunto in mensaje.Attachments:
            nombre = adjunto.FileName
            temp_path = self.temp_dir / nombre
            
            # Guardar adjunto
            adjunto.SaveAsFile(str(temp_path))
            
            # Si ya es PDF, agregarlo directamente
            if nombre.lower().endswith('.pdf'):
                pdfs.append(temp_path)
            # Si es imagen, convertir a PDF
            elif nombre.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                pdf_path = temp_path.with_suffix('.pdf')
                self.imagen_a_pdf(temp_path, pdf_path)
                pdfs.append(pdf_path)
            # Si es Word, intentar convertir
            elif nombre.lower().endswith(('.doc', '.docx')):
                pdf_path = temp_path.with_suffix('.pdf')
                self.word_a_pdf(temp_path, pdf_path)
                pdfs.append(pdf_path)
        
        return pdfs
    
    def combinar_pdfs(self, lista_pdfs, salida):
        """Combina múltiples PDFs en uno solo"""
        merger = PyPDF2.PdfMerger()
        
        for pdf in lista_pdfs:
            if pdf.exists():
                try:
                    merger.append(str(pdf))
                except:
                    print(f"⚠️ No se pudo agregar: {pdf.name}")
        
        merger.write(str(salida))
        merger.close()
    
    def limpiar_texto_para_nombre(self, texto):
        """Limpia texto para usar como nombre de archivo"""
        import re
        
        # Extraer palabras clave principales
        palabras_clave = ['Memorial', 'Desistimiento', 'Poder', 'Notificacion', 
                         'Alegatos', 'Recurso', 'Solicitud', 'Auto', 'Sentencia']
        
        for palabra in palabras_clave:
            if palabra.lower() in texto.lower():
                return palabra
        
        # Si no hay palabra clave, usar las primeras palabras
        texto_limpio = re.sub(r'[^\w\s]', '', texto)
        palabras = texto_limpio.split()[:2]
        return ''.join(p.capitalize() for p in palabras)
    
    def imagen_a_pdf(self, imagen_path, pdf_path):
        """Convierte imagen a PDF"""
        from PIL import Image
        
        imagen = Image.open(imagen_path)
        imagen.save(pdf_path, "PDF")
    
    def word_a_pdf(self, word_path, pdf_path):
        """Convierte Word a PDF usando win32com"""
        try:
            word = win32com.client.Dispatch("Word.Application")
            doc = word.Documents.Open(str(word_path))
            doc.SaveAs(str(pdf_path), FileFormat=17)  # 17 = PDF
            doc.Close()
            word.Quit()
        except:
            print(f"⚠️ No se pudo convertir Word a PDF: {word_path.name}")

# EJECUTAR PRUEBA
if __name__ == "__main__":
    print("🚀 Iniciando procesador automático...")
    procesador = ProcesadorAutomatico()
    
    # Procesar solo 3 correos para prueba
    procesador.procesar_correos_nuevos(limite=3)