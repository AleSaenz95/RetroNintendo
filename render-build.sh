#!/usr/bin/env bash

# Actualiza el sistema y agrega repositorio de Microsoft
apt-get update && apt-get install -y curl apt-transport-https gnupg unixodbc-dev
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instala el driver ODBC
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Limpieza del entorno
apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python
pip install --no-cache-dir -r requirements.txt
