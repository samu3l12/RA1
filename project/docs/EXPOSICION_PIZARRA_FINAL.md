EXPOSICIÓN — Guion final y tablas (lista para la pizarra)

Objetivo: versión final en lenguaje natural, lista para leer en voz alta (4–6 minutos). Incluye las tablas que pegaste en formato Markdown, en el orden de la presentación. Usa este archivo como fuente para copiar diapositivas o exportarlas.

Duración aproximada: 4–6 min en total; 40–60 segundos por diapositiva clave.

---

Índice rápido
1. Fuentes iniciales (raw)
2. Trazabilidad
3. Validaciones y cuarentena
4. Limpieza y deduplicación
5. Persistencia y KPIs
6. Cierre y preguntas frecuentes
7. Mascaras de validación (qué es `mask_valid`)
8. Ingesta: cómo funciona `get_data.py`

---

1) Fuentes iniciales (raw)

<!-- PARA LA PIZARRA: "Frase sugerida" es la línea corta que leerás en voz alta. Manténla breve y clara; este comentario solo se ve en el archivo fuente. -->
Estas son nuestras fuentes en crudo: ventas, catálogo de productos y clientes. Aquí empieza todo.

<!-- NOTA ORADOR: A continuación se muestran "primeras filas" o un "head" reducido. Las tablas están truncadas para la pizarra; si quieres mostrar más filas, abre el CSV/DB. -->
Ventas (`ventas_raw_head.csv`) — primeras filas (pega a modo de "foto"):

| fecha_venta | id_cliente | id_producto | unidades | precio_unitario |
|-------------|------------|-------------:|---------:|----------------:|
| 2025-07-07  | C001       | P001         | 2        | 2900            |
| 2025-07-07  | C002       | P002         | 1        | 2100            |
| 2025-07-07  | C003       | P003         | 3        | 420             |
| 2025-07-07  | C004       | P004         | 2        | 310             |
| 2025-07-07  | C005       | P005         | 1        | 3500            |

Productos (`productos_raw_head.csv`) — primeras filas:

| fecha_entrada | nombre_producto              | id_producto | unidades | precio_unitario |
|---------------|------------------------------|-------------|---------:|----------------:|
| 2025-01-03    | Lavadora Samsung 9kg         | P001        | 132      | 1450            |
| 2025-01-05    | Refrigerador LG 300L         | P002        | 118      | 2100            |
| 2025-01-06    | Microondas Panasonic 25L     | P003        | 140      | 420             |
| 2025-01-07    | Cafetera Oster 1.5L          | P004        | 125      | 310             |

Clientes (`clientes_raw_head.csv`) — primeras filas:

| fecha       | nombre  | apellido  | id_cliente |
|-------------|---------|-----------|------------|
| 2025-01-03  | Arturo  | Navarro   | C001       |
| 2025-01-04  | María   | López     | C002       |
| 2025-01-05  | Carlos  | García    | C003       |
| 2025-01-06  | Lucía   | Sánchez   | C004       |

---

2) Trazabilidad

<!-- PARA LA PIZARRA: "Frase sugerida" (trazabilidad) — leer en voz alta la frase corta. Este comentario es interno. -->
Añadimos trazabilidad para saber cuándo y en qué lote se procesó cada fila; esto facilita reproducir ejecuciones y auditar cambios.

<!-- NOTA ORADOR: Muestra aquí solo el head de la tabla de trazabilidad. Si necesitas ejemplos dinámicos, usa project/output/expo o consulta la DB. -->
`df_trace_head.csv` — ejemplo (head):

| fecha_venta | id_cliente | id_producto | _source_file | _ingest_ts                 | _batch_id  |
|-------------|------------|-------------|--------------|----------------------------|------------|
| 2025-07-07  | C001       | P001        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |
| 2025-07-07  | C002       | P002        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |
| 2025-07-07  | C003       | P003        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |

---

3) Validaciones y cuarentena

<!-- PARA LA PIZARRA: "Frase sugerida" (validaciones) — línea para leer. Manténla simple y con el mensaje de reglas principales. -->
Aplicamos reglas: fecha ISO, unidades >= 0, precio_unitario >= 0, id_producto con patrón P[0-9]+. Las filas que no cumplen van a 'quarantine' con la razón.

<!-- NOTA ORADOR: La tabla de 'quarantine' es un ejemplo; explica las razones más comunes (fecha inválida, unidades negativas, formato de id_producto). -->
`quarantine_head.csv` — ejemplos:

