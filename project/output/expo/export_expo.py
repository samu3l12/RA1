
"""
Script liviano para exportar ejemplos (heads) que usarás en la pizarra/exposición.
Genera CSVs en `project/output/expo/` a partir de:
 - project/data/drops/ventas.csv            -> ventas_raw_head.csv
 - project/data/productos.csv               -> productos_raw_head.csv
 - project/data/clientes.csv                -> clientes_raw_head.csv
 - project/output/parquet/clean_ventas.parquet -> clean_head.csv (si existe y hay soporte parquet)
 - project/output/ut1.db                     -> ventas_from_db_head.csv (consulta simple, si existe)

Uso (desde la raíz del repo):
    py -3 project\output\expo\export_expo.py

Nota: el script evita operaciones que fallan comprobando existencia de archivos. No instala dependencias.
"""
from pathlib import Path
import pandas as pd
import sqlite3
import importlib.util

ROOT = Path('project')
OUT = ROOT / 'output' / 'expo'
OUT.mkdir(parents=True, exist_ok=True)

# Rutas relativas dentro del repo
VENTAS = ROOT / 'data' / 'drops' / 'ventas.csv'
PRODUCTOS = ROOT / 'data' / 'productos.csv'
CLIENTES = ROOT / 'data' / 'clientes.csv'
PARQUET = ROOT / 'output' / 'parquet' / 'clean_ventas.parquet'
SQLITE = ROOT / 'output' / 'ut1.db'

print('Exportando ejemplos a:', OUT.resolve())

if VENTAS.exists():
    v = pd.read_csv(VENTAS, dtype=str)
    v.head(10).to_csv(OUT / 'ventas_raw_head.csv', index=False)
    print('ventas_raw_head.csv (rows):', len(v.head(10)))
else:
    print('Ventas fuente no encontrada:', VENTAS)

if PRODUCTOS.exists():
    p = pd.read_csv(PRODUCTOS, dtype=str)
    p.head(10).to_csv(OUT / 'productos_raw_head.csv', index=False)
    print('productos_raw_head.csv (rows):', len(p.head(10)))
else:
    print('Productos fuente no encontrada:', PRODUCTOS)

if CLIENTES.exists():
    c = pd.read_csv(CLIENTES, dtype=str)
    c.head(10).to_csv(OUT / 'clientes_raw_head.csv', index=False)
    print('clientes_raw_head.csv (rows):', len(c.head(10)))
else:
    print('Clientes fuente no encontrada:', CLIENTES)

# Parquet: solo si existe y hay motor disponible
if PARQUET.exists():
    arrow_spec = importlib.util.find_spec('pyarrow')
    fast_spec = importlib.util.find_spec('fastparquet')
    if arrow_spec or fast_spec:
        df_parquet = pd.read_parquet(PARQUET)
        df_parquet.head(10).to_csv(OUT / 'clean_head.csv', index=False)
        print('clean_head.csv (rows):', len(df_parquet.head(10)))
    else:
        print('Parquet encontrado pero falta motor (pyarrow/fastparquet). Saltando parquet.')
else:
    print('Parquet limpio no encontrado:', PARQUET)

# Si existe la DB SQLite, leer una consulta de ejemplo
if SQLITE.exists():
    conn = sqlite3.connect(SQLITE)
    try:
        q = "SELECT fecha, id_producto, SUM(importe) as importe, SUM(unidades) as unidades FROM ventas GROUP BY fecha, id_producto ORDER BY fecha LIMIT 10"
        df = pd.read_sql_query(q, conn)
        df.to_csv(OUT / 'ventas_from_db_head.csv', index=False)
        print('ventas_from_db_head.csv:', len(df))
    except Exception as e:
        print('Consulta de ejemplo falló:', e)
    finally:
        conn.close()
else:
    print('SQLite no encontrada:', SQLITE)

print('Export completo. Revisa project/output/expo/')

