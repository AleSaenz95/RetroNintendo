# Usa una imagen base de Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias y el driver ODBC 18
RUN apt-get update && \
    apt-get install -y curl apt-transport-https gnupg unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia los archivos de tu aplicación
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto para la aplicación
EXPOSE 5000

# Comando para correr la app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "servidor:app"]
