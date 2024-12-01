# Imagen base
FROM python:3.9-slim

# Instalar dependencias del sistema y nginx
RUN apt-get update && \
    apt-get install -y curl gnupg unixodbc-dev gcc nginx && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean

# Copiar configuración de Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Crear un directorio de trabajo y copiar los archivos del proyecto
WORKDIR /app
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 80 para Nginx
EXPOSE 80

# Comando para iniciar Nginx y el script de servidores
CMD service nginx start && python Iniciar_servidores.py
