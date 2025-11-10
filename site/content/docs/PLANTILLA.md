---
title: "Plantilla entregable — Proyecto UT1 RA1"
tags: ["UT1","RA1","docs"]
version: "1.0.0"
owner: "equipo-alumno"
status: "final"
---

# 1. Objetivo
Este documento describe el trabajo realizado para la ingestión, limpieza y modelado mínimo de ventas del proyecto.
Propósito principal: transformar los CSV de entrada en una tabla "plata" (datos tipados y deduplicados) y generar artefactos analíticos reproducibles para obtener KPI básicos. El objetivo es demostrar trazabilidad, calidad de datos y un flujo ETL sencillo que pueda extenderse a una capa "oro" (agregados para análisis).

# 2. Alcance
Cubre:
- Ingesta batch de CSV en `project/data/drops/` (ventas) junto con los CSV de catálogo (`project/data/productos.csv`) y clientes (`project/data/clientes.csv`).
- Limpieza: coerción de tipos, validaciones, quarantena (filas inválidas), deduplicación (clave natural: fecha, id_cliente, id_producto).
- Persistencia: Parquet para analítica (`project/output/parquet/clean_ventas.parquet`), SQLite (`project/output/ut1.db`) con tablas `raw_ventas`, `clean_ventas`, `quarantine_ventas` y vistas resumidas.
- Reporte mínimo: `project/output/reporte.md` y vistas SQL para KPI.

No cubre (fuera de este entregable):
- Pipelines en tiempo real/micro-batch.
- Enriquecimientos externos (pricing dinámico, inventarios en tiempo real).

# 3. Decisiones / Reglas
- Estrategia de ingestión: batch, ejecución manual/por script (`py -3 project/ingest/run.py`).
- Clave natural: `(fecha, id_cliente, id_producto)`; política: "último gana" según `_ingest_ts`.
- Idempotencia: se usa `_batch_id` para identificar lote; antes de insertar en `quarantine_ventas` se borran filas del mismo `_batch_id` para evitar duplicados en re-ejecuciones.
- Validaciones de calidad (reglas principales):
  - `fecha` debe parsearse como fecha ISO (YYYY-MM-DD)
  - `unidades` debe ser entero o numérico ≥ 0
  - `precio_unitario` debe convertirse a Decimal ≥ 0
  - `id_producto` debe cumplir el patrón `^P[0-9]+$`
  - Campos obligatorios: `fecha`, `id_cliente`, `id_producto`, `unidades`, `precio_unitario`
- Tratamiento de filas inválidas: van a `quarantine_ventas` (CSV: `project/output/quality/ventas_quarantine.csv`) con la columna `_reason` que describe la causa.

# 4. Procedimiento / Pasos (cómo reproducir)
Requisitos:
- Python 3.8+ con pandas, pyarrow (opcional para parquet), sqlite3 (incluido en Python).
- Ejecutar desde la raíz del repositorio.

Comandos principales:

1) Ejecutar el pipeline completo (ingesta → limpieza → persistencia):

```bash
py -3 project\ingest\run.py
```

2) Consultas rápidas en la DB SQLite (ejecutar con `sqlite3` o desde Python):

```sql
-- Listar tablas
SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name;

-- Ver primeras filas clean_ventas
SELECT * FROM clean_ventas LIMIT 20;

-- Ver quarantine
SELECT _reason,_row,_ingest_ts FROM quarantine_ventas ORDER BY _ingest_ts DESC LIMIT 50;
```

3) Rutas de salida (relevantes):
- Parquet limpio: `project/output/parquet/clean_ventas.parquet` (fallback CSV `project/output/parquet/clean_ventas.csv` si no hay pyarrow). 
- SQLite: `project/output/ut1.db` (tablas: `raw_ventas`, `clean_ventas`, `quarantine_ventas`; vistas: `ventas_diarias`).
- CSV de quarantine: `project/output/quality/ventas_quarantine.csv`.
- Reporte: `project/output/reporte.md`.

# 5. Evidencias (qué entregar como prueba)
- Fragmentos de `clean_ventas` (head) y `quarantine_ventas` (ejemplos con motivos).
- Parquet `clean_ventas.parquet` y DB `ut1.db` en `project/output/`.
- SQL ejecutadas / vistas generadas (archivo `project/sql/20_views.sql` y `project/sql/10_upserts.sql`).
- Reporte Markdown generado: `project/output/reporte.md`.

# 6. Resultados / KPI (salida real del run)
Resumen numérico de la ejecución que tienes actualmente:
- Filas ingestadas: 127
- Filas en `clean_ventas` (plata): 120
- Filas en `quarantine_ventas`: 7
- Importe total (vista `ventas_diarias`): 139050 (para la fecha 2025-07-07)

Porcentaje de filas en cuarentena ≈ 5.5%.

Top productos por importe (extracto):
- P065: 7000
- P001: 5800
- P069: 5600
- P029: 5600
- P021: 4350
(Ver `project/output/ut1.db` para el listado completo: consulta `SELECT id_producto, SUM(unidades*precio_unitario) AS importe_total FROM clean_ventas GROUP BY id_producto ORDER BY importe_total DESC LIMIT 20;`)

