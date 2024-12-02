# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requisitos y lo instala
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de tu aplicación
COPY . .

# Expone el puerto en el que correrá Flask
EXPOSE 5000

# Comando para iniciar el servidor
CMD ["python", "servidor.py"]
