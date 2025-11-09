-- Tablas ejemplo (SQLite u otro motor adaptando tipos)
CREATE TABLE IF NOT EXISTS raw_ventas(
  fecha TEXT, id_cliente TEXT, id_producto TEXT,
  unidades TEXT, precio_unitario TEXT,
  _ingest_ts TEXT, _source_file TEXT, _batch_id TEXT
);

CREATE TABLE IF NOT EXISTS clean_ventas(
  fecha TEXT, id_cliente TEXT, id_producto TEXT,
  unidades REAL, precio_unitario REAL,
  importe TEXT,
  _ingest_ts TEXT,
  PRIMARY KEY (fecha, id_cliente, id_producto)
);

CREATE TABLE IF NOT EXISTS quarantine_ventas(
  _reason TEXT, _row TEXT, _ingest_ts TEXT, _source_file TEXT, _batch_id TEXT
);
