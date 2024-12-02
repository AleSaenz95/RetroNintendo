# Imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY . /app

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto donde correrá la aplicación
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["python", "servidor.py"]
