# test_integration.py
import sys
import os
import time

# Asegurar que el directorio raíz está en el path para importar src como paquete
sys.path.insert(0, os.getcwd())

try:
    from src.cache_manager import CacheManager
    print("[OK] Import exitoso: src.cache_manager")
except ImportError as e:
    print(f"[ERROR] Error de importación: {e}")
    sys.exit(1)

def test_integration():
    print("=" * 60)
    print("TEST DE INTEGRACIÓN: CacheManager + FolderIndexer")
    print("=" * 60)

    # 1. Inicializar CacheManager
    print("\n1. Inicializando CacheManager...")
    cm = CacheManager()
    
    # Verificar si el indexer existe
    if hasattr(cm, 'indexer'):
        print("   [OK] cm.indexer existe")
    else:
        print("   [FAIL] cm.indexer NO existe")
        return

    # 2. Verificar estado inicial
    print(f"   Estado inicial index_ready: {cm.index_ready}")
    
    # 3. Simular datos en caché si está vacío
    if not cm.cache.valido or not cm.cache.directorios.get('directorios'):
        print("\n2. Cache vacío o inválido. Creando datos de prueba simulados...")
        test_data = [
            {'nombre': 'ProyectoAlpha', 'ruta_relativa': 'docs/ProyectoAlpha', 'ruta_absoluta': 'C:/test/ProyectoAlpha'},
            {'nombre': 'ProyectoBeta', 'ruta_relativa': 'docs/ProyectoBeta', 'ruta_absoluta': 'C:/test/ProyectoBeta'},
            {'nombre': 'Informe2024', 'ruta_relativa': 'docs/Informe2024', 'ruta_absoluta': 'C:/test/Informe2024'},
            {'nombre': 'Informe2025', 'ruta_relativa': 'docs/Informe2025', 'ruta_absoluta': 'C:/test/Informe2025'},
        ]
        cm.cache.directorios = {
            'directorios': test_data,
            'total': len(test_data),
            'timestamp': time.time()
        }
        cm.cache.valido = True
        cm.cache.ruta_base = "C:/test"
        print(f"   Datos simulados inyectados: {len(test_data)} carpetas")
        
        # Construir índice manualmente ya que inyectamos datos
        print("   Construyendo índice manualmente...")
        cm._build_index()
    
    # 4. Verificar que el índice está listo
    if cm.index_ready:
        print("   [OK] Índice marcado como LISTO")
    else:
        print("   [FAIL] Índice NO está listo")
        return

    # 5. Probar búsqueda
    print("\n3. Probando búsqueda 'Proye'...")
    start = time.time()
    resultados = cm.buscar_en_cache("Proye")
    duration = (time.time() - start) * 1000
    
    print(f"   Tiempo: {duration:.2f}ms")
    print(f"   Resultados encontrados: {len(resultados)}")
    
    found = False
    for r in resultados:
        print(f"   - {r[0]}")
        if "ProyectoAlpha" in r[0]:
            found = True
            
    if found:
        print("   [OK] Búsqueda exitosa: Se encontraron los resultados esperados")
    else:
        print("   [FAIL] Búsqueda fallida: No se encontraron los resultados esperados")

    # 6. Probar búsqueda contains (si implementado)
    print("\n4. Probando búsqueda contains '2024'...")
    resultados_contains = cm.buscar_en_cache("2024", use_prefix=False)
    print(f"   Resultados encontrados: {len(resultados_contains)}")
    for r in resultados_contains:
        print(f"   - {r[0]}")

if __name__ == "__main__":
    test_integration()
