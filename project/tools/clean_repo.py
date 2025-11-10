"""Limpia caches y archivos temporales del repositorio.
Uso: py -3 project\tools\clean_repo.py
"""
from pathlib import Path
import shutil
import os

ROOT = Path('.')
PATTERNS_FILES = ['*.pyc','*.pyo','*.pyd']
DIRS = ['__pycache__','.ipynb_checkpoints','.pytest_cache']

removed = []
for pattern in PATTERNS_FILES:
    for p in ROOT.rglob(pattern):
        try:
            p.unlink()
            removed.append(str(p))
        except Exception:
            pass

for d in DIRS:
    for p in ROOT.rglob(d):
        if p.is_dir():
            try:
                shutil.rmtree(p)
                removed.append(str(p))
            except Exception:
                pass

print('Limpieza completada. Elementos eliminados:', len(removed))

