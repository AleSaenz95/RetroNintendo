#!/usr/bin/env bash

# Actualiza los paquetes y agrega el repositorio de Microsoft
apt-get update && apt-get install -y curl apt-transport-https gnupg unixodbc-dev
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instala el driver ODBC 18
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Limpieza del entorno
apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala las dependencias de Python
pip install --no-cache-dir -r requirements.txt
