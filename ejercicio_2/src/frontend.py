import streamlit as st
import requests
import pandas as pd
import time
import os
from streamlit_lottie import st_lottie

# --- CONFIGURACIÓN ---
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000") 
st.set_page_config(page_title="MeLi Arcade", page_icon="🎮", layout="centered")

# --- ASSETS (Animaciones Lottie) ---
LOTTIE_ROBOT = "https://lottie.host/5a67b409-8ecc-4638-b644-8d4885eb241d/6Q7L9Z1w0j.json" 
LOTTIE_WIN = "https://lottie.host/93332462-81c8-4720-94e4-722055653ca6/0j7Y6Z1w0j.json" 

def load_lottieurl(url: str):
    """Intenta descargar la animación, si falla no rompe la app."""
    try:
        r = requests.get(url, timeout=2)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_bot = load_lottieurl(LOTTIE_ROBOT)
lottie_win = load_lottieurl(LOTTIE_WIN)

# --- CSS INJECTION (JUICE VISUAL) ---
page_bg_css = """
<style>
/* Fondo animado Gradiente Oscuro + MeLi Yellow sutil */
div.stApp {
    background: linear-gradient(-45deg, #2d3277, #1a1a1a, #2D3277, #333333);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    color: white;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Títulos y fuentes */
h1 {
    font-family: 'Helvetica Neue', sans-serif;
    color: #FFE600; /* Amarillo MeLi */
    text-shadow: 2px 2px 4px #000000;
}

/* Botones personalizados */
div.stButton > button {
    background-color: #FFE600;
    color: #2D3277;
    font-weight: bold;
    border-radius: 12px;
    border: 2px solid #2D3277;
    padding: 10px 24px;
    transition: all 0.3s;
}

div.stButton > button:hover {
    transform: scale(1.05);
    background-color: #ffffff;
    border-color: #FFE600;
}

/* Input de Chat */
.stTextInput > div > div > input {
    background-color: #1a1a1a;
    color: #FFE600;
    border: 1px solid #FFE600;
    border-radius: 10px;
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

# --- LÓGICA DE ESTADO ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "score" not in st.session_state:
    st.session_state.score = 0
# Corrección Barra: Inicializamos contador de preguntas
if "q_count" not in st.session_state:
    st.session_state.q_count = 1

# --- FUNCIONES DE JUEGO ---
def start_game(name, topic):
    try:
        payload = {"player_name": name, "topic": topic}
        res = requests.post(f"{API_URL}/start_game", json=payload)
        if res.status_code == 200:
            data = res.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.game_over = False
            st.session_state.messages = []
            st.session_state.score = 0
            st.session_state.q_count = 1 # Reiniciar barra
            st.session_state.messages.append({"role": "assistant", "content": data["message"]})
            st.rerun()
    except Exception as e:
        st.error(f"Error conectando a la API: {e}")

def submit_answer(answer):
    try:
        payload = {"session_id": st.session_state.session_id, "user_answer": answer}
        
        # Guardar puntaje anterior para detectar acierto
        prev_score = st.session_state.score
        
        st.session_state.messages.append({"role": "user", "content": answer})
        
        with st.spinner("🤖 El Juez está deliberando..."):
            res = requests.post(f"{API_URL}/submit_answer", json=payload)
        
        if res.status_code == 200:
            data = res.json()
            st.session_state.score = data["score"]
            st.session_state.messages.append({"role": "assistant", "content": data["message"]})
            
            # --- AGREGADO: GLOBOS (CONFETI) ---
            if data["score"] > prev_score:
                st.balloons()
            # ----------------------------------

            # --- AGREGADO: AVANCE BARRA PROGRESO ---
            if not data["game_over"]:
                st.session_state.q_count += 1
            # ---------------------------------------
            
            if data["game_over"]:
                st.session_state.game_over = True
                if data["score"] >= 20: 
                    st.balloons() # Doble premio si gana con buen puntaje
                else:
                    st.snow()
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

# --- INTERFAZ PRINCIPAL ---

# Header con Logo (Texto estilizado)
col_h1, col_h2 = st.columns([1, 4])
with col_h1:
    if lottie_bot:
        st_lottie(lottie_bot, height=80, key="header_anim")
    else:
        st.markdown("# 🤖") 
with col_h2:
    st.title("MeLi Expert Arcade")

# --- SIDEBAR: RANKING ---
with st.sidebar:
    st.markdown("### 🏆 Hall of Fame")
    if st.button("🔄 Refrescar Ranking"):
        try:
            res = requests.get(f"{API_URL}/leaderboard")
            if res.status_code == 200:
                df = pd.DataFrame(res.json())
                st.dataframe(
                    df, 
                    hide_index=True,
                    column_config={
                        "player_name": "Jugador",
                        "score": st.column_config.ProgressColumn("Puntaje", min_value=0, max_value=50, format="%d pts"),
                        "date": "Fecha"
                    }
                )
                st.caption("Nota: El ranking se calcula basado en la precisión semántica de las respuestas y la dificultad acumulada.")
        except:
            st.warning("API Offline")

# --- PANTALLA 1: LOBBY (Selección de Tema) ---
if not st.session_state.session_id:
    st.markdown("### 👋 ¡Bienvenido, Joven Aprendiz!")
    st.markdown("Elige tu desafío para demostrar tu conocimiento.")
    
    name = st.text_input("Ingresa tu Nickname:", placeholder="Ej: CloudMaster99")
    
    st.markdown("---")
    st.markdown("#### Selecciona un Tema:")
    
    # Tarjetas de selección (Usando columnas)
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)
    
    topic = None
    
    # Definición de Temas con Emojis
    if col1.button("🟡 MeLi Expert", use_container_width=True): topic = "MeLi Expert"
    if col2.button("🍿 Cultura Pop", use_container_width=True): topic = "Cultura Pop y Cine"
    if col3.button("🎮 Videojuegos", use_container_width=True): topic = "Historia de Videojuegos"
    if col4.button("💻 Tech History", use_container_width=True): topic = "Historia de la Tecnología"
    if col5.button("🌍 Datos Curiosos", use_container_width=True): topic = "Curiosidades del Mundo"

    # --- AGREGADO: TEMA LIBRE ---
    st.markdown("---")
    with st.expander("✨ ¿No te gusta ninguno? ¡Elige tu propio tema!"):
        with st.form("custom_topic_form"):
            c_custom1, c_custom2 = st.columns([3, 1])
            custom_topic_input = c_custom1.text_input("Escribe cualquier tema:", placeholder="Ej: Harry Potter, Física Cuántica...")
            submitted = c_custom2.form_submit_button("¡Jugar Tema Libre!")
            
            if submitted and custom_topic_input:
                topic = custom_topic_input
    # ----------------------------

    if topic and name:
        with st.spinner(f"Cargando módulo: {topic}..."):
            start_game(name, topic)
    elif topic and not name:
        st.warning("¡Por favor escribe tu nombre antes de elegir tema!")

# --- PANTALLA 2: ARENA DE JUEGO ---
else:
    # Barra de Progreso Superior
    score_col, status_col = st.columns([1, 3])
    with score_col:
        # En lugar de "Puntaje", mostramos la "Ronda"
        st.metric("Ronda", f"#{st.session_state.q_count}")
    with status_col:
        # Corrección Barra: Usamos el contador de preguntas (q_count) en vez del score
        # Suponemos 3 preguntas (ajusta el 3.0 si cambiaste MAX_QUESTIONS en el env) 
        max_q = 3.0
        progreso = min(st.session_state.q_count / max_q, 1.0)
        st.progress(progreso, text=f"Nivel {st.session_state.q_count} de {int(max_q)}")

    st.markdown("---")

    # Área de Chat (Historial)
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    # Renderizado especial si es un feedback largo
                    st.markdown(msg["content"])
            else:
                with st.chat_message("user", avatar="👨‍💻"):
                    st.markdown(f"**{msg['content']}**")

    # Input Area
    if not st.session_state.game_over:
        answer = st.chat_input("Escribe tu respuesta aquí...")
        if answer:
            submit_answer(answer)
    else:
        st.success("🏁 ¡Partida Finalizada!")
        
        col_end1, col_end2 = st.columns(2)
        
        with col_end1:
            if lottie_win:
                st_lottie(lottie_win, height=200, key="win_anim")
            else:
                st.markdown("<h1 style='text-align: center; font-size: 100px;'>🏆</h1>", unsafe_allow_html=True)

        with col_end2:
            st.markdown(f"### Tu Score Final: {st.session_state.score}")
            st.markdown("Revisa el ranking en el menú lateral para ver si entraste al Top 5.")
            
            if st.button("🎮 Jugar de Nuevo", use_container_width=True):
                st.session_state.session_id = None
                st.session_state.game_over = False
                st.session_state.score = 0
                st.session_state.q_count = 1
                st.session_state.messages = []
                st.rerun()