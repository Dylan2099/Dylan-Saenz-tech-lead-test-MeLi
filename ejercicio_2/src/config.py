import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Definimos la ruta base del proyecto (ejercicio_2)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Aseguramos que la carpeta data exista
DATA_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    PROJECT_ID: str
    REGION: str = "us-central1"
    MODEL_NAME: str = "gemini-2.5-flash" #modelo rapido y barato ideal para juego
    MAX_QUESTIONS: int = 3
    TRIVIA_TOPIC: str = "Google Cloud Platform"
    
    # Ruta absoluta a la DB dentro de la carpeta data
    DB_NAME: str = str(DATA_DIR / "trivia_game.db")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()