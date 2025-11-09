-- Ejemplo de UPSERT (SQLite ≥3.24)
INSERT INTO clean_ventas AS c (fecha,id_cliente,id_producto,unidades,precio_unitario,importe,_ingest_ts)
VALUES (:fecha,:idc,:idp,:u,:p,:imp,:ts)
ON CONFLICT(fecha,id_cliente,id_producto) DO UPDATE SET
  unidades = excluded.unidades,
  precio_unitario = excluded.precio_unitario,
  importe = excluded.importe,
  _ingest_ts = excluded._ingest_ts
WHERE excluded._ingest_ts > c._ingest_ts;
