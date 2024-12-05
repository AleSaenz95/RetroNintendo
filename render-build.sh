#!/usr/bin/env bash

# Actualizar paquetes
apt-get update

# Instalar dependencias necesarias
apt-get install -y gnupg curl

# Agregar la clave GPG del repositorio de Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Agregar el repositorio de Microsoft para el ODBC Driver 17
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instalar el driver ODBC 17
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

# Verificar instalación del driver
echo "Verificando instalación del Driver ODBC 17:"
odbcinst -q -d

# Limpiar archivos innecesarios
apt-get clean
rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
pip install --no-cache-dir -r requirements.txt
