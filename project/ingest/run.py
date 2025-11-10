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
ventas_raw = pd.read_csv(VENTAS_F, dtype=str, comment='#', skip_blank_lines=True)
productos_raw = pd.read_csv(PRODUCTOS_F, dtype=str)
clientes_raw = pd.read_csv(CLIENTES_F, dtype=str)

# Normalizar nombres de columna simples
ventas_raw.columns = [c.strip() for c in ventas_raw.columns]
if 'fecha_venta' in ventas_raw.columns and 'fecha' not in ventas_raw.columns:
    ventas_raw = ventas_raw.rename(columns={'fecha_venta': 'fecha'})
if 'precio' in ventas_raw.columns and 'precio_unitario' not in ventas_raw.columns:
    ventas_raw = ventas_raw.rename(columns={'precio': 'precio_unitario'})

# Añadir trazabilidad mínima SIEMPRE (sin nulos) en los tres RAW
_now = datetime.now(timezone.utc).isoformat()
_batch_id = 'batch-demo'
ventas_raw['_source_file'] = VENTAS_F.name
ventas_raw['_ingest_ts'] = _now
ventas_raw['_batch_id'] = _batch_id

# NUEVO: trazabilidad también en productos y clientes (para poblar tablas raw)
productos_raw['_source_file'] = PRODUCTOS_F.name
productos_raw['_ingest_ts'] = _now
productos_raw['_batch_id'] = _batch_id

clientes_raw['_source_file'] = CLIENTES_F.name
clientes_raw['_ingest_ts'] = _now
clientes_raw['_batch_id'] = _batch_id

# Completar 'nombre' en RAW para evitar nulos en tablas raw
# Productos: derivar nombre desde columnas comunes si falta
if 'nombre' not in productos_raw.columns:
    if 'nombre_producto' in productos_raw.columns:
        productos_raw['nombre'] = productos_raw['nombre_producto']
    elif 'descripcion' in productos_raw.columns:
        productos_raw['nombre'] = productos_raw['descripcion']
