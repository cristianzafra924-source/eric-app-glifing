import os
import time
import random
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, timedelta

from ejercicios_glifing import (
    ejercicio_silabas, ejercicio_palabra, ejercicio_dictado,
    ejercicio_discriminacion_letras, ejercicio_completar_silaba,
    ejercicio_frase, ejercicio_trabalenguas,
    get_ejercicio_aleatorio, verificar_respuesta,
    MENSAJES_CORRECTO, MENSAJES_INCORRECTO, MENSAJES_BIENVENIDA,
    tiempo_objetivo,
)
from progreso_glifing import (
    cargar_progreso, guardar_sesion, get_racha,
    get_aciertos_por_area, get_velocidad_serie,
    get_resumen_semanal, render_calendario_html,
    AREAS, AREA_NOMBRES, calcular_estrellas, get_db_status,
)

st.set_page_config(
    page_title="Super Eric – Método Glifing",
    page_icon="🦸",
    layout="centered",
)

# ── Estilos ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

.titulo {
    font-size: 2.4rem; font-weight: 900; text-align: center;
    background: linear-gradient(90deg, #FFD700, #FF8C00, #7F77DD);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-shadow: none; margin-bottom: 4px;
}
.subtitulo { text-align:center; color:#7F77DD; font-size:1rem; margin-bottom:12px; }

/* Tarjetas de ejercicio */
.pal-big {
    font-size: 3rem; font-weight: 900; color: #FFD700; text-align: center;
    letter-spacing: .12em; padding: 22px 16px;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 18px; border: 2px solid #7F77DD;
    margin: 10px 0; text-shadow: 0 0 20px rgba(255,215,0,.4);
}
.frase-card {
    font-size: 1.6rem; font-weight: 700; color: #fff; text-align: center;
    padding: 22px 20px; line-height: 1.6;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 18px; border: 2px solid #FFD700;
    margin: 10px 0;
}
.trabalenguas-card {
    font-size: 1.4rem; font-weight: 700; color: #FFD700; text-align: center;
    padding: 22px 20px; line-height: 1.6;
    background: linear-gradient(135deg, #2a1a2e, #1a0a2e);
    border-radius: 18px; border: 2px solid #FF8C00;
    margin: 10px 0; letter-spacing: .02em;
}
.sil-box {
    display: inline-block; font-size: 2rem; font-weight: 800; color: #1a1a2e;
    background: linear-gradient(135deg, #FFD700, #FF8C00);
    border-radius: 10px; padding: 8px 16px; margin: 4px;
    box-shadow: 0 4px 12px rgba(255,215,0,.3);
}

/* Feedback */
.ok  { color: #00FF88; font-size: 1.5rem; font-weight: 900; text-align: center;
       text-shadow: 0 0 20px #00FF88; padding: 8px; }
.err { color: #FF4444; font-size: 1.5rem; font-weight: 900; text-align: center;
       text-shadow: 0 0 20px #FF4444; padding: 8px; }

/* Mascota speech bubble */
.speech {
    background: rgba(127,119,221,.15); border: 1px solid #7F77DD;
    border-radius: 14px; padding: 10px 18px; margin: 8px auto;
    color: #FFD700; font-style: italic; font-size: 1rem;
    max-width: 420px; text-align: center;
}

/* Racha / puntos */
.racha-box {
    background: linear-gradient(135deg, #2a2000, #1a1000);
    border: 1px solid #FFD700; border-radius: 14px;
    padding: 10px 16px; text-align: center;
    font-size: 1rem; font-weight: 800; color: #FFD700;
}
.pts { font-size: 1.1rem; font-weight: 800; color: #7F77DD; }

/* Bonus */
.bonus {
    font-size: 1.2rem; font-weight: 900; color: #FFD700;
    text-align: center; text-shadow: 0 0 15px #FFD700;
    animation: pulse 0.5s ease-in-out 3;
}

@keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
@keyframes pulse  { 0%,100%{opacity:1} 50%{opacity:.5} }
</style>
""", unsafe_allow_html=True)

# ── Estado de sesión ──────────────────────────────────────────────────────────
_AREAS_INIT = {a: 0 for a in AREAS}
_defaults = {
    "puntos": 0, "total": 0,
    "ejercicio_actual": None, "respondido": False, "resultado": None,
    "dificultad": "fácil",
    "sesion_inicio":      None,
    "sesion_ej":          {a: 0 for a in AREAS},
    "sesion_ac":          {a: 0 for a in AREAS},
    "sesion_err":         {a: 0 for a in AREAS},
    "sesion_palabras":    0,
    "sesion_t_palabras":  0.0,
    "sesion_t_ej_inicio": None,
    "sesion_guardada":    False,
    "cal_year":           date.today().year,
    "cal_month":          date.today().month,
    "modo_timer":         False,
    "tiempo_ultimo_ej":   None,
    "bonus_obtenido":     False,
    "msg_heroe":          random.choice(MENSAJES_BIENVENIDA),
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v.copy() if isinstance(v, dict) else v

progreso = cargar_progreso()
racha    = get_racha(progreso)

# ── Mapeo tipo → área ─────────────────────────────────────────────────────────
TIPO_A_AREA = {
    "silaba":         "silabas",
    "palabra":        "palabras",
    "dictado":        "dictado",
    "discriminacion": "discriminacion",
    "completar":      "completar",
    "frase":          "frases",
    "trabalenguas":   "frases",
}

# ── Funciones de mascota y timer ──────────────────────────────────────────────
HEROE_IMG = "assets/heroe.png"

def mostrar_heroe(mensaje: str = "", size: int = 90):
    usa_img = os.path.exists(HEROE_IMG)
    if usa_img:
        cols = st.columns([1, 1, 1])
        with cols[1]:
            st.image(HEROE_IMG, width=size * 2)
    else:
        emoji_html = (
            f'<div style="font-size:{size}px;filter:drop-shadow(0 0 18px gold);'
            f'display:inline-block;animation:bounce 1.5s ease-in-out infinite">'
            f'🦸‍♂️</div><br>'
        )
        st.markdown(
            f'<div style="text-align:center">{emoji_html}</div>',
            unsafe_allow_html=True,
        )
    if mensaje:
        st.markdown(f'<div class="speech">💬 {mensaje}</div>', unsafe_allow_html=True)


def mostrar_heroe_sidebar(size: int = 60):
    usa_img = os.path.exists(HEROE_IMG)
    if usa_img:
        st.image(HEROE_IMG, width=size * 2)
    else:
        st.markdown(
            f'<div style="text-align:center;font-size:{size}px;'
            f'filter:drop-shadow(0 0 12px gold)">🦸‍♂️</div>',
            unsafe_allow_html=True,
        )


def mostrar_timer(segundos: int):
    components.html(f"""
<style>
.tb{{display:flex;align-items:center;gap:14px;
     background:linear-gradient(135deg,#0d0d1a,#1a1a2e);
     border-radius:14px;border:2px solid #7F77DD;padding:10px 18px}}
.tic{{font-size:2.8rem;font-weight:900;color:#FFD700;
      text-shadow:0 0 18px #FFD700;min-width:64px;text-align:center;
      font-family:'Segoe UI',sans-serif}}
.tbar{{flex:1;height:12px;background:#222;border-radius:6px;overflow:hidden}}
.tfill{{height:100%;width:100%;
        background:linear-gradient(90deg,#FF4444,#FFD700,#00CC66);
        border-radius:6px;transition:width 1s linear}}
.tlabel{{color:#7F77DD;font-size:.78rem;font-weight:700;white-space:nowrap}}
</style>
<div class="tb">
  <div><div class="tlabel">⏱ TIEMPO</div>
       <div class="tic" id="tc">{segundos}</div></div>
  <div style="flex:1"><div class="tbar"><div class="tfill" id="tf"></div></div></div>
</div>
<script>
(function(){{
  var total={segundos},left=total;
  var tc=document.getElementById('tc'),tf=document.getElementById('tf');
  var iv=setInterval(function(){{
    left=Math.max(0,left-1);
    tc.textContent=left;
    tf.style.width=(left/total*100)+'%';
    if(left<=5){{tc.style.color='#FF4444';tc.style.textShadow='0 0 18px #FF4444';}}
    if(left===0)clearInterval(iv);
  }},1000);
}})();
</script>""", height=78)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    mostrar_heroe_sidebar()
    st.markdown(
        '<div style="text-align:center;font-size:.95rem;font-weight:900;'
        'background:linear-gradient(90deg,#FFD700,#FF8C00);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent">'
        'SUPER ERIC</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.header("⚙️ Configuración")
    nombre = st.text_input("¿Cómo te llamas?", value="Eric")
    dificultad = st.selectbox("Nivel de dificultad", ["fácil", "medio", "difícil"])
    st.session_state.dificultad = dificultad
    tipo_ejercicio = st.selectbox(
        "Tipo de ejercicio",
        ["Aleatorio","Sílabas","Leer palabras","Dictado",
         "Discriminar letras","Completar sílaba","Frases","Trabalenguas"],
    )
    st.session_state.modo_timer = st.toggle("⏱ Modo cronometrado", value=st.session_state.modo_timer)
    st.markdown("---")
    st.markdown(f'<div class="pts">⭐ Sesión: {st.session_state.puntos}/{st.session_state.total}</div>', unsafe_allow_html=True)
    if racha > 0:
        st.markdown(f'<div class="racha-box">🔥 Racha: {racha} día{"s" if racha>1 else ""}</div>', unsafe_allow_html=True)
    st.markdown("")
    if st.button("🔄 Reiniciar puntuación"):
        st.session_state.puntos = 0
        st.session_state.total  = 0
        st.rerun()
    st.markdown("---")
    st.markdown("🟢 Nube activa" if get_db_status() else "🟡 Solo esta sesión")

# ── Cabecera ──────────────────────────────────────────────────────────────────
st.markdown('<div class="titulo">⚡ SUPER ERIC · Método Glifing ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">¡El superhéroe de la lectura!</div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_ej, tab_cal, tab_stats = st.tabs(["🦸 Ejercicios", "📅 Calendario", "📊 Estadísticas"])


# ── Funciones de sesión ───────────────────────────────────────────────────────
def nuevo_ejercicio():
    st.session_state.respondido       = False
    st.session_state.resultado        = None
    st.session_state.tiempo_ultimo_ej = None
    st.session_state.bonus_obtenido   = False
    st.session_state.sesion_t_ej_inicio = time.time()
    d = st.session_state.dificultad

    mapa = {
        "Sílabas":           lambda: ejercicio_silabas(),
        "Leer palabras":     lambda: ejercicio_palabra(d),
        "Dictado":           lambda: ejercicio_dictado(d),
        "Discriminar letras":lambda: ejercicio_discriminacion_letras(),
        "Completar sílaba":  lambda: ejercicio_completar_silaba(),
        "Frases":            lambda: ejercicio_frase(d),
        "Trabalenguas":      lambda: ejercicio_trabalenguas(d),
    }
    fn = mapa.get(tipo_ejercicio, lambda: get_ejercicio_aleatorio(d))
    st.session_state.ejercicio_actual = fn()


def registrar_respuesta(correcto: bool):
    if st.session_state.sesion_inicio is None:
        st.session_state.sesion_inicio = time.time()

    elapsed = time.time() - (st.session_state.sesion_t_ej_inicio or time.time())
    st.session_state.tiempo_ultimo_ej = round(elapsed, 1)

    ej   = st.session_state.ejercicio_actual
    area = TIPO_A_AREA.get(ej.get("tipo"), "silabas")
    st.session_state.sesion_ej[area] += 1
    st.session_state.total            += 1

    if correcto:
        st.session_state.sesion_ac[area] += 1
        st.session_state.puntos          += 1
        # Bonus por rapidez en modo cronometrado
        if st.session_state.modo_timer:
            lim = tiempo_objetivo(ej.get("tipo"), st.session_state.dificultad)
            if elapsed <= lim * 0.6:
                st.session_state.bonus_obtenido = True
    else:
        st.session_state.sesion_err[area] += 1

    if ej.get("tipo") == "palabra":
        st.session_state.sesion_palabras  += 1
        st.session_state.sesion_t_palabras += max(elapsed, 1)


def finalizar_sesion():
    if st.session_state.sesion_inicio is None:
        return
    dur_seg = time.time() - st.session_state.sesion_inicio
    dur_min = round(dur_seg / 60, 1)
    p, t    = st.session_state.sesion_palabras, st.session_state.sesion_t_palabras
    wpm     = round((p / t) * 60, 1) if p > 0 and t > 0 else 0.0
    total_ej = sum(st.session_state.sesion_ej.values())
    total_ac = sum(st.session_state.sesion_ac.values())
    pct      = round(total_ac / total_ej * 100 if total_ej else 0, 1)

    guardar_sesion({
        "fecha":                  date.today().isoformat(),
        "ejercicios_completados": dict(st.session_state.sesion_ej),
        "aciertos":               dict(st.session_state.sesion_ac),
        "errores":                dict(st.session_state.sesion_err),
        "velocidad_lectora":      wpm,
        "porcentaje_aciertos":    pct,
        "estrellas":              calcular_estrellas(pct),
        "duracion_minutos":       dur_min,
    })

    st.session_state.sesion_guardada = True
    for a in AREAS:
        st.session_state.sesion_ej[a]  = 0
        st.session_state.sesion_ac[a]  = 0
        st.session_state.sesion_err[a] = 0
    st.session_state.sesion_inicio     = None
    st.session_state.sesion_palabras   = 0
    st.session_state.sesion_t_palabras = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EJERCICIOS
# ══════════════════════════════════════════════════════════════════════════════
with tab_ej:
    if st.session_state.ejercicio_actual is None:
        nuevo_ejercicio()

    ej   = st.session_state.ejercicio_actual
    tipo = ej.get("tipo")

    # Alerta sesión guardada
    if st.session_state.sesion_guardada:
        st.success("✅ ¡Sesión guardada! Revisa tu Calendario para ver el progreso.")
        st.session_state.sesion_guardada = False

    # Mascota bienvenida (solo cuando no hay respuesta en curso)
    if not st.session_state.respondido:
        mostrar_heroe(st.session_state.msg_heroe, size=75)

    # Timer cronometrado
    if st.session_state.modo_timer and not st.session_state.respondido:
        seg = tiempo_objetivo(tipo, st.session_state.dificultad)
        mostrar_timer(seg)

    st.markdown(f"### {ej.get('pregunta','')}")
    respuesta = None

    # ── Mostrar ejercicio según tipo ──────────────────────────────────────────
    if tipo == "silaba":
        st.markdown(f'<div class="pal-big">{ej["objetivo"]}</div>', unsafe_allow_html=True)
        respuesta = st.radio("Elige la opción correcta:", ej["opciones"], key="r_sil")

    elif tipo == "palabra":
        sils = ej.get("silabas", [ej["objetivo"]])
        html = "".join(f'<span class="sil-box">{s}</span>' for s in sils)
        st.markdown(f'<div style="text-align:center;margin:10px 0">{html}</div>', unsafe_allow_html=True)
        respuesta = ej["objetivo"]

    elif tipo == "dictado":
        st.info("🔊 Tu profesor te dirá la palabra en voz alta.")
        respuesta = st.text_input("Escribe la palabra aquí:", key="r_dic").strip().lower()

    elif tipo == "discriminacion":
        st.markdown(f'<div class="pal-big">{ej["objetivo"]}</div>', unsafe_allow_html=True)
        respuesta = st.radio("¿Qué letra es?", ej["opciones"], key="r_dis")

    elif tipo == "completar":
        st.markdown(f'<div class="pal-big">{ej["palabra_con_hueco"]}</div>', unsafe_allow_html=True)
        respuesta = st.radio("Elige la sílaba correcta:", ej["opciones"], key="r_com")

    elif tipo == "frase":
        st.markdown(f'<div class="frase-card">{ej["objetivo"]}</div>', unsafe_allow_html=True)
        respuesta = ej["objetivo"]

    elif tipo == "trabalenguas":
        st.markdown(f'<div class="trabalenguas-card">🌀 {ej["objetivo"]}</div>', unsafe_allow_html=True)
        respuesta = ej["objetivo"]

    # ── Botones ───────────────────────────────────────────────────────────────
    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.respondido:
            es_lectura = tipo in ("palabra","frase","trabalenguas")
            label      = "✅ ¡Ya lo leí!" if es_lectura else "✅ Comprobar"
            if st.button(label, use_container_width=True, type="primary"):
                if es_lectura:
                    registrar_respuesta(True)
                    st.session_state.respondido = True
                    st.session_state.resultado  = True
                else:
                    correcto = str(respuesta).strip().lower() == ej["objetivo"].strip().lower()
                    registrar_respuesta(correcto)
                    st.session_state.respondido = True
                    st.session_state.resultado  = correcto
                st.session_state.msg_heroe = random.choice(
                    MENSAJES_CORRECTO if st.session_state.resultado else MENSAJES_INCORRECTO
                )
                st.rerun()

    with col2:
        if st.button("➡️ Siguiente", use_container_width=True):
            st.session_state.msg_heroe = random.choice(MENSAJES_BIENVENIDA)
            nuevo_ejercicio()
            st.rerun()

    # ── Resultado ─────────────────────────────────────────────────────────────
    if st.session_state.respondido and st.session_state.resultado is not None:
        mostrar_heroe(st.session_state.msg_heroe, size=85)

        if st.session_state.resultado:
            st.markdown('<div class="ok">🎉 ¡CORRECTO!</div>', unsafe_allow_html=True)
            if st.session_state.bonus_obtenido:
                st.markdown('<div class="bonus">⚡ ¡BONUS DE VELOCIDAD! +⭐</div>', unsafe_allow_html=True)
            st.balloons()
        else:
            st.markdown(
                f'<div class="err">❌ La respuesta era: <b>{ej["objetivo"]}</b></div>',
                unsafe_allow_html=True,
            )

        if st.session_state.tiempo_ultimo_ej is not None and st.session_state.modo_timer:
            st.caption(f"⏱ Tiempo: {st.session_state.tiempo_ultimo_ej}s")

    # ── Pie de sesión ─────────────────────────────────────────────────────────
    st.markdown("---")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        if st.session_state.sesion_inicio is not None:
            mins    = round((time.time() - st.session_state.sesion_inicio) / 60, 1)
            n_ej    = sum(st.session_state.sesion_ej.values())
            n_ac    = sum(st.session_state.sesion_ac.values())
            pct_ses = round(n_ac / n_ej * 100 if n_ej else 0)
            st.caption(f"⏱ {mins} min · {n_ej} ejercicios · {pct_ses}% aciertos")
    with col_b:
        if st.session_state.sesion_inicio is not None:
            if st.button("💾 Finalizar sesión", use_container_width=True):
                finalizar_sesion()
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CALENDARIO
# ══════════════════════════════════════════════════════════════════════════════
with tab_cal:
    MESES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    col_prev, col_mes, col_next = st.columns([1, 4, 1])
    with col_prev:
        if st.button("◀", use_container_width=True, key="cal_prev"):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12; st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with col_mes:
        st.markdown(
            f'<h4 style="text-align:center;margin:6px 0">'
            f'{MESES[st.session_state.cal_month]} {st.session_state.cal_year}</h4>',
            unsafe_allow_html=True,
        )
    with col_next:
        if st.button("▶", use_container_width=True, key="cal_next"):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1; st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    st.markdown(
        render_calendario_html(st.session_state.cal_year, st.session_state.cal_month, progreso),
        unsafe_allow_html=True,
    )

    st.markdown("")
    if racha > 0:
        st.markdown(
            f'<div class="racha-box">🔥 Racha: {racha} día{"s" if racha>1 else ""} seguido{"s" if racha>1 else ""}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("¡Practica hoy para iniciar tu racha de superhéroe!")

    st.markdown("---")
    st.subheader("📋 Detalle de sesión")
    fechas = sorted(progreso.keys(), reverse=True)

    if not fechas:
        mostrar_heroe("¡Completa tu primera sesión para ver tu historial!", size=60)
    else:
        hoy, ayer = date.today().isoformat(), (date.today() - timedelta(1)).isoformat()
        fmt  = lambda f: f"{f}  (hoy)" if f == hoy else (f"{f}  (ayer)" if f == ayer else f)
        fecha_sel = st.selectbox("Selecciona un día:", fechas, format_func=fmt)
        d = progreso[fecha_sel]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Aciertos",  f"{d.get('porcentaje_aciertos', 0):.1f}%")
        c2.metric("Estrellas", "⭐" * d.get("estrellas", 0))
        c3.metric("Duración",  f"{d.get('duracion_minutos', 0)} min")
        c4.metric("Velocidad", f"{d.get('velocidad_lectora', 0):.1f} wpm")

        st.markdown("**Aciertos por área:**")
        for area in AREAS:
            ac    = d.get("aciertos", {}).get(area, 0)
            total = d.get("ejercicios_completados", {}).get(area, 0)
            if total > 0:
                st.write(f"**{AREA_NOMBRES[area]}**: {ac}/{total}")
                st.progress(ac / total)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ESTADÍSTICAS
# ══════════════════════════════════════════════════════════════════════════════
with tab_stats:
    if not progreso:
        mostrar_heroe("¡Completa sesiones de ejercicios para ver tus estadísticas!", size=80)
    else:
        resumen = get_resumen_semanal(progreso)

        c1, c2, c3 = st.columns(3)
        c1.metric("🔥 Racha",             f"{racha} día{'s' if racha!=1 else ''}")
        c2.metric("📅 Días esta semana",   f"{resumen['dias_practicados']}/7")
        c3.metric("📖 Palabras esta sem.", resumen["total_palabras"])

        st.markdown("---")

        serie = get_velocidad_serie(progreso)
        if serie:
            st.subheader("📈 Velocidad lectora (palabras/min)")
            df_v = pd.DataFrame(serie, columns=["Fecha","WPM"]).set_index("Fecha")
            st.line_chart(df_v)

        st.subheader("📊 Aciertos por área — Esta semana vs. anterior")
        areas_act = resumen["areas_actual"]
        areas_ant = resumen["areas_anterior"]
        filas = []
        for area in AREAS:
            t_a = areas_act[area]["total"]; a_a = areas_act[area]["aciertos"]
            t_p = areas_ant[area]["total"]; a_p = areas_ant[area]["aciertos"]
            filas.append({
                "Área":            AREA_NOMBRES[area],
                "Esta semana %":   round(a_a/t_a*100 if t_a else 0, 1),
                "Semana anterior %": round(a_p/t_p*100 if t_p else 0, 1),
            })
        df_a = pd.DataFrame(filas).set_index("Área")
        if df_a[["Esta semana %","Semana anterior %"]].sum().sum() > 0:
            st.bar_chart(df_a)

        st.markdown("---")
        st.subheader("📅 Comparativa semanal")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Esta semana:**")
            for area in AREAS:
                t = areas_act[area]["total"]; a = areas_act[area]["aciertos"]
                if t > 0: st.write(f"• {AREA_NOMBRES[area]}: {a}/{t} ({round(a/t*100)}%)")
        with col2:
            st.markdown("**Semana anterior:**")
            for area in AREAS:
                t = areas_ant[area]["total"]; a = areas_ant[area]["aciertos"]
                if t > 0: st.write(f"• {AREA_NOMBRES[area]}: {a}/{t} ({round(a/t*100)}%)")

        st.markdown("---")
        st.subheader("🏆 Resumen semanal")
        if resumen["mejor_area"] != "—" or resumen["peor_area"] != "—":
            col1, col2 = st.columns(2)
            if resumen["mejor_area"] != "—":
                col1.success(f"✅ **Mejor área:** {resumen['mejor_area']}")
            if resumen["peor_area"] != "—":
                col2.warning(f"💪 **A reforzar:** {resumen['peor_area']}")

        if date.today().weekday() == 0 and resumen["dias_practicados"] == 0:
            st.info("🗓 ¡Es lunes! ¡Nueva semana, nuevos poderes de lectura!")

        st.markdown(f'<div class="speech" style="font-size:1.1rem;max-width:100%">{resumen["mensaje"]}</div>',
                    unsafe_allow_html=True)

# ── Pie ───────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Super Eric · Método Glifing · ¡El superhéroe de la lectura! 🦸")
