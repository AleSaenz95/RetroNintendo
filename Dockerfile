# Usa una imagen base oficial de Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema y el driver ODBC
RUN apt-get update && \
    apt-get install -y gnupg curl && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de la aplicación
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto para Flask
EXPOSE 5000

# Comando para ejecutar la app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "servidor:app"]
