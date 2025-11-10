from pathlib import Path
DATA = Path(__file__).resolve().parents[1] / "data"
DROPS = DATA / "drops"
DATA.mkdir(parents=True, exist_ok=True)
DROPS.mkdir(parents=True, exist_ok=True)

# Si hay un fichero con nombre erróneo ' productos.csv' (espacio), renombrarlo a 'productos.csv'
bad_prod = DATA / ' productos.csv'
good_prod = DATA / 'productos.csv'
try:
    if bad_prod.exists() and not good_prod.exists():
        bad_prod.replace(good_prod)
        print('Renombrado:', bad_prod, '->', good_prod)
except Exception as e:
    print('No se pudo renombrar productos (continuando):', e)

# Ventas de ejemplo: muchas filas válidas + algunas filas erróneas al final para probar quarantine
csv = """fecha_venta,id_cliente,id_producto,unidades,precio_unitario
2025-07-07,C001,P001,2,2900
2025-07-07,C002,P002,1,2100
2025-07-07,C003,P003,3,420
2025-07-07,C004,P004,2,310
2025-07-07,C005,P005,1,3500
2025-07-07,C006,P006,5,180
2025-07-07,C007,P007,2,95
2025-07-07,C008,P008,3,60
2025-07-07,C009,P009,1,2800
2025-07-07,C010,P010,2,650
2025-07-07,C011,P011,1,520
2025-07-07,C012,P012,2,480
2025-07-07,C013,P013,4,85
2025-07-07,C014,P014,5,45
2025-07-07,C015,P015,1,890
2025-07-07,C016,P016,2,250
2025-07-07,C017,P017,1,420
2025-07-07,C018,P018,1,370
2025-07-07,C019,P019,2,310
2025-07-07,C020,P020,1,1250

# --- filas erróneas para pruebas de quarantine ---
# 1) cliente faltante
2025-07-07,,P021,2,1500
# 2) id_producto mal formado
2025-07-07,C022,XX21,1,800
# 3) unidades negativas
2025-07-07,C023,P023,-2,420
# 4) precio negativo
2025-07-07,C024,P024,1,-100
# 5) fecha inválida
not-a-date,C025,P025,1,300
# 6) precio con formato no numérico
2025-07-07,C026,P026,1,one-hundred
"""

file_path = DROPS / "ventas.csv"
file_path.write_text(csv, encoding='utf-8')
print('Generado:', file_path)

