# Resumen breve de cambios y estado de `project/docs`

Resumen rápido
--------------
He hecho cambios en el pipeline y creado dos documentos de apoyo. Este archivo resume lo esencial en pocas líneas y lista el estado actual de los MD en `project/docs`.

Cambios principales realizados
----------------------------
- `project/ingest/run.py`: simplificado para leer explícitamente `productos.csv`, `clientes.csv` y `drops/ventas.csv`; mantiene trazabilidad, validación, dedupe y persistencia a parquet y SQLite.
- `project/data/clientes.csv`: añadida una fila errónea (id_cliente vacío) para demo de `quarantine`.
- Creado `project/docs/PLANTILLA_FILLED.md` (entregable, resumen ejecutivo).
- Creado `project/docs/EXPOSICION_NOTAS.md` (privado, notas para tu exposición de 5 minutos).

Estado y catálogo de `project/docs`
----------------------------------
A continuación indico cada fichero encontrado en `project/docs` y una nota corta sobre su contenido / si está poblado:

- `00-README-curso.md` — Contiene índice y orientación del curso. (Poblado)
- `10-diseno-ingesta.md` — Diseño de ingestión: estrategia, idempotencia y trazabilidad. (Poblado)
- `20-limpieza-calidad.md` — Reglas de limpieza y calidad (tipos, nulos, dedupe). (Poblado)
- `20-limpieza-calidad-ventas.md` — (no modificado por mí en esta sesión; revisar si necesitas contenido específico por ventas)
- `30-modelado-oro.md` — Definición de tablas oro y consultas SQL ejemplo. (Poblado)
- `30-modelado-oro-ventas.md` — (no modificado por mí; revisar para adaptar al dataset si quieres)
- `40-reporte-plantilla.md` — Plantilla de reporte ejecutivo. (Poblado)
- `40-reporte-plantilla-ventas.md` — (no modificado por mí; revisar si quieres un reporte específico por ventas)
- `99-lecciones-aprendidas.md` — Plantilla para lecciones aprendidas. (Poblado/placeholder)
- `PLANTILLA.md` — Plantilla general (metadatos + estructura). (Poblado)
- `PLANTILLA_FILLED.md` — NUEVO: versión rellenada con resumen ejecutivo del proyecto (entregable).
- `RESUMEN_EXPOSICION.md` — Contenido de apoyo para exposición (poblado).
- `EXPOSICION_NOTAS.md` — NUEVO: notas privadas y ejemplos para la exposición (poblado).

Archivos "vacíos" o placeholders
--------------------------------
He revisado los MD disponibles; ninguno es un fichero de 0 bytes. Algunos contienen placeholders o puntos suspensivos (`…`) donde se esperan tus textos (por ejemplo `99-lecciones-aprendidas.md` tiene secciones sin rellenar). Si quieres eliminar archivos que realmente estén vacíos (0 bytes) te doy comandos abajo.

Comandos cmd.exe para detectar y eliminar archivos vacíos en `project/docs`
----------------------------------------------------------------------------
1) Mostrar tamaño (bytes) de cada fichero en `project/docs` (útil para identificar archivos 0 bytes):

```cmd
for %F in (project\docs\*) do @echo %~zF %F
```

2) (Opcional) Eliminar ficheros de tamaño 0 en `project/docs` — **ejecuta solo si estás seguro**:

```cmd
for %F in (project\docs\*) do @if %~zF==0 del "%F"
```

Nota: si pones estos comandos dentro de un archivo batch (`.bat`), usa `%%F` en lugar de `%F`.

Comandos para eliminar un fichero concreto (ejemplo):

```cmd
del project\docs\EXPOSICION_NOTAS.md
```

O para mover a la papelera (PowerShell):

```powershell
Move-Item project\docs\EXPOSICION_NOTAS.md -Destination "$env:USERPROFILE\\Recycle.Bin"
```

(El ejemplo PowerShell no es necesario si trabajas solo en `cmd.exe`.)

Qué hago a continuación si quieres que siga
-----------------------------------------
- Puedo revisar y rellenar los `*-ventas.md` (por ejemplo `20-limpieza-calidad-ventas.md`, `30-modelado-oro-ventas.md`, `40-reporte-plantilla-ventas.md`) con ejemplos específicos usando tus CSV.
- Puedo quitar la fila errónea que añadí a `clientes.csv` si prefieres no dejarla.
- Puedo cambiar `run.py` para evitar escribir Parquet (usar CSV en su lugar) si prefieres no depender de `pyarrow`.

Dime cuál de las opciones quieres que haga ahora y lo implemento.

