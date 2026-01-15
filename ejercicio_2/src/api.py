from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

# Importamos nuestro core
from src.agents import app
from src.models import init_db, create_session, get_leaderboard, GameSession
from src.state import TriviaState
from src.config import settings

# Inicializamos la DB al arrancar la API
init_db()

app_api = FastAPI(title="Trivia Tech Lead API", version="1.0")

# --- Modelos de Datos para la API (Request/Response) ---
class StartGameRequest(BaseModel):
    player_name: str
    topic: str

class ChatRequest(BaseModel):
    session_id: int
    user_answer: Optional[str] = None # Puede ser None si es el primer turno

class GameStateResponse(BaseModel):
    message: str            # Texto a mostrar en Unity (Pregunta o Feedback)
    is_question: bool       # Para que Unity sepa si mostrar input de texto
    game_over: bool
    score: int
    session_id: int

class LeaderboardEntry(BaseModel):
    player_name: str
    score: int
    date: str

# --- Endpoints ---

@app_api.post("/start_game", response_model=GameStateResponse)
def start_game(request: StartGameRequest):
    """Inicia una partida y devuelve la primera pregunta."""
    
    # 1. Crear sesión en DB
    session_id = create_session(request.player_name)
    
    # 2. Configurar hilo de LangGraph
    thread_config = {"configurable": {"thread_id": str(session_id)}}
    
    # 3. Estado Inicial
    initial_state: TriviaState = { 
        "messages": [], "question_count": 0, "score": 0, "game_over": False,
        "session_id": session_id, "player_name": request.player_name,
        "topic": request.topic,
        "current_question": "", "current_answer": "", "user_answer": "", "last_feedback": ""
    }
    
    # 4. Invocar primer paso (Generar Pregunta)
    # Ejecutamos hasta que se detenga esperando input
    output = app.invoke(initial_state, config=thread_config)
    
    return GameStateResponse(
        message=output["current_question"],
        is_question=True,
        game_over=False,
        score=0,
        session_id=session_id
    )

@app_api.post("/submit_answer", response_model=GameStateResponse)
def submit_answer(request: ChatRequest):
    """Recibe la respuesta del usuario, evalúa y (si no termina) genera la siguiente pregunta."""
    
    thread_config = {"configurable": {"thread_id": str(request.session_id)}}
    
    # 1. Inyectar respuesta del usuario al grafo pausado
    app.update_state(thread_config, {"user_answer": request.user_answer})
    
    # 2. Reanudar ejecución (Evaluar -> [Check Game Over] -> Generar Siguiente Pregunta)
    # LangGraph correrá hasta la próxima pausa (después de generar la siguiente pregunta) 
    # O hasta terminar si es Game Over.
    output = app.invoke(None, config=thread_config)
    
    # 3. Construir respuesta para Unity
    # Aquí hay un truco: LangGraph corrió "Evaluar" Y "Generar Siguiente".
    # Unity necesita ver primero el Feedback y luego la Pregunta.
    # Para simplificar, enviaremos el Feedback + La Siguiente Pregunta juntos,
    # o Unity tendrá que parsearlo.
    
    if output["game_over"]:
        return GameStateResponse(
            message=f"Juego Terminado. {output.get('last_feedback', '')}",
            is_question=False,
            game_over=True,
            score=output["score"],
            session_id=request.session_id
        )
    else:
        # Combinamos Feedback anterior + Nueva Pregunta
        full_text = f"Feedback: {output.get('last_feedback', '')}\n\nSiguiente Pregunta: {output['current_question']}"
        return GameStateResponse(
            message=full_text,
            is_question=True,
            game_over=False,
            score=output["score"],
            session_id=request.session_id
        )

@app_api.get("/leaderboard", response_model=List[LeaderboardEntry])
def leaderboard():
    """Devuelve el Top 5 para mostrar en Unity."""
    results = get_leaderboard()
    return [
        LeaderboardEntry(
            player_name=row.player_name, 
            score=row.total_score,
            date=row.start_time.strftime("%Y-%m-%d")
        ) for row in results
    ]

# Para correr: uvicorn src.api:app_api --reload