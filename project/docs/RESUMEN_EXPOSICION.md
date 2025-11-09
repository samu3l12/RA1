# Resumen para exposición (5 minutos)

Este documento es TU apoyo personal para defender el proyecto en 5 minutos. No se entrega.

1) Objetivo (20–30s)
- Construimos un Mini-DWH con **productos** y **ventas** para practicar joins, medidas y KPIs.
- Insumos: `project/data/productos.csv` y `project/data/drops/ventas.csv`.

2) Flujo (60–90s)
- Ingesta (batch): leemos CSVs con trazabilidad (`_source_file`, `_ingest_ts`, `_batch_id`, `_row_id`).
- Limpieza (plata): coerción de tipos, validaciones, dedupe por `(fecha,id_cliente,id_producto)` con política "último gana".
- Persistencia: Parquet para analítica y SQLite para consultas SQL y upserts.
- Oro: agregaciones diarias por producto (importe, unidades, ticket medio).

3) Qué valida el pipeline (40–50s)
- Campos obligatorios: fecha, id_cliente, id_producto, unidades, precio_unitario.
- Rangos: unidades>=0, precio_unitario>=0.
- Dominios: id_producto con patrón `^P[0-9]+$`.
- Filas inválidas a cuarentena con razones (`ventas_quarantine.csv`).

> Nota: la implementación actual valida el formato de `id_producto`/`id_cliente` pero no verifica que esos ids existan en `productos.csv` o `clientes.csv`. Si se desea, se puede añadir una validación adicional que mueva a `quarantine` las ventas con referencias inexistentes en los catálogos.

4) Qué produce y dónde (30s)
- `project/output/parquet/clean_ventas.parquet` — fuente analítica.
- `project/output/ut1.db` — SQLite con tablas raw_ventas y clean_ventas y vistas (ventas_diarias).
- `project/output/reporte.md` — reporte con KPI y tablas.

5) Preguntas que pueden hacer y respuestas cortas (30–60s)
- ¿Cómo aseguras idempotencia? -> Upserts en SQLite + dedupe por `_ingest_ts`.
- ¿Por qué Decimal en precio? -> Precisión para dinero; evita errores de float.
- ¿Qué pasa si el catálogo cambia? -> Normalizar id_producto y actualizar dim_productos; validar contra catálogo en la limpieza.
- ¿Cómo evaluas calidad? -> % filas en quarantine y conteos por día.

6) Notas técnicas para responder (si te preguntan más detalle)
- Dedupe: `df.sort_values(['_ingest_ts','_row_id']).drop_duplicates(..., keep='last')`.
- Importes: multiplicación unidades*precio con Decimal y `.quantize(CENT)` para 2 decimales.
- Para escalar: particionar parquet por `fecha` o usar un motor (Delta/iceberg).

7) Mensaje final (10s)
- El pipeline es reproducible y genera proveniencia y métricas básicas; permite explicar decisiones de calidad y soportar análisis posteriores.
