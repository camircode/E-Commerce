FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ .

# Crear directorio de uploads
RUN mkdir -p /app/static/uploads

EXPOSE 5000

CMD ["python", "app.py"]
