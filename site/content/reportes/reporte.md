# Reporte — Ventas

## 1. Resumen ejecutivo
Periodo: **2025-07-07 → 2025-07-07**. Ingresos: **24745.00 €**. Ticket medio: **1237.25 €**. Transacciones (líneas clean): **20**. Se muestra concentración de ingresos y evolución diaria.

## 2. KPIs principales
| Indicador | Valor |
|-----------|-------|
| Ingresos totales | 24745.00 € |
| Ticket medio | 1237.25 € |
| Transacciones (líneas clean) | 20 |
| % cuarentena sobre procesadas | 23.08% |
| % ingresos top 5 productos | 62.64% |
| Nº productos necesarios para 80% ingresos (Pareto) | 6 |
| % ingresos producto líder | 23.44% |
| Día mayor ingreso | 2025-07-07 |
| Día menor ingreso | 2025-07-07 |

## 3. Top productos (importe y unidades)
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

## 4. Ventas por día (importe y líneas)
|fecha|importe_total|lineas|
|---|---|---|
|2025-07-07|24745.0|42.0|

## 5. Calidad de datos
| Métrica | Valor |
|---------|-------|
| Filas bronce (raw) | 26 |
| Filas plata (clean) | 20 |
| Filas quarantine | 6 |
| % quarantine | 23.08% |

## 6. Interpretación rápida
- La concentración de ingresos en pocos productos ayuda a decidir dónde enfocar promociones.
- El número de productos que aportan el 80% indica nivel de dependencia del catálogo.
- El día de mayor ingreso permite cruzar con eventos (campañas, lanzamientos).
- Un porcentaje alto de cuarentena sugiere revisar reglas o calidad del origen.

## 7. Supuestos
- Importe sin impuestos (EUR).
- Dedupe por `(fecha,id_cliente,id_producto)`; último gana por `_ingest_ts`.
- No se valida aún la existencia de id_producto en un catálogo externo.
