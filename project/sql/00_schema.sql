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

-- Productos: raw / clean / quarantine
CREATE TABLE IF NOT EXISTS raw_productos(
  id_producto TEXT, nombre TEXT, precio_unitario TEXT,
  _ingest_ts TEXT, _source_file TEXT, _batch_id TEXT
);

CREATE TABLE IF NOT EXISTS clean_productos(
  id_producto TEXT PRIMARY KEY, nombre TEXT, precio_unitario REAL,
  _ingest_ts TEXT, _source_file TEXT, _batch_id TEXT
);

CREATE TABLE IF NOT EXISTS quarantine_productos(
  _reason TEXT, _row TEXT, _ingest_ts TEXT, _source_file TEXT, _batch_id TEXT
);

-- Clientes: raw / clean / quarantine
CREATE TABLE IF NOT EXISTS raw_clientes(
  id_cliente TEXT, nombre TEXT,
  _ingest_ts TEXT, _source_file TEXT, _batch_id TEXT
);

CREATE TABLE IF NOT EXISTS clean_clientes(
  id_cliente TEXT PRIMARY KEY, nombre TEXT,
  _ingest_ts TEXT, _source_file TEXT, _batch_id TEXT
);

CREATE TABLE IF NOT EXISTS quarantine_clientes(
  _reason TEXT, _row TEXT, _ingest_ts TEXT, _source_file TEXT, _batch_id TEXT
);

-- Tabla ORO (se puede recrear desde clean_ventas)
CREATE TABLE IF NOT EXISTS ventas_diarias_producto(
  fecha TEXT, id_producto TEXT,
  importe_total REAL, unidades_total REAL, ticket_medio REAL
);
