# Usa una imagen base completa para evitar problemas con dependencias mínimas
FROM python:3.10-slim

# Configura el entorno de trabajo
WORKDIR /app

# Instala el driver ODBC y dependencias necesarias
RUN apt-get update && \
    apt-get install -y curl apt-transport-https gnupg unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el código de la aplicación
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto de la app
EXPOSE 5000

# Comando para ejecutar la app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "servidor:app"]
