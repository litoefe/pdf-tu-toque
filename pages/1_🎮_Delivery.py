import streamlit as st
import time
import random

st.set_page_config(page_title="¿Quién baja?", page_icon="🛵", layout="centered")

st.markdown("""
<style>
    .titulo-juego {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: 2px;
        margin-bottom: 0;
    }
    .subtitulo {
        text-align: center;
        font-size: 1rem;
        color: #888;
        margin-bottom: 2rem;
        letter-spacing: 4px;
        text-transform: uppercase;
    }
    .nombre-turno {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 1rem 0;
    }
    .subtexto {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }
    .semaforo-wrap {
        text-align: center;
        margin: 1.5rem 0;
    }
    .semaforo-box {
        display: inline-flex;
        gap: 14px;
        background: #111;
        border-radius: 14px;
        padding: 1.2rem 1.8rem;
        border: 3px solid #2a2a2a;
    }
    .luz {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: 3px solid #1a0000;
    }
    .luz-on {
        background: radial-gradient(circle at 35% 30%, #ff7777, #bb0000);
        box-shadow: 0 0 18px 7px #ff000077, 0 0 36px 14px #ff000022;
        border-color: #660000;
    }
    .luz-off {
        background: radial-gradient(circle at 35% 30%, #2a1010, #150000);
        border-color: #330000;
    }
    .arranca-text {
        text-align: center;
        font-size: 4.5rem;
        font-weight: 900;
        color: #00ff88;
        text-shadow: 0 0 25px #00ff8899;
        letter-spacing: 3px;
        margin: 1rem 0;
    }
    .tiempo-ok {
        text-align: center;
        font-size: 4rem;
        font-weight: 900;
        font-family: monospace;
    }
    .false-start-box {
        background: #1a0000;
        border: 2px solid #ff4444;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    .perdedor-box {
        background: linear-gradient(135deg, #150000, #200000);
        border: 3px solid #ff4444;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    .ranking-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 1rem;
        margin: 0.3rem 0;
        background: #111;
        border-radius: 8px;
        border-left: 4px solid #333;
    }
    .r-gold   { border-left-color: #FFD700; }
    .r-silver { border-left-color: #C0C0C0; }
    .r-bronze { border-left-color: #CD7F32; }
    .stButton > button { width: 100%; font-size: 1.1rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ── Session state ────────────────────────────────────────────────
defaults = {
    "fase": "registro",   # registro | turno | animacion | señal | resultado | final
    "jugadores": [],
    "tiempos": {},         # {nombre: ms}
    "jugador_actual": 0,
    "t_señal": 0.0,
    "false_start": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def ir_a(fase):
    st.session_state.fase = fase
    st.rerun()


def reset_game():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()


def semaforo_html(n_encendidas, apagado=False):
    luces = ""
    for i in range(5):
        if apagado or i >= n_encendidas:
            luces += '<div class="luz luz-off"></div>'
        else:
            luces += '<div class="luz luz-on"></div>'
    return f'<div class="semaforo-wrap"><div class="semaforo-box">{luces}</div></div>'


fase = st.session_state.fase


# ════════════════════════════════════════════════════════════════
# REGISTRO
# ════════════════════════════════════════════════════════════════
if fase == "registro":
    st.markdown('<div class="titulo-juego">🛵 ¿QUIÉN BAJA?</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Gran Premio del Delivery</div>', unsafe_allow_html=True)
    st.markdown(semaforo_html(0), unsafe_allow_html=True)
    st.markdown("---")

    n = st.number_input("¿Cuántos pilotos largan?", min_value=2, max_value=6, value=4, step=1)

    cols = st.columns(2)
    nombres = []
    for i in range(int(n)):
        with cols[i % 2]:
            nombre = st.text_input(f"Piloto {i + 1}", key=f"n{i}", placeholder=f"Nombre {i + 1}")
            nombres.append(nombre.strip())

    st.markdown("")
    if st.button("🏁  ¡Que larguen!", type="primary"):
        if not all(nombres):
            st.error("Completá todos los nombres antes de largar.")
        elif len(set(nombres)) < len(nombres):
            st.error("Hay nombres repetidos. Cada piloto necesita un nombre único.")
        else:
            st.session_state.jugadores = nombres
            st.session_state.tiempos = {}
            st.session_state.jugador_actual = 0
            ir_a("turno")


# ════════════════════════════════════════════════════════════════
# TURNO  –  pantalla de grilla del piloto actual
# ════════════════════════════════════════════════════════════════
elif fase == "turno":
    nombre = st.session_state.jugadores[st.session_state.jugador_actual]
    idx = st.session_state.jugador_actual
    total = len(st.session_state.jugadores)

    st.markdown(f'<div class="subtexto">Turno {idx + 1} de {total}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nombre-turno">🪖 {nombre}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtexto">Esperá la señal — ¡No arranques antes!</div>', unsafe_allow_html=True)
    st.markdown(semaforo_html(0), unsafe_allow_html=True)
    st.markdown("")

    if st.button("🚦  Entrar a la grilla", type="primary"):
        st.session_state.false_start = False
        ir_a("animacion")


# ════════════════════════════════════════════════════════════════
# ANIMACION  –  semáforo F1 (luces que se encienden + pausa random)
# El jugador puede presionar "TOQUE" → false start
# ════════════════════════════════════════════════════════════════
elif fase == "animacion":
    nombre = st.session_state.jugadores[st.session_state.jugador_actual]
    st.markdown(f'<div class="nombre-turno">🪖 {nombre}</div>', unsafe_allow_html=True)

    semaforo_slot = st.empty()
    semaforo_slot.markdown(semaforo_html(0), unsafe_allow_html=True)

    toque_slot = st.empty()

    # Las 5 luces se encienden de a una
    for i in range(1, 6):
        semaforo_slot.markdown(semaforo_html(i), unsafe_allow_html=True)
        time.sleep(0.75)

    # Pausa final aleatoria con las 5 luces encendidas (tensión máxima)
    time.sleep(random.uniform(0.5, 2.0))

    # ¡Señal! → guardamos el timestamp y pasamos a fase "señal"
    st.session_state.t_señal = time.time()
    ir_a("señal")


# ════════════════════════════════════════════════════════════════
# SEÑAL  –  ¡ARRANCÁ! – el jugador presiona TOQUE
# ════════════════════════════════════════════════════════════════
elif fase == "señal":
    nombre = st.session_state.jugadores[st.session_state.jugador_actual]
    st.markdown(f'<div class="nombre-turno">🪖 {nombre}</div>', unsafe_allow_html=True)
    st.markdown(semaforo_html(0, apagado=True), unsafe_allow_html=True)
    st.markdown('<div class="arranca-text">¡ ARRANCÁ !</div>', unsafe_allow_html=True)
    st.markdown("")

    if st.button("🛵  ¡ T O Q U E !", type="primary"):
        ms = int((time.time() - st.session_state.t_señal) * 1000)
        st.session_state.tiempos[nombre] = ms
        ir_a("resultado")


# ════════════════════════════════════════════════════════════════
# RESULTADO DEL TURNO
# ════════════════════════════════════════════════════════════════
elif fase == "resultado":
    nombre = st.session_state.jugadores[st.session_state.jugador_actual]
    tiempo = st.session_state.tiempos[nombre]
    jugaron = list(st.session_state.tiempos.keys())

    st.markdown(f'<div class="nombre-turno">{nombre}</div>', unsafe_allow_html=True)
    st.markdown("")

    if st.session_state.false_start:
        st.markdown("""
        <div class="false-start-box">
            <div style="font-size:2rem">⛔</div>
            <div style="font-size:1.5rem; font-weight:800; color:#ff4444">FALSE START</div>
            <div style="color:#ff8888; margin-top:0.3rem">Penalización: +2000 ms</div>
        </div>""", unsafe_allow_html=True)
    else:
        if tiempo < 250:
            color, comentario = "#00ff88", "🔥 ¡Reflejos de piloto de F1!"
        elif tiempo < 400:
            color, comentario = "#88ff44", "✅ Buen tiempo"
        elif tiempo < 650:
            color, comentario = "#ffcc00", "😬 Tiempo regular..."
        else:
            color, comentario = "#ff6644", "🐢 Ese estuvo leeento..."

        st.markdown(
            f'<div class="tiempo-ok" style="color:{color}">⚡ {tiempo} ms</div>',
            unsafe_allow_html=True
        )
        st.markdown(f'<div class="subtexto">{comentario}</div>', unsafe_allow_html=True)

    # Ranking parcial (sólo si ya jugaron 2+)
    if len(jugaron) > 1:
        st.markdown("---")
        st.markdown("**Parcial**")
        medallas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣"]
        parcial = sorted(st.session_state.tiempos.items(), key=lambda x: x[1])
        for i, (j, t) in enumerate(parcial):
            marca = " ← vos" if j == nombre else ""
            st.markdown(f"{medallas[i]} **{j}** — {t} ms{marca}")

    st.markdown("")
    siguiente = st.session_state.jugador_actual + 1
    es_ultimo = siguiente >= len(st.session_state.jugadores)

    etiqueta = "🏁  Ver resultados finales" if es_ultimo else "Siguiente piloto  →"
    if st.button(etiqueta, type="primary"):
        if es_ultimo:
            ir_a("final")
        else:
            st.session_state.jugador_actual = siguiente
            st.session_state.false_start = False
            ir_a("turno")


# ════════════════════════════════════════════════════════════════
# RESULTADOS FINALES
# ════════════════════════════════════════════════════════════════
elif fase == "final":
    st.markdown('<div class="titulo-juego">🏆 RESULTADOS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Gran Premio del Delivery</div>', unsafe_allow_html=True)
    st.markdown("")

    ranking = sorted(st.session_state.tiempos.items(), key=lambda x: x[1])
    medallas  = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣"]
    clases_r  = ["r-gold", "r-silver", "r-bronze", "", "", ""]

    for i, (nombre, tiempo) in enumerate(ranking):
        clase = clases_r[i] if i < len(clases_r) else ""
        st.markdown(f"""
        <div class="ranking-item {clase}">
            <span style="font-size:1.3rem">{medallas[i]}&nbsp; <strong>{nombre}</strong></span>
            <span style="font-family:monospace; font-size:1.2rem; color:#aaa">{tiempo}&nbsp;ms</span>
        </div>""", unsafe_allow_html=True)

    perdedor = ranking[-1][0]
    st.markdown(f"""
    <div class="perdedor-box">
        <div style="color:#ff6666; font-size:0.85rem; letter-spacing:3px; text-transform:uppercase">
            🛵 Le toca bajar
        </div>
        <div style="color:white; font-size:3rem; font-weight:900; margin:0.4rem 0">
            {perdedor}
        </div>
        <div style="color:#ff9999; font-size:1.1rem">
            📦 El delivery está esperando en la puerta
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("")
    if st.button("🔄  Jugar de nuevo", type="primary"):
        reset_game()
