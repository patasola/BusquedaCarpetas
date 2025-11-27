# procesador_test_real.py
import win32com.client
from pathlib import Path
import re
from datetime import datetime

print("=== PROCESADOR DE PRUEBA - CORREO REAL ===\n")

# Conectar con Outlook
outlook = win32com.client.Dispatch("Outlook.Application")
namespace = outlook.GetNamespace("MAPI")
inbox = namespace.GetDefaultFolder(6)

# Obtener el correo
correo = inbox.Items.Item(1)

print(f"📧 ANALIZANDO CORREO:")
print(f"   De: {correo.SenderName}")
print(f"   Asunto: {correo.Subject}")
print(f"   Fecha: {correo.ReceivedTime}")
print(f"   Cuerpo (primeros 200 caracteres):")
print(f"   {correo.Body[:200]}...")

print(f"\n🔍 BÚSQUEDA DE EXPEDIENTE:")

# Buscar patrones de expediente
texto_completo = f"{correo.Subject}\n{correo.Body}"

# Patrones de búsqueda
patrones = [
    (r'(\d{4})-(\d{3,4})', 'Formato YYYY-XXX'),
    (r'Radicado\s*No\.\s*(\d{23})', 'Radicado completo'),
    (r'Proceso\s*(\d+)', 'Número de proceso'),
    (r'Expediente\s*(\d+)', 'Número expediente'),
]

expediente_encontrado = None
for patron, descripcion in patrones:
    match = re.search(patron, texto_completo, re.IGNORECASE)
    if match:
        print(f"   ✅ Encontrado con patrón '{descripcion}': {match.group(0)}")
        expediente_encontrado = match.group(0)
        break
else:
    print(f"   ❌ No se encontró ningún patrón de expediente")

print(f"\n📁 SIMULACIÓN DE GUARDADO:")
if expediente_encontrado:
    print(f"   El correo se guardaría en el expediente: {expediente_encontrado}")
else:
    print(f"   El correo iría a la carpeta 'Pendiente_Revisión'")
    print(f"   Razón: No se pudo identificar automáticamente el expediente")

print(f"\n💡 SUGERENCIA:")
print(f"   Para este tipo de correos, podrías:")
print(f"   1. Crear una regla por remitente (Fredy Rico -> expediente específico)")
print(f"   2. Buscar palabras clave en el cuerpo")
print(f"   3. Moverlo a revisión manual")

# Preguntar si quiere mover el correo a una carpeta específica
print(f"\n⚠️ ACCIÓN MANUAL:")
print(f"Este correo parece ser informativo, no judicial.")
print(f"¿Deseas crear una carpeta 'No_Judiciales' para estos casos? (s/n): ", end="")
respuesta = input()

if respuesta.lower() == 's':
    try:
        # Crear carpeta si no existe
        carpeta_no_judicial = inbox.Folders.Add("No_Judiciales")
        print(f"✅ Carpeta 'No_Judiciales' creada")
    except:
        print(f"ℹ️ La carpeta ya existe o no se pudo crear")