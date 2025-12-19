# src/folder_indexer.py - Índice Trie para búsqueda ultra-rápida V.5.0
"""
Índice Trie (Prefix Tree) optimizado para búsqueda de carpetas.
Reduce búsquedas de O(n) a O(m) donde m = largo del criterio.
"""

import time
from typing import List, Dict, Tuple

class TrieNode:
    """Nodo del árbol Trie"""
    __slots__ = ['children', 'folder_indices', 'is_end']
    
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.folder_indices: List[int] = []  # Índices de carpetas que contienen este prefijo
        self.is_end: bool = False

class FolderIndexer:
    """
    Índice Trie optimizado para búsqueda de carpetas.
    
    Ventajas:
    - Búsqueda O(m) vs O(n) lineal
    - Soporte para prefijos
    - Resultados ordenados por relevancia
    """
    
    def __init__(self):
        self.root = TrieNode()
        self.folders: List[Dict] = []  # Array de todas las carpetas
        self.indexed = False
        
    def build_index(self, carpetas: List[Dict]) -> float:
        """
        Construye el índice Trie a partir de la lista de carpetas.
        
        Args:
            carpetas: Lista de diccionarios con 'nombre', 'ruta_relativa', 'ruta_absoluta'
        
        Returns:
            Tiempo de construcción en segundos
        """
        start_time = time.time()
        
        self.folders = carpetas
        self.root = TrieNode()
        
        for idx, carpeta in enumerate(carpetas):
            nombre_lower = carpeta['nombre'].lower()
            # Insertar nombre completo
            self._insert(nombre_lower, idx)
            
            # OPTIMIZACIÓN: También indexar por palabras individuales
            # Ejemplo: "Proyecto Web" → indexa "proyecto" y "web"
            palabras = nombre_lower.split()
            if len(palabras) > 1:
                for palabra in palabras:
                    if len(palabra) > 2:  # Ignorar palabras muy cortas
                        self._insert(palabra, idx)
        
        self.indexed = True
        build_time = time.time() - start_time
        
        print(f"[INDEXER] Índice construido: {len(carpetas):,} carpetas en {build_time:.3f}s")
        return build_time
    
    def _insert(self, texto: str, folder_idx: int):
        """Inserta un texto en el Trie"""
        node = self.root
        
        for char in texto:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            
            # Agregar índice a todos los nodos del camino
            if folder_idx not in node.folder_indices:
                node.folder_indices.append(folder_idx)
        
        node.is_end = True
    
    def search(self, criterio: str, max_results: int = 2000) -> List[Tuple]:
        """
        Búsqueda ultra-rápida usando el índice Trie.
        
        Args:
            criterio: Texto a buscar
            max_results: Máximo número de resultados
        
        Returns:
            Lista de tuplas (nombre, ruta_relativa, ruta_absoluta)
        """
        if not self.indexed or not self.folders:
            print("[INDEXER] Índice no disponible")
            return []
        
        start_time = time.time()
        criterio_lower = criterio.lower().strip()
        
        if not criterio_lower:
            return []
        
        # Navegar al nodo del prefijo
        node = self.root
        for char in criterio_lower:
            if char not in node.children:
                # No hay resultados con este prefijo
                search_time = time.time() - start_time
                print(f"[INDEXER] Sin resultados para '{criterio}' en {search_time*1000:.1f}ms")
                return []
            node = node.children[char]
        
        # Recolectar índices (ya están en el nodo)
        result_indices = node.folder_indices[:max_results]
        
        # Convertir índices a resultados
        resultados = []
        for idx in result_indices:
            carpeta = self.folders[idx]
            resultados.append((
                carpeta['nombre'],
                carpeta['ruta_relativa'],
                carpeta['ruta_absoluta']
            ))
        
        search_time = time.time() - start_time
        print(f"[INDEXER] Búsqueda '{criterio}': {len(resultados)} resultados en {search_time*1000:.1f}ms")
        
        return resultados
    
    def search_contains(self, criterio: str, max_results: int = 2000) -> List[Tuple]:
        """
        Búsqueda que encuentra el criterio en cualquier parte del nombre.
        Más lento que search() pero más flexible.
        
        Args:
            criterio: Texto a buscar
            max_results: Máximo número de resultados
        
        Returns:
            Lista de tuplas (nombre, ruta_relativa, ruta_absoluta)
        """
        if not self.indexed or not self.folders:
            return []
        
        start_time = time.time()
        criterio_lower = criterio.lower().strip()
        
        if not criterio_lower:
            return []
        
        # Búsqueda lineal (fallback para contains)
        # En el futuro se podría optimizar con suffix tree
        resultados = []
        for carpeta in self.folders:
            if len(resultados) >= max_results:
                break
            
            if criterio_lower in carpeta['nombre'].lower():
                resultados.append((
                    carpeta['nombre'],
                    carpeta['ruta_relativa'],
                    carpeta['ruta_absoluta']
                ))
        
        search_time = time.time() - start_time
        print(f"[INDEXER] Búsqueda contains '{criterio}': {len(resultados)} en {search_time*1000:.1f}ms")
        
        return resultados
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del índice"""
        def count_nodes(node):
            count = 1
            for child in node.children.values():
                count += count_nodes(child)
            return count
        
        return {
            'indexed': self.indexed,
            'total_folders': len(self.folders),
            'total_nodes': count_nodes(self.root) if self.indexed else 0
        }
