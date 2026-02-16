# src/database_manager.py - Gestor de Base de Datos SQL Server
import pyodbc
import threading
import time
import sys

class DatabaseManager:
    """Gestor de conexión a SQL Server para consulta de expedientes"""
    
    def __init__(self, app):
        self.app = app
        self.connection = None
        self.dsn = "csjsql"  # DSN correcto
        self.user = ""
        self.password = ""
        self._lock = threading.Lock()

        # Cache en memoria para optimizar búsquedas repetidas
        self._cache = {}  # {radicado: (demandante, demandado)}
        self._cache_max_size = 500

        # Connection pooling - Keep-alive
        self.last_query_time = 0
        self.keep_alive_timer = None

        # Auto-conectar al inicio
        self._auto_connect()    
        
    def conectar(self):
        """Establece conexión con la BD con reintentos robustos para SSPI"""
        intentos = [
            # Intento 1: DSN Estándar
            f"DSN={self.dsn};",
            # Intento 2: Trusted_Connection explícito
            f"DSN={self.dsn};Trusted_Connection=yes;",
            # Intento 3: Integrated Security explícito
            f"DSN={self.dsn};Integrated Security=SSPI;",
            # Intento 4: Ambos flags de seguridad (algunos drivers lo requieren)
            f"DSN={self.dsn};Trusted_Connection=yes;Integrated Security=SSPI;",
            # Intento 5: Conexión directa (si el usuario provee credenciales)
            f"DSN={self.dsn};UID={self.user};PWD={self.password};" if self.user else None
        ]
        
        last_error = ""
        for i, conn_str in enumerate(intentos):
            if not conn_str: continue
            try:
                # print(f"[DB] Intentando variante {i+1}...") 
                self.connection = pyodbc.connect(conn_str, timeout=3)
                print(f"[DB] Conexión exitosa (Variante {i+1})")
                sys.stdout.flush()
                return True
            except Exception as e:
                last_error = str(e)
                # print(f"[DB] Falló variante {i+1}: {last_error}")
                continue

        print(f"[DB Error] Sin conexión SQL tras {len(intentos)} intentos. Último error: {last_error}")
        sys.stdout.flush()
        return False

    def obtener_info_proceso(self, radicado):
        """
        Busca información de partes para un radicado.
        Retorna: (demandante, demandado)
        """
        # Verificar cache primero
        if radicado in self._cache:
            self.last_query_time = time.time()
            return self._cache[radicado]
        if not self.connection:
            if not self.conectar():
                return None, None
                
        try:
            cursor = self.connection.cursor()
            
            # Limpiar radicado para asegurar que tenga 23 dígitos
            # Eliminamos guiones y espacios
            radicado_limpio = ''.join(filter(str.isdigit, str(radicado)))
            
            # Si tiene más de 23 dígitos (ej: tiene sufijos), cortamos a 23
            if len(radicado_limpio) > 23:
                radicado_limpio = radicado_limpio[:23]
            
            # Si tiene menos de 23, intentamos buscar con LIKE
            # pero idealmente debe ser exacto para T112DRSUJEPROC
            
            query = """
                SELECT A112CODISUJE, A112NOMBSUJE 
                FROM T112DRSUJEPROC 
                WHERE A112LLAVPROC = ?
            """
            
            cursor.execute(query, (radicado_limpio,))
            rows = cursor.fetchall()
            
            demandantes = []
            demandados = []
            
            for row in rows:
                codigo = row[0]
                nombre = row[1].strip() if row[1] else ""
                
                if codigo == '0001': # Demandante
                    demandantes.append(nombre)
                elif codigo == '0002': # Demandado
                    demandados.append(nombre)
            
            # Unir múltiples partes con " | "
            str_demandante = " | ".join(demandantes) if demandantes else "Desconocido"
            str_demandado = " | ".join(demandados) if demandados else "Desconocido"

            # Si no se encontró nada, retornar None para no llenar con "Desconocido"
            if not demandantes and not demandados:
                self._cache[radicado] = (None, None)
                return None, None

            # Guardar en cache
            result = (str_demandante, str_demandado)
            self._cache[radicado] = result

            # Limpiar cache si excede tamaño máximo (FIFO simple)
            if len(self._cache) > self._cache_max_size:
                for _ in range(100):
                    self._cache.pop(next(iter(self._cache)))
            self.last_query_time = time.time()
            return result
            
        except pyodbc.Error as e:
            print(f"[DB Query Error] {e}")
            # Si hay error de conexión, intentamos reconectar una vez
            if "08S01" in str(e) or "08001" in str(e):
                self.connection = None
            return None, None
        finally:
            try:
                cursor.close()
            except:
                pass

    def test_connection(self, dsn, user="", password=""):
        """Prueba una configuración de conexión"""
        try:
            conn_str = f"DSN={dsn};"
            if user:
                conn_str += f"UID={user};PWD={password};"
            
            conn = pyodbc.connect(conn_str, timeout=3)
            conn.close()
            return True, "Conexión exitosa"
        except Exception as e:
            return False, str(e)
        
    def limpiar_cache(self):
        """Limpia el cache de procesos"""
        self._cache.clear()
        print("[DB] Cache limpiado")

    def get_cache_stats(self):
        """Retorna estadísticas del cache"""
        return {
            'size': len(self._cache),
            'max_size': self._cache_max_size
        }
      
    def _auto_connect(self):
        """Mantiene conexión viva con keep-alive timer"""
        if not self.connection or self._connection_stale():
            self.conectar()
        
        if self.keep_alive_timer:
            self.keep_alive_timer.cancel()
        
        self.keep_alive_timer = threading.Timer(300, self._auto_connect)
        self.keep_alive_timer.daemon = True
        self.keep_alive_timer.start()

    def _connection_stale(self):
        """Verifica si conexión inactiva >10 min"""
        if self.last_query_time == 0:
            return False
        return time.time() - self.last_query_time > 600
