---
title: "Plantilla entregable — Proyecto UT1 RA1"
tags: ["UT1","RA1","docs"]
version: "1.0.1"
owner: "equipo-alumno"
status: "final"
---

# 1. Objetivo
Transformar los CSV de ventas, productos y clientes en datos limpios (plata) y agregados (oro) básicos, demostrando trazabilidad, calidad y cálculo de KPI (ingresos, ticket medio, top productos).

# 2. Alcance
Incluye ingestión batch, limpieza (tipado, validaciones, dedupe "último gana"), cuarentena de filas inválidas y generación de artefactos analíticos (Parquet + SQLite + reporte). No incluye procesos en tiempo real ni enriquecimientos externos.

# 3. Decisiones / Reglas
- Clave natural ventas: (fecha, id_cliente, id_producto) → último gana por _ingest_ts.
- Validaciones: fecha ISO, unidades >=0, precio_unitario >=0, id_producto ^P[0-9]+$.
- Campos obligatorios: fecha, id_cliente, id_producto, unidades, precio_unitario.
- Filas inválidas → quarantine con motivo.

# 4. Procedimiento reproducible
1. Ejecutar: `py -3 project/ingest/run.py`
2. Revisar artefactos en project/output/ (Parquet, ut1.db, reporte.md).
3. Consultar KPI vía vistas/SQL.

# 5. Evidencias
- Filas raw: 26
- Filas clean: 20
- Filas quarantine: 6
- Periodo: 2025-07-07 → 2025-07-07

# 6. Resultados / KPI
- Ingresos totales: 24745.00
- Ticket medio: 1237.25
- Transacciones: 20
- % cuarentena: 23.08%

Top productos (importe / unidades):

|id_producto|importe|unidades|
|---|---|---|
|P001|5800.0|2|
|P005|3500.0|1|
|P009|2800.0|1|
|P002|2100.0|1|
|P010|1300.0|2|
|P003|1260.0|3|
|P020|1250.0|1|
|P012|960.0|2|
|P006|900.0|5|
|P015|890.0|1|

Ventas por día (importe_total / líneas):

|fecha|importe_total|lineas|
|---|---|---|
|2025-07-07|24745.0|42.0|

# 7. Lecciones
Mantener trazabilidad (_ingest_ts, _source_file, _batch_id) simplifica idempotencia y auditoría. Dedupe por timestamp evita duplicados. Separar clean vs quarantine permite mejorar reglas sin perder visibilidad.

# 8. Próximos pasos
Persistir y ampliar capa oro (más agregados), añadir tests automáticos de % quarantine, validar catálogo completo de productos, documentación de SLA.
