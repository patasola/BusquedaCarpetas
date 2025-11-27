# extractor_expedientes_mejorado.py
import re
import json
from pathlib import Path
from datetime import datetime
import logging

class ExtractorExpedientesMejorado:
    def __init__(self):
        # Configurar logging
        logging.basicConfig(
            filename='procesamiento_correos.log',
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        
        # Cargar o crear base de conocimiento
        self.db_path = Path("expedientes_conocidos.json")
        self.cargar_base_conocimiento()
        
        # Patrones de búsqueda ordenados por confiabilidad
        self.patrones = [
            # Patrón 1: Formato expediente en asunto (más confiable)
            (r'(\d{4})-(\d{3,4})', 'expediente_corto', 0.95),
            
            # Patrón 2: Radicado completo
            (r'110013105017(\d{4})(\d{5})00', 'radicado_completo', 0.90),
            
            # Patrón 3: Después de "Radicado No."
            (r'Radicado\s*No\.\s*(\d{23})', 'radicado_texto', 0.85),
            
            # Patrón 4: Después de "Exp." o "Expediente"
            (r'(?:Exp\.|Expediente)\s*(\d{4})-(\d{3,4})', 'exp_texto', 0.80),
        ]
    
    def cargar_base_conocimiento(self):
        """Carga la base de datos de expedientes conocidos"""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
        else:
            # Crear estructura inicial
            self.db = {
                'expedientes': {},
                'remitentes': {},
                'patrones_exitosos': {},
                'estadisticas': {
                    'total_procesados': 0,
                    'exitosos': 0,
                    'fallidos': 0
                }
            }
            self.guardar_base_conocimiento()
    
    def guardar_base_conocimiento(self):
        """Guarda la base de datos actualizada"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=2, ensure_ascii=False)
    
    def extraer_expediente(self, asunto, cuerpo, remitente):
        """
        Extrae el expediente con múltiples estrategias
        Retorna: (expediente, confianza, método)
        """
        texto_completo = f"{asunto}\n{cuerpo}"
        
        # Estrategia 1: Buscar con patrones
        for patron, nombre, confianza_base in self.patrones:
            match = re.search(patron, texto_completo, re.IGNORECASE)
            if match:
                if nombre == 'expediente_corto' or nombre == 'exp_texto':
                    expediente = f"{match.group(1)}-{match.group(2).lstrip('0')}"
                elif nombre == 'radicado_completo':
                    año = match.group(1)
                    exp = match.group(2).lstrip('0')[:3]
                    expediente = f"{año}-{exp}"
                elif nombre == 'radicado_texto':
                    # Extraer año y expediente del radicado de 23 dígitos
                    radicado = match.group(1)
                    año = radicado[14:18]
                    exp = radicado[18:21].lstrip('0')
                    expediente = f"{año}-{exp}"
                
                # Registrar patrón exitoso
                self.db['patrones_exitosos'][nombre] = \
                    self.db['patrones_exitosos'].get(nombre, 0) + 1
                
                logging.info(f"Expediente encontrado: {expediente} (método: {nombre}, confianza: {confianza_base})")
                return expediente, confianza_base, nombre
        
        # Estrategia 2: Buscar por remitente conocido
        if remitente in self.db['remitentes']:
            expedientes_remitente = self.db['remitentes'][remitente]
            if len(expedientes_remitente) == 1:
                # Si este remitente siempre envía del mismo expediente
                expediente = expedientes_remitente[0]
                logging.info(f"Expediente por remitente: {expediente}")
                return expediente, 0.70, 'remitente'
        
        # Estrategia 3: Buscar nombres de partes
        for exp, datos in self.db['expedientes'].items():
            if 'partes' in datos:
                for parte in datos['partes']:
                    if parte.lower() in texto_completo.lower():
                        logging.info(f"Expediente por nombre de parte: {exp}")
                        return exp, 0.60, 'nombre_parte'
        
        logging.warning(f"No se pudo identificar expediente. Asunto: {asunto[:50]}")
        return None, 0.0, None
    
    def aprender_de_clasificacion(self, expediente, asunto, remitente, partes=None):
        """Actualiza la base de conocimiento con nueva información"""
        # Actualizar expedientes
        if expediente not in self.db['expedientes']:
            self.db['expedientes'][expediente] = {
                'creado': datetime.now().isoformat(),
                'contador': 0,
                'partes': []
            }
        
        self.db['expedientes'][expediente]['contador'] += 1
        
        # Actualizar partes si se proporcionan
        if partes:
            for parte in partes:
                if parte not in self.db['expedientes'][expediente]['partes']:
                    self.db['expedientes'][expediente]['partes'].append(parte)
        
        # Actualizar remitentes
        if remitente not in self.db['remitentes']:
            self.db['remitentes'][remitente] = []
        if expediente not in self.db['remitentes'][remitente]:
            self.db['remitentes'][remitente].append(expediente)
        
        # Actualizar estadísticas
        self.db['estadisticas']['total_procesados'] += 1
        self.db['estadisticas']['exitosos'] += 1
        
        self.guardar_base_conocimiento()
    
    def generar_reporte(self):
        """Genera estadísticas de efectividad"""
        total = self.db['estadisticas']['total_procesados']
        if total == 0:
            return "No hay datos para reportar"
        
        exitosos = self.db['estadisticas']['exitosos']
        tasa_exito = (exitosos / total) * 100
        
        reporte = f"""
        === REPORTE DE PROCESAMIENTO ===
        Total procesados: {total}
        Exitosos: {exitosos} ({tasa_exito:.1f}%)
        
        Métodos más efectivos:
        """
        
        for metodo, cantidad in sorted(self.db['patrones_exitosos'].items(), 
                                      key=lambda x: x[1], reverse=True):
            reporte += f"  - {metodo}: {cantidad} veces\n"
        
        return reporte