# Diseño de ingestión

## Resumen
Este documento describe cómo entran los datos en el proyecto, la frecuencia de ingestión y las garantías mínimas que aplicamos. Su objetivo es servir como guía operativa y documental para reproducir e inspeccionar la ingestión de los CSV (`productos.csv`, `clientes.csv`, `drops/ventas.csv`) en el pipeline.

## Fuente
- **Origen:** CSVs en el repositorio: `project/data/productos.csv`, `project/data/clientes.csv`, `project/data/drops/ventas.csv`.
- **Formato:** CSV (texto). Columnas esperadas en ventas: `fecha` (ISO), `id_cliente`, `id_producto`, `unidades`, `precio_unitario`.
- **Frecuencia:** batch (ejecución manual / programada desde la raíz del repo). La entrega local del repo asume ejecución puntual antes de generar reportes.

## Estrategia
- **Modo:** batch (ejecución por archivo). No hay streaming en la entrega actual.
- **Incremental:** el pipeline consume el CSV de drops y aplica deduplicación por clave natural; la idempotencia se garantiza en la capa de destino (SQLite) mediante upserts y `_ingest_ts`.
- **Particionado:** no aplica en esta entrega (Parquet de salida no particionado); opción recomendada: particionar por `fecha` si crece el volumen.

## Idempotencia y deduplicación
- **batch_id:** se genera `_batch_id` por ejecución (UUID corto) y `_ingest_ts` (timestamp UTC) para trazabilidad.
- **clave natural:** `(fecha, id_cliente, id_producto)`.
- **Política:** “último gana por `_ingest_ts`”: en memoria se ordena por `_ingest_ts` y se ejecuta `drop_duplicates(..., keep='last')`; en SQLite se usan upserts con condición basada en `_ingest_ts`.

## Checkpoints y trazabilidad
- **trazabilidad:** cada fila conserva `_source_file`, `_ingest_ts`, `_batch_id` y `_row_id` (posición de archivo) para auditoría y resolución de conflictos.
- **DLQ / quarantine:** filas inválidas se guardan en `project/output/quality/ventas_quarantine.csv` junto con `motivo` para corrección manual. Opcionalmente se puede volcar `quarantine` a la BD si se desea más trazabilidad.

## SLA / Operación
- **Disponibilidad:** el pipeline es manual; si se automatiza, se recomienda ejecutarlo fuera de horas punta (p. ej., 03:00 UTC).
- **Alertas:** se recomienda añadir alertas si el % de `quarantine` excede un umbral (ej. 5%).

## Riesgos / Antipatrones
- No validar existencia referencial contra catálogos puede producir datos huérfanos en `clean_ventas`; por ahora sólo validamos formato (regex) y rangos.
- Usar float para dinero en vez de Decimal puede generar imprecisiones; en este proyecto los cálculos de importe se hacen con `Decimal` y se persisten en Parquet/DB como string para preservar precisión.
- SQLite no es adecuado para concurrencia alta; si el proyecto escala, migrar a un RDBMS (Postgres) o un almacén analítico.

## Procedimiento operativo (cómo ejecutar)
1. Situarse en la raíz del repositorio (donde está la carpeta `project`).
2. Ejecutar el pipeline de ingestión/limpieza:

```cmd
py -3 project\ingest\run.py
```

3. Salidas clave:
- `project/output/quality/ventas_quarantine.csv` — filas en cuarentena y motivos.
- `project/output/parquet/clean_ventas.parquet` — ventas limpias para analítica (importe guardado como string).
- `project/output/ut1.db` — SQLite con `raw_ventas` y `clean_ventas` (upserts aplicados).

4. Verificación rápida de la BD:

```cmd
py -3 project\ingest\check_db.py
```

## Notas / Recomendaciones
- Si se requiere validar que `id_producto`/`id_cliente` existan en catálogo, añadir la comprobación en la fase de limpieza y mover las filas no coincidentes a `quarantine`.
- Para grandes volúmenes, cambiar estrategia de upserts por batch o tabla temporal + MERGE para mejorar rendimiento.

## Contacto / Dueños
- Responsable (entregable): Estudiante / autor del repo.
- Soporte técnico: revisar `project/ingest/run.py` y `project/sql/` para entender la implementación.

