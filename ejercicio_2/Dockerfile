# Imagen base oficial de Python (Ligera)
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0

# Directorio de trabajo
WORKDIR /app

# Dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/ src/
COPY .env .

# --- CORRECCIÓN DE PERMISOS AQUÍ ---
# 1. Creamos el usuario
RUN useradd -m appuser

# 2. Creamos la carpeta data explícitamente para que exista
RUN mkdir -p /app/data

# 3. Le regalamos TODA la carpeta /app al usuario appuser
RUN chown -R appuser:appuser /app
# -----------------------------------

# Cambiamos al usuario seguro
USER appuser

# Puertos
EXPOSE 8000 8501

# Comando por defecto
CMD ["uvicorn", "src.api:app_api", "--host", "0.0.0.0", "--port", "8000"]