# procesador_correo_real.py
import win32com.client
import re
from pathlib import Path
from datetime import datetime
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image
import shutil

class ProcesadorCorreoJuzgado:
    def __init__(self):
        self.outlook = win32com.client.Dispatch("Outlook.Application")
        self.namespace = self.outlook.GetNamespace("MAPI")
        self.inbox = self.namespace.GetDefaultFolder(6)
        self.ruta_base = Path(r"C:\Users\edperezp\OneDrive - Consejo Superior de la Judicatura\Juzgado 17\Procesos")
        
    def extraer_expediente_mejorado(self, texto):
        """Extrae expediente con patrones más flexibles"""
        
        # PATRONES MEJORADOS - Más tolerantes a variaciones
        patrones = [
            # Patrón 1: Con espacios y diferentes guiones
            (r'RADICADO:\s*(\d{4})\s*[–\-—]\s*(\d{3,4})', 'radicado_espacios'),
            
            # Patrón 2: Formato estándar
            (r'(\d{4})-(\d{3,4})', 'formato_estandar'),
            
            # Patrón 3: Solo números consecutivos 2023171
            (r'(?:RADICADO|Rad|Exp|Expediente)[:\s]*(\d{4})(\d{3})', 'numeros_juntos'),
            
            # Patrón 4: Radicado completo
            (r'110013105017(\d{4})(\d{5})00', 'radicado_completo'),
        ]
        
        for patron, nombre in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                año = match.group(1)
                num = match.group(2).lstrip('0')
                expediente = f"{año}-{num}"
                return expediente, nombre
        
        return None, None
    
    def procesar_correo_actual(self):
        """Procesa el correo actual en la bandeja"""
        correo = self.inbox.Items.Item(1)
        
        print("="*70)
        print("📧 PROCESANDO CORREO DEL JUZGADO")
        print("="*70)
        
        print(f"\n📋 INFORMACIÓN DEL CORREO:")
        print(f"   De: {correo.SenderName}")
        print(f"   Asunto: {correo.Subject[:80]}")
        print(f"   Fecha: {correo.ReceivedTime}")
        print(f"   Adjuntos: {correo.Attachments.Count}")
        
        if correo.Attachments.Count > 0:
            print(f"\n   📎 Lista de adjuntos:")
            for i, adj in enumerate(correo.Attachments, 1):
                print(f"      {i}. {adj.FileName}")
        
        # Buscar expediente
        texto_completo = f"{correo.Subject}\n{correo.Body[:500]}"
        expediente, metodo = self.extraer_expediente_mejorado(texto_completo)
        
        print(f"\n🔍 BÚSQUEDA DE EXPEDIENTE:")
        if expediente:
            print(f"   ✅ EXPEDIENTE ENCONTRADO: {expediente}")
            print(f"   📍 Método usado: {metodo}")
        else:
            print(f"   ❌ No se encontró expediente")
            return False
        
        # Construir ruta
        año = expediente.split('-')[0]
        num = expediente.split('-')[1].zfill(5)
        
        # Ajustar según tu estructura real
        ruta_expediente = self.ruta_base / año / "Ordinario" / expediente
        
        # Verificar si existe la carpeta base del año
        ruta_año = self.ruta_base / año
        if ruta_año.exists():
            # Buscar la carpeta exacta del expediente
            posibles_rutas = [
                ruta_expediente,
                self.ruta_base / año / "Ordinario" / f"{año}-{num.lstrip('0')}",
                self.ruta_base / año / "Ordinario" / f"{expediente}"
            ]
            
            for ruta in posibles_rutas:
                if ruta.exists():
                    # Buscar subcarpeta con radicado completo
                    subcarpetas = list(ruta.glob("*"))
                    if subcarpetas:
                        ruta_final = subcarpetas[0]  # Usar la primera subcarpeta
                        break
            else:
                # Si no existe, usar la estructura estándar
                radicado = f"110013105017{año}{num}00"
                ruta_final = ruta_expediente / radicado
        else:
            # Crear estructura nueva
            radicado = f"110013105017{año}{num}00"
            ruta_final = ruta_expediente / radicado
        
        print(f"\n📁 RUTA DE DESTINO:")
        print(f"   {ruta_final}")
        
        if ruta_final.exists():
            print(f"   ✅ La carpeta existe")
            archivos_existentes = list(ruta_final.glob("*.pdf"))
            print(f"   📄 Archivos PDF existentes: {len(archivos_existentes)}")
            consecutivo = len(archivos_existentes) + 1
        else:
            print(f"   ⚠️ La carpeta NO existe (se creará)")
            consecutivo = 1
        
        # Generar nombre del archivo
        fecha = correo.ReceivedTime.strftime("%d-%m-%y")
        
        # Identificar tipo de documento
        asunto_upper = correo.Subject.upper()
        if "MEMORIAL" in asunto_upper:
            tipo_doc = "Memorial"
        elif "IMPULSO" in asunto_upper:
            tipo_doc = "ImpulsoProcesal"
        elif "SOLICITUD" in asunto_upper or "SOLICTUD" in asunto_upper:
            tipo_doc = "Solicitud"
        else:
            tipo_doc = "Documento"
        
        nombre_archivo = f"{consecutivo:02d}{tipo_doc}{fecha}.pdf"
        
        print(f"\n📝 ARCHIVO A CREAR:")
        print(f"   Nombre: {nombre_archivo}")
        print(f"   Consecutivo: {consecutivo}")
        print(f"   Tipo detectado: {tipo_doc}")
        
        # Información del demandante/demandada
        demandante_match = re.search(r'DEMANDANTE:\s*([^-]+)', correo.Subject)
        demandada_match = re.search(r'DEMANDADA:\s*(.+)', correo.Subject)
        
        if demandante_match or demandada_match:
            print(f"\n👥 PARTES DEL PROCESO:")
            if demandante_match:
                print(f"   Demandante: {demandante_match.group(1).strip()}")
            if demandada_match:
                print(f"   Demandada: {demandada_match.group(1).strip()}")
        
        print(f"\n🎯 RESUMEN DE ACCIONES (MODO SIMULACIÓN):")
        print(f"   1. Crear PDF del correo")
        print(f"   2. Agregar los {correo.Attachments.Count} adjuntos al PDF")
        print(f"   3. Guardar como: {nombre_archivo}")
        print(f"   4. En la ruta: {ruta_final}")
        print(f"   5. Mover correo a carpeta 'Procesados'")
        
        # Preguntar si proceder
        print(f"\n{'='*70}")
        print(f"⚠️  ¿Deseas proceder con el procesamiento REAL? (s/n)")
        print(f"    's' = Crear carpetas y guardar archivos")
        print(f"    'n' = Solo simulación")
        respuesta = input("    Tu respuesta: ")
        
        if respuesta.lower() == 's':
            print(f"\n🚀 PROCESAMIENTO REAL...")
            
            try:
                # Crear carpeta si no existe
                ruta_final.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Carpeta verificada: {ruta_final}")
                
                # IMPORTANTE: Usar ruta ABSOLUTA para el directorio temporal
                temp_dir = Path.cwd() / "temp_procesamiento"
                
                # Limpiar si existe de antes
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                temp_dir.mkdir(exist_ok=True)
                print(f"   ✅ Directorio temporal creado: {temp_dir}")
                
                # 1. Crear PDF del correo
                pdf_correo = temp_dir / "00_correo.pdf"
                self.crear_pdf_correo(correo, pdf_correo)
                
                # 2. Guardar adjuntos con ruta ABSOLUTA
                for i, adj in enumerate(correo.Attachments, 1):
                    # Usar ruta absoluta completa
                    archivo_adj = temp_dir / adj.FileName
                    archivo_adj_absoluto = str(archivo_adj.absolute())
                    
                    print(f"   📎 Guardando: {adj.FileName}")
                    print(f"      En: {archivo_adj_absoluto}")
                    
                    adj.SaveAsFile(archivo_adj_absoluto)
                    print(f"   ✅ Adjunto guardado: {adj.FileName}")
                
                # 3. Combinar todos los PDFs
                archivo_final = ruta_final / nombre_archivo
                self.combinar_todos_pdfs(pdf_correo, temp_dir, archivo_final)
                
                # 4. Limpiar temporales
                shutil.rmtree(temp_dir)
                print(f"   ✅ Archivos temporales eliminados")
                
                # 5. Marcar correo como procesado
                correo.Categories = f"Procesado_{expediente}"
                correo.Save()
                print(f"   ✅ Correo marcado como procesado")
                
                # 6. Crear o mover a carpeta Procesados
                try:
                    carpeta_procesados = self.inbox.Folders("Procesados")
                except:
                    carpeta_procesados = self.inbox.Folders.Add("Procesados")
                    print(f"   ✅ Carpeta 'Procesados' creada")
                
                correo.Move(carpeta_procesados)
                print(f"   ✅ Correo movido a carpeta 'Procesados'")
                
                print(f"\n{'='*70}")
                print(f"✅✅✅ PROCESO COMPLETADO EXITOSAMENTE ✅✅✅")
                print(f"{'='*70}")
                print(f"   Expediente: {expediente}")
                print(f"   Archivo: {archivo_final}")
                print(f"   Tamaño: {archivo_final.stat().st_size / 1024:.1f} KB")
                
                # Log de éxito
                with open("procesamiento_exitoso.log", "a", encoding="utf-8") as log:
                    log.write(f"{datetime.now()}: {expediente} - {nombre_archivo}\n")
                
                return True
                
            except Exception as e:
                print(f"\n❌ ERROR durante el procesamiento: {e}")
                import traceback
                traceback.print_exc()  # Para ver exactamente dónde falla
                return False
    
    def crear_pdf_correo(self, correo, archivo_salida):
        """Crea un PDF del correo con formato profesional"""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        
        # Crear documento PDF
        doc = SimpleDocTemplate(str(archivo_salida), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor='black',
            spaceAfter=30
        )
        
        story.append(Paragraph("CORREO ELECTRÓNICO", titulo_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Información del correo
        info_style = styles['Normal']
        story.append(Paragraph(f"<b>De:</b> {correo.SenderName}", info_style))
        story.append(Paragraph(f"<b>Para:</b> {correo.To}", info_style))
        story.append(Paragraph(f"<b>Fecha:</b> {correo.ReceivedTime.strftime('%d/%m/%Y %H:%M')}", info_style))
        story.append(Paragraph(f"<b>Asunto:</b> {correo.Subject}", info_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Cuerpo del correo
        story.append(Paragraph("<b>Mensaje:</b>", info_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Limpiar y formatear el cuerpo
        cuerpo_limpio = correo.Body.replace('\r\n', '<br/>')
        cuerpo_limpio = cuerpo_limpio.replace('\n', '<br/>')
        
        # Dividir en párrafos si es muy largo
        lineas = cuerpo_limpio.split('<br/>')
        for linea in lineas[:100]:  # Limitar a 100 líneas
            if linea.strip():
                story.append(Paragraph(linea, info_style))
        
        # Construir PDF
        doc.build(story)
        print(f"   ✅ PDF del correo creado")
        return archivo_salida

    def combinar_todos_pdfs(self, pdf_correo, adjuntos_dir, archivo_final):
        """Combina el PDF del correo con los adjuntos"""
        merger = PyPDF2.PdfMerger()
        
        # 1. Agregar PDF del correo
        merger.append(str(pdf_correo))
        print(f"   ✅ PDF del correo agregado")
        
        # 2. Agregar adjuntos PDFs
        for archivo in adjuntos_dir.glob("*.pdf"):
            if archivo != pdf_correo:  # No agregar el correo dos veces
                try:
                    merger.append(str(archivo))
                    print(f"   ✅ Adjunto agregado: {archivo.name}")
                except Exception as e:
                    print(f"   ⚠️ No se pudo agregar {archivo.name}: {e}")
        
        # 3. Agregar imágenes convertidas a PDF
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            for imagen in adjuntos_dir.glob(ext):
                try:
                    # Convertir imagen a PDF
                    pdf_imagen = imagen.with_suffix('.temp.pdf')
                    img = Image.open(imagen)
                    img.save(str(pdf_imagen), "PDF")
                    merger.append(str(pdf_imagen))
                    print(f"   ✅ Imagen convertida y agregada: {imagen.name}")
                except Exception as e:
                    print(f"   ⚠️ No se pudo procesar imagen {imagen.name}: {e}")
        
        # 4. Guardar PDF combinado
        merger.write(str(archivo_final))
        merger.close()
        print(f"   ✅ PDF final creado: {archivo_final.name}")

# EJECUTAR
if __name__ == "__main__":
    procesador = ProcesadorCorreoJuzgado()
    procesador.procesar_correo_actual()