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

# Copia el archivo .env (opcional si lo estás manejando localmente)
COPY .env .env

# Expone el puerto principal (puedes ajustar si tienes un único puerto para iniciar_servidores.py)
EXPOSE 5000

# Comando para iniciar el script que levanta todos los servidores
CMD ["python", "iniciar_servidores.py"]
