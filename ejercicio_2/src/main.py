import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.config import settings
from src.models import init_db, create_session, get_leaderboard
from src.agents import app 
from src.state import TriviaState 

console = Console()

def run_game():
    init_db()
    console.print(Panel(f"🚀 Iniciando Trivia Tech Lead\nTema: {settings.TRIVIA_TOPIC}", style="bold blue"))
    
    # --- PASO 0: Registro de Jugador ( Multi-participante) ---
    player_name = console.input("\n[bold green]Ingresa tu nombre para el Ranking > [/bold green]")
    session_id = create_session(player_name)
    
    # Configuración del Hilo con ID único basado en la sesión DB
    thread_config = {"configurable": {"thread_id": str(session_id)}}
    
    # Estado inicial con los datos del jugador
    initial_state: TriviaState = { 
        "messages": [], "question_count": 0, "score": 0, "game_over": False,
        "session_id": session_id, "player_name": player_name,
        "current_question": "", "current_answer": "", "user_answer": "", "last_feedback": ""
    }

    # Primer arranque
    app.invoke(initial_state, config=thread_config)
    
    # Bucle de interacción
    while True:
        current_state_snapshot = app.get_state(thread_config)
        state_values = current_state_snapshot.values
        
        if not state_values or state_values.get("game_over"):
            break

        # Mostrar Pregunta
        q = state_values.get("current_question")
        i = state_values.get("question_count", 0) + 1
        console.print(f"\n[bold yellow]Pregunta {i}/{settings.MAX_QUESTIONS}:[/bold yellow]")
        console.print(f"{q}")
        
        # Pedir Input
        user_input = console.input("\n[bold cyan]Tu respuesta > [/bold cyan]")
        
        # Reanudar
        app.update_state(thread_config, {"user_answer": user_input})
        result = app.invoke(None, config=thread_config)
        
        # Feedback
        feedback = result.get("last_feedback")
        if feedback:
            color = "green" if "Correct" in str(feedback) else "blue"
            console.print(f"\n[bold {color}]Feedback:[/bold {color}] {feedback}")
        
        if result.get("game_over"):
            break

    # --- REPORTE FINAL Y RANKING ---
    final_score = app.get_state(thread_config).values.get('score', 0)
    console.print(Panel(f"🏆 Juego Terminado, {player_name}!\nPuntaje Final: {final_score}", style="bold green"))
    
    console.print("\n[bold magenta]📊 LEADERBOARD - TOP JUGADORES[/bold magenta]")
    
    # Crear tabla bonita para el ranking
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="dim")
    table.add_column("Jugador")
    table.add_column("Puntaje", justify="right")
    table.add_column("Fecha", justify="right")

    top_players = get_leaderboard()
    for idx, player in enumerate(top_players, 1):
        is_current = " (Tú)" if player.id == session_id else ""
        style = "bold green" if player.id == session_id else "white"
        table.add_row(
            str(idx), 
            f"{player.player_name}{is_current}", 
            str(player.total_score),
            player.start_time.strftime("%Y-%m-%d %H:%M"),
            style=style
        )
    
    console.print(table)

if __name__ == "__main__":
    try:
        run_game()
    except Exception as e:
        console.print(f"\n[bold red]Error crítico:[/bold red] {e}")