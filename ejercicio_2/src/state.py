import operator
from typing import Annotated, List, TypedDict

class TriviaState(TypedDict):
    """
    Define la estructura de datos que viaja a través del grafo.
    """
    # Historial de mensajes (Chat)
    # los nuevos mensajes se suman a la lista, no la reemplazan
    messages: Annotated[List[str], operator.add] 
    
    # Control del flujo del juego
    question_count: int
    game_over: bool

    #datos de la sesión
    session_id: int 
    player_name: str
    topic: str  

    # Datos de la ronda actual
    current_question: str
    current_answer: str       # Esto NO se muestra al usuario
    user_answer: str          # Lo que el humano escribe
    
    # Puntuación y Feedback
    score: int                # Score interno
    last_feedback: str        # Explicación educativa