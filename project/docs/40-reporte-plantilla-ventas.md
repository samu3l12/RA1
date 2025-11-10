# Reporte — Ventas

## 1. Resumen ejecutivo
Periodo: **{periodo_ini} → {periodo_fin}**. Ingresos: **{ingresos:.2f} €**. Ticket medio: **{ticket:.2f} €**. Transacciones (líneas clean): **{trans}**. Se muestra concentración de ingresos, diversidad y evolución diaria.

## 2. KPIs principales
| Indicador | Valor |
|-----------|-------|
| Ingresos totales | {ingresos:.2f} € |
| Ticket medio (media) | {ticket:.2f} € |
| Ticket mediano | {mediana_ticket:.2f} € |
| Transacciones (líneas clean) | {trans} |
| Productos distintos | {productos_distintos} |
| Clientes distintos | {clientes_distintos} |
| Diversidad productos (productos/ líneas %) | {diversidad_productos_pct:.2f}% |
| % cuarentena sobre procesadas | {pct_quarantine:.2f}% |
| % ingresos top 5 productos | {top5_pct:.2f}% |
| Nº productos para 80% ingresos (Pareto) | {pareto_80_count} |
| % ingresos producto líder | {top_product_pct:.2f}% |
| % ingresos cliente líder | {top_cliente_pct:.2f}% |
| Día mayor ingreso | {dia_max} |
| Día menor ingreso | {dia_min} |

## 3. Top productos (importe y unidades)
{top_table}

## 4. Ventas por día (importe y líneas)
{by_day_table}

## 5. Ingresos por categoría (top)
{cat_table}

## 6. Calidad de datos
| Métrica | Valor |
|---------|-------|
| Filas bronce (raw) | {bronze} |
| Filas plata (clean) | {clean} |
| Filas quarantine | {quarantine} |
| % quarantine | {pct_quarantine:.2f}% |

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
