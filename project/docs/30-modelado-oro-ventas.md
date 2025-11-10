---
title: "Modelo oro — Ventas"
owner: "equipo-alumno"
periodicidad: "diaria"
version: "1.0.1"
---

# Resumen
Documento que describe la capa ORO para ventas: tablas resultantes, métricas claves (KPI), consultas SQL para obtenerlas y ejemplos de resultados extraídos del artefacto analítico generado por `run.py` (SQLite + Parquet).

# Tablas ORO
- `clean_ventas` (línea de venta): filas validadas, tipadas y deduplicadas.
- `ventas_diarias` (vista): agregación por `fecha` (ya creada como vista `ventas_diarias`).

# Métricas (KPI)
- Ingresos netos (periodo mostrado): Σ(`unidades * precio_unitario`) sobre `clean_ventas`.
- Ticket medio: `Ingresos netos / nº_transacciones`.
- Nº transacciones (líneas válidas).

# Supuestos
- Todas las cifras en EUR sin ajuste por impuestos ni inflaciones.
- Dedupe: clave natural `(fecha, id_cliente, id_producto)`, política "último gana" basada en `_ingest_ts`.

# Consultas base (SQL ejecutables)
```sql
-- 1) Ingresos por día
SELECT fecha, SUM(unidades * precio_unitario) AS importe_total, COUNT(*) AS lineas
FROM clean_ventas
GROUP BY fecha;
```

```sql
-- 2) Ticket medio por día
SELECT fecha, (SUM(unidades * precio_unitario) / COUNT(*)) AS ticket_medio
FROM clean_ventas
GROUP BY fecha;
```

```sql
-- 3) Top productos (importe total)
SELECT id_producto, SUM(unidades * precio_unitario) AS importe
FROM clean_ventas
GROUP BY id_producto
ORDER BY importe DESC
LIMIT 10;
```

```sql
-- 4) Calidad rápida: conteos clean / quarantine / total
SELECT
  (SELECT COUNT(*) FROM clean_ventas) AS filas_plata,
  (SELECT COUNT(*) FROM quarantine_ventas) AS filas_quarantine,
  ((SELECT COUNT(*) FROM clean_ventas) + (SELECT COUNT(*) FROM quarantine_ventas)) AS total_procesadas;
```

# (análisis Pareto): ¿Cuál es el número mínimo de productos que explica el 80% de los ingresos y cuáles son?
```sql
WITH prod AS (
  SELECT id_producto, SUM(unidades * precio_unitario) AS importe
  FROM clean_ventas
  GROUP BY id_producto
), ranked AS (
  SELECT
    id_producto,
    importe,
    SUM(importe) OVER (ORDER BY importe DESC) AS cum_importe,
    SUM(importe) OVER () AS total_importe,
    ROW_NUMBER() OVER (ORDER BY importe DESC) AS k
  FROM prod
)
SELECT k AS productos_necesarios,
       ROUND(100.0 * cum_importe / total_importe, 2) AS pct_acumulado,
       (SELECT GROUP_CONCAT(id_producto)
        FROM ranked r2
        WHERE r2.k <= ranked.k) AS productos
FROM ranked
WHERE cum_importe >= 0.80 * total_importe
ORDER BY k
LIMIT 1;
```

# Ejemplo de resultados (snapshot actual)
- Ingresos totales: 24745.00
- Ticket medio: 1237.25
- Líneas clean: 20
- Filas quarantine: 6
- Top producto: P001


# Ejemplos (2 filas) de artefactos Parquet

## Parquet: clean_ventas (ejemplo — 2 filas)
| fecha | id_cliente | id_producto | unidades | precio_unitario | importe | _ingest_ts |
|---|---|---|---:|---:|---:|---|
| 2025-07-07 | C001 | P001 | 2 | 2900 | 5800.00 | 2025-11-10T11:36:06.350870+00:00 |
| 2025-07-07 | C088 | P088 | 1 | 60 | 60.00 | 2025-11-10T11:36:06.350870+00:00 |

## Parquet: productos (ejemplo — 2 filas)
| fecha_entrada | id_producto | nombre_producto | precio_unitario | categoria |
|---|---|---|---:|---|
| 2025-01-03 | P001 | Lavadora Samsung 9kg | 1450 | electrodomestico |
| 2025-01-05 | P002 | Refrigerador LG 300L | 2100 | electrodomestico |

## Parquet: clientes (ejemplo — 2 filas)
| fecha | id_cliente | nombre | apellido |
|---|---|---|---|
| 2025-01-03 | C001 | Arturo | Navarro |
| 2025-01-04 | C002 | María | López |

## Parquet / Vista ORO: ventas_diarias (ejemplo)
| fecha | importe_total | lineas |
|---|---:|---:|
| 2025-07-07 | 139050 | 120 |

<!--
Presentador: muestra estas dos filas por artefacto y explica que son ejemplos extraídos del Parquet/SQLite que genera `run.py`. Si necesitas más filas, en el notebook puedes cargar el Parquet y usar df.head(N).
-->
