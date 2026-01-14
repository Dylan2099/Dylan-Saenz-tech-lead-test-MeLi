import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configuración centralizada del proyecto.
    Lee automáticamente las variables desde el archivo .env
    """
    # Configuración de Google Cloud
    PROJECT_ID: str
    REGION: str = "us-central1"
    
    # Configuración del Modelo
    # Usamos Flash porque es rápido y barato para tareas simples como trivia
    MODEL_NAME: str = "gemini-1.5-flash-001" 
    
    # Configuración del Juego
    MAX_QUESTIONS: int = 5
    TRIVIA_TOPIC: str = "Google Cloud Platform"
    
    # Base de Datos
    DB_NAME: str = "trivia_game.db"

    class Config:
        env_file = ".env"
        extra = "ignore" # Ignora variables extra en el .env si las hay

# Instanciamos la configuración para importarla desde otros archivos
settings = Settings()