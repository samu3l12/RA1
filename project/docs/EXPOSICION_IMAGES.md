EXPOSICIÓN — Preparación de imágenes (OPCIÓN A)

Objetivo: generar imágenes `expo_*.png` a partir de las tablas para insertarlas directamente en las diapositivas.

Directorio de salida: `project/output/expo/`

Archivos que se generarán:
- `expo_1_ventas.png` (head de ventas)
- `expo_2_productos.png` (head de productos)
- `expo_3_clientes.png` (head de clientes)
- `expo_4_trace.png` (df con trazabilidad - head)
- `expo_5_quarantine.png` (ejemplos de quarantine)
- `expo_6_clean.png` (head de clean)
- `expo_7_kpis.png` (fragmento de vista analítica)

Notas:
- Las tablas se limitan a 6 filas por imagen para legibilidad.
- Uso recomendado: generación desde el entorno virtual que contiene pandas y matplotlib.

Script sugerido: `project/tools/generate_expo_images.py`
- El script lee los CSVs, crea DataFrames de ejemplo y exporta imágenes PNG con formato legible.
- A continuación incluyo el contenido del script; puedes ejecutarlo con:

```bash
py -3 project/tools/generate_expo_images.py
```

Contenido del script (`project/tools/generate_expo_images.py`):

```python
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

OUT = Path('project') / 'output' / 'expo'
OUT.mkdir(parents=True, exist_ok=True)

def df_to_png(df, path, title=None):
    # Simplificado: renderiza una tabla con matplotlib
    fig, ax = plt.subplots(figsize=(8, 0.6 + 0.4*len(df)))
    ax.axis('off')
    if title:
        ax.set_title(title, fontsize=12, pad=12)
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.2)
    plt.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

# Lecturas (ajusta si tus CSVs tienen otras rutas)
ventas = pd.read_csv('project/data/drops/ventas.csv', dtype=str).head(6)
productos = pd.read_csv('project/data/productos.csv', dtype=str).head(6)
clientes = pd.read_csv('project/data/clientes.csv', dtype=str).head(6)

# Ejemplos derivados (trace/quarantine/clean) - intenta cargar si existen en output
try:
    df_trace = pd.read_csv('project/output/expo/df_trace_head.csv', dtype=str)
except Exception:
    df_trace = ventas.copy()

try:
    quarantine = pd.read_csv('project/output/quality/ventas_quarantine.csv', dtype=str).head(6)
except Exception:
    quarantine = pd.DataFrame(columns=ventas.columns)

try:
    clean = pd.read_parquet('project/output/parquet/clean_ventas.parquet').head(6)
except Exception:
    clean = ventas.copy()

# Exportar imágenes
df_to_png(ventas, OUT / 'expo_1_ventas.png', title='Ventas (head)')
df_to_png(productos, OUT / 'expo_2_productos.png', title='Productos (head)')
df_to_png(clientes, OUT / 'expo_3_clientes.png', title='Clientes (head)')
df_to_png(df_trace.head(6), OUT / 'expo_4_trace.png', title='Trazabilidad (head)')
if not quarantine.empty:
    df_to_png(quarantine.head(6), OUT / 'expo_5_quarantine.png', title='Quarantine (ejemplos)')
else:
    # Exportar una tabla vacía con mensaje
    df_to_png(pd.DataFrame([['No hay filas en quarantine']]), OUT / 'expo_5_quarantine.png', title='Quarantine (vacío)')

df_to_png(clean.head(6), OUT / 'expo_6_clean.png', title='Clean (head)')

# KPIs: ejemplo simple (agrupar por id_producto)
kpi = clean.copy()
if not kpi.empty:
    kpi_group = kpi.groupby('id_producto', as_index=False).agg({'importe':'sum','unidades':'sum'})
    kpi_group['ticket_medio'] = (kpi_group['importe'].astype(float)/kpi_group['unidades'].astype(float)).round(2)
    df_to_png(kpi_group.head(6), OUT / 'expo_7_kpis.png', title='KPIs (ejemplo)')
else:
    df_to_png(pd.DataFrame([['No hay datos para KPIs']]), OUT / 'expo_7_kpis.png', title='KPIs (vacío)')

print('Imágenes generadas en', OUT)
```

---

Si quieres que ejecute el script aquí (en el workspace) y genere las imágenes, doy el paso y las creo; en caso contrario te doy el script y lo ejecutas localmente. Si ejecutamos aquí, sólo asegúrate de que las dependencias (pandas, matplotlib) están instaladas en el entorno.

Fecha: 2025-11-10

