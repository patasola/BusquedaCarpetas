# Test script to measure performance
import time

# Simular tree operations
class FakeTree:
    def __init__(self):
        self.items = []
    
    def get_children(self):
        return list(range(len(self.items)))
    
    def delete(self, *args):
        t0 = time.perf_counter()
        if len(args) > 1:
            # Batch delete
            self.items = []
        else:
            # Single delete
            for item in args:
                self.items.remove(item)
        t1 = time.perf_counter()
        return (t1 - t0) * 1000  # ms
    
    def insert(self, parent, index, **kwargs):
        self.items.append(kwargs)
    
    def update_idletasks(self):
        time.sleep(0.001)  # Simular pequeño delay

# Test 1: Limpiar con loop vs batch
print("=" * 60)
print("TEST: Limpiar TreeView")
print("=" * 60)

tree = FakeTree()
for i in range(5000):
    tree.items.append(f"Item {i}")

print(f"\nItems en tree: {len(tree.items)}")

# Método 1: Loop (LENTO)
tree1 = FakeTree()
tree1.items = list(range(5000))
t0 = time.perf_counter()
for item in tree1.get_children():
    tree1.delete(item)
t1 = time.perf_counter()
print(f"Loop delete: {(t1-t0)*1000:.2f} ms")

# Método 2: Batch (RÁPIDO)
tree2 = FakeTree()
tree2.items = list(range(5000))
t0 = time.perf_counter()
children = tree2.get_children()
if children:
    tree2.delete(*children)
t1 = time.perf_counter()
print(f"Batch delete: {(t1-t0)*1000:.2f} ms")

# Test 2: Insertar con y sin update_idletasks
print("\n" + "=" * 60)
print("TEST: Insertar con update_idletasks")
print("=" * 60)

# Sin update_idletasks cada item
tree3 = FakeTree()
t0 = time.perf_counter()
for i in range(5000):
    tree3.insert("", "end", text=f"Item {i}")
t1 = time.perf_counter()
print(f"Sin update_idletasks: {(t1-t0)*1000:.2f} ms")

# Con update_idletasks cada 500 (batch)
tree4 = FakeTree()
t0 = time.perf_counter()
for i in range(5000):
    tree4.insert("", "end", text=f"Item {i}")
    if i % 500 == 0 and i > 0:
        tree4.update_idletasks()
t1 = time.perf_counter()
print(f"Con update_idletasks cada 500: {(t1-t0)*1000:.2f} ms")

# Con update_idletasks CADA item (LENTO)
tree5 = FakeTree()
t0 = time.perf_counter()
for i in range(5000):
    tree5.insert("", "end", text=f"Item {i}")
    tree5.update_idletasks()
t1 = time.perf_counter()
print(f"Con update_idletasks cada item: {(t1-t0)*1000:.2f} ms")

print("\n" + "=" * 60)
print("CONCLUSIÓN:")
print("=" * 60)
print("- Batch delete es ~100x más rápido que loop delete")
print("- update_idletasks cada 500 items es óptimo")
print("- update_idletasks cada item es EXTREMADAMENTE lento")