| idx | fecha_venta | id_cliente | id_producto | unidades | precio_unitario | reason                |
|-----|-------------|------------|-------------|---------:|----------------:|-----------------------|
| 120 | NaT         | C200       | P200        | 2        | 100             | fecha inválida        |
| 121 | NaT         | C201       | P201        | 1        | 200             | fecha inválida        |
| 123 | 2025-07-07  | C203       | X123        | 2        | 400             | id_producto inesperado|
| 124 | 2025-07-07  | C204       | P204        | -1       | 500             | unidades inválidas    |

---

4) Limpieza y deduplicación

<!-- PARA LA PIZARRA: "Frase sugerida" (limpieza) — frase corta que resuma dedupe y calculo de importe. -->
Limpiamos y desduplicamos por (fecha, id_cliente, id_producto). Política: 'último gana' según la marca de ingestión. Además calculamos `importe` = `unidades` × `precio_unitario`.

<!-- NOTA ORADOR: La tabla 'clean' muestra el resultado ya tipado y con importe calculado; usa esta vista para explicar el flujo ETL sencillo. -->
`clean_head.csv` (resultado final) — ejemplo (head):

| fecha       | id_cliente | id_producto | unidades | precio_unitario | importe |
|-------------|------------|-------------|---------:|----------------:|--------:|
| 2025-07-07  | C001       | P001        | 2.0      | 2900.00         | 5800.00 |
| 2025-07-07  | C002       | P002        | 1.0      | 2100.00         | 2100.00 |
| 2025-07-07  | C003       | P003        | 3.0      | 420.00          | 1260.00 |
| 2025-07-07  | C006       | P006        | 5.0      | 180.00          | 900.00  |

---

5) Persistencia y KPIs

<!-- PARA LA PIZARRA: "Frase sugerida" (persistencia/KPIs) — frase corta para leer. -->
Guardamos la tabla limpia en Parquet para analítica y en SQLite para consultas; a partir de ahí generamos las vistas que alimentan el reporte y los KPI.

<!-- NOTA ORADOR: La vista 'ventas_diarias' o 'ventas_diarias_producto' es la agregación que usarás para mostrar KPIs. -->
`ventas_diarias_producto` (ejemplo):

| fecha       | id_producto | importe | unidades | ticket_medio |
|-------------|-------------|--------:|--------:|-------------:|
| 2025-07-07  | P001        | 5800.00 | 2.0     | 2900.00     |
| 2025-07-07  | P002        | 2100.00 | 1.0     | 2100.00     |

---

6) Cierre y preguntas frecuentes
Texto para decir: "Este es el flujo completo, desde que llega el dato hasta que obtenemos información confiable. ¿Preguntas?"

---

Resumen ejecutivo (texto de apoyo para la exposición)

Recibimos los datos en bruto (ventas, productos y clientes), añadimos trazabilidad con `fecha_ejecucion` y `batch_id` para reproducibilidad, aplicamos validaciones (tipos, rangos y dominios) y colocamos en `quarantine` las filas inválidas con su motivo. Lo que queda válido lo limpiamos y desduplicamos por la clave natural (fecha, id_cliente, id_producto), dejando 'último gana' según la marca de ingestión; calculamos `importe` = `unidades` × `precio_unitario` y persistimos los resultados para análisis.

---

Mascaras de validación (qué es `mask_valid`)

En el proceso de limpieza usamos una "máscara" booleana llamada `mask_valid`. Es una Serie de pandas que marca True/False para cada fila según si cumple todas las reglas de calidad. Las filas con `True` pasan a `clean_ventas`; las filas con `False` van a `quarantine_ventas` (junto con la razón).

Cómo se construye (resumen):
- Comprobamos que `fecha` se haya parseado correctamente (ISO / timestamp).  
- `unidades` debe ser numérico y >= 0.  
- `precio_unitario` debe convertirse a Decimal y ser >= 0.  
- `id_cliente` y `id_producto` deben existir y no estar vacíos.  
- `id_producto` debe cumplir el dominio: ^P[0-9]+$ (p. ej. P001, P20).

En código Python (simplificado):

