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
    ejercicio_frase, ejercicio_trabalenguas, ejercicio_velocidad_bloque,
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
    page_title="Fluyo Kids",
    page_icon="🦸",
    layout="centered",
)

# ── Temas de color ────────────────────────────────────────────────────────────
TEMAS = {
    "🌑 Oscuro":  {"bg":"#1E1E1E","bg2":"#2D2D2D","prim":"#7F77DD","txt":"#FFFFFF","gold":"#FFD700"},
    "☀️ Claro":   {"bg":"#F0F2F6","bg2":"#FFFFFF", "prim":"#5A52C0","txt":"#1a1a2e","gold":"#B8860B"},
    "🟣 Galaxia": {"bg":"#06001A","bg2":"#120037", "prim":"#BB44FF","txt":"#FFFFFF","gold":"#FFD700"},
    "🌿 Selva":   {"bg":"#071A07","bg2":"#0D330D", "prim":"#27AE60","txt":"#FFFFFF","gold":"#F1C40F"},
    "🔥 Fuego":   {"bg":"#1A0700","bg2":"#330D00", "prim":"#FF5722","txt":"#FFFFFF","gold":"#FFD700"},
    "🎨 Personalizar": None,
}

# ── Estado de sesión ──────────────────────────────────────────────────────────
_defaults = {
    "puntos":0,"total":0,
    "ejercicio_actual":None,"respondido":False,"resultado":None,
    "dificultad":"fácil",
    "sesion_inicio":None,
    "sesion_ej":       {a:0 for a in AREAS},
    "sesion_ac":       {a:0 for a in AREAS},
    "sesion_err":      {a:0 for a in AREAS},
    "sesion_palabras":0,"sesion_t_palabras":0.0,
    "sesion_t_ej_inicio":None,
    "sesion_guardada":False,
    "cal_year":date.today().year,"cal_month":date.today().month,
    "modo_timer":False,
    "timer_iniciado":False,
    "tema_nombre":"🌑 Oscuro",
    "color_prim":"#7F77DD","color_bg":"#1E1E1E",
    "bonus_obtenido":False,"tiempo_ultimo_ej":None,
    "estilo_letra":"imprenta",
    "vel_bloque":None,"vel_bloques_hechos":0,"vel_wpms":[],
    "vel_ultimo_wpm":None,"vel_ultimo_seg":None,
    "msg_heroe":random.choice(MENSAJES_BIENVENIDA),
}
for k,v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v.copy() if isinstance(v,dict) else v

# ── Tema activo ───────────────────────────────────────────────────────────────
def get_tema() -> dict:
    nombre = st.session_state.get("tema_nombre","🌑 Oscuro")
    if nombre == "🎨 Personalizar":
        bg = st.session_state.get("color_bg","#1E1E1E")
        pr = st.session_state.get("color_prim","#7F77DD")
        return {"bg":bg,"bg2":bg,"prim":pr,"txt":"#FFFFFF","gold":"#FFD700"}
    return TEMAS.get(nombre, TEMAS["🌑 Oscuro"])

T = get_tema()

# ── CSS dinámico según tema ────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&family=Dancing+Script:wght@700;900&display=swap');
html,body,[class*="css"]{{font-family:'Nunito',sans-serif}}

/* Tema de fondo */
.stApp,[data-testid="stAppViewContainer"]{{background-color:{T['bg']} !important}}
[data-testid="stSidebar"]{{background-color:{T['bg2']} !important}}
[data-testid="stSidebar"]>div{{background-color:{T['bg2']} !important}}
[data-testid="stHeader"]{{background-color:{T['bg']} !important}}
.block-container{{background-color:{T['bg']} !important}}

/* Textos */
h1,h2,h3,h4,p,.stMarkdown,label,.stCaption{{color:{T['txt']} !important}}

/* Inputs */
.stTextInput>div>div>input{{background-color:{T['bg2']} !important;color:{T['txt']} !important;border-color:{T['prim']} !important}}
.stSelectbox>div>div{{background-color:{T['bg2']} !important;color:{T['txt']} !important}}

/* Botones primarios */
.stButton>button[kind="primary"]{{
    background:linear-gradient(135deg,{T['prim']},{T['gold']}) !important;
    color:white !important;border:none !important;
    font-weight:900 !important;border-radius:12px !important;
}}
.stButton>button{{border-color:{T['prim']} !important;color:{T['txt']} !important}}

