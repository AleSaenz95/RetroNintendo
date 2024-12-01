# Imagen base
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (para SQL Server y otras librerías)
RUN apt-get update && \
    apt-get install -y curl gnupg unixodbc-dev gcc && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puertos necesarios
EXPOSE 5000 5001 5003 5004 5009 5011

# Comando para correr el script que inicia todos los servidores
CMD ["python", "Iniciar_servidores.py"]
