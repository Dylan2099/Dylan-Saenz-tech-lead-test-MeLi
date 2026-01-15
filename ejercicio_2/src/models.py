from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select, func, desc

from src.config import settings

# --- Tablas ---

class GameSession(SQLModel, table=True):
    """Representa una partida de un jugador."""
    id: Optional[int] = Field(default=None, primary_key=True)
    player_name: str
    total_score: int = 0
    start_time: datetime = Field(default_factory=datetime.utcnow)

class QuestionLog(SQLModel, table=True):
    """Detalle de cada pregunta dentro de una sesión."""
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="gamesession.id") # Relación con la sesión
    question_text: str
    correct_answer: str
    user_answer: str
    is_correct: bool
    feedback: str
    score_awarded: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- Motor DB ---
sqlite_url = f"sqlite:///{settings.DB_NAME}"
engine = create_engine(sqlite_url)

def init_db():
    SQLModel.metadata.create_all(engine)

# --- Funciones de Analítica ---

def create_session(player_name: str) -> int:
    """
    Inicializa una nueva sesión de juego en la base de datos.

    Args:
        player_name (str): El nombre o nickname del jugador.

    Returns:
        int: El ID único de la sesión creada (Primary Key).
    """
    with Session(engine) as session:
        game = GameSession(player_name=player_name)
        session.add(game)
        session.commit()
        session.refresh(game)
        return game.id

def update_session_score(session_id: int, points: int):
    """Suma puntos a la sesión actual."""
    with Session(engine) as session:
        game = session.get(GameSession, session_id)
        if game:
            game.total_score += points
            session.add(game)
            session.commit()

def get_leaderboard(top_n: int = 5):
    """
    Genera el reporte de ranking comparando el desempeño de los participantes.
    
    Cumple con el requisito de análisis de resultados y generación de reporte.
    Ordena las sesiones por puntaje total de forma descendente.

    Args:
        top_n (int, optional): Cantidad de jugadores a mostrar. Por defecto 5.

    Returns:
        List[GameSession]: Lista de objetos de sesión ordenados por puntaje.
    """
    with Session(engine) as session:
        # Query para obtener las mejores sesiones
        statement = select(GameSession).order_by(desc(GameSession.total_score)).limit(top_n)
        results = session.exec(statement).all()
        return results