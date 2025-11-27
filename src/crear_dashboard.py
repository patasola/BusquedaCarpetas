# crear_dashboard.py
import pandas as pd
from datetime import datetime
import json

# Cargar estadísticas
with open('expedientes_conocidos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Crear DataFrame
df_stats = pd.DataFrame([
    {
        'Fecha': datetime.now().strftime('%Y-%m-%d'),
        'Total Procesados': data['estadisticas']['total_procesados'],
        'Exitosos': data['estadisticas']['exitosos'],
        'Tasa Éxito': (data['estadisticas']['exitosos'] / 
                      max(data['estadisticas']['total_procesados'], 1) * 100)
    }
])

# Guardar o actualizar Excel
try:
    df_existente = pd.read_excel('dashboard_procesamiento.xlsx')
    df_final = pd.concat([df_existente, df_stats], ignore_index=True)
except:
    df_final = df_stats

df_final.to_excel('dashboard_procesamiento.xlsx', index=False)
print("📊 Dashboard actualizado: dashboard_procesamiento.xlsx")