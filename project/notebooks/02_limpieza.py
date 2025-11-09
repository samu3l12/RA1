#%%
"""
02 · Limpieza de ventas (script equivalente al notebook)

- Tipos y formatos: fecha ISO (UTC→date), unidades entero ≥ 0, precio_unitario Decimal ≥ 0
- Nulos y rangos: filas inválidas → quarantine con causa
- Dominio: id_producto cumple ^P[0-9]+$
- Deduplicación: clave (fecha, id_cliente, id_producto), último gana por _ingest_ts
- Estandarización: trim + normalización de tildes + mayúsculas en códigos
- Trazabilidad: _ingest_ts, _source_file, _batch_id
- QA: % a quarantine y conteos por día
"""

#%% 1) Configuración: imports y rutas (estilo run.py)
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext
import unicodedata as ud
import re
import uuid
import pandas as pd

# Configuración monetaria (2 decimales)
getcontext().prec = 28
CENT = Decimal("0.01")

# Rutas (anclado al repo)
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "drops"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "quality").mkdir(parents=True, exist_ok=True)
VENTAS_FILE = DATA / "ventas.csv"
assert VENTAS_FILE.exists(), f"No existe el archivo de ventas: {VENTAS_FILE}"
print("ROOT:", ROOT)

#%% 2) Ingesta mínima + trazabilidad (_source_file, _ingest_ts, _batch_id)
_now_ts = datetime.now(timezone.utc).isoformat()
_batch_id = "py-" + uuid.uuid4().hex[:8]
raw_df = pd.read_csv(VENTAS_FILE, dtype=str)
raw_df["_source_file"] = VENTAS_FILE.name
raw_df["_ingest_ts"] = _now_ts
raw_df["_batch_id"] = _batch_id
print(f"Ingestadas {len(raw_df)} filas desde {VENTAS_FILE.name}.")

#%% 3) Helpers (texto y dinero)

def norm_text(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    if s == "":
        return None
    s_nfkd = ud.normalize("NFKD", s)
    s_ascii = "".join(c for c in s_nfkd if not ud.combining(c))
    return s_ascii.upper()


def to_decimal_money(x) -> Decimal | None:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    s = str(x).strip()
    if s == "":
        return None
    s = s.replace(",", ".")
    try:
        d = Decimal(s)
    except (InvalidOperation, ValueError):
        return None
    return d.quantize(CENT, rounding=ROUND_HALF_UP)

id_producto_re = re.compile(r"^P[0-9]+$")

#%% 4) Preparación de DataFrame (columnas obligatorias)
df = raw_df.copy()
for c in [
    "fecha_venta",
    "fecha",
    "id_cliente",
    "id_producto",
    "unidades",
    "precio_unitario",
    "_ingest_ts",
    "_source_file",
    "_batch_id",
]:
    if c not in df.columns:
        df[c] = None

#%% 5) Estandarización de códigos (trim + tildes → ASCII + mayúsculas)
df["id_cliente"] = df["id_cliente"].map(norm_text)
df["id_producto"] = df["id_producto"].map(norm_text)

#%% 6) Coerción de fecha (ISO→UTC→date) desde 'fecha' o 'fecha_venta'
# Elegimos 'fecha' solo si existe y TIENE datos; si no, usamos 'fecha_venta'
fecha_col = "fecha" if ("fecha" in df.columns and df["fecha"].notna().any()) else "fecha_venta"
df["fecha"] = pd.to_datetime(df[fecha_col], errors="coerce", utc=True).dt.date

#%% 7) Coerción de unidades (entero ≥ 0, sin fracciones)
u_num = pd.to_numeric(df["unidades"], errors="coerce")
mask_int = u_num.notna() & (u_num % 1 == 0)
df["unidades"] = u_num.where(mask_int).astype("Int64")

#%% 8) Coerción de precio_unitario (Decimal ≥ 0)
df["precio_unitario"] = df["precio_unitario"].map(to_decimal_money)

#%% 9) Validación (causas) y partición clean/quarantine

def causas_de(row):
    causas = []
    if pd.isna(row["fecha"]):
        causas.append("fecha_invalida")
    if row["id_cliente"] in (None, ""):
        causas.append("id_cliente_vacio")
    if row["id_producto"] in (None, ""):
        causas.append("id_producto_vacio")
    elif not id_producto_re.match(str(row["id_producto"])):
        causas.append("id_producto_patron")
    if pd.isna(row["unidades"]) or (pd.notna(row["unidades"]) and int(row["unidades"]) < 0):
        causas.append("unidades_invalido")
    if (row["precio_unitario"] is None) or (
        row["precio_unitario"] is not None and row["precio_unitario"] < 0
    ):
        causas.append("precio_invalido")
    return ",".join(causas)


df["_error_cause"] = df.apply(causas_de, axis=1)
valid = df["_error_cause"].eq("")
quarantine = df.loc[~valid].copy()
clean = df.loc[valid].copy()
print(f"Quarantine: {len(quarantine)} filas · Clean: {len(clean)} filas")

#%% 10) Resumen de causas (QA)
if not quarantine.empty:
    causas_count = (
        quarantine["_error_cause"].str.split(",").explode().value_counts().rename_axis("causa").reset_index(name="filas")
    )
    print("Resumen de causas:\n", causas_count.to_string(index=False))

#%% 11) Deduplicación (último gana) y cálculo de importe
if not clean.empty:
    clean = (
        clean.sort_values("_ingest_ts").drop_duplicates(
            subset=["fecha", "id_cliente", "id_producto"], keep="last"
        )
    )
    clean["importe"] = [
        (Decimal(int(u)) * p) if (pd.notna(u) and p is not None) else None
        for u, p in zip(clean["unidades"], clean["precio_unitario"])
    ]

#%% 12) QA rápida (% quarantine y conteos por día)
total = len(df)
q = len(quarantine)
pct_q = (100 * q / total) if total else 0
print(f"% a quarantine: {pct_q:.1f}%  (quarantine={q} / total={total})")

if not clean.empty and "importe" in clean.columns:
    by_day = (
        clean.groupby("fecha", as_index=False)
        .agg(
            transacciones=("id_producto", "count"),
            unidades=("unidades", "sum"),
            importe_total=(
                "importe",
                lambda s: sum([x for x in s if isinstance(x, Decimal)], Decimal("0.00")),
            ),
        )
        .sort_values("fecha")
    )
    print("\nConteos por día:\n", by_day.to_string(index=False))
else:
    print("\nConteos por día: (sin datos de clean)")

#%% 13) Guardado de quarantine y muestra de datos
q_path = OUT / "quality" / "ventas_quarantine.csv"
quarantine.to_csv(q_path, index=False)
print("\nGuardado quarantine en", q_path)
print("\nClean (head):\n", (clean.head(5).to_string(index=False) if not clean.empty else "(sin datos)"))
print("\nQuarantine (head):\n", (quarantine.head(5).to_string(index=False) if not quarantine.empty else "(sin datos)"))