```python
mask_valid = (
    df['fecha'].notna()
    & df['unidades_num'].notna() & (df['unidades_num'] >= 0)
    & df['precio_unitario_dec'].notna() & (df['precio_unitario_dec'] >= Decimal('0'))
    & df['id_cliente'].notna() & (df['id_cliente'].str.strip() != '')
    & df['id_producto'].notna() & (df['id_producto'].str.strip() != '')
    & df['id_producto'].astype(str).str.match(r'^P[0-9]+$', na=False)
)
```

Fragmento de `mask_valid_summary` (muestra):

| idx | valid |
|----:|:-----:|
| 0   | True  |
| 1   | True  |
| 2   | True  |
| 3   | True  |
| ... | ...   |
| 119 | True  |
| 120 | False |  <!-- fecha inválida -->
| 121 | False |  <!-- fecha inválida -->
| 122 | True  |

Nota: en tu ejecución real `clean_ventas` tiene 120 filas y `quarantine_ventas` 7 filas; `mask_valid` refleja exactamente esa partición.

Resumen numérico (mask_valid_summary)

| valid | count |
|:-----:|------:|
| True  |   120 |
| False |     7 |
| Total |   127 |

Interpretación rápida: de las 127 filas ingestadas, 120 pasaron las validaciones y 7 fueron enviadas a cuarentena con la razón indicada; el porcentaje de cuarentena es ~5.5%.

¿Por qué es útil la máscara?
- Permite separar la lógica de validación del resto del pipeline.  
- Facilita generar estadísticas rápidas (porcentaje en quarantine) y auditoría.  
- Es la entrada para construir `quarantine` (filas inválidas con motivo) y `clean` (filas válidas).  


Ingesta: cómo funciona `get_data.py` (resumen para el MD)

Objetivo: leer los CSV/NDJSON de `project/data/drops/`, añadir trazabilidad mínima y devolver un DataFrame "raw" para la limpieza.

Conceptos clave que añade la ingesta:
- `_source_file`: nombre del fichero origen (p. ej. `ventas.csv`).  
- `_ingest_ts`: marca de tiempo ISO de la ejecución (permite aplicar la política "último gana").  
- `_batch_id`: identificador del lote/ejecución (útil para idempotencia y auditoría).

Fragmento típico de `get_data.py` (simplificado):

```python
from datetime import datetime, timezone
import uuid
import pandas as pd

_now_ts = datetime.now(timezone.utc).isoformat()
_batch_id = 'batch-' + uuid.uuid4().hex[:8]
raw_df = pd.read_csv('project/data/drops/ventas.csv', dtype=str)
raw_df['_source_file'] = 'ventas.csv'
raw_df['_ingest_ts'] = _now_ts
raw_df['_batch_id'] = _batch_id
```

Explicación de variables:
- `_now_ts` → fecha/hora UTC en formato ISO. Se usa para saber cuándo se recibió el lote.  
- `_batch_id` → id único de la ejecución; permite identificar todas las filas de un mismo lote y soporta idempotencia (por ejemplo, eliminar registros previos del mismo `_batch_id` antes de insertar).  
- `raw_df` → DataFrame con los datos tal como se leyeron del CSV; después se transforma, valida y se separa en `clean`/`quarantine`.

Buenas prácticas relacionadas con la ingesta
- Siempre añadir `_source_file`, `_ingest_ts` y `_batch_id` para trazabilidad.  
- No modificar los datos raw in-place (trabajar sobre copias: `df = raw_df.copy()`) para mantener la evidencia original si hace falta.  
- Registrar (o exportar) el `raw_df.head()` a `project/output/expo/` para evidencias y para la presentación.

---
<!--
Preparación práctica (antes de presentar)
- Asegúrate de tener el repo en la raíz del entorno de ejecución y de ejecutar `python project/ingest/run.py` desde ahí.
- Añade 1–2 filas erróneas en `project/data/drops/ventas.csv` para demostrar `quarantine` en vivo.
- Exporta las capturas (o genera imágenes) en `project/output/expo/` con nombres `expo_1_ventas.png`, `expo_2_trace.png`, etc. (puedo generarlas si me das OK).
- Revisa `project/output/parquet/clean_ventas.parquet` y `project/output/ut1.db` antes de la demo.
-->
Siguiente pasos (opcional)
- Generar automáticamente imágenes `expo_*.png` a partir de estas tablas.
- Crear `EXPOSICION_SLIDES_READY.md` con cada diapositiva lista para copiar en PowerPoint/Keynote.
- Preparar un ZIP con CSVs e imágenes para entrega.

Fecha: 2025-11-10
