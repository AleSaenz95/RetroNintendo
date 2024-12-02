#!/bin/bash

# Migrar base de datos o cualquier configuración inicial
echo "Iniciando aplicación..."

# Ejecutar el servidor
exec gunicorn -b 0.0.0.0:5000 servidor:app
