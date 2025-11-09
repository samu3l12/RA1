# Plantilla de reporte (resumen ejecutivo)

**Titular**: Qué pasa + por qué importa + qué hacemos.

Ej.: Ingresos +9% vs semana previa por P20. Reponer stock y replicar promo.

1) Métricas clave
-----------------
- Ingresos: __ € (↑/↓)
- Ticket medio: __ €
- Transacciones: __

2) Contribución por producto
----------------------------
| Producto | Importe | % |
|---------:|--------:|--:|
| P10      |      —  | — |
| P20      |      —  | — |
| ...      |      —  | — |

(Insertar tabla con `id_producto`, `importe` y porcentaje sobre el total.)

3) Evolución diaria
-------------------
- Periodo analizado: {periodo_ini} a {periodo_fin}
- Series diarias: tabla/mini-gráfico con fecha, importe_total, transacciones.
- Observaciones:
  - Enero 2025: …
  - Señalar picos/vales y eventos (promos, lanzamientos) que expliquen variaciones.

4) Calidad de datos
-------------------
- Filas procesadas: bronce __ · plata __ · quarantine __
- % filas en quarantine: __ %
- Motivos principales de quarantine:
  - fecha inválida: __
  - unidades no numéricas / negativas: __
  - precio_unitario inválido / negativo: __
  - id_cliente / id_producto faltantes: __

(Adjuntar en el anexo ejemplos de filas de `ventas_quarantine.csv` y conteos por motivo.)

5) Próximos pasos
-----------------
- Acción 1: (p.ej., revisar catálogo de productos para P20; responsable: Nombre; plazo: fecha)
- Acción 2: (p.ej., corregir subida de precios erróneos; responsable: Nombre; plazo: fecha)
- Acción 3: (p.ej., añadir validación regex para `id_producto` y alertas automáticas)

Anexos / Evidencias
-------------------
- `project/output/parquet/clean_ventas.parquet` (o CSV export)
- `project/output/quality/ventas_quarantine.csv` (ejemplos de filas y motivos)
- Consultas SQL reproducibles en `project/sql/` para generar tablas/segmentos usados en el reporte

Instrucciones rápidas para generar el reporte desde el pipeline
--------------------------------------------------------------
1. Ejecutar: py -3 project\ingest\run.py
2. Abrir: project\output\reporte.md (resumen mínimo)
3. Completar la plantilla con valores extraídos de `clean_ventas.parquet` y `ut1.db`.
