EXPOSICIÓN — Slides listos (OPCIÓN B)

Usa este archivo para copiar y pegar cada diapositiva directa a PowerPoint/Keynote.
Cada sección contiene: Título, frase exacta para leer, imagen sugerida (nombre de fichero) y una tabla pequeña (muestra) lista para pegar.

Duración recomendada: 4–6 minutos en total.

---

DIAPOSITIVA 1 — Fuentes en crudo
Título: Fuentes en crudo
Frase (leer): Estas son nuestras fuentes en crudo: ventas, catálogo de productos y clientes. Aquí empieza todo.
Imagen sugerida: `expo_1_ventas.png`, `expo_1_productos.png`, `expo_1_clientes.png` (tres mini-imágenes)
Tabla (muestra corta — pega como imagen o tabla):

| fecha_venta | id_cliente | id_producto | unidades | precio_unitario |
|-------------|------------|-------------:|---------:|----------------:|
| 2025-07-07  | C001       | P001         | 2        | 2900            |
| 2025-07-07  | C002       | P002         | 1        | 2100            |
| 2025-07-07  | C003       | P003         | 3        | 420             |
| 2025-07-07  | C004       | P004         | 2        | 310             |
| 2025-07-07  | C005       | P005         | 1        | 3500            |

Notas: muestra solo 4–6 filas para que la diapositiva sea legible.

---

DIAPOSITIVA 2 — Trazabilidad
Título: Trazabilidad
Frase (leer): Añadimos trazabilidad para saber cuándo y en qué lote se procesó cada fila; así reproducimos ejecuciones y auditamos cambios.
Imagen sugerida: `expo_2_trace.png`
Tabla (muestra corta):

| fecha_venta | id_cliente | id_producto | _source_file | _ingest_ts                 | _batch_id  |
|-------------|------------|-------------|--------------|----------------------------|------------|
| 2025-07-07  | C001       | P001        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |
| 2025-07-07  | C002       | P002        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |
| 2025-07-07  | C003       | P003        | ventas.csv   | 2025-11-10T11:36:06+00:00  | batch-demo |

---

DIAPOSITIVA 3 — Validaciones y cuarentena
Título: Validaciones y cuarentena
Frase (leer): Aplicamos reglas: fecha ISO, unidades ≥ 0, precio_unitario ≥ 0 y id_producto con patrón P123. Las filas que no cumplen van a 'quarantine' con la razón.
Imagen sugerida: `expo_3_quarantine.png`
Tabla (ejemplos cortos):

| idx | fecha_venta | id_cliente | id_producto | unidades | precio_unitario | reason                |
|-----|-------------|------------|-------------|---------:|----------------:|-----------------------|
| 120 | NaT         | C200       | P200        | 2        | 100             | fecha inválida        |
| 124 | 2025-07-07  | C204       | P204        | -1       | 500             | unidades inválidas    |
| 123 | 2025-07-07  | C203       | X123        | 2        | 400             | id_producto inesperado|

---

DIAPOSITIVA 4 — Limpieza y deduplicación
Título: Limpieza y deduplicación
Frase (leer): Desduplicamos por la clave natural (fecha, id_cliente, id_producto) — 'último gana' según `_ingest_ts` — y calculamos `importe` = `unidades` × `precio_unitario`.
Imagen sugerida: `expo_4_clean.png`
Tabla (muestra):

| fecha       | id_cliente | id_producto | unidades | precio_unitario | importe |
|-------------|------------|-------------|---------:|----------------:|--------:|
| 2025-07-07  | C001       | P001        | 2        | 2900            | 5800    |
| 2025-07-07  | C002       | P002        | 1        | 2100            | 2100    |
| 2025-07-07  | C003       | P003        | 3        | 420             | 1260    |

---

DIAPOSITIVA 5 — Persistencia y KPIs
Título: Persistencia y KPIs
Frase (leer): Guardamos los datos limpios en Parquet y SQLite; desde ahí generamos vistas para los KPI: ingresos, ticket medio y unidades vendidas.
Tabla (muestra vista analítica):

| fecha       | id_producto | importe | unidades | ticket_medio |
|-------------|-------------|--------:|--------:|-------------:|
| 2025-07-07  | P001        | 5800    | 2       | 2900         |
| 2025-07-07  | P002        | 2100    | 1       | 2100         |

---

DIAPOSITIVA 6 — Capa ORO (persistida)
Título: Capa ORO — ventas diarias por producto
Frase (leer): Además de la vista, persistimos la tabla ORO `ventas_diarias_producto` que se guarda en SQLite y como Parquet para consumo analítico.
Tabla (ejemplo ORO — 4 filas):

| fecha       | id_producto | importe_total | unidades_total | ticket_medio |
|-------------|-------------|--------------:|---------------:|-------------:|
| 2025-07-07  | P065        | 7000          | 2              | 3500.00      |
| 2025-07-07  | P001        | 5800          | 2              | 2900.00      |
| 2025-07-07  | P069        | 5600          | 2              | 2800.00      |
| 2025-07-07  | P029        | 5600          | 2              | 2800.00      |

Notas prácticas: rutas — `project/output/ut1.db` (tabla `ventas_diarias_producto`); `project/output/parquet/ventas_diarias_producto.parquet`.

---

DIAPOSITIVA FINAL — Cierre y próximos pasos
Título: Cierre y próximos pasos
Frase (leer): Resumen: pasamos de raw → clean → persistencia. Recomendación: automatizar tests de calidad y añadir alertas si el % de quarantine sube por encima de un umbral.
Imagen sugerida: `expo_final_acciones.png`

---

Preparación práctica antes de la exposición
- Coloca las imágenes `expo_*.png` en `project/output/expo/` o pega las tablas en las diapositivas. Mantén cada tabla corta (4–6 filas) para legibilidad.
- Si quieres que genere las imágenes automáticamente, elige la Opción A y las crearé.

Fecha: 2025-11-10
