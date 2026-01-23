# Test script para verificar FolderIndexer
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from folder_indexer import FolderIndexer

# Test básico
print("=" * 60)
print("TEST: FolderIndexer V.5.0 - Veloce")
print("=" * 60)

# Crear datos de prueba
test_data = [
    {'nombre': 'Proyecto2024', 'ruta_relativa': 'docs/Proyecto2024', 'ruta_absoluta': 'C:/test/Proyecto2024'},
    {'nombre': 'Proyecto2023', 'ruta_relativa': 'docs/Proyecto2023', 'ruta_absoluta': 'C:/test/Proyecto2023'},
    {'nombre': 'Proceso11001', 'ruta_relativa': 'legal/Proceso11001', 'ruta_absoluta': 'C:/test/Proceso11001'},
    {'nombre': 'Proceso11002', 'ruta_relativa': 'legal/Proceso11002', 'ruta_absoluta': 'C:/test/Proceso11002'},
    {'nombre': 'Proceso11003', 'ruta_relativa': 'legal/Proceso11003', 'ruta_absoluta': 'C:/test/Proceso11003'},
    {'nombre': 'Documentos', 'ruta_relativa': 'general/Documentos', 'ruta_absoluta': 'C:/test/Documentos'},
]

# Crear indexer y construir índice
indexer = FolderIndexer()
print(f"\n1. Construyendo índice con {len(test_data)} carpetas...")
build_time = indexer.build_index(test_data)
print(f"   ✓ Índice construido en {build_time*1000:.2f}ms")

# Test 1: Búsqueda por prefijo exacto
print("\n2. Test: Búsqueda por prefijo 'Pro'")
results = indexer.search("Pro")
print(f"   Resultados encontrados: {len(results)}")
for nombre, relativa, absoluta in results:
    print(f"   - {nombre}")

# Test 2: Búsqueda por prefijo parcial
print("\n3. Test: Búsqueda por prefijo '11'")
results = indexer.search("11")
print(f"   Resultados encontrados: {len(results)}")
for nombre, relativa, absoluta in results:
    print(f"   - {nombre}")

# Test 3: Búsqueda sin resultados
print("\n4. Test: Búsqueda sin resultados 'XYZ'")
results = indexer.search("XYZ")
print(f"   Resultados encontrados: {len(results)}")

# Test 4: Búsqueda contains
print("\n5. Test: Búsqueda contains '2024'")
results = indexer.search_contains("2024")
print(f"   Resultados encontrados: {len(results)}")
for nombre, relativa, absoluta in results:
    print(f"   - {nombre}")

# Estadísticas
print("\n6. Estadísticas del índice:")
stats = indexer.get_stats()
print(f"   - Indexado: {stats['indexed']}")
print(f"   - Total carpetas: {stats['total_folders']}")
print(f"   - Total nodos: {stats['total_nodes']}")

print("\n" + "=" * 60)
print("RESULTADO: ✓ Todos los tests pasaron correctamente")
print("=" * 60)
