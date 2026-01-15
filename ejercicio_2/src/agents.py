import os
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver # IMPORTANTE: Para recordar el estado
from pydantic import BaseModel, Field
from sqlmodel import Session

# Importaciones internas
from src.config import settings
from src.state import TriviaState
from src.models import engine, QuestionLog, update_session_score

# --- 1. Configuración del LLM ---
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.7,
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
    """Agente 1: Genera una pregunta."""
    prompt = f"""Eres un experto en trivias sobre: {settings.TRIVIA_TOPIC}.
    Genera una pregunta desafiante. Devuelve pregunta y respuesta por separado."""
    
    structured_llm = llm.with_structured_output(QuestionSchema)
    response = structured_llm.invoke(prompt)
    
    return {
        "current_question": response.question,
        "current_answer": response.answer,
        "messages": [f"🤖 Pregunta: {response.question}"]
    }

def evaluate_answer_node(state: TriviaState):
    """Agente 2: Evalúa la respuesta."""
    user_input = state["user_answer"]
    correct_ans = state["current_answer"]
    question = state["current_question"]
    session_id = state["session_id"] # Obtenemos el ID de la sesión actual
    
    prompt = f"""
    Pregunta: {question}
    Correcta: {correct_ans}
    Usuario: {user_input}
    Evalúa si es correcta y da feedback educativo sin decir puntos.
    """
    
    structured_llm = llm.with_structured_output(EvaluationSchema)
    eval_result = structured_llm.invoke(prompt)
    
    # 1. Guardar el Log detallado
    with Session(engine) as session:
        log = QuestionLog(
            session_id=session_id, # Vinculamos a la sesión
            question_text=question,
            correct_answer=correct_ans,
            user_answer=user_input,
            is_correct=eval_result.is_correct,
            feedback=eval_result.feedback,
            score_awarded=eval_result.points
        )
        session.add(log)
        session.commit()
    
    # 2. Actualizar el Score Global de la Sesión
    update_session_score(session_id, eval_result.points)
    
    next_count = state["question_count"] + 1
    is_game_over = next_count >= settings.MAX_QUESTIONS
    
    return {
        "score": state["score"] + eval_result.points,
        "last_feedback": eval_result.feedback,
        "question_count": next_count,
        "game_over": is_game_over
    }

# --- 4. Lógica Condicional (DEFINIDA ANTES DEL GRAFO) ---
def check_game_over(state: TriviaState):
    if state["game_over"]:
        return "end_game"
    return "continue"

# --- 5. Construcción del Grafo ---
workflow = StateGraph(TriviaState)

workflow.add_node("quiz_master", generate_question_node)
workflow.add_node("judge", evaluate_answer_node)

workflow.set_entry_point("quiz_master")

# Flujo: QuizMaster -> Judge (Pero pararemos antes de Judge con interrupt)
workflow.add_edge("quiz_master", "judge")

# Flujo Condicional después del Juez
workflow.add_conditional_edges(
    "judge",
    check_game_over,
    {
        "continue": "quiz_master",
        "end_game": END
    }
)

# --- 6. Compilación con Memoria ---
memory = MemorySaver() # Esto permite pausar y reanudar

app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["judge"] # Nos detenemos justo antes de evaluar para pedir input
)