# Plantilla de reporte — Ventas

## Periodo analizado
- Fecha inicio: {periodo_ini}
- Fecha fin   : {periodo_fin}

## KPIs principales
- Ingresos totales: {ingresos:.2f} €
- Ticket medio: {ticket:.2f} €
- Transacciones: {trans}

## Top productos
{top_table}

## Ventas por día
{by_day_table}

## Calidad
- Filas bronce: {bronze}
- Filas clean: {clean}
- Filas quarantine: {quarantine}

## Notas y supuestos
- Datos sin impuestos. Dinero en EUR.
- Dedupe por `(fecha,id_cliente,id_producto)`; último gana por `_ingest_ts`.

