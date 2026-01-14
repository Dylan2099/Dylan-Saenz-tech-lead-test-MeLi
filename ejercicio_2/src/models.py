from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session

# Importamos para saber dónde guardar el archivo db
from ejercicio_2.src.config import settings

# --- Definición de Tablas ---

class QuestionLog(SQLModel, table=True):
    """
    Tabla de auditoría: Guarda cada interacción individual.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    question_text: str
    correct_answer: str
    user_answer: str
    is_correct: bool
    feedback: str
    score_awarded: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- Configuración del Motor de BD ---

# Conexión a SQLite (archivo local)
sqlite_url = f"sqlite:///{settings.DB_NAME}"
engine = create_engine(sqlite_url)

def init_db():
    """Crea las tablas si no existen."""
    SQLModel.metadata.create_all(engine)