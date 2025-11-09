from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import re
from decimal import Decimal, ROUND_HALF_UP, getcontext

# Rutas fijas (relativas al repo). El script se ejecuta desde la raíz del repo.
VENTAS_F = Path('project') / 'data' / 'drops' / 'ventas.csv'
PRODUCTOS_F = Path('project') / 'data' / 'productos.csv'
CLIENTES_F = Path('project') / 'data' / 'clientes.csv'
OUT = Path('project') / 'output'
(OUT / 'quality').mkdir(parents=True, exist_ok=True)
(OUT / 'parquet').mkdir(parents=True, exist_ok=True)

# Ajustes Decimal
getcontext().prec = 28
CENT = Decimal('0.01')

# Exigir que los tres CSV estén presentes (no placeholders)
missing = [str(p) for p in (VENTAS_F, PRODUCTOS_F, CLIENTES_F) if not p.exists()]
if missing:
    raise FileNotFoundError(f'Missing required CSV(s): {missing}. Asegúrate de ejecutar desde la raíz del repo y de que los archivos existan.')

# Leer archivos (ahora obligatorios)
ventas_raw = pd.read_csv(VENTAS_F, dtype=str)
productos_raw = pd.read_csv(PRODUCTOS_F, dtype=str)
clientes_raw = pd.read_csv(CLIENTES_F, dtype=str)

# Normalizar nombres de columna simples
ventas_raw.columns = [c.strip() for c in ventas_raw.columns]
if 'fecha_venta' in ventas_raw.columns and 'fecha' not in ventas_raw.columns:
    ventas_raw = ventas_raw.rename(columns={'fecha_venta': 'fecha'})
if 'precio' in ventas_raw.columns and 'precio_unitario' not in ventas_raw.columns:
    ventas_raw = ventas_raw.rename(columns={'precio': 'precio_unitario'})

# Añadir trazabilidad mínima si falta
_now = datetime.now(timezone.utc).isoformat()
ventas_raw['_source_file'] = ventas_raw.get('_source_file', str(VENTAS_F.name))
ventas_raw['_ingest_ts'] = ventas_raw.get('_ingest_ts', _now)
ventas_raw['_batch_id'] = ventas_raw.get('_batch_id', 'batch-demo')

# Coerciones y saneamiento básico
df = ventas_raw.copy()
for c in ['fecha', 'id_cliente', 'id_producto', 'unidades', 'precio_unitario']:
    if c not in df.columns:
        df[c] = None

# tipos
df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce').dt.date
# unidades como número (float/Int) pero para importe usaremos int
df['unidades_num'] = pd.to_numeric(df['unidades'], errors='coerce')

# helper Decimal para precio
def to_decimal_money(x):
    if pd.isna(x) or x in (None, ''):
        return None
    s = str(x).strip().replace(',', '.')
    try:
        return Decimal(s).quantize(CENT, rounding=ROUND_HALF_UP)
    except Exception:
        return None

# Columna Decimal de precio_unitario
df['precio_unitario_dec'] = df['precio_unitario'].map(to_decimal_money)

# Reglas de validación
pat_p = re.compile(r'^P[0-9]+$')
mask_valid = (
    df['fecha'].notna()
    & df['unidades_num'].notna() & (df['unidades_num'] >= 0)
    & df['precio_unitario_dec'].notna() & (df['precio_unitario_dec'] >= Decimal('0'))
    & df['id_cliente'].notna() & (df['id_cliente'].astype(str).str.strip() != '')
    & df['id_producto'].notna() & (df['id_producto'].astype(str).str.strip() != '')
    & df['id_producto'].astype(str).str.match(pat_p, na=False)
)

quarantine = df.loc[~mask_valid].copy()
clean = df.loc[mask_valid].copy()

# Añadir motivo(s) en la quarantena
if not quarantine.empty:
    def motivo(r):
        reasons = []
        if pd.isna(r['fecha']):
            reasons.append('fecha inválida')
        if pd.isna(r['unidades_num']) or (isinstance(r['unidades_num'], (int, float)) and r['unidades_num'] < 0):
            reasons.append('unidades inválidas')
        try:
            p = r['precio_unitario_dec']
            if p is None or p < Decimal('0'):
                reasons.append('precio inválido')
        except Exception:
            reasons.append('precio inválido')
        if pd.isna(r['id_cliente']) or str(r['id_cliente']).strip() == '':
            reasons.append('id_cliente faltante')
        if pd.isna(r['id_producto']) or str(r['id_producto']).strip() == '':
            reasons.append('id_producto faltante')
        else:
            if not pat_p.match(str(r['id_producto'])):
                reasons.append('id_producto formato inesperado')
        return '; '.join(reasons)
    quarantine['motivo'] = quarantine.apply(motivo, axis=1)

