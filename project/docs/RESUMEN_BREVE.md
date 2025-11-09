Resumen breve de los cambios y del estado de `project/docs`

Checklist (rápido)
- [x] He simplificado `project/ingest/run.py` para leer explícitamente los 3 CSV (productos, clientes, drops/ventas).
- [x] Añadí una fila errónea en `project/data/clientes.csv` para demo de `quarantine`.
- [x] Creé `project/docs/PLANTILLA_FILLED.md` (entregable) y `project/docs/EXPOSICION_NOTAS.md` (privado).
- [x] Revisé todos los ficheros en `project/docs` y catalogué su estado en `project/docs/RESUMEN_CAMBIOS.md`.

Resumen (2–3 líneas)
He dejado el pipeline compacto y explícito: lee `productos.csv`, `clientes.csv` y `drops/ventas.csv`, aplica trazabilidad (`_source_file`, `_ingest_ts`, `_batch_id`), valida y separa filas inválidas en `output/quality/ventas_quarantine.csv`, deduplica por `(fecha,id_cliente,id_producto)` (último gana) y guarda ventas limpias en `output/parquet/clean_ventas.parquet` y en SQLite (`output/ut1.db`). Además añadí documentación de apoyo y notas para tu exposición.

> Nota: la implementación actual valida el formato de `id_producto`/`id_cliente` pero no comprueba que esos ids existan en los ficheros de catálogo (`productos.csv` y `clientes.csv`). Si quieres que la limpieza también verifique existencia en catálogo, puedo añadir esa validación para mover a `quarantine` las filas con referencias inexistentes.

Estado de `project/docs` (confirmación)
- He leído todos los MD en `project/docs` y creé `PLANTILLA_FILLED.md`, `EXPOSICION_NOTAS.md` y `RESUMEN_CAMBIOS.md`.
- Ningún fichero en `project/docs` es 0 bytes: algunos contienen placeholders (`…`) que puedes rellenar con contenido final.

Comandos (cmd.exe) para detectar y eliminar archivos vacíos en `project/docs`

1) Ver tamaños (bytes) de los ficheros en `project/docs`:

```cmd
for %F in (project\docs\*) do @echo %~zF %F
```

2) Eliminar ficheros de tamaño 0 (ejecuta solo si estás seguro):

```cmd
for %F in (project\docs\*) do @if %~zF==0 del "%F"
```

Nota: si ejecutas en un archivo batch (`.bat`) usa `%%F` en lugar de `%F`.

Comando para eliminar un fichero concreto (ejemplo):

```cmd
del project\docs\EXPOSICION_NOTAS.md
```

Si quieres que quite la fila errónea de `clientes.csv`, borre algún MD o rellene alguno de los placeholders (`…`) te lo hago ahora: dime qué fichero quieres que modifique y lo edito.
