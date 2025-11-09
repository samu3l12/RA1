# Plantilla rellenada - Proyecto UT1

1. Objetivo
-----------
Este documento describe el pipeline mínimo desarrollado para este proyecto y sirve para:
- Explicar qué problema resuelve: convertir los CSV de entrada (productos, clientes y drops/ventas) en un Mini‑DWH usable para análisis (dim_productos + fact_ventas) y reportes de KPI.
- Soportar decisiones operacionales y de calidad: justificar las reglas de limpieza, la política de deduplicación y la estrategia de persistencia (parquet + SQLite).
- Servir como evidencia reproducible para la entrega y para auditoría de datos (trazabilidad).

2. Alcance
----------
Cubre:
- Ingesta batch de los CSV en `project/data` y `project/data/drops/ventas.csv`.
- Limpieza: coerción de tipos, validaciones básicas, separación en `quarantine` y `clean`.
- Modelado mínimo: generación de `dim_productos` y tabla de hechos `fact_ventas` (vía upserts en SQLite y parquet para analítica).
- Salida: parquet listo para análisis, base SQLite con vistas y un `reporte.md` resumen.

No cubre:
- Integración con sistemas externos (APIs, colas), ni pipelines en streaming.
- Gobernanza avanzada (versionado de esquemas, control de accesos) ni orquestación en producción.

3. Decisiones / Reglas
----------------------
- Estrategia de ingestión: batch (archivo único `project/data/drops/ventas.csv`); idempotencia conseguida mediante upserts a la base SQLite y dedupe local por `_ingest_ts`.
- Clave natural: `(fecha, id_cliente, id_producto)`.
- Idempotencia: implementada vía deduplicación (sort + drop_duplicates keep='last' por `_ingest_ts`) y upserts SQL (`project/sql/10_upserts.sql`).
- Validaciones de calidad implementadas:
  - Tipos: `fecha` -> date ISO, `unidades` -> entero, `precio_unitario` -> decimal.
  - Nulos: campos obligatorios (`fecha`, `id_cliente`, `id_producto`, `unidades`, `precio_unitario`) → filas inválidas a `ventas_quarantine.csv`.
  - Rangos: `unidades >= 0`, `precio_unitario >= 0`.
  - Dominios: `id_producto` recomendado con patrón `^P[0-9]+$` (se puede añadir validación estricta si se desea).
  - Nota: la implementación actual valida el formato de `id_producto`/`id_cliente` pero NO verifica que esos ids existan en los ficheros de catálogo (`productos.csv`, `clientes.csv`). Si se desea, se puede añadir una validación adicional que mueva a `quarantine` las ventas con referencias inexistentes en los catálogos.
- Estandarización: trim de texto y normalización (tildes) para campos de catálogo; códigos en mayúsculas.
- Trazabilidad: mantener `_source_file`, `_ingest_ts`, `_batch_id` en `raw_ventas`.

## Persistencia en SQLite (ut1.db)

- El pipeline persiste también los datos limpios en `project/output/ut1.db`.
- Esquema y scripts relevantes: `project/sql/00_schema.sql` (esquema), `project/sql/10_upserts.sql` (upserts), `project/sql/20_views.sql` (vistas).
- Detalles:
  - `raw_ventas`: volcado del CSV con trazabilidad.
  - `clean_ventas`: filas validadas insertadas/actualizadas vía UPSERT; clave primaria `(fecha,id_cliente,id_producto)`.
  - `importe` se calcula con Decimal y se guarda en la BD como `TEXT` (cadena) para preservar precisión; en Parquet se guarda también como string.
  - `ventas_quarantine.csv` contiene las filas en cuarentena (motivo); por defecto no se vuelca en la BD.

4. Procedimiento / Pasos (reproducible)
--------------------------------------
Requisitos mínimos: Python 3, pandas, sqlite3; `pyarrow` o `fastparquet` sólo si quieres parquet (opcional; el script puede adaptarse a CSV).

Pasos para reproducir desde la raíz del repositorio:

1) Ejecutar el pipeline de ingestión/limpieza:

```bash
py -3 project\ingest\run.py
```

2) Comprobar outputs generados en `project/output/`:
- Parquet (ventas limpias): `project/output/parquet/clean_ventas.parquet`
- CSV de cuarentena: `project/output/quality/ventas_quarantine.csv`
- Base SQLite con vistas: `project/output/ut1.db`
- Reporte resumen: `project/output/reporte.md`

3) Reproducir consultas de ejemplo (desde SQLite):
- Abrir `project/output/ut1.db` con DB Browser o sqlite3 y ejecutar las vistas `ventas_diarias` o queries de ejemplo en `project/sql/20_views.sql`.

5. Evidencias
-------------
Incluir en la entrega (sugerido):
- `project/output/parquet/clean_ventas.parquet` (o su export CSV) como evidencia de la capa plata/oro.
- `project/output/quality/ventas_quarantine.csv` con ejemplos de filas inválidas y motivo.
- `project/output/ut1.db` con tablas `raw_ventas` y `clean_ventas` (o vistas equivalentes).
- `project/output/reporte.md` (resumen con KPI) y capturas de consultas SQL sobre `ut1.db`.

Fragmentos útiles (ejemplos a incluir en el anexo):
- Count de filas procesadas: SELECT COUNT(*) FROM raw_ventas;
- Count de filas clean: SELECT COUNT(*) FROM fact_ventas; (o vista equivalente)
- Top productos: SQL mostrado en `project/docs/30-modelado-oro-ventas.md`.

6. Resultados (KPI)
-------------------
KPIs calculados por el pipeline y contenidos en `reporte.md`:
- Ingresos totales: Σ(unidades * precio_unitario) — archivo: `project/output/reporte.md`.
- Transacciones / líneas procesadas: número de filas en `clean`.
- Ticket medio: ingresos totales / nº transacciones.

En la entrega final se incluirán valores numéricos extraídos del `clean_ventas.parquet` y tablas por día / por categoría (si hay dimensión `categoria` en `productos.csv`).

7. Lecciones aprendidas
-----------------------
- Qué salió bien:
  - Separación clara entre raw, clean y quarantine facilita auditoría y debugging.
  - Uso de trazabilidad (`_ingest_ts`, `_source_file`) permite decidir política de "último gana".
- Qué mejorar / cambiar en producción:
  - Usar Decimal para dinero en transformaciones críticas (evitar float) y asegurar exactitud en base de datos.
  - Añadir pruebas automáticas (unitarias) sobre las validaciones y on-boarding de nuevos ficheros.
  - Añadir un motor de orquestación y versiones de datos (p. ej. Airflow + control de versiones de esquemas).

8. Próximos pasos (acciones y dueños)
------------------------------------
- Estudiante (tú): revisar `project/docs/PLANTILLA_FILLED.md`, completar `99-lecciones-aprendidas.md` con notas reales del trabajo y preparar la demo de 5 min usando `EXPOSICION_NOTAS.md`.
- Entrega: subir `project/output/reporte.md`, `clean_ventas.parquet` (o CSV) y `ut1.db` al repositorio de entrega.
- Opcional (mejora técnica): migrar almacenamiento analítico a Parquet particionado por `fecha` y agregar validación regex para `id_producto` y `id_cliente`.
