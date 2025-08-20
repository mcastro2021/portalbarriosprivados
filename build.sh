#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p uploads
mkdir -p logs

# Inicializar base de datos
python init_db.py
