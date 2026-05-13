# web_server/server.py - BusquedaCarpetas Web Server V7
import os
import sys
import json
import subprocess
import sqlite3
import threading
import unicodedata
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS

# ─── Añadir el directorio raíz al path para importar ContentIndexer ─────────
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)
from src.core.content_indexer import ContentIndexer

# ─── Configuración ───────────────────────────────────────────────────────────
PORT = 8080
HOST = '0.0.0.0'  # Escuchar en todas las interfaces de red
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
CLIENT_DIR = os.path.join(os.path.dirname(__file__), 'client')

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)

indexer = ContentIndexer()

# ─── Normalización Unicode ───────────────────────────────────────────────────
def strip_accents(text):
    """Elimina diacríticos y convierte a minúsculas para búsqueda insensible a acentos"""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).lower()

def search_normalized(q, field, extension):
    """Busca con la query original Y su versión sin acentos, fusiona sin duplicados"""
    results = indexer.search(q, search_field=field, extension=extension)
    seen = {r['path'] for r in results}

    q_norm = strip_accents(q)
    if q_norm != q.lower():  # Solo si hay diferencia
        results2 = indexer.search(q_norm, search_field=field, extension=extension)
        for r in results2:
            if r['path'] not in seen:
                results.append(r)
                seen.add(r['path'])
    return results
_indexing_status = {'running': False, 'message': 'Listo', 'progress': 0}
_indexing_lock = threading.Lock()

# ─── Rutas Principales ───────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

# ─── API: Búsqueda ───────────────────────────────────────────────────────────

@app.route('/api/search')
def search():
    q = request.args.get('q', '').strip()
    ext = request.args.get('ext', 'all').strip()
    field = request.args.get('field', 'content').strip()
    limit = min(int(request.args.get('limit', 200)), 500)

    if not q or len(q) < 2:
        return jsonify({'results': [], 'count': 0, 'query': q})

    try:
        extension = None if ext == 'all' else f'.{ext}'
        results = search_normalized(q, field, extension)

        # Limitar y serializar
        limited = results[:limit]
        serialized = []
        for r in limited:
            serialized.append({
                'name': r.get('name', ''),
                'path': r.get('path', ''),
                'snippet': r.get('snippet', ''),
                'is_folder': r.get('is_folder', False),
                'ext': os.path.splitext(r.get('name', ''))[1].lower().lstrip('.'),
                'dir': os.path.dirname(r.get('path', '')),
                'mtime': r.get('mtime')
            })

        return jsonify({
            'results': serialized,
            'count': len(results),
            'showing': len(serialized),
            'query': q
        })
    except Exception as e:
        return jsonify({'error': str(e), 'results': [], 'count': 0}), 500

# ─── API: Estadísticas ───────────────────────────────────────────────────────

