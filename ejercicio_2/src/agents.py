import os
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver 
from pydantic import BaseModel, Field
from sqlmodel import Session

# Importaciones internas
from src.config import settings
from src.state import TriviaState
from src.models import engine, QuestionLog, update_session_score

# --- 1. Configuración del LLM ---
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.8, # Subimos un poco la temperatura para más variedad
    project=settings.PROJECT_ID,
    location=settings.REGION
)

# --- 2. Estructuras de Salida ---
class QuestionSchema(BaseModel):
    question: str = Field(description="La pregunta de trivia.")
    answer: str = Field(description="La respuesta correcta breve y concisa.")

class EvaluationSchema(BaseModel):
    is_correct: bool = Field(description="True si la respuesta es conceptualmente correcta.")
    feedback: str = Field(description="Explicación educativa sin revelar el score numérico.")
    points: int = Field(description="10 puntos si es correcta, 0 si no.")

# --- 3. Definición de Nodos ---

def generate_question_node(state: TriviaState):
    """Agente 1: Genera una pregunta con personalidad y MEMORIA."""
    topic = state.get("topic", "General")
    
    # --- FIX REPETICIÓN: Extraer preguntas anteriores del historial ---
    # Buscamos en los mensajes previos textos que empiecen con "🤖 Host:"
    previous_questions = [
        msg.replace("🤖 Host: ", "") 
        for msg in state.get("messages", []) 
        if isinstance(msg, str) and "Host:" in msg
    ]
    history_context = f"PREGUNTAS YA HECHAS (¡PROHIBIDO REPETIRLAS!): {previous_questions}" if previous_questions else ""
    # ---------------------------------------------------------------

    meli_context = ""
    if topic == "MeLi Expert":
        meli_context = """
        CONTEXTO MERCADO LIBRE:
        - Fundador: Marcos Galperin (1999, garaje en Saavedra).
        - Ecosistema: Mercado Pago, Mercado Envíos (Full), Mercado Shops, Mercado Crédito.
        - Hitos: Cotiza en NASDAQ (MELI), es la empresa más valiosa de Latam.
        - Cultura: "Beta continuo", "Emprender tomando riesgos", logo del codo a codo en pandemia.
        - Colores: Amarillo (#FFE600) y Azul oscuro.
        """

    prompt = f"""
    Eres el anfitrión carismático de un show de trivia llamado "MeLi Arcade".
    Tu tono es energético, breve y divertido.
    
    El tema elegido es: {topic}.
    {meli_context}
    
    {history_context}

    INSTRUCCIONES:
    1. Genera una pregunta NUEVA y diferente a las anteriores.
    2. Si es videojuegos, NO preguntes siempre de Mario. Varía (Zelda, Pacman, Doom, Minecraft, etc).
    3. Curiosidades y Fun Facts. No datos académicos.
    4. Respuesta corta (3-4 palabras).

    Genera la pregunta y la respuesta correcta.
    """
    
    structured_llm = llm.with_structured_output(QuestionSchema)
    response = structured_llm.invoke(prompt)
    
    return {
        "current_question": response.question,
        "current_answer": response.answer,
        "messages": [f"🤖 Host: {response.question}"]
    }

def evaluate_answer_node(state: TriviaState):
    """Agente 2: Evalúa la respuesta."""
    user_input = state["user_answer"]
    correct_ans = state["current_answer"]
    question = state["current_question"]
    session_id = state["session_id"] 
    
    prompt = f"""
    Pregunta: {question}
    Correcta: {correct_ans}
    Usuario: {user_input}
    Evalúa si es correcta y da feedback educativo sin decir puntos.
    """
    
    structured_llm = llm.with_structured_output(EvaluationSchema)
    eval_result = structured_llm.invoke(prompt)
    
    with Session(engine) as session:
        log = QuestionLog(
            session_id=session_id,
            question_text=question,
            correct_answer=correct_ans,
            user_answer=user_input,
            is_correct=eval_result.is_correct,
            feedback=eval_result.feedback,
            score_awarded=eval_result.points
        )
        session.add(log)
        session.commit()
    
    update_session_score(session_id, eval_result.points)
    
    next_count = state["question_count"] + 1
    is_game_over = next_count >= settings.MAX_QUESTIONS
    
    return {
        "score": state["score"] + eval_result.points,
        "last_feedback": eval_result.feedback,
        "question_count": next_count,
        "game_over": is_game_over
    }

# --- 4. Lógica Condicional ---
def check_game_over(state: TriviaState):
    if state["game_over"]:
        return "end_game"
    return "continue"

# --- 5. Construcción del Grafo ---
workflow = StateGraph(TriviaState)
workflow.add_node("quiz_master", generate_question_node)
workflow.add_node("judge", evaluate_answer_node)
workflow.set_entry_point("quiz_master")
workflow.add_edge("quiz_master", "judge")
workflow.add_conditional_edges(
    "judge",
    check_game_over,
    {
        "continue": "quiz_master",
        "end_game": END
    }
)

# --- 6. Compilación ---
memory = MemorySaver() 
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["judge"] 
)