# Normalizar espacios si existe
if 'nombre' in productos_raw.columns:
    productos_raw['nombre'] = productos_raw['nombre'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Clientes: derivar nombre si falta
if 'nombre' not in clientes_raw.columns:
    if 'razon_social' in clientes_raw.columns:
        clientes_raw['nombre'] = clientes_raw['razon_social']
    elif 'apellido' in clientes_raw.columns:
        clientes_raw['nombre'] = clientes_raw['apellido']
# Normalizar espacios si existe
if 'nombre' in clientes_raw.columns:
    clientes_raw['nombre'] = clientes_raw['nombre'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Coerciones y saneamiento básico
# --- VENTAS ---------------------------------------------------------------
df = ventas_raw.copy()
for c in ['fecha', 'id_cliente', 'id_producto', 'unidades', 'precio_unitario']:
    if c not in df.columns:
        df[c] = None

# Normalizar códigos (trim + upper) antes de validar
_df_norm = lambda x: (x.strip().upper() if isinstance(x, str) else x)
df['id_cliente'] = df['id_cliente'].apply(_df_norm)
df['id_producto'] = df['id_producto'].apply(_df_norm)

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
pat_c = re.compile(r'^C[0-9]+$')
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

# Persistir resultados mínimos (ventas)
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
        pass
    # siempre exportar CSV también
    clean_csv = clean.copy()
    clean_csv['importe'] = clean_csv['importe'].map(lambda x: None if x is None else str(x))
    clean_csv.to_csv(OUT / 'parquet' / 'clean_ventas.csv', index=False)

# --- NUEVA SECCIÓN: PRODUCTOS --------------------------------------------
prod = productos_raw.copy()
prod.columns = [c.strip() for c in prod.columns]
# asegurar columnas y normalizar nombres (aceptar nombre_producto)
if 'nombre' not in prod.columns:
    if 'nombre_producto' in prod.columns:
        prod['nombre'] = prod['nombre_producto']
    else:
        prod['nombre'] = prod.get('descripcion', None)

# helper seguro para strip (no convertir None a 'None')
def safe_strip_series(s):
    return s.apply(lambda x: x.strip() if isinstance(x, str) else x)

# aplicar strip a columnas relevantes para evitar espacios que rompan las máscaras
for col in ['id_producto', 'nombre', 'precio_unitario']:
    if col in prod.columns:
        prod[col] = safe_strip_series(prod[col])
# Forzar mayúsculas en id_producto para cumplir ^P[0-9]+$
if 'id_producto' in prod.columns:
    prod['id_producto'] = prod['id_producto'].apply(lambda x: x.upper() if isinstance(x, str) else x)

# trazabilidad mínima
prod['_source_file'] = PRODUCTOS_F.name
prod['_ingest_ts'] = _now
prod['_batch_id'] = _batch_id

# coerciones
prod['precio_unitario_dec'] = prod.get('precio_unitario').map(to_decimal_money) if 'precio_unitario' in prod.columns else None
mask_prod_valid = (
    prod['id_producto'].notna() & prod['id_producto'].astype(str).str.match(pat_p, na=False)
    & prod['nombre'].notna() & (prod['nombre'].astype(str).str.strip() != '')
)
prod_quarantine = prod.loc[~mask_prod_valid].copy()
prod_clean = prod.loc[mask_prod_valid].copy()

if not prod_quarantine.empty:
    def motivo_prod(r):
        reasons = []
        if pd.isna(r['id_producto']) or not pat_p.match(str(r['id_producto'])):
            reasons.append('id_producto inválido')
        if pd.isna(r['nombre']) or str(r['nombre']).strip() == '':
            reasons.append('nombre faltante')
        return '; '.join(reasons)
    prod_quarantine['motivo'] = prod_quarantine.apply(motivo_prod, axis=1)

# Persistir productos: quality + parquet
prod_quarantine.to_csv(OUT / 'quality' / 'productos_quarantine.csv', index=False)
if not prod_clean.empty:
    try:
        pc = prod_clean.copy()
        pc.to_parquet(OUT / 'parquet' / 'clean_productos.parquet', index=False)
    except Exception:
        pass
    # siempre CSV
    prod_clean.to_csv(OUT / 'parquet' / 'clean_productos.csv', index=False)

# --- NUEVA SECCIÓN: CLIENTES --------------------------------------------
cli = clientes_raw.copy()
cli.columns = [c.strip() for c in cli.columns]
# si hay columnas nombre/apellido, combinar apellido opcionalmente en nombre completo
if 'nombre' in cli.columns and 'apellido' in cli.columns:
    # crear nombre completo si el usuario lo desea: mantener 'nombre' (primero) y crear 'nombre_full'
    cli['nombre_full'] = cli.apply(lambda r: (str(r['nombre']).strip() + ' ' + str(r['apellido']).strip()).strip() if pd.notna(r.get('nombre')) else (str(r.get('apellido')).strip() if pd.notna(r.get('apellido')) else None), axis=1)
    # conservar 'nombre' como está (el script usa 'nombre')

# aplicar strip seguro a columnas clave
for col in ['id_cliente', 'nombre']:
    if col in cli.columns:
        cli[col] = safe_strip_series(cli[col])
# Forzar mayúsculas en id_cliente para cumplir ^C[0-9]+$
if 'id_cliente' in cli.columns:
    cli['id_cliente'] = cli['id_cliente'].apply(lambda x: x.upper() if isinstance(x, str) else x)

if 'nombre' not in cli.columns and 'nombre_full' in cli.columns:
    cli['nombre'] = cli['nombre_full']

if 'id_cliente' not in cli.columns:
    cli['id_cliente'] = None
if 'nombre' not in cli.columns:
    cli['nombre'] = cli.get('razon_social', None)

# trazabilidad
cli['_source_file'] = CLIENTES_F.name
cli['_ingest_ts'] = _now
cli['_batch_id'] = _batch_id

mask_cli_valid = (
    cli['id_cliente'].notna() & (cli['id_cliente'].astype(str).str.strip() != '')
    & cli['nombre'].notna() & (cli['nombre'].astype(str).str.strip() != '')
    & cli['id_cliente'].astype(str).str.match(pat_c, na=False)
)
cli_quarantine = cli.loc[~mask_cli_valid].copy()
cli_clean = cli.loc[mask_cli_valid].copy()

if not cli_quarantine.empty:
    def motivo_cli(r):
        reasons = []
        if pd.isna(r['id_cliente']) or str(r['id_cliente']).strip() == '':
            reasons.append('id_cliente faltante')
        else:
            if not pat_c.match(str(r['id_cliente'])):
                reasons.append('id_cliente formato inesperado')
        if pd.isna(r['nombre']) or str(r['nombre']).strip() == '':
            reasons.append('nombre faltante')
        return '; '.join(reasons)
    cli_quarantine['motivo'] = cli_quarantine.apply(motivo_cli, axis=1)

# Persistir clientes: quality + parquet
cli_quarantine.to_csv(OUT / 'quality' / 'clientes_quarantine.csv', index=False)
if not cli_clean.empty:
    try:
        cc = cli_clean.copy()
        cc.to_parquet(OUT / 'parquet' / 'clean_clientes.parquet', index=False)
    except Exception:
        pass
    # siempre CSV
    cli_clean.to_csv(OUT / 'parquet' / 'clean_clientes.csv', index=False)

# --- NUEVA SECCIÓN: Persistir en SQLite (ut1.db) - añadir productos/clientes ---
import sqlite3
DB = OUT / 'ut1.db'
con = sqlite3.connect(DB)
# PRAGMAs para acelerar escrituras en lotes (evitar bloqueos en IDE)
con.execute('PRAGMA journal_mode=WAL;')
con.execute('PRAGMA synchronous=NORMAL;')

# Crear esquema si no existe
schema_sql = (Path(__file__).resolve().parents[1] / 'sql' / '00_schema.sql').read_text(encoding='utf-8')
con.executescript(schema_sql)
# Tablas extra de cuarentena para productos y clientes
con.executescript(
    """
    CREATE TABLE IF NOT EXISTS quarantine_productos (
        _reason      TEXT,
        _row         TEXT,
        _ingest_ts   TEXT,
        _source_file TEXT,
        _batch_id    TEXT
    );
    CREATE TABLE IF NOT EXISTS quarantine_clientes (
        _reason      TEXT,
        _row         TEXT,
        _ingest_ts   TEXT,
        _source_file TEXT,
        _batch_id    TEXT
    );
    """
)

# Volcar raw_ventas (usar columnas de trazabilidad y los valores originales)
if not ventas_raw.empty:
    df_raw_sql = ventas_raw.copy()
    cols_raw = ['fecha','id_cliente','id_producto','unidades','precio_unitario','_ingest_ts','_source_file','_batch_id']
    for c in cols_raw:
        if c not in df_raw_sql.columns:
            df_raw_sql[c] = None
    df_raw_sql = df_raw_sql[cols_raw]
    df_raw_sql.to_sql('raw_ventas', con, if_exists='append', index=False, method='multi', chunksize=1000)

# Persistir raw_productos / raw_clientes
if not productos_raw.empty:
    rp = productos_raw.copy()
    # asegurar columnas razonables
    for c in ['id_producto','nombre','precio_unitario','_ingest_ts','_source_file','_batch_id']:
        if c not in rp.columns:
            rp[c] = None
    rp = rp[['id_producto','nombre','precio_unitario','_ingest_ts','_source_file','_batch_id']]
    rp.to_sql('raw_productos', con, if_exists='append', index=False, method='multi', chunksize=1000)

if not clientes_raw.empty:
    rc = clientes_raw.copy()
    for c in ['id_cliente','nombre','_ingest_ts','_source_file','_batch_id']:
        if c not in rc.columns:
            rc[c] = None
    rc = rc[['id_cliente','nombre','_ingest_ts','_source_file','_batch_id']]
    rc.to_sql('raw_clientes', con, if_exists='append', index=False, method='multi', chunksize=1000)

# Persistir filas de quarantine_ventas en la tabla quarantine_ventas
if not quarantine.empty:
    batch_vals = quarantine.get('_batch_id')
    batch_id_val = None
    if batch_vals is not None and len(batch_vals) > 0:
        batch_id_val = str(batch_vals.iloc[0])
    if batch_id_val:
        con.execute("DELETE FROM quarantine_ventas WHERE _batch_id = ?", (batch_id_val,))
    insert_q = "INSERT INTO quarantine_ventas(_reason,_row,_ingest_ts,_source_file,_batch_id) VALUES (?,?,?,?,?)"
    row_cols = ['fecha','id_cliente','id_producto','unidades','precio_unitario']
    batch_rows = []
    for _, r in quarantine.iterrows():
        reason = r.get('motivo', '')
        row_dict = {c: (None if pd.isna(r.get(c)) else r.get(c)) for c in row_cols}
        batch_rows.append((reason, str(row_dict), r.get('_ingest_ts'), r.get('_source_file'), r.get('_batch_id')))
    if batch_rows:
        con.executemany(insert_q, batch_rows)
    con.commit()

# Persistir quarantine_productos
if not prod_quarantine.empty:
    batch_vals = prod_quarantine.get('_batch_id')
    batch_id_val = None
    if batch_vals is not None and len(batch_vals) > 0:
        batch_id_val = str(batch_vals.iloc[0])
    if batch_id_val:
        con.execute("DELETE FROM quarantine_productos WHERE _batch_id = ?", (batch_id_val,))
    insert_qp = "INSERT INTO quarantine_productos(_reason,_row,_ingest_ts,_source_file,_batch_id) VALUES (?,?,?,?,?)"
    row_cols = ['id_producto','nombre','precio_unitario']
    batch_rows = []
    for _, r in prod_quarantine.iterrows():
        reason = r.get('motivo', '')
        row_dict = {c: (None if pd.isna(r.get(c)) else r.get(c)) for c in row_cols}
        batch_rows.append((reason, str(row_dict), r.get('_ingest_ts'), r.get('_source_file'), r.get('_batch_id')))
    if batch_rows:
        con.executemany(insert_qp, batch_rows)
    con.commit()

# Persistir quarantine_clientes
if not cli_quarantine.empty:
    batch_vals = cli_quarantine.get('_batch_id')
    batch_id_val = None
    if batch_vals is not None and len(batch_vals) > 0:
        batch_id_val = str(batch_vals.iloc[0])
    if batch_id_val:
        con.execute("DELETE FROM quarantine_clientes WHERE _batch_id = ?", (batch_id_val,))
    insert_qc = "INSERT INTO quarantine_clientes(_reason,_row,_ingest_ts,_source_file,_batch_id) VALUES (?,?,?,?,?)"
    row_cols = ['id_cliente','nombre']
    batch_rows = []
    for _, r in cli_quarantine.iterrows():
        reason = r.get('motivo', '')
        row_dict = {c: (None if pd.isna(r.get(c)) else r.get(c)) for c in row_cols}
        batch_rows.append((reason, str(row_dict), r.get('_ingest_ts'), r.get('_source_file'), r.get('_batch_id')))
    if batch_rows:
        con.executemany(insert_qc, batch_rows)
    con.commit()

# Upserts para clean_ventas
if not clean.empty:
    upsert_sql = (Path(__file__).resolve().parents[1] / 'sql' / '10_upserts.sql').read_text(encoding='utf-8')
    params_list = []
    for _, r in clean.iterrows():
        try:
            u_val = float(r['unidades']) if pd.notna(r.get('unidades')) else None
        except Exception:
            u_val = None
        try:
            p_val = float(r['precio_unitario']) if pd.notna(r.get('precio_unitario')) else None
        except Exception:
            p_val = float(r.get('precio_unitario_dec')) if r.get('precio_unitario_dec') is not None else None
        imp_val = None
        if 'importe' in r.index and r['importe'] is not None:
            imp_val = str(r['importe'])
        params_list.append({
            'fecha': str(r['fecha']) if pd.notna(r['fecha']) else None,
            'idc': r['id_cliente'],
            'idp': r['id_producto'],
            'u': u_val,
            'p': p_val,
            'imp': imp_val,
            'ts': r['_ingest_ts']
        })
    if params_list:
        con.executemany(upsert_sql, params_list)
    con.commit()

# Persistir clean_productos / clean_clientes en SQLite
if not prod_clean.empty:
    pc = prod_clean.copy()
    if 'precio_unitario_dec' in pc.columns:
        pc['precio_unitario'] = pc['precio_unitario_dec'].map(lambda x: None if x is None else float(x))
    pc_cols = [c for c in ['id_producto','nombre','precio_unitario','_ingest_ts','_source_file','_batch_id'] if c in pc.columns]
    pc[pc_cols].to_sql('clean_productos', con, if_exists='replace', index=False, method='multi', chunksize=1000)

if not cli_clean.empty:
    cc = cli_clean.copy()
    cc_cols = [c for c in ['id_cliente','nombre','_ingest_ts','_source_file','_batch_id'] if c in cc.columns]
    cc[cc_cols].to_sql('clean_clientes', con, if_exists='replace', index=False, method='multi', chunksize=1000)

# Crear vistas y capa ORO
views_sql = (Path(__file__).resolve().parents[1] / 'sql' / '20_views.sql').read_text(encoding='utf-8')
con.executescript(views_sql)

create_oro_sql = """
DROP TABLE IF EXISTS ventas_diarias_producto;
CREATE TABLE ventas_diarias_producto AS
SELECT fecha,
       id_producto,
       SUM(unidades * precio_unitario) AS importe_total,
       SUM(unidades) AS unidades_total,
       ROUND(SUM(unidades * precio_unitario) / NULLIF(SUM(unidades),0), 2) AS ticket_medio
FROM clean_ventas
GROUP BY fecha, id_producto;
"""
con.executescript(create_oro_sql)

# Exportar ORO a Parquet/CSV
try:
    df_oro = pd.read_sql_query('SELECT * FROM ventas_diarias_producto', con)
    df_oro['importe_total'] = pd.to_numeric(df_oro['importe_total'], errors='coerce')
    df_oro['unidades_total'] = pd.to_numeric(df_oro['unidades_total'], errors='coerce')
    (OUT / 'parquet').mkdir(parents=True, exist_ok=True)
    df_oro.to_parquet(OUT / 'parquet' / 'ventas_diarias_producto.parquet', index=False)
except Exception:
    df_oro = pd.read_sql_query('SELECT * FROM ventas_diarias_producto', con)
# CSV siempre
df_oro.to_csv(OUT / 'parquet' / 'ventas_diarias_producto.csv', index=False)

con.commit()
con.close()

# ================= Documentos Markdown =================
DOCS = Path('project') / 'docs'
raw_rows = len(ventas_raw)
clean_rows = len(clean)
quar_rows = len(quarantine)
periodo_ini = str(clean['fecha'].min()) if clean_rows else ''
periodo_fin = str(clean['fecha'].max()) if clean_rows else ''
ingresos_total_dec = sum([x for x in clean['importe'] if x is not None]) if clean_rows else Decimal('0')
transacciones = clean_rows
ticket_medio_dec = (ingresos_total_dec / Decimal(transacciones)) if transacciones else Decimal('0')

if clean_rows:
    tmp = clean.copy()
    tmp['importe_num'] = tmp['importe'].map(lambda x: float(x) if x is not None else 0.0)
    top_prod = (tmp
                .groupby('id_producto', as_index=False)
                .agg(importe=('importe_num', 'sum'), unidades=('unidades', 'sum'))
                .sort_values('importe', ascending=False)
                .head(10))
else:
    top_prod = pd.DataFrame(columns=['id_producto','importe','unidades'])

ventas_dia = (df_oro.groupby('fecha', as_index=False)
              .agg(importe_total=('importe_total','sum'), lineas=('unidades_total','sum'))) if not df_oro.empty else pd.DataFrame(columns=['fecha','importe_total','lineas'])

# KPIs adicionales para el reporte
procesadas = clean_rows + quar_rows
pct_quarantine = (100.0 * quar_rows / procesadas) if procesadas else 0.0

# Nuevas métricas
if clean_rows:
    # ticket por línea = importe (Decimal) / 1 transacción (cada línea es transacción)
    # mediana ticket = mediana de importe por línea
    importes_float = [float(x) for x in clean['importe'] if x is not None]
    mediana_ticket = float(pd.Series(importes_float).median()) if importes_float else 0.0
    productos_distintos = clean['id_producto'].nunique()
    clientes_distintos = clean['id_cliente'].nunique()
    diversidad_productos_pct = (100.0 * productos_distintos / clean_rows) if clean_rows else 0.0
    # Top cliente %
    tmp_cli = clean.copy()
    tmp_cli['imp_num'] = [float(x) if x is not None else 0.0 for x in tmp_cli['importe']]
    total_imp_float = sum(tmp_cli['imp_num'])
    if total_imp_float > 0:
        top_cliente_pct = 100.0 * (tmp_cli.groupby('id_cliente')['imp_num'].sum().max() / total_imp_float)
    else:
        top_cliente_pct = 0.0
else:
    mediana_ticket = 0.0
    productos_distintos = 0
    clientes_distintos = 0
    diversidad_productos_pct = 0.0
    top_cliente_pct = 0.0

# (recalcular total_imp_float para coherencia con métricas previas)
if clean_rows:
    total_imp_float = float(ingresos_total_dec)
else:
    total_imp_float = 0.0

if not top_prod.empty and total_imp_float > 0:
    top5_sum = float(top_prod['importe'].head(5).sum())
    top5_pct = 100.0 * top5_sum / total_imp_float
    top_product_pct = 100.0 * float(top_prod.iloc[0]['importe']) / total_imp_float
    cum = top_prod['importe'].cumsum()
    pareto_80_count = int((cum >= 0.80 * total_imp_float).idxmax()) + 1 if (cum >= 0.80 * total_imp_float).any() else len(top_prod)
else:
    top5_pct = 0.0
    top_product_pct = 0.0
    pareto_80_count = 0

# Ingresos por categoría (si productos tiene categoría)
if clean_rows and 'categoria' in productos_raw.columns:
    # Join simple para categoría
    prod_cat = productos_raw[['id_producto','categoria']].drop_duplicates()
    clean_cat = clean.merge(prod_cat, on='id_producto', how='left')
    clean_cat['imp_num'] = [float(x) if x is not None else 0.0 for x in clean_cat['importe']]
    cat_agg = (clean_cat.groupby('categoria', dropna=False)
               .agg(ingresos=('imp_num','sum'), productos=('id_producto','nunique'))
               .reset_index()
               .sort_values('ingresos', ascending=False)
               .head(10))
else:
    cat_agg = pd.DataFrame(columns=['categoria','ingresos','productos'])

if not ventas_dia.empty:
    dia_max = str(ventas_dia.loc[ventas_dia['importe_total'].idxmax(), 'fecha'])
    dia_min = str(ventas_dia.loc[ventas_dia['importe_total'].idxmin(), 'fecha'])
else:
    dia_max = ''
    dia_min = ''

def md_table(df, cols, max_rows=None):
    if df is None or df.empty:
        return '\n_N/A_\n'
    d = df[cols].copy()
    if max_rows:
        d = d.head(max_rows)
    out = ['|' + '|'.join(cols) + '|', '|' + '|'.join(['---']*len(cols)) + '|']
    for _, r in d.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            if isinstance(v, Decimal):
                v = f"{v:.2f}"
            vals.append(str(v))
        out.append('|' + '|'.join(vals) + '|')
    return '\n'.join(out)

# Rellenar reporte usando plantilla (40-reporte-plantilla-ventas.md)
reporte_tpl_path = DOCS / '40-reporte-plantilla-ventas.md'
# Fallbacks: si no hay datos, mostrar SQL en bloque de código
top_table_md = md_table(top_prod, ['id_producto','importe','unidades'])
if top_prod is None or top_prod.empty or top_table_md.strip() == '_N/A_':
    top_table_md = (
        'No hay datos para mostrar.\n\n'
        '```sql\n'
        'SELECT id_producto, SUM(unidades * precio_unitario) AS importe\n'
        'FROM clean_ventas\n'
        'GROUP BY id_producto\n'
        'ORDER BY importe DESC\n'
        'LIMIT 10;\n'
        '```'
    )
by_day_md = md_table(ventas_dia, ['fecha','importe_total','lineas'])
if ventas_dia is None or ventas_dia.empty or by_day_md.strip() == '_N/A_':
    by_day_md = (
        'No hay datos para mostrar.\n\n'
        '```sql\n'
        'SELECT fecha, SUM(unidades * precio_unitario) AS importe_total, COUNT(*) AS lineas\n'
        'FROM clean_ventas\n'
        'GROUP BY fecha;\n'
        '```'
    )
cat_table_md = md_table(cat_agg, ['categoria','ingresos','productos']) if not cat_agg.empty else 'No disponible'
if reporte_tpl_path.exists():
    tpl = reporte_tpl_path.read_text(encoding='utf-8')
    filled = tpl.format(
        periodo_ini=periodo_ini,
        periodo_fin=periodo_fin,
        ingresos=float(ingresos_total_dec),
        ticket=float(ticket_medio_dec),
        mediana_ticket=mediana_ticket,
        trans=transacciones,
        productos_distintos=productos_distintos,
        clientes_distintos=clientes_distintos,
        diversidad_productos_pct=diversidad_productos_pct,
        pct_quarantine=pct_quarantine,
        top5_pct=top5_pct,
        pareto_80_count=pareto_80_count,
        top_product_pct=top_product_pct,
        top_cliente_pct=top_cliente_pct,
        dia_max=dia_max,
        dia_min=dia_min,
        top_table=top_table_md,
        by_day_table=by_day_md,
        cat_table=cat_table_md,
        bronze=raw_rows,
        clean=clean_rows,
        quarantine=quar_rows
    )
    (OUT / 'reporte.md').write_text(filled, encoding='utf-8')
else:
    (OUT / 'reporte.md').write_text('# Reporte — Ventas\n\nPlantilla no encontrada.', encoding='utf-8')

# Rellenar PLANTILLA.md
plantilla_filled_path = DOCS / 'PLANTILLA.md'
pct_quar = (quar_rows * 100 / raw_rows) if raw_rows else 0
plantilla_contenido = f"""---
title: "Plantilla entregable — Proyecto UT1 RA1"
tags: ["UT1","RA1","docs"]
version: "1.0.1"
owner: "equipo-alumno"
status: "final"
---

# 1. Objetivo
Transformar los CSV de ventas, productos y clientes en datos limpios (plata) y agregados (oro) básicos, demostrando trazabilidad, calidad y cálculo de KPI (ingresos, ticket medio, top productos).

# 2. Alcance
Incluye ingestión batch, limpieza (tipado, validaciones, dedupe "último gana"), cuarentena de filas inválidas y generación de artefactos analíticos (Parquet + SQLite + reporte). No incluye procesos en tiempo real ni enriquecimientos externos.

# 3. Decisiones / Reglas
- Clave natural ventas: (fecha, id_cliente, id_producto) → último gana por _ingest_ts.
- Validaciones: fecha ISO, unidades >=0, precio_unitario >=0, id_producto ^P[0-9]+$.
- Campos obligatorios: fecha, id_cliente, id_producto, unidades, precio_unitario.
- Filas inválidas → quarantine con motivo.

# 4. Procedimiento reproducible
1. Ejecutar: `py -3 project/ingest/run.py`
2. Revisar artefactos en project/output/ (Parquet, ut1.db, reporte.md).
3. Consultar KPI vía vistas/SQL.

# 5. Evidencias
- Filas raw: {raw_rows}
- Filas clean: {clean_rows}
- Filas quarantine: {quar_rows}
- Periodo: {periodo_ini} → {periodo_fin}

# 6. Resultados / KPI
- Ingresos totales: {ingresos_total_dec:.2f}
- Ticket medio: {ticket_medio_dec:.2f}
- Transacciones: {transacciones}
- % cuarentena: {pct_quar:.2f}%

Top productos (importe / unidades):

{md_table(top_prod, ['id_producto','importe','unidades'])}

Ventas por día (importe_total / líneas):

{md_table(ventas_dia, ['fecha','importe_total','lineas'])}

# 7. Lecciones
Mantener trazabilidad (_ingest_ts, _source_file, _batch_id) simplifica idempotencia y auditoría. Dedupe por timestamp evita duplicados. Separar clean vs quarantine permite mejorar reglas sin perder visibilidad.

# 8. Próximos pasos
Persistir y ampliar capa oro (más agregados), añadir tests automáticos de % quarantine, validar catálogo completo de productos, documentación de SLA.
"""
plantilla_filled_path.write_text(plantilla_contenido, encoding='utf-8')

# Actualizar snapshot en 30-modelado-oro-ventas.md
modelo_oro_path = DOCS / '30-modelado-oro-ventas.md'
if modelo_oro_path.exists():
    original = modelo_oro_path.read_text(encoding='utf-8')
    import re as _re
    nuevo_bloque = (f"# Ejemplo de resultados (snapshot actual)\n"
                    f"- Ingresos totales: {ingresos_total_dec:.2f}\n"
                    f"- Ticket medio: {ticket_medio_dec:.2f}\n"
                    f"- Líneas clean: {clean_rows}\n"
                    f"- Filas quarantine: {quar_rows}\n"
                    f"- Top producto: {top_prod.iloc[0]['id_producto'] if not top_prod.empty else 'N/A'}\n")
    if '# Ejemplo de resultados' in original:
        mod = _re.sub(r'# Ejemplo de resultados[\s\S]*?(?=\n# |\Z)', nuevo_bloque + '\n', original, count=1)
    else:
        mod = original + '\n\n' + nuevo_bloque + '\n'
    modelo_oro_path.write_text(mod, encoding='utf-8')

print('OK · reporte generado:', (OUT / 'reporte.md'))