@app.route('/api/stats')
def stats():
    try:
        s = indexer.get_index_stats()
        
        # Añadir info de última modificación de la BD
        db_path = indexer.db_path
        last_update = ''
        if os.path.exists(db_path):
            mtime = os.path.getmtime(db_path)
            last_update = datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M')

        return jsonify({
            'total_files': s.get('total_files', 0),
            'last_update': last_update,
            'db_size_mb': round(os.path.getsize(db_path) / (1024*1024), 2) if os.path.exists(db_path) else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ─── API: Abrir Carpeta (solo en el servidor) ────────────────────────────────

@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    data = request.get_json()
    path = data.get('path', '')
    
    if not path or not os.path.exists(path):
        return jsonify({'ok': False, 'error': 'Ruta no encontrada'}), 404
    
    try:
        # Si es un archivo, abrir su carpeta contenedora
        if os.path.isfile(path):
            folder = os.path.dirname(path)
            # En Windows, abrir Explorer y seleccionar el archivo
            subprocess.Popen(['explorer', '/select,', os.path.normpath(path)])
        else:
            subprocess.Popen(['explorer', os.path.normpath(path)])
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

# ─── API: Descargar Archivo ──────────────────────────────────────────────────

@app.route('/api/download')
def download():
    path = request.args.get('path', '')
    if not path or not os.path.isfile(path):
        abort(404)
    
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    
    try:
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        abort(500)

# ─── API: Estado del indexado ────────────────────────────────────────────────

@app.route('/api/indexing-status')
def indexing_status():
    return jsonify(_indexing_status)

# ─── API: Obtener ubicaciones configuradas ───────────────────────────────────

@app.route('/api/locations')
def get_locations():
    try:
        app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser("~"))
        config_path = os.path.join(app_data, "BusquedaCarpetas", "search_locations.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                locations = json.load(f)
            return jsonify({'locations': locations})
        return jsonify({'locations': []})
    except Exception as e:
        return jsonify({'locations': [], 'error': str(e)})

# ─── API: Archivos del Cliente ──────────────────────────────────────────────────

@app.route('/client/<path:filename>')
def serve_client_file(filename):
    """Sirve los archivos del instalador del cliente"""
    return send_from_directory(CLIENT_DIR, filename)

@app.route('/download/instalar_cliente.bat')
def download_installer():
    """Genera dinámicamente el instalador con la IP del servidor embebida"""
    import socket
    local_ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except: pass

    bat_content = f"""@echo off
chcp 65001 >nul
title Instalador BusquedaCarpetas - Acceso Directo

echo.
echo  ============================================================
echo   BusquedaCarpetas - Instalador de Acceso Directo
echo  ============================================================
echo.
echo  Configurando acceso para: http://{local_ip}:{PORT}
echo.

set "SERVIDOR={local_ip}"
set "PUERTO={PORT}"
set "INSTALL_DIR=%LOCALAPPDATA%\\BusquedaCarpetasClient"

echo [1/3] Preparando directorio...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [2/3] Descargando manejador (handler.vbs)...
del "%INSTALL_DIR%\\handler.vbs" 2>nul

echo Intentando con curl...
curl -s -f "http://%SERVIDOR%:%PUERTO%/client/handler.vbs" -o "%INSTALL_DIR%\\handler.vbs"

if not exist "%INSTALL_DIR%\\handler.vbs" (
    echo Intentando con PowerShell...
    powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'http://%SERVIDOR%:%PUERTO%/client/handler.vbs' -OutFile '%INSTALL_DIR%\\handler.vbs'"
)

if not exist "%INSTALL_DIR%\\handler.vbs" (
    echo.
    echo ERROR CRITICO: No se pudo descargar el archivo de control.
    echo Verifica que tengas acceso a http://%SERVIDOR%:%PUERTO% en el navegador.
    echo.
    pause
    exit /b 1
)

echo [3/3] Registrando protocolo busqueda:// en el sistema...
REG ADD "HKCU\\Software\\Classes\\busqueda" /ve /d "URL:BusquedaCarpetas Protocol" /f >nul
REG ADD "HKCU\\Software\\Classes\\busqueda" /v "URL Protocol" /d "" /f >nul
REG ADD "HKCU\\Software\\Classes\\busqueda\\shell" /f >nul
REG ADD "HKCU\\Software\\Classes\\busqueda\\shell\\open" /f >nul
REG ADD "HKCU\\Software\\Classes\\busqueda\\shell\\open\\command" /ve /d "wscript.exe \\"%INSTALL_DIR%\\handler.vbs\\" \\"%%1\\"" /f >nul

echo.
echo  ============================================================
echo   ¡INSTALACION EXITOSA!
echo  ============================================================
echo.
echo  Ya puedes abrir archivos directamente desde el buscador.
echo  Vuelve al navegador y haz una busqueda de prueba.
echo.
pause
"""
    from flask import Response
    return Response(
        bat_content.encode('cp1252', errors='replace'),
        mimetype='application/octet-stream',
        headers={'Content-Disposition': 'attachment; filename=instalar_cliente.bat'}
    )

@app.route('/instalar')
def installer_page():
    """Página de instalación del cliente con instrucciones"""
    return send_from_directory(STATIC_DIR, 'install.html')

@app.route('/api/server-info')
def server_info():
    """Devuelve info del servidor"""
    import socket
    local_ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except: pass
    return jsonify({'ip': local_ip, 'port': PORT, 'is_server': True})

# ─── Punto de entrada ────────────────────────────────────────────────────────

if __name__ == '__main__':
    local_ip = '127.0.0.1'
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except: pass

    print("=" * 60)
    print("  BusquedaCarpetas Web Server V7 'Purgatorio'")
    print("=" * 60)
    print(f"  Local:   http://localhost:{PORT}")
    print(f"  Red:     http://{local_ip}:{PORT}")
    print(f"  BD:      {indexer.db_path}")
    print("=" * 60)
    print("  Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
