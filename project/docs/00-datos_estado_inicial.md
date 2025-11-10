# Estado inicial de los CSV (muestras para la exposición)

Objetivo: mostrar cómo llegan los datos antes de la limpieza y qué variables/artefactos usarás en la pizarra para explicar la transformación (raw → clean → DB).

> Ruta de los ficheros (relativas al repo):
> - `project/data/drops/ventas.csv`
> - `project/data/productos.csv`
> - `project/data/clientes.csv`

---

## 1) Ventas — `project/data/drops/ventas.csv`

Breve descripción: ventas con columnas tipo: fecha_venta, id_cliente, id_producto, unidades, precio_unitario.

Muestra (primeras filas, tabla):

| fecha_venta | id_cliente | id_producto | unidades | precio_unitario |
|-------------|------------|------------:|---------:|----------------:|
| 2025-07-07  | C001       | P001        | 2        | 2900            |
| 2025-07-07  | C002       | P002        | 1        | 2100            |
| 2025-07-07  | C003       | P003        | 3        | 420             |
| 2025-07-07  | C004       | P004        | 2        | 310             |
| 2025-07-07  | C005       | P005        | 1        | 3500            |

Raw (líneas tal cual, encabezado + ejemplo de contenido):

```
fecha_venta,id_cliente,id_producto,unidades,precio_unitario
2025-07-07,C001,P001,2,2900
2025-07-07,C002,P002,1,2100
...
2025-07-07,C120,P120,1,1250
bad-date,C200,P200,2,100
2025-13-01,C201,P201,1,200
2025-07-07,,P202,1,300
2025-07-07,C203,X123,2,400
2025-07-07,C204,P204,-1,500
2025-07-07,C205,P205,1,-100
2025-07-07,C206,P-207,abc,600
```

Notas importantes (qué buscar en la exposición):
- Hay filas bien formadas (fechas ISO, IDs tipo Cxxx/Pxxx).
- Ejemplos de problemas incluidos (líneas finales): fecha inválida, id_cliente vacío, id_producto que no cumple patrón `^P[0-9]+$`, unidades negativas, precio negativo, unidades no numéricas.
- Estas líneas deberían terminar en `quarantine` tras la limpieza con la causa explicada.

---

## 2) Productos — `project/data/productos.csv`

Breve descripción: catálogo con columnas como fecha_entrada, nombre_producto, id_producto, unidades, precio_unitario, categoria.

Muestra (primeras filas, tabla):

| fecha_entrada | nombre_producto                 | id_producto | unidades | precio_unitario | categoria        |
|---------------|----------------------------------|-------------|---------:|----------------:|------------------|
| 2025-01-03    | Lavadora Samsung 9kg            | P001        | 132      | 1450            | electrodomestico |
| 2025-01-05    | Refrigerador LG 300L            | P002        | 118      | 2100            | electrodomestico |
| 2025-01-06    | Microondas Panasonic 25L        | P003        | 140      | 420             | electrodomestico |
| 2025-01-07    | Cafetera Oster 1.5L             | P004        | 125      | 310             | electrodomestico |
| 2025-01-08    | Televisor Sony 55"             | P005        | 115      | 3500            | electronica      |

Raw (encabezado + ejemplo):

```
fecha_entrada,nombre_producto,id_producto,unidades,precio_unitario,categoria
2025-01-03,Lavadora Samsung 9kg,P001,132,1450,electrodomestico
2025-01-05,Refrigerador LG 300L,P002,118,2100,electrodomestico
...
```

Notas para la exposición:
- El catálogo suele utilizarse para validar `id_producto` en las ventas (referencial). Si una venta hace referencia a un `id_producto` que no existe en `productos.csv`, puede marcarse para revisión.
- `precio_unitario` en catálogo puede usarse como `precio_lista`; en facturación se suele usar el `precio_unitario` de la venta.

---

## 3) Clientes — `project/data/clientes.csv`

Breve descripción: fichero con `id_cliente`, nombre y apellidos.

Muestra (primeras filas, tabla):

| fecha       | nombre  | apellido  | id_cliente |
|-------------|---------|-----------|------------|
| 2025-01-03  | Arturo  | Navarro   | C001       |
| 2025-01-04  | María   | López     | C002       |
| 2025-01-05  | Carlos  | García    | C003       |

Raw (encabezado + ejemplo):

```
fecha,nombre,apellido,id_cliente 
2025-01-03, Arturo, Navarro, C001 
2025-01-04, María, López, C002 
...
```

Notas:
- Algunos CSV pueden tener espacios extra alrededor de campos (ej.: líneas con `, Arturo, Navarro, C001 `). En la limpieza se estandarizan (trim) y se normalizan tildes.

---

## Sección para la pizarra — versión pulida y lista para la exposición

