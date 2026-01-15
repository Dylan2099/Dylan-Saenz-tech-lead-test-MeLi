import operator
from typing import Annotated, List, TypedDict

class TriviaState(TypedDict):
    """
    Define la estructura completa del estado del juego que fluye a través del grafo.
    
    Attributes:
        messages (List[str]): Historial de conversación (Append-only).
        question_count (int): Contador actual de preguntas realizadas.
        game_over (bool): Bandera para detener el ciclo de juego.
        session_id (int): ID de la base de datos para persistencia.
        player_name (str): Nombre del jugador actual.
        topic (str): Tema seleccionado para la trivia.
        current_question (str): Última pregunta generada por el Host.
        current_answer (str): Respuesta correcta de la última pregunta (Ground Truth).
        user_answer (str): Último input proporcionado por el usuario.
        score (int): Puntaje acumulado de la sesión.
        last_feedback (str): Última retroalimentación generada por el Juez.
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