/* Título */
.titulo{{
    font-size:2.4rem;font-weight:900;text-align:center;
    background:linear-gradient(90deg,{T['gold']},{T['prim']});
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    margin-bottom:4px
}}
.subtitulo{{text-align:center;color:{T['prim']};font-size:1rem;margin-bottom:12px}}

/* Tarjetas ejercicio */
.pal-big{{
    font-size:3rem;font-weight:900;color:{T['gold']};text-align:center;
    letter-spacing:.12em;padding:22px 16px;
    background:linear-gradient(135deg,{T['bg2']},{T['bg']});
    border-radius:18px;border:2px solid {T['prim']};
    margin:10px 0;text-shadow:0 0 20px rgba(255,215,0,.4)
}}
.frase-card{{
    font-size:1.6rem;font-weight:700;color:{T['txt']};text-align:center;
    padding:22px 20px;line-height:1.6;
    background:linear-gradient(135deg,{T['bg2']},{T['bg']});
    border-radius:18px;border:2px solid {T['gold']};margin:10px 0
}}
.trabalenguas-card{{
    font-size:1.4rem;font-weight:700;color:{T['gold']};text-align:center;
    padding:22px 20px;line-height:1.6;
    background:linear-gradient(135deg,{T['bg2']},{T['bg']});
    border-radius:18px;border:2px dashed {T['prim']};margin:10px 0
}}
.sil-box{{
    display:inline-block;font-size:2rem;font-weight:800;color:{T['bg']};
    background:linear-gradient(135deg,{T['gold']},{T['prim']});
    border-radius:10px;padding:8px 16px;margin:4px;
    box-shadow:0 4px 12px rgba(255,215,0,.3)
}}

