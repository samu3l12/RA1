<!-- NUEVA DIAPOSITIVA: Ingesta / get_data.py (movida al principio) -->
Diapositiva 1 — Ingesta (get_data.py)
Título: Ingesta y qué hace `get_data.py`
 En este proyecto el módulo `get_data.py` prepara el CSV de entrada para las pruebas: crea las carpetas `project/data/` y `project/data/drops/`, corrige un posible fichero mal nombrado (`project/data/ productos.csv` → `productos.csv`) y escribe el archivo `project/data/drops/ventas.csv` con un bloque de filas válidas seguido de varias filas erróneas para probar la cuarentena.

Detalles exactos:
- Crea directorios `project/data/` y `project/data/drops/` si no existen.
- Si existe `project/data/ productos.csv` (con espacio inicial), lo renombra a `project/data/productos.csv`.
- Escribe `project/data/drops/ventas.csv` como texto plano. El fichero que genera usa el encabezado `fecha_venta` (no `fecha`) y en el ejemplo incorpora líneas de comentario que comienzan con `#` (p.ej. `# --- filas erróneas para pruebas de quarantine ---`).
- El script sobrescribe el CSV existente y luego imprime en consola: `Generado: project/data/drops/ventas.csv`.

Importante — qué NO hace este script:
- No realiza limpieza ni valida filas (eso lo hace `run.py`).
- No añade campos de trazabilidad (`_source_file`, `_ingest_ts`, `_batch_id`) dentro del CSV; `run.py` añade/normaliza columnas cuando lee el CSV (por ejemplo renombra `fecha_venta` a `fecha` si hace falta).

Cómo ejecutarlo (comando):

```bash
py -3 project\ingest\get_data.py
```

Consejo práctico para la demo:
- Muestra el contenido del CSV generado (head) para explicar por qué hay filas que caerán en `quarantine` (las líneas comentadas y las filas erróneas). Luego ejecuta `py -3 project\ingest\run.py` para demostrar la separación `clean`/`quarantine`.

Diapositiva 1 — Fuentes en crudo
Título: Fuentes en crudo
Texto para leer: Estas son nuestras fuentes en crudo: ventas, catálogo de productos y clientes. Aquí empieza todo.
Imagen sugerida: expo_1_ventas.png / expo_1_productos.png / expo_1_clientes.png

<!-- Reemplazado: tablas embebidas en Markdown en lugar de imágenes -->

Ventas:

| fecha_venta | id_cliente | id_producto | unidades | precio_unitario |
|-------------|------------|-------------:|---------:|----------------:|
| 2025-07-07  | C001       | P001         | 2        | 2900            |
| 2025-07-07  | C002       | P002         | 1        | 2100            |
| 2025-07-07  | C003       | P003         | 3        | 420             |
| 2025-07-07  | C004       | P004         | 2        | 310             |
| 2025-07-07  | C005       | P005         | 1        | 3500            |
| 2025-07-07  | C006       | P006         | 5        | 180             |

Productos:

| fecha_entrada | nombre_producto              | id_producto | unidades | precio_unitario |
|---------------|------------------------------|-------------|---------:|----------------:|
| 2025-01-03    | Lavadora Samsung 9kg         | P001        | 132      | 1450            |
| 2025-01-05    | Refrigerador LG 300L         | P002        | 118      | 2100            |
| 2025-01-06    | Microondas Panasonic 25L     | P003        | 140      | 420             |
| 2025-01-07    | Cafetera Oster 1.5L          | P004        | 125      | 310             |

Clientes:

| fecha       | nombre  | apellido  | id_cliente |
|-------------|---------|-----------|------------|
| 2025-01-03  | Arturo  | Navarro   | C001       |
| 2025-01-04  | María   | López     | C002       |
| 2025-01-05  | Carlos  | García    | C003       |
| 2025-01-06  | Lucía   | Sánchez   | C004       |

Notas: muestra las 6 filas y el nombre de la variable `ventas_raw` en la diapositiva para referencia.

---

Diapositiva 2 — Trazabilidad
Título: Trazabilidad
Texto para leer: Añadimos trazabilidad para saber cuándo y en qué lote se procesó cada fila; esto facilita reproducir ejecuciones y auditar cambios.
Imagen sugerida: expo_2_trace.png

<!-- Tabla embebida: trazabilidad (head) -->

| fecha_venta | id_cliente | id_producto | _source_file | _ingest_ts                 | _batch_id  |
|-------------|------------|-------------|--------------|----------------------------|------------|
| 2025-07-07  | C001       | P001        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |
| 2025-07-07  | C002       | P002        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |
| 2025-07-07  | C003       | P003        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |
| 2025-07-07  | C004       | P004        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |

Notas: resalta `_ingest_ts` y `_source_file` en la diapositiva.

---

Diapositiva 3 — Validaciones y cuarentena
Título: Validaciones y cuarentena
Texto para leer: Aplicamos reglas: fecha ISO, unidades >= 0, precio_unitario >= 0 y id_producto con patrón P[0-9]+. Las filas que no cumplen van a 'quarantine' con el motivo registrado.
Imagen sugerida: expo_3_quarantine.png

