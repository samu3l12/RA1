# Notas para exposición (5 minutos)

Objetivo general (10–15s)
-------------------------
Presentar en 5 minutos qué hace el proyecto: ingesta batch de ventas, limpieza con reglas de calidad, creación de un mini‑DWH (dim_productos + fact_ventas) y generación de un reporte con KPIs (ingresos, ticket medio, transacciones).

Guion cronometrado (5 min)
---------------------------
- 0:00–0:15 — Titular / mensaje clave: "Pipeline batch que convierte CSV de ventas en un mini‑DWH listo para análisis y reporting".
- 0:15–0:45 — Flujo alto (ingesta → limpieza → persistencia): explicar las piezas y outputs.
- 0:45–2:15 — Ejecución / demo corta: ejecutar pipeline y mostrar outputs clave.
- 2:15–3:30 — Resultados y KPIs (leer `reporte.md` o consultar DB).
- 3:30–4:30 — Calidad de datos y trazabilidad (quarantine, motivos y `_ingest_ts`).
- 4:30–5:00 — Conclusión y próximos pasos.

Mensajes clave que debes transmitir
----------------------------------
- Trazabilidad: cada fila lleva `_source_file`, `_ingest_ts` y `_batch_id` para auditoría y para aplicar la política “último gana”.
- Calidad: las filas inválidas se separan en `project/output/quality/ventas_quarantine.csv` con motivo para corrección.
- Persistencia doble: Parquet para analítica (`project/output/parquet/clean_ventas.parquet`) y SQLite (`project/output/ut1.db`) para consultas y entrega.

Comandos rápidos (ejemplo para la demo — ejecútalos desde la raíz del repo)
--------------------------------------------------------------------------
1) Ejecutar la limpieza y persistencia:

    ```cmd
    py -3 project\ingest\run.py
    ```

2) Ver el CSV de cuarentena (si lo hay):

    ```cmd
    type project\output\quality\ventas_quarantine.csv
    ```

3) Ver el reporte generado:

    ```cmd
    type project\output\reporte.md
    ```

4) Inspeccionar la BD (script de ayuda):

    ```cmd
    py -3 project\ingest\check_db.py
    ```

Demo sugerida (paso a paso)
---------------------------
1. Ejecuta `run.py` para reproducir todo el pipeline (limpieza, parquet, sqlite, reporte).
2. Abre `project/output/reporte.md` y muestra: ingresos totales, ticket medio y % quarantine.
3. Ejecuta `py -3 project\ingest\check_db.py` y muestra 2‑3 filas de `clean_ventas` y que `importe` coincide con lo mostrado en el reporte.
4. Muestra `project/output/quality/ventas_quarantine.csv` y explica los motivos más frecuentes.

Preguntas frecuentes y respuestas cortas (prepárate para esto)
-------------------------------------------------------------
Q: ¿Cómo garantizas idempotencia? 
A: Deduplicación por `(fecha,id_cliente,id_producto)` con "último gana" por `_ingest_ts` y upserts en SQLite.

Q: ¿Qué pasa con los productos desconocidos en catálogo?
A: Actualmente validamos formato (`^P[0-9]+$`) y otros rangos; no validamos existencia referencial contra `productos.csv` salvo que se active esa comprobación (documentado en `project/docs`).

Q: ¿Por qué usar Decimal para importes? 
A: Para evitar errores de redondeo de float en dinero; en memoria usamos Decimal y persistimos `importe` como texto para preservar exactitud.

Q: ¿Dónde reviso las filas inválidas? 
A: `project/output/quality/ventas_quarantine.csv` contiene las filas quarantena y la columna `motivo` con la(s) causa(s).

Q: ¿Se puede automatizar? 
A: Sí — el pipeline es batch y se puede ejecutar periódicamente; para producción recomendamos particionar Parquet por fecha y usar un motor SQL para upserts por lotes.

Notas técnicas para consultas rápidas
------------------------------------
- `mask` en pandas: serie booleana usada para separar `clean` y `quarantine` (`clean = df.loc[mask]`).
- `df.copy()`: evita alterar el DataFrame original.
- `_ingest_ts` usa zona UTC y permite comparar ejecuciones.

Consejos para la demo (práctico)
-------------------------------
- Ten abierto el archivo `project/output/reporte.md` y la DB (`ut1.db` en DB Browser) para mostrar datos en orden rápido.
- Si el tiempo es limitado, prioriza: (1) titular/objetivo, (2) demo rápida del pipeline, (3) dos KPIs y la cuarentena.

Fin — si quieres, te preparo una diapositiva con estas notas o un script corto que ejecute los comandos y muestre las salidas más relevantes automáticamente.
