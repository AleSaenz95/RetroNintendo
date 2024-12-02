# Usa una imagen base oficial de Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu aplicación
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que corre la app
EXPOSE 5000

# Comando para correr el servidor Flask
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "servidor:app"]
