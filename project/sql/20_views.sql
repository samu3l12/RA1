-- Vista simple de ventas diarias
CREATE VIEW IF NOT EXISTS ventas_diarias AS
SELECT fecha, SUM(unidades*precio_unitario) AS importe_total, COUNT(*) AS lineas
FROM clean_ventas
GROUP BY fecha;