/* Timer start button */
.timer-btn{{
    background:linear-gradient(135deg,#FF6B35,{T['gold']});
    border:none;border-radius:14px;padding:12px 28px;
    font-size:1.2rem;font-weight:900;color:white;
    cursor:pointer;width:100%;text-align:center;
    box-shadow:0 0 20px rgba(255,107,53,.4);
    animation:pulse 1.5s ease-in-out infinite
}}

/* Feedback */
.ok{{color:#00FF88;font-size:1.5rem;font-weight:900;text-align:center;
     text-shadow:0 0 20px #00FF88;padding:8px}}
.err{{color:#FF4444;font-size:1.5rem;font-weight:900;text-align:center;
      text-shadow:0 0 20px #FF4444;padding:8px}}
.bonus{{font-size:1.2rem;font-weight:900;color:{T['gold']};text-align:center;
        text-shadow:0 0 15px {T['gold']}}}
.speech{{
    background:rgba(127,119,221,.15);border:1px solid {T['prim']};
    border-radius:14px;padding:10px 18px;margin:8px auto;
    color:{T['gold']};font-style:italic;font-size:1rem;
    max-width:440px;text-align:center
}}
.racha-box{{
    background:linear-gradient(135deg,{T['bg2']},{T['bg']});
    border:1px solid {T['gold']};border-radius:14px;
    padding:10px 16px;text-align:center;
    font-size:1rem;font-weight:800;color:{T['gold']}
}}
.pts{{font-size:1.1rem;font-weight:800;color:{T['prim']}}}

/* Grid de velocidad */
.vel-grid{{
    display:grid;grid-template-columns:repeat(3,1fr);
    gap:10px;padding:18px;margin:10px 0;
    background:linear-gradient(135deg,{T['bg2']},{T['bg']});
    border-radius:18px;border:2px solid {T['prim']}
}}
.vel-word{{
    font-size:1.55rem;font-weight:900;color:{T['txt']};
    text-align:center;padding:10px 4px;border-radius:10px;
    background:rgba(127,119,221,.13);border:1px solid {T['prim']}
}}
.vel-stat{{
    text-align:center;font-size:1rem;font-weight:800;
    color:{T['gold']};margin:4px 0
}}

/* Estilos de letra */
.f-cursiva{{font-family:'Dancing Script',cursive !important;font-size:1.12em !important}}
.f-imprenta{{font-family:'Nunito',sans-serif !important}}
.f-mayuscula{{font-family:'Nunito',sans-serif !important;text-transform:uppercase !important;letter-spacing:.05em !important}}

/* Botón selector de letra */
.font-btn-label{{
    text-align:center;font-size:.72rem;font-weight:800;
    letter-spacing:.12em;color:{T['prim']};margin:6px 0 2px
}}

@keyframes bounce{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.6}}}}

/* Imagen héroe con fondo transparente */
[data-testid="stImage"] img{{
    filter:drop-shadow(0 0 22px rgba(255,215,0,.6));
}}

/* Sidebar — todo centrado */
[data-testid="stSidebar"] .stMarkdown{{text-align:center}}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown strong{{text-align:center;display:block}}
[data-testid="stSidebar"] [data-testid="stImage"]{{text-align:center !important}}
[data-testid="stSidebar"] [data-testid="stImage"] img{{margin:0 auto !important;display:block !important}}
[data-testid="stSidebar"] [data-testid="stRadio"]>div{{display:flex !important;flex-direction:column !important;align-items:center !important}}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"]{{display:flex !important;flex-direction:column !important;align-items:center !important}}
[data-testid="stSidebar"] [data-testid="stRadio"] label{{display:inline-flex !important;width:auto !important}}
[data-testid="stSidebar"] [data-testid="stRadio"] p{{text-align:left !important}}
[data-testid="stSidebar"] .stButton{{display:flex;justify-content:center}}
[data-testid="stSidebar"] .stButton>button{{margin:0 auto}}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stToggle label{{text-align:center;display:block;width:100%}}
[data-testid="stSidebar"] .stCaption{{text-align:center}}
</style>
""", unsafe_allow_html=True)

# ── Carga progreso ─────────────────────────────────────────────────────────────
progreso = cargar_progreso()
racha    = get_racha(progreso)

TIPO_A_AREA = {
    "silaba":"silabas","palabra":"palabras","dictado":"dictado",
    "discriminacion":"discriminacion","completar":"completar",
    "frase":"frases","trabalenguas":"frases",
}
HEROE_IMG = "assets/heroe.png"

# ── Mascota ────────────────────────────────────────────────────────────────────
def mostrar_heroe(mensaje:str="", size:int=90):
    usa_img = os.path.exists(HEROE_IMG)
    if usa_img:
        cols = st.columns([1,1,1])
        with cols[1]:
            st.image(HEROE_IMG, width=size*2)
    else:
        st.markdown(
            f'<div style="text-align:center;font-size:{size}px;'
            f'filter:drop-shadow(0 0 18px gold);'
            f'display:block;animation:bounce 1.5s ease-in-out infinite">🦸‍♂️</div>',
            unsafe_allow_html=True,
        )
    if mensaje:
        st.markdown(f'<div class="speech">💬 {mensaje}</div>', unsafe_allow_html=True)

def mostrar_heroe_sidebar():
    usa_img = os.path.exists(HEROE_IMG)
    if usa_img:
        _, col, _ = st.columns([1, 3, 1])
        with col:
            st.image(HEROE_IMG, use_container_width=True)
    else:
        st.markdown(
            '<div style="text-align:center;font-size:60px;'
            'filter:drop-shadow(0 0 12px gold)">🦸‍♂️</div>',
            unsafe_allow_html=True,
        )

# ── Cronómetro JavaScript ──────────────────────────────────────────────────────
def mostrar_timer(segundos_objetivo: int):
    # Calcula el tiempo restante real usando el reloj del servidor → sobrevive reruns
    t0 = st.session_state.get("sesion_t_ej_inicio") or time.time()
    elapsed     = time.time() - t0
    left_init   = max(0, segundos_objetivo - int(elapsed))
    pct_init    = round(left_init / segundos_objetivo * 100) if segundos_objetivo else 0
    color_init  = "#FF4444" if left_init <= 5 else T["gold"]

    components.html(f"""
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:transparent;overflow:hidden}}
.tb{{display:flex;align-items:center;gap:14px;
     background:linear-gradient(135deg,#0d0d1a,#1a1a2e);
     border-radius:14px;border:2px solid {T['prim']};
     padding:12px 18px;height:78px;width:100%}}
.left-col{{display:flex;flex-direction:column;align-items:center;min-width:70px}}
.tlabel{{color:{T['prim']};font-size:.78rem;font-weight:700;letter-spacing:.05em}}
.tic{{font-size:2.6rem;font-weight:900;line-height:1;
      text-shadow:0 0 18px {color_init};color:{color_init}}}
.right-col{{flex:1;display:flex;flex-direction:column;gap:4px}}
.tbar{{width:100%;height:14px;background:#333;border-radius:7px;overflow:hidden}}
.tfill{{height:100%;width:{pct_init}%;border-radius:7px;
        background:linear-gradient(90deg,#FF4444 0%,{T['gold']} 50%,#00CC66 100%);
        transition:width 1s linear}}
.tpct{{color:#888;font-size:.7rem;text-align:right}}
</style>
<div class="tb">
  <div class="left-col">
    <div class="tlabel">⏱ TIEMPO</div>
    <div class="tic" id="tc">{left_init}</div>
  </div>
  <div class="right-col">
    <div class="tbar"><div class="tfill" id="tf"></div></div>
    <div class="tpct" id="tp">{pct_init}%</div>
  </div>
</div>
<script>
(function(){{
  var total={segundos_objetivo}, left={left_init};
  var tc=document.getElementById('tc');
  var tf=document.getElementById('tf');
  var tp=document.getElementById('tp');
  function update(){{
    var pct=Math.round(left/total*100);
    tc.textContent=left;
    tf.style.width=pct+'%';
    tp.textContent=pct+'%';
    if(left<=5){{tc.style.color='#FF4444';tc.style.textShadow='0 0 18px #FF4444';}}
  }}
  update();
  if(left>0){{
    var iv=setInterval(function(){{
      left=Math.max(0,left-1);
      update();
      if(left===0)clearInterval(iv);
    }},1000);
  }}
}})();
</script>""", height=100)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    mostrar_heroe_sidebar()
    st.markdown(
        f'<div style="text-align:center;font-size:.95rem;font-weight:900;'
        f'background:linear-gradient(90deg,{T["gold"]},{T["prim"]});'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent">'
        f'SUPER ERIC</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Tema de color ──────────────────────────────────────────────────────────
    st.markdown("**🎨 Tema de color**")
    for _tnombre in TEMAS.keys():
        _sel = st.session_state.tema_nombre == _tnombre
        if st.button(
            f"⭐ {_tnombre}" if _sel else _tnombre,
            key=f"tema_btn_{_tnombre}",
            use_container_width=True,
            type="primary" if _sel else "secondary",
        ):
            st.session_state.tema_nombre = _tnombre
            st.rerun()

    if st.session_state.tema_nombre == "🎨 Personalizar":
        col1, col2 = st.columns(2)
        with col1:
            cp = st.color_picker("Principal", st.session_state.color_prim)
            if cp != st.session_state.color_prim:
                st.session_state.color_prim = cp; st.rerun()
        with col2:
            cb = st.color_picker("Fondo", st.session_state.color_bg)
            if cb != st.session_state.color_bg:
                st.session_state.color_bg = cb; st.rerun()

    st.markdown("---")
    st.markdown("**⚙️ Ejercicios**")
    nombre = st.text_input("¿Cómo te llamas?", value="Eric")
    dificultad = st.selectbox("Nivel", ["fácil","medio","difícil"])
    st.session_state.dificultad = dificultad
    tipo_ejercicio = st.selectbox(
        "Tipo de ejercicio",
        ["Aleatorio","Sílabas","Leer palabras","Dictado",
         "Discriminar letras","Completar sílaba","Frases","Trabalenguas",
         "⚡ Velocidad"],
    )
    st.session_state.modo_timer = st.toggle(
        "⏱ Activar cronómetro", value=st.session_state.modo_timer
    )
    st.markdown("---")
    st.markdown(f'<div class="pts">⭐ {st.session_state.puntos}/{st.session_state.total}</div>',
                unsafe_allow_html=True)
    if racha > 0:
        st.markdown(f'<div class="racha-box">🔥 Racha: {racha} día{"s" if racha>1 else ""}</div>',
                    unsafe_allow_html=True)
    st.markdown("")
    if st.button("🔄 Reiniciar"):
        st.session_state.puntos = 0; st.session_state.total = 0; st.rerun()
    st.markdown("---")
    st.markdown("🟢 Nube activa" if get_db_status() else "🟡 Solo esta sesión")

# ── Cabecera ───────────────────────────────────────────────────────────────────
st.markdown('<div class="titulo">⚡ Fluyo Kids ⚡</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitulo">¡El superhéroe de la lectura!</div>', unsafe_allow_html=True)

tab_ej, tab_cal, tab_stats = st.tabs(["🦸 Ejercicios","📅 Calendario","📊 Estadísticas"])

# ── Funciones sesión ───────────────────────────────────────────────────────────
def nuevo_ejercicio():
    st.session_state.respondido       = False
    st.session_state.resultado        = None
    st.session_state.tiempo_ultimo_ej = None
    st.session_state.bonus_obtenido   = False
    st.session_state.timer_iniciado   = False
    st.session_state.sesion_t_ej_inicio = None   # espera a que Eric pulse Iniciar
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

def registrar_respuesta(correcto:bool):
    if st.session_state.sesion_inicio is None:
        st.session_state.sesion_inicio = time.time()
    t0      = st.session_state.sesion_t_ej_inicio or time.time()
    elapsed = time.time() - t0
    st.session_state.tiempo_ultimo_ej = round(elapsed, 1)
    ej   = st.session_state.ejercicio_actual
    area = TIPO_A_AREA.get(ej.get("tipo"), "silabas")
    st.session_state.sesion_ej[area] += 1
    st.session_state.total            += 1
    if correcto:
        st.session_state.sesion_ac[area] += 1
        st.session_state.puntos          += 1
        if st.session_state.timer_iniciado:
            lim = tiempo_objetivo(ej.get("tipo"), st.session_state.dificultad)
            if elapsed <= lim * 0.6:
                st.session_state.bonus_obtenido = True
    else:
        st.session_state.sesion_err[area] += 1
    if ej.get("tipo") == "palabra":
        st.session_state.sesion_palabras  += 1
        st.session_state.sesion_t_palabras += max(elapsed, 1)

def finalizar_sesion():
    if st.session_state.sesion_inicio is None: return
    dur   = round((time.time()-st.session_state.sesion_inicio)/60, 1)
    p,t   = st.session_state.sesion_palabras, st.session_state.sesion_t_palabras
    wpm   = round((p/t)*60, 1) if p>0 and t>0 else 0.0
    n_ej  = sum(st.session_state.sesion_ej.values())
    n_ac  = sum(st.session_state.sesion_ac.values())
    pct   = round(n_ac/n_ej*100 if n_ej else 0, 1)
    guardar_sesion({
        "fecha":date.today().isoformat(),
        "ejercicios_completados":dict(st.session_state.sesion_ej),
        "aciertos":dict(st.session_state.sesion_ac),
        "errores":dict(st.session_state.sesion_err),
        "velocidad_lectora":wpm,"porcentaje_aciertos":pct,
        "estrellas":calcular_estrellas(pct),"duracion_minutos":dur,
    })
    st.session_state.sesion_guardada = True
    for a in AREAS:
        st.session_state.sesion_ej[a]=0
        st.session_state.sesion_ac[a]=0
        st.session_state.sesion_err[a]=0
    st.session_state.sesion_inicio=None
    st.session_state.sesion_palabras=0
    st.session_state.sesion_t_palabras=0.0

# ── Modo Velocidad ─────────────────────────────────────────────────────────────
def mostrar_modo_velocidad():
    d  = st.session_state.dificultad
    fc = f"f-{st.session_state.estilo_letra}"

    # Iniciar bloque si no hay uno
    if st.session_state.vel_bloque is None:
        st.session_state.vel_bloque          = ejercicio_velocidad_bloque(12, d)
        st.session_state.timer_iniciado      = False
        st.session_state.sesion_t_ej_inicio  = None if st.session_state.modo_timer else time.time()

    ej = st.session_state.vel_bloque

    st.markdown('<div class="titulo" style="font-size:1.6rem">⚡ VELOCIDAD LECTORA</div>',
                unsafe_allow_html=True)

    # Resultado del bloque anterior
    if st.session_state.vel_ultimo_wpm is not None:
        st.markdown(
            f'<div class="vel-stat">Bloque {st.session_state.vel_bloques_hechos} · '
            f'⚡ {st.session_state.vel_ultimo_wpm:.0f} pal/min · '
            f'⏱ {st.session_state.vel_ultimo_seg:.1f}s</div>',
            unsafe_allow_html=True,
        )
    if st.session_state.vel_bloques_hechos > 1:
        avg = sum(st.session_state.vel_wpms) / len(st.session_state.vel_wpms)
        st.markdown(f'<div class="vel-stat" style="font-size:.85rem;opacity:.75">'
                    f'Media: {avg:.0f} pal/min · {st.session_state.vel_bloques_hechos} bloques</div>',
                    unsafe_allow_html=True)

    # ── Cronómetro (igual que otros ejercicios) ────────────────────────────────
    if st.session_state.modo_timer:
        if not st.session_state.timer_iniciado:
            if st.button("⏱ ¡INICIAR TIEMPO!", use_container_width=True, key="btn_timer_vel"):
                st.session_state.timer_iniciado     = True
                st.session_state.sesion_t_ej_inicio = time.time()
                st.rerun()
        else:
            mostrar_timer(60)

    # Grid de palabras
    html = '<div class="vel-grid">'
    for p in ej["palabras"]:
        html += f'<div class="vel-word {fc}">{p}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    # Botón principal
    if st.button("⚡ ¡Ya lo leí! → Siguiente bloque",
                 use_container_width=True, type="primary"):
        t0      = st.session_state.sesion_t_ej_inicio or time.time()
        elapsed = max(time.time() - t0, 0.5)
        n       = ej["num_palabras"]
        wpm     = round(n / elapsed * 60, 1)

        st.session_state.vel_wpms.append(wpm)
        st.session_state.vel_bloques_hechos += 1
        st.session_state.vel_ultimo_wpm      = wpm
        st.session_state.vel_ultimo_seg      = round(elapsed, 1)

        # Acumula en estadísticas de sesión
        if st.session_state.sesion_inicio is None:
            st.session_state.sesion_inicio = time.time()
        st.session_state.sesion_ej["palabras"]  += n
        st.session_state.sesion_ac["palabras"]  += n
        st.session_state.sesion_palabras         += n
        st.session_state.sesion_t_palabras       += elapsed

        # Nuevo bloque — resetea timer
        st.session_state.vel_bloque          = None
        st.session_state.timer_iniciado      = False
        st.session_state.sesion_t_ej_inicio  = None
        st.rerun()

    st.markdown("---")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        if st.session_state.sesion_inicio is not None:
            mins = round((time.time() - st.session_state.sesion_inicio) / 60, 1)
            st.caption(f"⏱ {mins} min · {st.session_state.vel_bloques_hechos} bloques")
    with col_b:
        if st.session_state.sesion_inicio is not None:
            if st.button("💾 Finalizar sesión", use_container_width=True):
                st.session_state.vel_bloque = None
                st.session_state.vel_ultimo_wpm = None
                finalizar_sesion(); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EJERCICIOS
# ══════════════════════════════════════════════════════════════════════════════
with tab_ej:
    if tipo_ejercicio == "⚡ Velocidad":
        mostrar_modo_velocidad()
    else:
        if st.session_state.ejercicio_actual is None:
            nuevo_ejercicio()
        ej   = st.session_state.ejercicio_actual
        tipo = ej.get("tipo")

        if st.session_state.sesion_guardada:
            st.success("✅ ¡Sesión guardada! Mira el Calendario para ver tu progreso.")
            st.session_state.sesion_guardada = False

        # Mascota
        if not st.session_state.respondido:
            mostrar_heroe(st.session_state.msg_heroe, size=75)

        # ── Cronómetro activable por Eric ──────────────────────────────────────
        if st.session_state.modo_timer and not st.session_state.respondido:
            if not st.session_state.timer_iniciado:
                st.markdown("")
                if st.button("⏱ ¡INICIAR TIEMPO!", use_container_width=True, key="btn_timer"):
                    st.session_state.timer_iniciado = True
                    st.session_state.sesion_t_ej_inicio = time.time()
                    st.rerun()
            else:
                seg = tiempo_objetivo(tipo, st.session_state.dificultad)
                mostrar_timer(seg)

        # ── Selector de tipo de letra ───────────────────────────────────────────
        st.markdown('<div class="font-btn-label">🌟 TIPO DE LETRA</div>', unsafe_allow_html=True)
        _estilos = [("imprenta","📝 Imprenta"),("cursiva","✏️ Cursiva"),("mayuscula","🔠 MAYÚSC.")]
        _fc1, _fc2, _fc3 = st.columns(3)
        for _col, (_key, _lbl) in zip([_fc1, _fc2, _fc3], _estilos):
            with _col:
                _sel = st.session_state.estilo_letra == _key
                if st.button(
                    f"⭐ {_lbl}" if _sel else _lbl,
                    key=f"font_{_key}", use_container_width=True,
                    type="primary" if _sel else "secondary",
                ):
                    st.session_state.estilo_letra = _key
                    st.rerun()
        fc = f"f-{st.session_state.estilo_letra}"
        st.markdown("")

        # ── Ejercicio ──────────────────────────────────────────────────────────
        st.markdown(f"### {ej.get('pregunta','')}")
        respuesta = None

        if tipo == "silaba":
            st.markdown(f'<div class="pal-big {fc}">{ej["objetivo"]}</div>', unsafe_allow_html=True)
            respuesta = st.radio("Elige la opción correcta:", ej["opciones"], key="r_sil")
        elif tipo == "palabra":
            sils = ej.get("silabas",[ej["objetivo"]])
            html = "".join(f'<span class="sil-box {fc}">{s}</span>' for s in sils)
            st.markdown(f'<div style="text-align:center;margin:10px 0">{html}</div>', unsafe_allow_html=True)
            respuesta = ej["objetivo"]
        elif tipo == "dictado":
            st.info("🔊 Tu profesor te dirá la palabra en voz alta.")
            respuesta = st.text_input("Escribe la palabra aquí:", key="r_dic").strip().lower()
        elif tipo == "discriminacion":
            st.markdown(f'<div class="pal-big {fc}">{ej["objetivo"]}</div>', unsafe_allow_html=True)
            respuesta = st.radio("¿Qué letra es?", ej["opciones"], key="r_dis")
        elif tipo == "completar":
            st.markdown(f'<div class="pal-big {fc}">{ej["palabra_con_hueco"]}</div>', unsafe_allow_html=True)
            respuesta = st.radio("Elige la sílaba correcta:", ej["opciones"], key="r_com")
        elif tipo == "frase":
            st.markdown(f'<div class="frase-card {fc}">{ej["objetivo"]}</div>', unsafe_allow_html=True)
            respuesta = ej["objetivo"]
        elif tipo == "trabalenguas":
            st.markdown(f'<div class="trabalenguas-card {fc}">🌀 {ej["objetivo"]}</div>', unsafe_allow_html=True)
            respuesta = ej["objetivo"]

        # ── Botones ────────────────────────────────────────────────────────────
        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.respondido:
                es_lectura = tipo in ("palabra","frase","trabalenguas")
                label = "✅ ¡Ya lo leí!" if es_lectura else "✅ Comprobar"
                if st.button(label, use_container_width=True, type="primary"):
                    if not st.session_state.sesion_t_ej_inicio:
                        st.session_state.sesion_t_ej_inicio = time.time()
                    correcto = True if es_lectura else (
                        str(respuesta).strip().lower() == ej["objetivo"].strip().lower()
                    )
                    registrar_respuesta(correcto)
                    st.session_state.respondido = True
                    st.session_state.resultado  = correcto
                    st.session_state.msg_heroe  = random.choice(
                        MENSAJES_CORRECTO if correcto else MENSAJES_INCORRECTO
                    )
                    st.rerun()
        with col2:
            if st.button("➡️ Siguiente", use_container_width=True):
                st.session_state.msg_heroe = random.choice(MENSAJES_BIENVENIDA)
                nuevo_ejercicio(); st.rerun()

        # ── Resultado ──────────────────────────────────────────────────────────
        if st.session_state.respondido and st.session_state.resultado is not None:
            mostrar_heroe(st.session_state.msg_heroe, size=85)
            if st.session_state.resultado:
                st.markdown('<div class="ok">🎉 ¡CORRECTO!</div>', unsafe_allow_html=True)
                if st.session_state.bonus_obtenido:
                    st.markdown(f'<div class="bonus">⚡ ¡BONUS DE VELOCIDAD! ⭐</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(
                    f'<div class="err">❌ La respuesta era: <b>{ej["objetivo"]}</b></div>',
                    unsafe_allow_html=True,
                )
            if st.session_state.tiempo_ultimo_ej and st.session_state.timer_iniciado:
                st.caption(f"⏱ Tiempo: {st.session_state.tiempo_ultimo_ej}s")

        # ── Pie sesión ──────────────────────────────────────────────────────────
        st.markdown("---")
        col_a, col_b = st.columns([2,1])
        with col_a:
            if st.session_state.sesion_inicio is not None:
                mins = round((time.time()-st.session_state.sesion_inicio)/60, 1)
                n_ej = sum(st.session_state.sesion_ej.values())
                n_ac = sum(st.session_state.sesion_ac.values())
                pct  = round(n_ac/n_ej*100 if n_ej else 0)
                st.caption(f"⏱ {mins} min · {n_ej} ejercicios · {pct}% aciertos")
        with col_b:
            if st.session_state.sesion_inicio is not None:
                if st.button("💾 Finalizar sesión", use_container_width=True):
                    finalizar_sesion(); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CALENDARIO
# ══════════════════════════════════════════════════════════════════════════════
with tab_cal:
    MESES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    col_prev, col_mes, col_next = st.columns([1,4,1])
    with col_prev:
        if st.button("◀", use_container_width=True, key="cal_prev"):
            if st.session_state.cal_month==1:
                st.session_state.cal_month=12; st.session_state.cal_year-=1
            else: st.session_state.cal_month-=1
            st.rerun()
    with col_mes:
        st.markdown(
            f'<h4 style="text-align:center;margin:6px 0">'
            f'{MESES[st.session_state.cal_month]} {st.session_state.cal_year}</h4>',
            unsafe_allow_html=True)
    with col_next:
        if st.button("▶", use_container_width=True, key="cal_next"):
            if st.session_state.cal_month==12:
                st.session_state.cal_month=1; st.session_state.cal_year+=1
            else: st.session_state.cal_month+=1
            st.rerun()

    st.markdown(render_calendario_html(
        st.session_state.cal_year, st.session_state.cal_month, progreso),
        unsafe_allow_html=True)

    st.markdown("")
    if racha>0:
        st.markdown(
            f'<div class="racha-box">🔥 Racha: {racha} día{"s" if racha>1 else ""} seguido{"s" if racha>1 else ""}</div>',
            unsafe_allow_html=True)
    else:
        st.info("¡Practica hoy para iniciar tu racha de superhéroe!")

    st.markdown("---")
    st.subheader("📋 Detalle de sesión")
    fechas = sorted(progreso.keys(), reverse=True)
    if not fechas:
        mostrar_heroe("¡Completa tu primera sesión!", size=60)
    else:
        hoy  = date.today().isoformat()
        ayer = (date.today()-timedelta(1)).isoformat()
        fmt  = lambda f: f"{f} (hoy)" if f==hoy else (f"{f} (ayer)" if f==ayer else f)
        fs   = st.selectbox("Selecciona un día:", fechas, format_func=fmt)
        d    = progreso[fs]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Aciertos",  f"{d.get('porcentaje_aciertos',0):.1f}%")
        c2.metric("Estrellas", "⭐"*d.get("estrellas",0))
        c3.metric("Duración",  f"{d.get('duracion_minutos',0)} min")
        c4.metric("Velocidad", f"{d.get('velocidad_lectora',0):.1f} wpm")
        st.markdown("**Aciertos por área:**")
        for area in AREAS:
            ac = d.get("aciertos",{}).get(area,0)
            tot= d.get("ejercicios_completados",{}).get(area,0)
            if tot>0:
                st.write(f"**{AREA_NOMBRES[area]}**: {ac}/{tot}")
                st.progress(ac/tot)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ESTADÍSTICAS
# ══════════════════════════════════════════════════════════════════════════════
with tab_stats:
    if not progreso:
        mostrar_heroe("¡Completa sesiones para ver tus estadísticas!", size=80)
    else:
        resumen = get_resumen_semanal(progreso)
        c1,c2,c3 = st.columns(3)
        c1.metric("🔥 Racha",           f"{racha} día{'s' if racha!=1 else ''}")
        c2.metric("📅 Días esta semana", f"{resumen['dias_practicados']}/7")
        c3.metric("📖 Palabras",         resumen["total_palabras"])
        st.markdown("---")
        serie = get_velocidad_serie(progreso)
        if serie:
            st.subheader("📈 Velocidad lectora (palabras/min)")
            df_v = pd.DataFrame(serie,columns=["Fecha","WPM"]).set_index("Fecha")
            st.line_chart(df_v)
        st.subheader("📊 Aciertos por área")
        areas_act = resumen["areas_actual"]
        areas_ant = resumen["areas_anterior"]
        filas=[]
        for area in AREAS:
            t_a=areas_act[area]["total"]; a_a=areas_act[area]["aciertos"]
            t_p=areas_ant[area]["total"]; a_p=areas_ant[area]["aciertos"]
            filas.append({"Área":AREA_NOMBRES[area],
                          "Esta semana %":round(a_a/t_a*100 if t_a else 0,1),
                          "Semana anterior %":round(a_p/t_p*100 if t_p else 0,1)})
        df_a = pd.DataFrame(filas).set_index("Área")
        if df_a[["Esta semana %","Semana anterior %"]].sum().sum()>0:
            st.bar_chart(df_a)
        st.markdown("---")
        st.subheader("🏆 Resumen semanal")
        if resumen["mejor_area"]!="—" or resumen["peor_area"]!="—":
            col1,col2 = st.columns(2)
            if resumen["mejor_area"]!="—": col1.success(f"✅ **Mejor:** {resumen['mejor_area']}")
            if resumen["peor_area"]!="—":  col2.warning(f"💪 **A reforzar:** {resumen['peor_area']}")
        st.markdown(
            f'<div class="speech" style="font-size:1.1rem;max-width:100%">'
            f'{resumen["mensaje"]}</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Fluyo Kids · ¡El superhéroe de la lectura! 🦸")
