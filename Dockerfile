# Usa una imagen base de Python
FROM python:3.9-slim

# Instala las dependencias de sistema necesarias para pyodbc
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    libodbc1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requisitos y lo instala
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de tu aplicación
COPY . .

# Configurar las variables de entorno para la base de datos
ENV DRIVER="{SQL Server}"
ENV SERVER="tiusr3pl.cuc-carrera-ti.ac.cr"
ENV DATABASE="tiusr3pl_RetroNintendo"
ENV UID="tiusr3pl66"
ENV PWD="LpsLt5Awx&nb8$b2"

# Expone el puerto en el que correrá Flask
EXPOSE 5000

# Comando para iniciar el script de múltiples servidores
CMD ["python", "Iniciar_servidores.py"]
