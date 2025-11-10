# Reglas de limpieza y calidad — Ventas

Este documento describe cómo se limpian y validan las ventas antes de usarlas para análisis.

## Tipos y formatos
- fecha en ISO (YYYY-MM-DD) o timestamp UTC normalizado a fecha.
- unidades como número entero mayor o igual que 0.
- precio_unitario como decimal mayor o igual que 0 (se evita usar float para dinero).

## Campos obligatorios
- fecha, id_cliente, id_producto, unidades, precio_unitario.
- Las filas que no los cumplen se envían a cuarentena con un motivo concreto.

## Validaciones
- unidades >= 0 y de tipo numérico.
- precio_unitario >= 0 y convertible a decimal.
- id_producto coincide con el patrón ^P[0-9]+$.

## Deduplicación
- Clave natural: (fecha, id_cliente, id_producto).
- Política: “último gana” ordenando por _ingest_ts.

## Estandarización de texto
- Recorte de espacios y mayúsculas en identificadores (id_cliente, id_producto).

## Trazabilidad
- En todas las capas se mantienen _source_file, _ingest_ts y _batch_id para poder rastrear qué lote y qué fichero originó cada fila.

## QA rápida
- Porcentaje de filas que van a cuarentena y conteos por día para comprobar que el volumen procesado coincide con lo esperado.

## Persistencia
- Plata (clean): se guarda en SQLite (tabla clean_ventas) y en Parquet (project/output/parquet/clean_ventas.parquet).
- Bronce (raw): se guarda en SQLite (tabla raw_ventas) con las columnas originales y la trazabilidad.
- Cuarentena: se guarda como CSV en project/output/quality/ventas_quarantine.csv y también en SQLite (quarantine_ventas) con el motivo y la fila original serializada.
