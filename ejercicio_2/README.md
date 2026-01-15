# 🎮 MeLi Arcade: AI-Powered Trivia Agent

Este módulo implementa un sistema interactivo de trivia utilizando **Agentes de IA Generativa** orquestados con grafos de estado. La solución está diseñada bajo una arquitectura de microservicios desacoplada, separando la lógica de negocio (Backend) de la interfaz de usuario (Frontend).

## 🏗 Arquitectura del Sistema

El sistema consta de dos servicios contenerizados que se comunican vía HTTP:

1.  **Backend (Brain):** API REST construida con **FastAPI**.
    *   Orquestación: **LangGraph** (Stateful Multi-Agent).
    *   IA: **Vertex AI (Gemini 1.5 Flash)**.
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
    MODEL_NAME=gemini-1.5-flash-001
    
    # Configuración del Juego
    MAX_QUESTIONS=3
    TRIVIA_TOPIC="Google Cloud Platform"
    
    # Networking (Para Docker, dejar así. Para local, usar http://127.0.0.1:8000)
    API_URL=http://backend:8000
    ```

---

## 🚀 Ejecución con Docker (Recomendado)

La forma más sencilla de probar el sistema es utilizando Docker Compose, que orquesta ambos servicios y la red interna.

1.  Asegúrate de estar en la carpeta `ejercicio_2`:
    ```bash
    cd ejercicio_2
    ```

2.  Construye y levanta los servicios:
    ```bash
    docker-compose up --build
    ```

3.  Accede a la aplicación:
    *   **Frontend (Juego):** [http://localhost:8501](http://localhost:8501)
    *   **Backend (Docs API):** [http://localhost:8000/docs](http://localhost:8000/docs)

> **Nota:** La base de datos SQLite persistirá en la carpeta `./data` de tu máquina local gracias al volumen configurado en docker-compose.

---

## 🐍 Ejecución Manual (Local Python)

Si prefieres ejecutar sin Docker para desarrollo o depuración:

1.  **Crear entorno virtual e instalar dependencias:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: .\venv\Scripts\Activate
    pip install -r requirements.txt
    ```

2.  **Levantar el Backend (Terminal 1):**
    ```bash
    uvicorn src.api:app_api --reload --port 8000
    ```

3.  **Levantar el Frontend (Terminal 2):**
    *Nota: En local, asegúrate de que API_URL en tu .env sea http://127.0.0.1:8000*
    ```bash
    streamlit run src/frontend.py
    ```

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

## ✅ Endpoints Principales

- `POST /start_game`: Inicializa sesión y grafo de LangGraph.
- `POST /submit_answer`: Inyecta input humano en el grafo pausado y avanza el estado.
- `GET /leaderboard`: Consulta analítica de mejores puntajes.

---
**Tech Stack:** Python 3.11, LangGraph, Vertex AI, FastAPI, Streamlit, Docker.