# Dedupe (último gana por _ingest_ts)
if not clean.empty:
    clean = clean.sort_values('_ingest_ts').drop_duplicates(subset=['fecha','id_cliente','id_producto'], keep='last')
    # Calcular importe con Decimal: Decimal(int(unidades)) * precio_unitario_dec
    importes = []
    for u, p in zip(clean['unidades_num'].tolist(), clean['precio_unitario_dec'].tolist()):
        if pd.isna(u) or p is None:
            importes.append(None)
        else:
            try:
                importes.append((Decimal(int(u)) * p).quantize(CENT, rounding=ROUND_HALF_UP))
            except Exception:
                importes.append(None)
    clean['precio_unitario'] = clean['precio_unitario_dec']
    clean['unidades'] = clean['unidades_num']
    clean['importe'] = importes

# Persistir resultados mínimos
quarantine.to_csv(OUT / 'quality' / 'ventas_quarantine.csv', index=False)

# Guardado a Parquet/CSV para analítica (ya hecho arriba)
if not clean.empty:
    # parquet opcional (si pyarrow está instalado)
    try:
        # pandas/pyarrow puede no soportar Decimal nativamente; convertir importes a string para parquet
        clean_to_save = clean.copy()
        # convertir Decimal a string para preservar precisión
        clean_to_save['importe'] = clean_to_save['importe'].map(lambda x: None if x is None else str(x))
        clean_to_save.to_parquet(OUT / 'parquet' / 'clean_ventas.parquet', index=False)
    except Exception:
        # si no hay pyarrow, guardar CSV (Decimal se serializa como string)
        clean.to_csv(OUT / 'parquet' / 'clean_ventas.csv', index=False)

# --- NUEVA SECCIÓN: Persistir en SQLite (ut1.db) ---
import sqlite3
DB = OUT / 'ut1.db'
con = sqlite3.connect(DB)
# Crear esquema si no existe
schema_sql = (Path(__file__).resolve().parents[1] / 'sql' / '00_schema.sql').read_text(encoding='utf-8')
con.executescript(schema_sql)

# Volcar raw_ventas (usar columnas de trazabilidad y los valores originales)
if not ventas_raw.empty:
    df_raw_sql = ventas_raw.copy()
    # asegurar columnas
    cols_raw = ['fecha','id_cliente','id_producto','unidades','precio_unitario','_ingest_ts','_source_file','_batch_id']
    for c in cols_raw:
        if c not in df_raw_sql.columns:
            df_raw_sql[c] = None
    df_raw_sql = df_raw_sql[cols_raw]
    df_raw_sql.to_sql('raw_ventas', con, if_exists='append', index=False)

# Upserts para clean_ventas usando el SQL proporcionado
if not clean.empty:
    upsert_sql = (Path(__file__).resolve().parents[1] / 'sql' / '10_upserts.sql').read_text(encoding='utf-8')
    # Ejecutar por fila (pequeños volúmenes); para muchos registros se puede hacer batching
    for _, r in clean.iterrows():
        # convertir a tipos simples para DB: unidades float/int, precio float
        try:
            u_val = float(r['unidades']) if pd.notna(r.get('unidades')) else None
        except Exception:
            u_val = None
        try:
            p_val = float(r['precio_unitario']) if pd.notna(r.get('precio_unitario')) else None
        except Exception:
            # si tenemos precio_unitario_dec, usar float de Decimal
            p_val = float(r.get('precio_unitario_dec')) if r.get('precio_unitario_dec') is not None else None
        # importe como string del Decimal para preservarlo en BD (schema declara importe TEXT)
        imp_val = None
        if 'importe' in r.index and r['importe'] is not None:
            imp_val = str(r['importe'])
        params = {
            'fecha': str(r['fecha']) if pd.notna(r['fecha']) else None,
            'idc': r['id_cliente'],
            'idp': r['id_producto'],
            'u': u_val,
            'p': p_val,
            'imp': imp_val,
            'ts': r['_ingest_ts']
        }
        con.execute(upsert_sql, params)
    con.commit()

# Crear vistas
views_sql = (Path(__file__).resolve().parents[1] / 'sql' / '20_views.sql').read_text(encoding='utf-8')
con.executescript(views_sql)
con.close()

# Mensaje final
print('done -> clean:', len(clean), 'quarantine:', len(quarantine))
print('quarantine file:', (OUT / 'quality' / 'ventas_quarantine.csv'))
