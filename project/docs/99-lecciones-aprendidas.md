# Lecciones aprendidas

## Qué salió bien
- Separar claramente las capas (raw, clean, oro) simplificó la revisión y la trazabilidad.
- Mantener _ingest_ts y _batch_id permitió repetir cargas sin duplicar filas (política “último gana”).
- El cálculo de ingresos y ticket medio resultó directo gracias a la limpieza previa de tipos.
- Exportar a Parquet y SQLite facilitó tanto el análisis rápido como la consulta con SQL.

## Qué mejorar
- Ajustar las reglas para reducir el porcentaje de cuarentena; algunas filas terminan en cuarentena por formatos mínimos que podrían corregirse automáticamente.
- Añadir validación cruzada con catálogo de productos (no se comprobó todavía si todos los id_producto existen realmente en una lista de referencia).
- Incorporar pruebas automáticas (tests) para detectar cambios involuntarios en la lógica de limpieza.
- Homogeneizar el tratamiento del precio para evitar diferentes representaciones (Decimal vs string).

## Siguientes pasos
- Completar verificación de catálogo y añadir una capa de enriquecimiento de productos si se requiere.
- Implementar métricas adicionales en la capa oro (por ejemplo, ingresos por segmento de cliente si el CSV de clientes aporta esa información).
- Automatizar ejecución periódica y generar alertas si el % de cuarentena supera un umbral definido.
- Documentar SLA y tiempos estimados de procesamiento.

## Apéndice (evidencias)
- Artefactos generados: Parquet limpio (ventas, productos, clientes), tablas en SQLite (raw_*, clean_*, quarantine_*), vista de agregación diaria.
- Reporte con ingresos y ticket medio listo para presentar.
