# procesador_correcto.py
import win32com.client
import re
from pathlib import Path
from datetime import datetime
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

class ProcesadorCorregido:
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application")
        self.namespace = self.outlook.GetNamespace("MAPI")
        self.inbox = self.namespace.GetDefaultFolder(6)
        self.ruta_base = Path(r"C:\Users\edperezp\OneDrive - Consejo Superior de la Judicatura\Juzgado 17\Procesos")
        
    def procesar(self):
        """Procesa el correo con estructura correcta de carpetas"""
        correo = self.inbox.Items.Item(1)
        
        print("\n" + "="*70)
        print("📂 PROCESADOR CORREGIDO - ESTRUCTURA REAL")
        print("="*70)
        
        # 1. Información del correo
        print(f"\n📧 Correo: {correo.Subject[:60]}")
        print(f"   De: {correo.SenderName}")
        print(f"   Adjuntos: {correo.Attachments.Count}")
        
        # Listar adjuntos para identificar cuáles procesar
        adjuntos_reales = []
        for adj in correo.Attachments:
            # Ignorar imágenes típicas de firma
            if adj.FileName.lower() in ['image001.png', 'image002.png', 'image003.png', 
                                        'image001.jpg', 'outlook.png']:
                print(f"   ⏭️ Ignorando firma: {adj.FileName}")
            else:
                adjuntos_reales.append(adj)
                print(f"   📎 Adjunto real: {adj.FileName}")
        
        # 2. Extraer expediente
        match = re.search(r'RADICADO:\s*(\d{4})\s*[–\-—]\s*(\d{3,4})', correo.Subject, re.IGNORECASE)
        if not match:
            print("❌ No se encontró expediente")
            return False
        
        expediente = f"{match.group(1)}-{match.group(2).lstrip('0')}"
        año = match.group(1)
        num = match.group(2).zfill(5)
        
        print(f"\n✅ Expediente: {expediente}")
        
        # 3. Buscar la carpeta correcta con subcarpetas
        ruta_expediente = self.ruta_base / año / "Ordinario" / expediente / f"110013105017{año}{num}00"
        
        # Verificar si ya existe y buscar subcarpetas
        if ruta_expediente.exists():
            # Buscar subcarpetas existentes (Memoriales, Autos, etc.)
            subcarpetas = [d for d in ruta_expediente.iterdir() if d.is_dir()]
            
            if subcarpetas:
                print(f"\n📁 Subcarpetas encontradas:")
                for i, sub in enumerate(subcarpetas, 1):
                    print(f"   {i}. {sub.name}")
                
                # Determinar carpeta según tipo de documento
                tipo_doc = self.determinar_tipo_documento(correo.Subject)
                carpeta_destino = None
                
                # Buscar carpeta apropiada
                for sub in subcarpetas:
                    if tipo_doc.lower() in sub.name.lower():
                        carpeta_destino = sub
                        break
                
                # Si no encuentra carpeta específica, usar la primera o crear una
                if not carpeta_destino:
                    if "MEMORIAL" in correo.Subject.upper():
                        carpeta_destino = ruta_expediente / "Memoriales"
                        carpeta_destino.mkdir(exist_ok=True)
                    elif "AUTO" in correo.Subject.upper():
                        carpeta_destino = ruta_expediente / "Autos"
                        carpeta_destino.mkdir(exist_ok=True)
                    else:
                        carpeta_destino = ruta_expediente  # Usar raíz si no hay subcarpetas
                
                ruta_final = carpeta_destino
            else:
                # No hay subcarpetas, usar la raíz
                ruta_final = ruta_expediente
        else:
            # Crear estructura nueva
            ruta_expediente.mkdir(parents=True, exist_ok=True)
            ruta_final = ruta_expediente
        
        print(f"📂 Guardando en: {ruta_final}")
        
        # 4. Obtener consecutivo
        archivos_pdf = list(ruta_final.glob("*.pdf"))
        consecutivo = len(archivos_pdf) + 1
        fecha = correo.ReceivedTime.strftime("%d-%m-%y")
        
        # 5. Determinar nombre del archivo
        tipo_doc = self.determinar_tipo_documento(correo.Subject)
        nombre_archivo = f"{consecutivo:02d}{tipo_doc}{fecha}.pdf"
        
        print(f"📝 Archivo final: {nombre_archivo}")
        print(f"   Consecutivo: {consecutivo}")
        
        # 6. Crear carpeta temporal FUERA de OneDrive
        temp_dir = Path("C:/temp_juzgado")
        if temp_dir.exists():
            # Limpiar archivos anteriores
            for archivo in temp_dir.glob("*"):
                try:
                    archivo.unlink()
                except:
                    pass
        temp_dir.mkdir(exist_ok=True)
        
        print(f"\n🚀 Procesando...")
        
        try:
            # 7. PRIMERO: Crear PDF del correo
            pdf_correo = temp_dir / "00_correo.pdf"
            self.crear_pdf_correo_completo(correo, pdf_correo)
            
            # 8. Lista de PDFs a combinar (empezando con el correo)
            pdfs_a_combinar = [pdf_correo]
            
            # 9. Procesar solo adjuntos reales (no firmas)
            for i, adj in enumerate(adjuntos_reales, 1):
                archivo_adj = temp_dir / f"adj_{i}_{adj.FileName}"
                adj.SaveAsFile(str(archivo_adj.absolute()))
                
                if adj.FileName.lower().endswith('.pdf'):
                    pdfs_a_combinar.append(archivo_adj)
                    print(f"   ✅ PDF adjunto procesado: {adj.FileName}")
                else:
                    print(f"   ⏭️ Archivo no PDF ignorado: {adj.FileName}")
            
            # 10. COMBINAR: Correo + Adjuntos en un solo PDF
            archivo_final = ruta_final / nombre_archivo
            
            if len(pdfs_a_combinar) > 0:
                merger = PyPDF2.PdfMerger()
                
                # Agregar en orden: primero el correo, luego los adjuntos
                for pdf_path in pdfs_a_combinar:
                    try:
                        merger.append(str(pdf_path))
                        print(f"   ➕ Agregado al PDF final: {pdf_path.name}")
                    except Exception as e:
                        print(f"   ⚠️ Error agregando {pdf_path.name}: {e}")
                
                merger.write(str(archivo_final))
                merger.close()
                print(f"\n✅ PDF FINAL CREADO: {archivo_final.name}")
                print(f"   Contiene: Correo + {len(pdfs_a_combinar)-1} adjunto(s)")
            
            # 11. Limpiar temporales
            try:
                for archivo in temp_dir.glob("*"):
                    archivo.unlink()
            except:
                pass
            
            # 12. Marcar y mover correo
            correo.Categories = f"Procesado_{expediente}"
            correo.Save()
            
            # Crear/obtener carpeta Procesados
            try:
                carpeta_procesados = self.inbox.Folders("Procesados")
            except:
                carpeta_procesados = self.inbox.Folders.Add("Procesados")
            
            correo.Move(carpeta_procesados)
            print(f"✅ Correo movido a 'Procesados'")
            
            print(f"\n" + "="*70)
            print(f"✅✅✅ PROCESO COMPLETADO ✅✅✅")
            print(f"="*70)
            print(f"Expediente: {expediente}")
            print(f"Ubicación: {archivo_final}")
            print(f"Tamaño: {archivo_final.stat().st_size / 1024:.1f} KB")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def determinar_tipo_documento(self, asunto):
        """Determina el tipo de documento basado en el asunto"""
        asunto_upper = asunto.upper()
        
        # Lista de tipos comunes en orden de prioridad
        tipos = [
            ("MEMORIAL", "Memorial"),
            ("DESISTIMIENTO", "Desistimiento"),
            ("RECURSO", "Recurso"),
            ("ALEGATOS", "Alegatos"),
            ("PODER", "Poder"),
            ("SOLICITUD", "Solicitud"),
            ("IMPULSO", "ImpulsoProcesal"),
            ("NOTIFICACION", "Notificacion"),
            ("AUTO", "Auto"),
            ("SENTENCIA", "Sentencia")
        ]
        
        for palabra, tipo in tipos:
            if palabra in asunto_upper:
                return tipo
        
        return "Documento"
    
    def crear_pdf_correo_completo(self, correo, archivo_salida):
        """Crea un PDF completo del correo con todo el contenido"""
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        
        doc = SimpleDocTemplate(str(archivo_salida), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Estilo para encabezado
        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#000080'),
            spaceAfter=20
        )
        
        # Encabezado
        story.append(Paragraph("CORREO ELECTRÓNICO", titulo_style))
        story.append(Spacer(1, 12))
        
        # Información del correo con mejor formato
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=20
        )
        
        story.append(Paragraph("<b>INFORMACIÓN DEL MENSAJE</b>", styles['Heading2']))
        story.append(Spacer(1, 6))
        
        story.append(Paragraph(f"<b>De:</b> {correo.SenderName} ({correo.SenderEmailAddress})", info_style))
        story.append(Paragraph(f"<b>Para:</b> {correo.To}", info_style))
        story.append(Paragraph(f"<b>Fecha:</b> {correo.ReceivedTime.strftime('%d de %B de %Y - %H:%M')}", info_style))
        story.append(Paragraph(f"<b>Asunto:</b> {correo.Subject}", info_style))
        
        if correo.CC:
            story.append(Paragraph(f"<b>CC:</b> {correo.CC}", info_style))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>CONTENIDO DEL MENSAJE</b>", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Cuerpo del correo - procesar todo el contenido
        cuerpo = correo.Body
        # Convertir saltos de línea para ReportLab
        cuerpo = cuerpo.replace('\r\n', '<br/>')
        cuerpo = cuerpo.replace('\n', '<br/>')
        cuerpo = cuerpo.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        
        # Dividir en párrafos para mejor renderizado
        parrafos = cuerpo.split('<br/><br/>')
        
        for parrafo in parrafos:
            if parrafo.strip():
                try:
                    story.append(Paragraph(parrafo, styles['Normal']))
                    story.append(Spacer(1, 6))
                except:
                    # Si hay problemas con caracteres especiales
                    texto_limpio = parrafo.encode('ascii', 'ignore').decode('ascii')
                    story.append(Paragraph(texto_limpio, styles['Normal']))
                    story.append(Spacer(1, 6))
        
        # Construir PDF
        doc.build(story)
        print(f"   ✅ PDF del correo creado (con todo el contenido)")

# EJECUTAR
if __name__ == "__main__":
    print("🔧 PROCESADOR CORREGIDO - v2")
    procesador = ProcesadorCorregido()
    
    if procesador.inbox.Items.Count == 0:
        print("❌ No hay correos en la bandeja")
    else:
        procesador.procesar()