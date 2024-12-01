#!/bin/bash
# Actualizar repositorios
apt-get update && apt-get install -y curl apt-transport-https unixodbc-dev

# Agregar repositorio de Microsoft para controladores ODBC
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instalar el controlador ODBC para SQL Server
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17