<!-- Tabla embebida: quarantine ejemplos -->

| idx | fecha_venta | id_cliente | id_producto | unidades | precio_unitario | reason                |
|-----|-------------|------------|-------------|---------:|----------------:|-----------------------|
| 120 | NaT         | C200       | P200        | 2        | 100             | fecha inválida        |
| 121 | NaT         | C201       | P201        | 1        | 200             | fecha inválida        |
| 123 | 2025-07-07  | C203       | X123        | 2        | 400             | id_producto inesperado|
| 124 | 2025-07-07  | C204       | P204        | -1       | 500             | unidades inválidas    |

Notas: explica cada razón brevemente en la exposición.

---

Diapositiva 4 — Limpieza y deduplicación
Título: Limpieza y deduplicación
Texto para leer: Desduplicamos por la clave natural (fecha, id_cliente, id_producto). Política: 'último gana' según `_ingest_ts`. Calculamos `importe` = `unidades` × `precio_unitario`.
Imagen sugerida: expo_4_clean.png

<!-- Tabla embebida: clean (head) -->

| fecha       | id_cliente | id_producto | unidades | precio_unitario | importe |
|-------------|------------|-------------|---------:|----------------:|--------:|
| 2025-07-07  | C001       | P001        | 2        | 2900            | 5800    |
| 2025-07-07  | C002       | P002        | 1        | 2100            | 2100    |
| 2025-07-07  | C003       | P003        | 3        | 420             | 1260    |
| 2025-07-07  | C006       | P006        | 5        | 180             | 900     |
| 2025-07-07  | C007       | P007        | 2        | 95              | 190     |
| 2025-07-07  | C008       | P008        | 3        | 60              | 180     |

Notas: pone un recuadro en la diapositiva con métricas (filas iniciales → limpias → quarantine %).

---

Diapositiva 5 — Persistencia y KPIs
Título: Persistencia y KPIs
Texto para leer: Guardamos los datos limpios en Parquet y SQLite; desde ahí generamos vistas que alimentan los KPI: ingresos, ticket medio y unidades vendidas.
Imagen sugerida: expo_5_kpis.png

<!-- Tabla embebida: KPIs ejemplo -->

| fecha       | id_producto | importe | unidades | ticket_medio |
|-------------|-------------|--------:|--------:|-------------:|
| 2025-07-07  | P001        | 5800    | 2       | 2900         |
| 2025-07-07  | P002        | 2100    | 1       | 2100         |
| 2025-07-07  | P003        | 1260    | 3       | 420          |
| 2025-07-07  | P006        | 900     | 5       | 180          |

Notas: incluye en la diapositiva el path del Parquet y del .db para que el tribunal lo vea.

<!-- NUEVA: capa ORO persistida -->

Diapositiva 6 — Capa ORO (persistida)
Título: Capa ORO — ventas diarias por producto
Texto para leer: Además de la vista, ahora persistimos la tabla ORO `ventas_diarias_producto` para análisis y entrega; está disponible como tabla en SQLite y como Parquet para consumo analítico.
Rutas: `project/output/ut1.db` → tabla `ventas_diarias_producto`; `project/output/parquet/ventas_diarias_producto.parquet` (o CSV si no hay pyarrow).

Tabla ORO (ejemplo — 4 filas):

| fecha       | id_producto | importe_total | unidades_total | ticket_medio |
|-------------|-------------|--------------:|---------------:|-------------:|
| 2025-07-07  | P065        | 7000          | 2              | 3500.00      |
| 2025-07-07  | P001        | 5800          | 2              | 2900.00      |
| 2025-07-07  | P069        | 5600          | 2              | 2800.00      |
| 2025-07-07  | P029        | 5600          | 2              | 2800.00      |

Notas: muestra dónde consultar la tabla ORO y cómo usarla para generar gráficos/insights.

---

Diapositiva final — Cierre y próximos pasos
Título: Cierre y próximos pasos
Texto para leer: Resumen: pasamos de raw → clean → persistencia. Recomendación: automatizar tests de calidad y activar alertas si el % de quarantine sube por encima de un umbral aceptable.
Imagen sugerida: expo_final_acciones.png

<!-- Reemplazado: tabla de cierre en Markdown en lugar de imagen -->

| Acción | Responsable |
|--------|-------------|
| Automatizar tests de calidad | Equipo de datos |
| Configurar alertas por % de quarantine | Operaciones / DevOps |
| Documentar reglas y supuestos en `project/docs/` | Autor del proyecto |

---

Preparación práctica antes de la exposición
- Verifica `project/output/parquet/clean_ventas.parquet` y `project/output/ut1.db`.
- Si quieres mostrar `quarantine` en vivo, añade 1–2 filas erróneas a `project/data/drops/ventas.csv` y ejecuta `python project/ingest/run.py`.
- Si quieres generar imágenes desde este repo, ejecuta:
