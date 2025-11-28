# src/database_manager.py - Gestor de Base de Datos SQL Server
import pyodbc
import threading
import time

class DatabaseManager:
    """Gestor de conexión a SQL Server para consulta de expedientes"""
    
    def __init__(self, app):
        self.app = app
        self.connection = None
        self.dsn = "csjsql"  # DSN correcto
        self.user = ""
        self.password = ""
        self._lock = threading.Lock()
        
    def conectar(self):
        """Establece conexión con la BD"""
        try:
            # Intentar conectar usando DSN
            conn_str = f"DSN={self.dsn};"
            if self.user:
                conn_str += f"UID={self.user};PWD={self.password};"
            
            # Opción alternativa con Driver directo si no hay DSN
            # conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=servidor;DATABASE=db;UID={user};PWD={pwd}"
            
            self.connection = pyodbc.connect(conn_str, timeout=3)
            return True
        except Exception as e:
            print(f"[DB Error] No se pudo conectar: {e}")
            return False

    def obtener_info_proceso(self, radicado):
        """
        Busca información de partes para un radicado.
        Retorna: (demandante, demandado)
        """
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
                return None, None
                
            return str_demandante, str_demandado
            
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
