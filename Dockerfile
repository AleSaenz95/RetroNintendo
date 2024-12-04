# Usa una imagen base más completa
FROM python:3.10-buster

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias y el driver ODBC
RUN apt-get update && \
    apt-get install -y curl apt-transport-https gnupg unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Copia los archivos de tu aplicación
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que corre la app
EXPOSE 5000

# Comando para correr el servidor Flask
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "servidor:app"]
