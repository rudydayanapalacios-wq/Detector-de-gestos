FROM python:3.11-slim

WORKDIR /app

# Librerías nativas necesarias para MediaPipe y OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libegl1 \
    libgles2 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del backend
COPY . .

# Exponer el puerto y ejecutar la aplicación FastAPI
EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]