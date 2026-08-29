#!/usr/bin/env python
"""
Script para descargar y configurar archivos estáticos (Bootstrap, jQuery, etc)
Ejecutar: python setup_static_files.py
"""

import os
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
VENDOR_DIR = STATIC_DIR / 'vendor'

# Crear directorios
BOOTSTRAP_DIR = VENDOR_DIR / 'bootstrap'
BOOTSTRAP_DIR.mkdir(parents=True, exist_ok=True)

print("Descargando archivos estáticos...")

# URLs de CDN
BOOTSTRAP_CSS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
BOOTSTRAP_JS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"

# Crear carpetas css y js
(BOOTSTRAP_DIR / 'css').mkdir(exist_ok=True)
(BOOTSTRAP_DIR / 'js').mkdir(exist_ok=True)

files_to_download = [
    (BOOTSTRAP_CSS, BOOTSTRAP_DIR / 'css' / 'bootstrap.min.css'),
    (BOOTSTRAP_JS, BOOTSTRAP_DIR / 'js' / 'bootstrap.bundle.min.js'),
]

for url, filepath in files_to_download:
    try:
        print(f"Descargando: {url}")
        urllib.request.urlretrieve(url, filepath)
        print(f"✓ Guardado en: {filepath}")
    except Exception as e:
        print(f"✗ Error descargando {url}: {e}")
        print(f"  Intenta descargar manualmente desde: {url}")

print("\n✓ Configuración completada.")
print("\nAhora ejecuta:")
print("  python manage.py collectstatic --noinput")