He preparado una guía corta, clara y pensada para ser leída en voz alta durante 4–6 minutos. Solo contiene lo necesario: qué capturas tomar, qué variables (dataframes) debes mostrar y frases cortas para cada diapositiva. No hay código.

Diapositiva 1 — Fuentes (mensaje de apertura)
- Qué mostrar: 3 capturas (o una imagen con 3 columnas) con las primeras filas de cada fichero.
  - Variable a fotografiar: `ventas_raw` (head)
  - Variable a fotografiar: `productos_raw` (head)
  - Variable a fotografiar: `clientes_raw` (head)
- Texto breve para decir: "Estas son nuestras fuentes en crudo: ventas, catálogo de productos y clientes. Aquí empieza el proceso." 

Diapositiva 2 — Añadimos trazabilidad (por qué es importante)
- Qué mostrar: captura del dataframe de trabajo con las columnas de trazabilidad visibles.
  - Variable a fotografiar: `df` (mostrar `_ingest_ts`/`fecha_ejecucion`, `_source_file`, `batch_id`)
- Texto breve para decir: "Añadimos trazabilidad para saber cuándo y desde qué archivo se procesó cada fila; así reproducimos y auditamos ejecuciones fácilmente." 

Diapositiva 3 — Validaciones y cuarentena (qué queda fuera)
- Qué mostrar: montaje con dos paneles: izquierda `ventas_raw`, derecha `quarantine` (ejemplos con columna `reason`).
  - Variables soporte: `mask_valid` (resumen numérico) y `quarantine` (ejemplos con `reason`).
- Texto breve para decir: "Aplicamos reglas sencillas: formato de fecha ISO, unidades ≥ 0, precio ≥ 0 y `id_producto` con formato `P123`. Las filas que no cumplen van a 'quarantine' con la causa." 

Diapositiva 4 — Limpieza final y políticas (dedupe y cálculos)
- Qué mostrar: `clean` / `clean_to_save` (primeras filas) y un recuadro con métricas: filas iniciales → limpias → quarantine (%).
  - Variable a fotografiar: `clean` o `clean_to_save`
- Texto breve para decir: "Desduplicamos por clave natural (fecha, id_cliente, id_producto) — política: 'último gana' según la marca de ingestión — y calculamos `importe` = `unidades` × `precio_unitario`." 

Diapositiva 5 — Persistencia y resultado analítico
- Qué mostrar: comprobación visual de los artefactos y un fragmento de la vista analítica (KPIs):
  - Parquet: `project/output/parquet/clean_ventas.parquet` (ruta)
  - SQLite: `project/output/ut1.db` (ruta)
  - Fragmento de `views_sql` o `ventas_diarias_producto` con columnas `fecha`, `id_producto`, `importe`, `unidades`, `ticket_medio`
- Texto breve para decir: "Guardamos el resultado para analítica (Parquet) y para consultas (SQLite). Desde ahí creamos las vistas y calculamos los KPI." 

Qué variables exportar (lista final para tus capturas)
- ventas_raw — CSV original (head)
- productos_raw — catálogo (head)
- clientes_raw — clientes (head)
- df — copia de trabajo con `_ingest_ts`/`fecha_ejecucion`, `_source_file`, `batch_id`
- mask_valid — resumen (conteos)
- quarantine — ejemplos con `reason`
- clean / clean_to_save — resultado final (head)
- df_raw_sql — versión para BD (opcional)
- upsert_result — resumen de inserción/actualización (opcional)
- views_sql — fragmento de la vista analítica (opcional)

Frases rápidas (léelas tal cual durante la demo)
- "Recibimos los datos en bruto: ventas, productos y clientes."
- "Añadimos trazabilidad: fecha de ejecución y batch id para reproducibilidad." 
- "Aplicamos validaciones; las filas inválidas van a 'quarantine' con la causa." 
- "Desduplicamos por clave natural: 'último gana' según el timestamp de ingestión." 
- "Calculamos importe = unidades × precio_unitario y persistimos para análisis." 

Glosario corto (una o dos frases cada término)
- Máscara (`mask`): condición True/False por fila que define si una fila es válida.
- Quarantine: tabla de filas inválidas con una columna `reason` que explica el motivo.
- Trazabilidad: columnas `_ingest_ts`/`fecha_ejecucion`, `_source_file`, `batch_id` que permiten rastrear origen y ejecución.
- Dedupe: eliminar duplicados por (fecha, id_cliente, id_producto) conservando la fila con timestamp más reciente.
- Importe: campo calculado = unidades × precio_unitario (en código usar Decimal; en la pizarra muestra el número).

Consejo final (práctico)
- Para una demo clara: introduce 1–2 filas intencionadamente erróneas en `project/data/drops/ventas.csv` (fecha inválida, unidades negativas), ejecuta el pipeline y muestra cómo esas filas acaban en `quarantine` con su `reason`.

---

