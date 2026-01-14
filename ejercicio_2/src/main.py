import sys
from rich.console import Console
from rich.panel import Panel

# Importaciones internas
from .config import settings
from .models import init_db
from .agents import app

# Inicializamos la consola bonita ( con Rich)
console = Console()

def run_game():
    """Bucle principal de ejecución del juego."""
    
    # 1. Inicializar BD
    init_db()
    
    console.print(Panel(f"🚀 Iniciando Trivia Tech Lead\nTema: {settings.TRIVIA_TOPIC}", style="bold blue"))
    
    # 2. Estado Inicial
    state = {
        "messages": [],
        "question_count": 0,
        "score": 0,
        "game_over": False,
        "current_question": "",
        "current_answer": "",
        "user_answer": "",
        "last_feedback": ""
    }
    
    # 3. Game Loop
    # El grafo empieza en 'quiz_master', genera pregunta y para.
    # se lee el input, actualizamos el estado y reanudamos en 'judge'.
    
    while not state["game_over"]:
        # --- Fase 1: Generar Pregunta ---
        # Ejecutamos el grafo hasta que se detenga (END después de quiz_master)
        for event in app.stream(state):
            #no se muestran logs pero podriamos añadir
            pass
            
        # Obtenemos el estado actualizado tras la ejecución
        # Para simplificar este script, llamamos a los nodos manualmente
        # Si usáramos app.invoke() completo, necesitaríamos `interrupt_before`.
        
        # A) Invocamos solo el Generador
        res_gen = app.nodes["quiz_master"](state)
        state.update(res_gen) # Actualizamos libreta
        
        # Mostrar Pregunta
        console.print(f"\n[bold yellow]Pregunta {state['question_count'] + 1}/{settings.MAX_QUESTIONS}:[/bold yellow]")
        console.print(f"{state['current_question']}")
        
        # --- Fase 2: Input del Usuario ---
        user_input = console.input("\n[bold cyan]Tu respuesta > [/bold cyan]")
        state["user_answer"] = user_input
        
        # --- Fase 3: Evaluar ---
        res_eval = app.nodes["judge"](state)
        state.update(res_eval)
        
        # Mostrar Feedback
        color = "green" if "True" in str(res_eval.get("score", 0) > state["score"] - 10) else "blue" # Simple visual
        console.print(f"\n[bold {color}]Feedback:[/bold {color}] {state['last_feedback']}")
        
    # Fin del juego
    console.print(Panel(f"🏆 Juego Terminado\nPuntaje Final: {state['score']}", style="bold green"))

if __name__ == "__main__":
    try:
        run_game()
    except KeyboardInterrupt:
        console.print("\n👋 Juego cancelado.")
    except Exception as e:
        console.print(f"\n[bold red]Error crítico:[/bold red] {e}")