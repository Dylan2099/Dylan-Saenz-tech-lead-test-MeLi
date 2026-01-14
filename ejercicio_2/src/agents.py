from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from sqlmodel import Session

# Importaciones internas
from ejercicio_2.src.config import settings
from ejercicio_2.src.state import TriviaState
from ejercicio_2.src.models import engine, QuestionLog

# --- 1. Configuración del LLM ---
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.7, # Creatividad media
    project=settings.PROJECT_ID,
    location=settings.REGION
)

# --- 2. Estructuras de Salida (JSON Schema) ---
# Esto garantiza que la IA no "alucine" formatos raros
class QuestionSchema(BaseModel):
    question: str = Field(description="La pregunta de trivia.")
    answer: str = Field(description="La respuesta correcta breve y concisa.")

class EvaluationSchema(BaseModel):
    is_correct: bool = Field(description="True si la respuesta es conceptualmente correcta.")
    feedback: str = Field(description="Explicación educativa sin revelar el score numérico.")
    points: int = Field(description="10 puntos si es correcta, 0 si no.")

# --- 3. Definición de Nodos (Funciones) ---

def generate_question_node(state: TriviaState):
    """Agente 1: Genera una pregunta basada en el tema."""
    
    # Instrucciones para el LLM
    prompt = f"""Eres un experto en trivias sobre: {settings.TRIVIA_TOPIC}.
    Genera una pregunta desafiante pero justa.
    Devuelve la pregunta y la respuesta correcta por separado.
    """
    
    # Invocamos al LLM forzando la estructura JSON
    structured_llm = llm.with_structured_output(QuestionSchema)
    response = structured_llm.invoke(prompt)
    
    # Actualizamos el estado 
    return {
        "current_question": response.question,
        "current_answer": response.answer,
        "messages": [f"🤖 Pregunta: {response.question}"]
    }

def evaluate_answer_node(state: TriviaState):
    """Agente 2: Compara la respuesta y guarda en BD."""
    
    user_input = state["user_answer"]
    correct_ans = state["current_answer"]
    question = state["current_question"]
    
    # Instrucciones para el Juez
    prompt = f"""
    Pregunta original: {question}
    Respuesta correcta oficial: {correct_ans}
    Respuesta del usuario: {user_input}
    
    Tarea:
    1. Evalúa si el usuario acertó (sé flexible con typos).
    2. Provee feedback educativo explicando por qué es (o no) correcta.
    3. NO menciones el puntaje numérico en el feedback.
    """
    
    structured_llm = llm.with_structured_output(EvaluationSchema)
    eval_result = structured_llm.invoke(prompt)
    
    # --- Persistencia (Guardar en DB) ---
    with Session(engine) as session:
        log = QuestionLog(
            question_text=question,
            correct_answer=correct_ans,
            user_answer=user_input,
            is_correct=eval_result.is_correct,
            feedback=eval_result.feedback,
            score_awarded=eval_result.points
        )
        session.add(log)
        session.commit()
    
    # Calculamos si el juego debe terminar
    next_count = state["question_count"] + 1
    is_game_over = next_count >= settings.MAX_QUESTIONS
    
    return {
        "score": state["score"] + eval_result.points,
        "last_feedback": eval_result.feedback,
        "question_count": next_count,
        "game_over": is_game_over,
        "messages": [f"👨‍⚖️ Juez: {eval_result.feedback}"]
    }

# --- 4. Construcción del Grafo (Workflow) ---

workflow = StateGraph(TriviaState)

# Añadimos los nodos
workflow.add_node("quiz_master", generate_question_node)
workflow.add_node("judge", evaluate_answer_node)

# Definimos el punto de entrada
workflow.set_entry_point("quiz_master")

# Definimos las conexiones
# Después de preguntar, vamos al FIN del turno (para esperar input del usuario)
workflow.add_edge("quiz_master", END) 

# Después de evaluar, decidimos si seguir o parar
def check_game_over(state: TriviaState):
    if state["game_over"]:
        return END
    return "quiz_master" # Bucle: Volver a preguntar

workflow.add_conditional_edges(
    "judge",
    check_game_over
)

# Compilamos la aplicación
app = workflow.compile()