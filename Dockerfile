# Imagen base
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto
EXPOSE 5000

# Comando para correr la aplicación
CMD ["python", "RetroNintendo.py"]
