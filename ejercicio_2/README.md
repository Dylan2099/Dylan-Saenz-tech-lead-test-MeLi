# 🎮 MeLi Arcade: AI-Powered Trivia Agent

![App Preview](./assets/app_preview_v2.png)

> **🔴 Live Demo:** [Haz clic aquí para jugar](https://meli-frontend-856233821367.us-central1.run.app)

Este módulo implementa un sistema interactivo de trivia utilizando **Agentes de IA Generativa** orquestados con grafos de estado. La solución está diseñada bajo una arquitectura de microservicios desacoplada, separando la lógica de negocio (Backend) de la interfaz de usuario (Frontend).

## 🏗 Arquitectura del Sistema

El sistema consta de dos servicios contenerizados que se comunican vía HTTP:

1.  **Backend (Brain):** API REST construida con **FastAPI**.
    *   Orquestación: **LangGraph** (Stateful Multi-Agent).
    *   IA: **Vertex AI (Gemini 2.5 Flash)**.
    *   Persistencia: **SQLModel** (SQLite) para sesiones y ranking.
2.  **Frontend (Face):** Interfaz interactiva construida con **Streamlit**.
    *   Gamificación: Animaciones Lottie y sistema de feedback visual.
    *   Comunicación: Cliente HTTP que consume la API del backend.

---

## ⚙️ Configuración Previa (Crucial)

Antes de ejecutar, es necesario configurar las credenciales y variables de entorno.

1.  **Google Cloud Platform:**
    *   Asegúrate de tener un proyecto en GCP con la API de **Vertex AI** habilitada.
    *   Debes tener configurada la autenticación local (si corres en local) o montar las credenciales en Docker (si aplica).

2.  **Variables de Entorno (.env):**
    Crea un archivo llamado `.env` dentro de la carpeta `ejercicio_2/`. Copia el siguiente contenido y reemplaza con tus datos:

    ```env
    # ID de tu proyecto en Google Cloud
    PROJECT_ID=tu-id-de-proyecto-real
    
    # Región de despliegue (ej. us-central1)
    REGION=us-central1
    
    # Modelo a utilizar
    MODEL_NAME=gemini-2.5-flash
    
    # Configuración del Juego
    MAX_QUESTIONS=3
    TRIVIA_TOPIC="Google Cloud Platform"
    
    # Networking
    # - Docker/Cloud: API_URL=http://backend:8000 (o URL real)
    # - Local Python: API_URL=http://127.0.0.1:8000
    API_URL=http://backend:8000
    ```

---

## 🚀 Ejecución con Docker (Local)

La forma más sencilla de probar el sistema localmente es utilizando Docker Compose.

1.  Construye y levanta los servicios:
    ```bash
    cd ejercicio_2
    docker-compose up --build
    ```

2.  Accede a la aplicación:
    *   **Frontend (Juego):** [http://localhost:8501](http://localhost:8501)
    *   **Backend (Docs API):** [http://localhost:8000/docs](http://localhost:8000/docs)

> **Nota:** La base de datos SQLite persistirá en la carpeta `./data` de tu máquina local gracias al volumen configurado.

---

## ☁️ Despliegue en Google Cloud Run

Para llevar esta arquitectura a producción en un entorno Serverless:

### 1. Preparación
Asegúrate de tener `gcloud` CLI instalado y autenticado.
```bash
gcloud auth login
gcloud config set project TU_PROJECT_ID
```

### 2. Crear Repositorio de Artefactos
```bash
gcloud artifacts repositories create meli-repo --repository-format=docker --location=us-central1
```

### 3. Desplegar Backend (API)
```bash
# Construir imagen
gcloud builds submit --tag us-central1-docker.pkg.dev/TU_PROJECT_ID/meli-repo/backend:v1 .

# Desplegar servicio
gcloud run deploy meli-backend \
  --image us-central1-docker.pkg.dev/TU_PROJECT_ID/meli-repo/backend:v1 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars "PROJECT_ID=TU_PROJECT_ID,REGION=us-central1,MAX_QUESTIONS=3,TRIVIA_TOPIC=Google Cloud"
```
*Copia la URL generada (ej: `https://meli-backend-xyz.a.run.app`).*

### 4. Desplegar Frontend (UI)
```bash
# Construir imagen (reutilizamos el mismo Dockerfile inteligente)
gcloud builds submit --tag us-central1-docker.pkg.dev/TU_PROJECT_ID/meli-repo/frontend:v1 .

# Desplegar conectando con el Backend
gcloud run deploy meli-frontend \
  --image us-central1-docker.pkg.dev/TU_PROJECT_ID/meli-repo/frontend:v1 \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8501 \
  --set-env-vars "API_URL=TU_URL_DEL_BACKEND" \
  --command="streamlit" \
  --args="run,src/frontend.py,--server.port=8501,--server.address=0.0.0.0"
```

> **Consideración de Arquitectura:** En Cloud Run, el sistema de archivos es efímero. La base de datos SQLite se reiniciará con cada nuevo despliegue. Para persistencia real en producción, se recomienda conectar el servicio a **Google Cloud SQL**.

---

## 📂 Estructura de Archivos

```text
ejercicio_2/
├── src/
│   ├── agents.py      # Lógica de LangGraph (Nodos y Flujo)
│   ├── api.py         # Endpoints FastAPI
│   ├── frontend.py    # UI Streamlit
│   ├── models.py      # Esquema de Base de Datos (SQLModel)
│   ├── state.py       # Definición del Estado del Grafo
│   └── config.py      # Gestión de configuración
├── data/              # Almacenamiento persistente (SQLite)
├── Dockerfile         # Definición de imagen unificada
├── docker-compose.yml # Orquestación de servicios
└── requirements.txt   # Dependencias del proyecto
```

---
**Tech Stack:** Python 3.11, LangGraph, Vertex AI, FastAPI, Streamlit, Docker, Cloud Run.
