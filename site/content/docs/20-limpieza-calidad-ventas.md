# Reglas de limpieza y calidad — Ventas (adaptado)

## Tipos y formatos
- `fecha`: ISO (`YYYY-MM-DD` o `TIMESTAMP` UTC)
- `unidades`: entero ≥ 0
- `precio_unitario`: decimal ≥ 0 (guardar en Parquet y en SQLite como NUMERIC/REAL)

## Campos obligatorios
- `fecha`, `id_cliente`, `id_producto`, `unidades`, `precio_unitario`
- Filas inválidas → `project/output/quality/ventas_quarantine.csv`

## Validaciones específicas
- `unidades >= 0` y entero
- `precio_unitario >= 0`
- `id_producto` debe coincidir con `^P[0-9]+$` (si el catálogo tiene otro formato, adaptarlo)

## Dedupe
- Clave natural: `(fecha, id_cliente, id_producto)`
- Política: último gana por `_ingest_ts` + orden en fichero

## Estandarización
- Trim, normalización de tildes, mayúsculas en ids

## Trazabilidad
- Mantener `_source_file`, `_ingest_ts`, `_batch_id`, `_row_id`

## QA rápida
- % filas a quarantine
- Conteos por día vs. esperado

## Nota sobre la implementación actual (`run.py`)
- `run.py` (en `project/ingest/`) ahora lee de forma explícita:
  - `project/data/productos.csv`
  - `project/data/clientes.csv`
  - `project/data/drops/ventas.csv` (archivo principal de ventas)
- Salidas:
  - Quarantine: `project/output/quality/ventas_quarantine.csv`
  - Ventas limpias (parquet): `project/output/parquet/clean_ventas.parquet` (requiere `pyarrow` o `fastparquet` en el entorno)
  - SQLite: `project/output/ut1.db` con tablas `raw_ventas` y las vistas/upserts definidos en `project/sql/`.
- Nota práctica: si tu entorno no tiene `pyarrow`, puedo ajustar `run.py` para escribir CSV en vez de Parquet; dime si prefieres eso.

- Nota importante sobre validación de catálogo:
  - La implementación actual valida el formato de `id_producto` (regex `^P[0-9]+$`) pero NO comprueba si el `id_producto` o `id_cliente` existen realmente en los ficheros de catálogo (`productos.csv`, `clientes.csv`).
  - Si deseas que las ventas referencien sólo productos/clientes existentes, puedo añadir esa validación para mover a `quarantine` las filas con referencias inexistentes en catálogo.

## Persistencia en SQLite (ut1.db)

- El pipeline además de guardar Parquet, persiste datos en una base SQLite ubicada en `project/output/ut1.db`.
- Esquema usado: `project/sql/00_schema.sql` (crea `raw_ventas`, `clean_ventas`, `quarantine_ventas`).
- Qué se guarda:
  - `raw_ventas`: volcado de las filas tal como llegaron del CSV con trazabilidad (`_ingest_ts`, `_source_file`, `_batch_id`).
  - `clean_ventas`: filas validadas (clave natural: `fecha,id_cliente,id_producto`) insertadas/actualizadas mediante UPSERT (`project/sql/10_upserts.sql`).
  - Nota: la cuarentena se guarda por defecto en CSV (`project/output/quality/ventas_quarantine.csv`); no se vuelca automáticamente en `quarantine_ventas` a menos que se active explícitamente.
- Columna `importe`: el cálculo se realiza con `Decimal` en memoria y, para preservar precisión, se guarda en la BD como `TEXT` (cadena) y en Parquet como string; en SQL se puede convertir a número si se desea.
- Verificación rápida (desde la raíz del repo):

```cmd
py -3 project\ingest\run.py
py -3 project\ingest\check_db.py
```

(esto creará/actualizará `project/output/ut1.db` y mostrará tablas y recuentos).
