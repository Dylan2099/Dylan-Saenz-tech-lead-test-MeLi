# IA Tech Lead Technical Test - Dylan N. Sáenz

Este repositorio contiene la solución a la prueba técnica para el rol de **AI Tech Lead**.
La solución se divide en dos componentes principales según lo solicitado.

## Estructura del Proyecto

### [Ejercicio 1: Arquitectura RAG](./ejercicio_1/)
Diseño de una arquitectura Cloud-Native en GCP para un sistema RAG empresarial escalable.
- **Enfoque:** Serverless, Asíncrono y Optimizado para Costos (FinOps).
- **Stack:** Vertex AI, Cloud Run, Document AI, Redis.

### [Ejercicio 2: Agente de Trivia Interactivo](./ejercicio_2/)
Implementación de un sistema Multi-Agente orquestado con **LangGraph** y **Vertex AI**.
- **Patrón:** State Machine (Grafo cíclico) para control estricto del flujo de juego.
- **Ingeniería:** 
  - Validación de datos con **Pydantic**.
  - Persistencia con **SQLModel**.
  - Seguridad mediante gestión de entorno (.env).
  - Estructura modular lista para CI/CD.

## Requisitos Previos
- Python 3.10+
- Cuenta de Google Cloud Platform (Vertex AI API habilitada)