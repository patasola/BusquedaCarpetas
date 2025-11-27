# test_procesamiento.py
print("=== MODO PRUEBA SEGURO ===")
print("Este script procesará 1 correo y te mostrará el resultado sin moverlo")

from procesador_automatico_v1 import ProcesadorAutomatico

# Crear procesador en modo prueba
procesador = ProcesadorAutomatico()

# Obtener el correo más reciente
mensajes = procesador.inbox.Items
mensajes.Sort("[ReceivedTime]", True)
primer_correo = mensajes.GetFirst()

print(f"\n📧 Correo seleccionado:")
print(f"   Asunto: {primer_correo.Subject}")
print(f"   De: {primer_correo.SenderName}")
print(f"   Fecha: {primer_correo.ReceivedTime}")

respuesta = input("\n¿Procesar este correo? (s/n): ")
if respuesta.lower() == 's':
    resultado = procesador.procesar_correo_individual(primer_correo)
    
    print(f"\n📊 RESULTADO:")
    print(f"   Exitoso: {resultado['exitoso']}")
    print(f"   Expediente: {resultado['expediente']}")
    print(f"   Archivo: {resultado['archivo']}")
    print(f"   Razón: {resultado['razon']}")
    
    if resultado['exitoso']:
        print("\n✅ El correo se procesó correctamente!")
        print("   NO se ha movido de tu bandeja (modo prueba)")
        print(f"   Revisa el archivo en: {resultado['archivo']}")