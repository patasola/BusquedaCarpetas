# test_outlook_conexion.py
import win32com.client
import PyPDF2
from pathlib import Path

print("=== TEST DE CONEXIÓN OUTLOOK ===")

try:
    # Conectar con Outlook
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    inbox = namespace.GetDefaultFolder(6)  # 6 = Inbox
    
    # Contar correos
    total_correos = inbox.Items.Count
    print(f"✅ Conexión exitosa")
    print(f"📧 Total de correos en bandeja: {total_correos}")
    
    # Mostrar los últimos 3 correos
    mensajes = inbox.Items
    mensajes.Sort("[ReceivedTime]", True)
    
    print("\n📬 Últimos 3 correos:")
    for i in range(min(3, total_correos)):
        msg = mensajes.Item(i+1)
        print(f"\n  {i+1}. Asunto: {msg.Subject[:60]}")
        print(f"     De: {msg.SenderName}")
        print(f"     Adjuntos: {msg.Attachments.Count}")
        
        # Buscar expediente en el asunto
        import re
        match = re.search(r'(\d{4})-(\d{3,4})', msg.Subject)
        if match:
            print(f"     🎯 Expediente detectado: {match.group(0)}")
    
except Exception as e:
    print(f"❌ Error: {e}")