#!/usr/bin/env bash

# Actualiza los paquetes del sistema
apt-get update && apt-get install -y curl apt-transport-https gnupg unixodbc-dev

# Agrega la clave y el repositorio de Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instala el driver ODBC para SQL Server
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Limpia el caché para reducir el tamaño
apt-get clean && rm -rf /var/lib/apt/lists/*

# Configura el archivo odbcinst.ini (si no está configurado automáticamente)
cat <<EOL > /etc/odbcinst.ini
[ODBC Driver 17 for SQL Server]
Description=Microsoft ODBC Driver 17 for SQL Server
Driver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.9.so.2.1
UsageCount=1
EOL

# Instala las dependencias de Python en un entorno virtual
pip install --no-cache-dir -r requirements.txt
