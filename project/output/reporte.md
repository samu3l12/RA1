# Plantilla de reporte (resumen ejecutivo)

**Titular**: Ingresos 139850.00 € · Transacciones 121 · Quarantine 6 (4.7%)

## 1) Métricas clave

- Ingresos: 139850.00 €

- Ticket medio: 1155.79 €

- Transacciones: 121


## 2) Contribución por producto

| Producto | Importe | % |
|---------:|--------:|--:|

| P065 | 7000.00 | 5% |

| P001 | 5800.00 | 4% |

| P029 | 5600.00 | 4% |

| P069 | 5600.00 | 4% |

| P021 | 4350.00 | 3% |

| P062 | 4200.00 | 3% |

| P045 | 3500.00 | 3% |

| P025 | 3500.00 | 3% |

| P005 | 3500.00 | 3% |

| P085 | 3500.00 | 3% |

| P105 | 3500.00 | 3% |

| P081 | 2900.00 | 2% |

| P101 | 2900.00 | 2% |

| P041 | 2900.00 | 2% |

| P089 | 2800.00 | 2% |

| P049 | 2800.00 | 2% |

| P109 | 2800.00 | 2% |

| P009 | 2800.00 | 2% |

| P040 | 2500.00 | 2% |

| P042 | 2100.00 | 2% |

| P002 | 2100.00 | 2% |

| P102 | 2100.00 | 2% |

| P082 | 2100.00 | 2% |

| P022 | 2100.00 | 2% |

| P061 | 1450.00 | 1% |

| P010 | 1300.00 | 1% |

| P050 | 1300.00 | 1% |

| P110 | 1300.00 | 1% |

| P090 | 1300.00 | 1% |

| P003 | 1260.00 | 1% |

| P060 | 1250.00 | 1% |

| P080 | 1250.00 | 1% |

| P020 | 1250.00 | 1% |

| P100 | 1250.00 | 1% |

| P120 | 1250.00 | 1% |

| P091 | 1040.00 | 1% |

| P032 | 960.00 | 1% |

| P072 | 960.00 | 1% |

| P012 | 960.00 | 1% |

| P039 | 930.00 | 1% |

| P099 | 930.00 | 1% |

| P006 | 900.00 | 1% |

| P075 | 890.00 | 1% |

| P115 | 890.00 | 1% |

| P095 | 890.00 | 1% |

| P035 | 890.00 | 1% |

| P055 | 890.00 | 1% |

| P015 | 890.00 | 1% |

| P063 | 840.00 | 1% |

| P083 | 840.00 | 1% |


## 3) Evolución diaria

- Periodo analizado: 2025-07-07 a 2025-07-07

| Fecha | Importe total | Transacciones |
|------:|--------------:|--------------:|

| 2025-07-07 | 139850.00 | 121 |


## 4) Calidad de datos

- Filas procesadas: bronce 127 · plata 121 · quarantine 6

- % filas en quarantine: 4.7%

- Motivos principales de quarantine:

  - fecha inválida: 2

  - id_cliente faltante: 1

  - unidades inválidas: 1

  - precio inválido: 1

  - unidades inválidas; id_producto formato inesperado: 1


## 5) Próximos pasos

- Revisar filas en `project/output/quality/ventas_quarantine.csv` y corregir origen.

- Añadir validaciones adicionales y alertas si el % de quarantine supera el umbral aceptable.
