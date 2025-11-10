# Reporte — Ventas

## 1. Resumen ejecutivo
Periodo: **2025-07-07 → 2025-07-07**. Ingresos: **24745.00 €**. Ticket medio: **1237.25 €**. Transacciones (líneas clean): **20**. Se muestra concentración de ingresos, diversidad y evolución diaria.

## 2. KPIs principales
| Indicador | Valor |
|-----------|-------|
| Ingresos totales | 24745.00 € |
| Ticket medio (media) | 1237.25 € |
| Ticket mediano | 755.00 € |
| Transacciones (líneas clean) | 20 |
| Productos distintos | 20 |
| Clientes distintos | 20 |
| Diversidad productos (productos/ líneas %) | 100.00% |
| % cuarentena sobre procesadas | 23.08% |
| % ingresos top 5 productos | 62.64% |
| Nº productos para 80% ingresos (Pareto) | 6 |
| % ingresos producto líder | 23.44% |
| % ingresos cliente líder | 23.44% |
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

## 5. Ingresos por categoría (top)
|categoria|ingresos|productos|
|---|---|---|
|electrodomestico|11170.0|6|
|electronica|4820.0|3|
|computacion|4470.0|4|
|muebles|1480.0|2|
|oficina|1250.0|1|
|redes|620.0|1|
|seguridad|370.0|1|
|iluminacion|340.0|1|
|electrico|225.0|1|

## 6. Calidad de datos
| Métrica | Valor |
|---------|-------|
| Filas bronce (raw) | 26 |
| Filas plata (clean) | 20 |
| Filas quarantine | 6 |
| % quarantine | 23.08% |

## 7. Interpretación rápida
- Concentración: pocos productos / clientes explican gran parte de ingresos.
- Diversidad de productos ayuda a evaluar dependencia del catálogo.
- Mediana de ticket complementa a la media para detectar sesgos por valores altos.
- Categorías con más ingreso orientan priorización comercial.
- Porcentaje de cuarentena indica calidad de origen y robustez de reglas.

## 8. Supuestos
- Importe sin impuestos (EUR).
- Dedupe por `(fecha,id_cliente,id_producto)`; último gana por `_ingest_ts`.
- Catálogo no validado externamente.
