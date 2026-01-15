# Imagen base oficial de Python (Ligera)
FROM python:3.11-slim

# Variables de entorno para optimizar Python en Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Esto asegura que Streamlit y FastAPI escuchen en todas las interfaces dentro del container
    HOST=0.0.0.0

# Directorio de trabajo
WORKDIR /app

# Instalamos dependencias de sistema (gcc suele ser necesario para algunas libs de python)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiamos requirements e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente y el .env (Para la prueba técnica se incluye, en prod real se inyecta)
COPY src/ src/
COPY .env .

# Creamos usuario no-root por seguridad
RUN useradd -m appuser
USER appuser

# Exponemos puertos (8000 para API, 8501 para Streamlit)
EXPOSE 8000 8501

# El comando por defecto (se sobreescribe en el docker-compose)
CMD ["uvicorn", "src.api:app_api", "--host", "0.0.0.0", "--port", "8000"]