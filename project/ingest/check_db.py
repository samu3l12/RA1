import sqlite3
from pathlib import Path
DB=Path('project')/'output'/'ut1.db'
print('DB exists', DB.exists(), DB)
if not DB.exists():
    raise SystemExit('DB not found')
con=sqlite3.connect(DB)
cur=con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables=[r[0] for r in cur.fetchall()]
print('tables:', tables)
for t in ['raw_ventas','clean_ventas','quarantine_ventas']:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(t, cur.fetchone()[0])
    except Exception as e:
        print('no table or error for', t, e)
# sample rows including importe
try:
    cur.execute('SELECT fecha,id_cliente,id_producto,unidades,precio_unitario,importe,_ingest_ts FROM clean_ventas LIMIT 5')
    for r in cur.fetchall():
        print('row:', r)
except Exception as e:
    print('error reading clean_ventas', e)
con.close()