# Por qué el pipeline llegó hasta "plata" y no hasta "oro"
- Definiciones (capas):
  - Bronce: raw (datos tal cual se ingestan) → `raw_ventas`.
  - Plata: datos limpiados, tipados, deduplicados → `clean_ventas` (persistidos en Parquet y SQLite).
  - Oro: agregados y modelos listos para consumo analítico (ej.: `ventas_diarias_producto`, `ventas_por_categoria`) — normalmente se construyen a partir de `plata`.

Estado actual:
- El pipeline implementado ya produce `raw_ventas`, `clean_ventas` y una vista `ventas_diarias` (ejemplo de agregado por fecha). Esto cubre parte de la capa "oro" en modo vista.
- No se creó una tabla/permanente "oro" (parquet o tabla SQL) con todas las agregaciones de producto-dia; se dejó la agregación como vista para simplificar reproducibilidad y evitar duplicar datos.

Razón y recomendaciones:
- Decisión consciente: mantener la capa oro como vista permite recalcular los agregados sin duplicar almacenamiento. Para informes puntuales eso es suficiente.
- Si quieres entregar una capa "oro" persistida (recomendado para escalado o rendimiento): generar y persistir `ventas_diarias_producto` como Parquet y tabla SQL. Ejemplo SQL para generar oro:

```sql
-- Agregado oro: ventas diarias por producto
CREATE TABLE IF NOT EXISTS ventas_diarias_producto AS
SELECT fecha,
       id_producto,
       SUM(unidades * precio_unitario) AS importe_total,
       SUM(unidades) AS unidades_total,
       ROUND(SUM(unidades * precio_unitario) / NULLIF(SUM(unidades),0),2) AS ticket_medio
FROM clean_ventas
GROUP BY fecha, id_producto;
```

O con pandas (para Parquet + sqlite):

```python
import pandas as pd
from pathlib import Path
import sqlite3

p = Path('project') / 'output' / 'parquet' / 'clean_ventas.parquet'
df = pd.read_parquet(p)
ore = df.groupby(['fecha','id_producto'], as_index=False).agg(importe_total=('importe', 'sum'), unidades_total=('unidades','sum'))
ore['ticket_medio'] = (ore['importe_total'] / ore['unidades_total']).round(2)
ore.to_parquet(Path('project')/'output'/'parquet'/'ventas_diarias_producto.parquet', index=False)
# opcional: persistir en sqlite
con = sqlite3.connect(Path('project')/'output'/'ut1.db')
ore.to_sql('ventas_diarias_producto', con, if_exists='replace', index=False)
con.close()
```

# 7. Lecciones aprendidas (breve)
- Añadir trazabilidad mínima (`_source_file`, `_ingest_ts`, `_batch_id`) es clave para idempotencia y auditoría.  
- Guardar `importe` como texto (Decimal→string) preserva precisión al almacenar en SQLite/CSV; para análisis numérico reconvertir a Decimal/float con cuidado.  
- Mantener la capa oro como vista acelera iteración; persistirla es necesario si la carga/consulta crece.

# 8. Próximos pasos (acciones y dueños)

- Pasos prioritarios: comprobar que los productos mencionados en `project/data/drops/ventas.csv` realmente existen en el fichero de catálogo `project/data/productos.csv`. Si aparecen productos que no están en el catálogo, hay que decidir qué hacer (añadirlos al catálogo, asignarlos a un código genérico o mover esas filas a cuarentena para revisarlas manualmente). Responsable: equipo (alumno X).

- Una vez resueltas las discrepancias del catálogo, generar y guardar la tabla de análisis (la capa "oro" `ventas_diarias_producto`) como un archivo Parquet y como tabla en la base de datos SQLite. Hacer esto sólo después de asegurar que los datos de producto están correctos para no contaminar los KPI. Responsable: equipo (alumno X).

- Automatizar comprobaciones básicas de calidad: por ejemplo, un script que calcule el % de filas en cuarentena por lote y que detecte productos desconocidos cada vez que se ejecute el proceso. Esto ayuda a detectar regresiones y a dar confianza antes de publicar la capa "oro". Responsable: equipo (alumno Y).

- Guardar la información original de las filas que van a cuarentena en formato fácil de leer (por ejemplo JSON) para acelerar la investigación y corrección manual. Responsable: equipo (alumno Z).


---

Annex: consultas rápidas (copiar/pegar en sqlite3)

```sql
-- Conteos
SELECT (SELECT COUNT(*) FROM clean_ventas) AS filas_plata, (SELECT COUNT(*) FROM quarantine_ventas) AS filas_quarantine;

-- Top productos
SELECT id_producto, SUM(unidades * precio_unitario) AS importe_total
FROM clean_ventas
GROUP BY id_producto
ORDER BY importe_total DESC
LIMIT 20;

-- Ventas diarias (vista)
SELECT * FROM ventas_diarias ORDER BY fecha DESC LIMIT 50;
```
