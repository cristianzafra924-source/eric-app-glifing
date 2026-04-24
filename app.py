import streamlit as st
import time
import pandas as pd
from datetime import date, timedelta

from ejercicios_glifing import (
    ejercicio_silabas, ejercicio_palabra, ejercicio_dictado,
    ejercicio_discriminacion_letras, ejercicio_completar_silaba,
    get_ejercicio_aleatorio, verificar_respuesta,
)
from progreso_glifing import (
    cargar_progreso, guardar_sesion, get_racha,
    get_semana_datos, get_aciertos_por_area, get_velocidad_serie,
    get_resumen_semanal, render_calendario_html,
    AREAS, AREA_NOMBRES, calcular_estrellas, get_db_status,
)

st.set_page_config(
    page_title="App de Eric – Método Glifing",
    page_icon="📚",
    layout="centered",
)

st.markdown("""
<style>
.titulo    { font-size:2.2rem; font-weight:800; color:#4A90D9; text-align:center; }
.pal-big   { font-size:3rem; font-weight:700; color:#2C3E50; text-align:center;
             letter-spacing:.15em; padding:18px; background:#EBF5FB;
             border-radius:14px; margin:8px 0; }
.sil-box   { display:inline-block; font-size:2rem; font-weight:600; color:#fff;
             background:#4A90D9; border-radius:8px; padding:6px 14px; margin:3px; }
.ok        { color:#27AE60; font-size:1.5rem; font-weight:700; text-align:center; }
.err       { color:#E74C3C; font-size:1.5rem; font-weight:700; text-align:center; }
.pts       { font-size:1.2rem; font-weight:600; color:#8E44AD; }
.racha-box { background:#fff7cc; border-radius:12px; padding:12px 18px;
             text-align:center; font-size:1.1rem; font-weight:600; color:#b8860b; }
.msg-box   { background:#fff7cc; border-radius:14px; padding:16px;
             text-align:center; font-size:1.15rem; margin-top:12px; }
</style>
""", unsafe_allow_html=True)

# ── Estado de sesión ──────────────────────────────────────────────────────────
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
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v.copy() if isinstance(v, dict) else v

# ── Carga progreso ────────────────────────────────────────────────────────────
progreso = cargar_progreso()

# ── Cabecera ──────────────────────────────────────────────────────────────────
st.markdown('<div class="titulo">📚 App de Eric · Método Glifing</div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuración")
    nombre = st.text_input("¿Cómo te llamas?", value="Eric")
    dificultad = st.selectbox("Nivel de dificultad", ["fácil", "medio", "difícil"])
    st.session_state.dificultad = dificultad
    tipo_ejercicio = st.selectbox(
        "Tipo de ejercicio",
        ["Aleatorio", "Sílabas", "Leer palabras", "Dictado", "Discriminar letras", "Completar sílaba"],
    )
    st.markdown("---")
    racha = get_racha(progreso)
    st.markdown(
        f'<div class="pts">⭐ Sesión: {st.session_state.puntos}/{st.session_state.total}</div>',
        unsafe_allow_html=True,
    )
    if racha > 0:
        st.markdown(
            f'<div class="racha-box">🔥 Racha: {racha} día{"s" if racha > 1 else ""}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("")
    if st.button("🔄 Reiniciar puntuación"):
        st.session_state.puntos = 0
        st.session_state.total  = 0
        st.rerun()
    st.markdown("---")
    if get_db_status():
        st.markdown("🟢 Progreso guardado en la nube")
    else:
        st.markdown("🟡 Guardado solo en esta sesión")
        st.caption("Configura Supabase en secrets para guardar de forma permanente.")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_ej, tab_cal, tab_stats = st.tabs(["📝 Ejercicios", "📅 Calendario", "📊 Estadísticas"])

# ── Mapeo tipo → área ─────────────────────────────────────────────────────────
TIPO_A_AREA = {
    "silaba":         "silabas",
    "palabra":        "palabras",
    "dictado":        "dictado",
    "discriminacion": "discriminacion",
    "completar":      "completar",
}

# ── Funciones de sesión ───────────────────────────────────────────────────────
def nuevo_ejercicio():
    st.session_state.respondido     = False
    st.session_state.resultado      = None
    st.session_state.sesion_t_ej_inicio = time.time()
    d = st.session_state.dificultad
    if tipo_ejercicio == "Sílabas":
        st.session_state.ejercicio_actual = ejercicio_silabas()
    elif tipo_ejercicio == "Leer palabras":
        st.session_state.ejercicio_actual = ejercicio_palabra(d)
    elif tipo_ejercicio == "Dictado":
        st.session_state.ejercicio_actual = ejercicio_dictado(d)
    elif tipo_ejercicio == "Discriminar letras":
        st.session_state.ejercicio_actual = ejercicio_discriminacion_letras()
    elif tipo_ejercicio == "Completar sílaba":
        st.session_state.ejercicio_actual = ejercicio_completar_silaba()
    else:
        st.session_state.ejercicio_actual = get_ejercicio_aleatorio(d)


def registrar_respuesta(correcto: bool):
    if st.session_state.sesion_inicio is None:
        st.session_state.sesion_inicio = time.time()
    ej   = st.session_state.ejercicio_actual
    area = TIPO_A_AREA.get(ej.get("tipo"), "silabas")
    st.session_state.sesion_ej[area] += 1
    st.session_state.total            += 1
    if correcto:
        st.session_state.sesion_ac[area] += 1
        st.session_state.puntos          += 1
    else:
        st.session_state.sesion_err[area] += 1
    if ej.get("tipo") == "palabra":
        elapsed = time.time() - (st.session_state.sesion_t_ej_inicio or time.time())
        st.session_state.sesion_palabras  += 1
        st.session_state.sesion_t_palabras += max(elapsed, 1)


def finalizar_sesion():
    if st.session_state.sesion_inicio is None:
        return
    duracion_seg = time.time() - st.session_state.sesion_inicio
    duracion_min = round(duracion_seg / 60, 1)
    p = st.session_state.sesion_palabras
    t = st.session_state.sesion_t_palabras
    wpm = round((p / t) * 60, 1) if p > 0 and t > 0 else 0.0
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
        "duracion_minutos":       duracion_min,
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

    ej = st.session_state.ejercicio_actual

    if st.session_state.sesion_guardada:
        st.success("✅ ¡Sesión guardada! Consulta el Calendario para ver tu progreso.")
        st.session_state.sesion_guardada = False

    st.subheader(f"¡Hola, {nombre}! 👋")
    st.write(ej.get("pregunta", ""))

    tipo     = ej.get("tipo")
    respuesta = None

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

    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.respondido:
            label = "✅ ¡Ya lo leí!" if tipo == "palabra" else "✅ Comprobar"
            if st.button(label, use_container_width=True):
                if tipo == "palabra":
                    registrar_respuesta(True)
                    st.session_state.respondido = True
                    st.session_state.resultado  = True
                else:
                    correcto = str(respuesta).strip().lower() == ej["objetivo"].strip().lower()
                    registrar_respuesta(correcto)
                    st.session_state.respondido = True
                    st.session_state.resultado  = correcto
                st.rerun()

    with col2:
        if st.button("➡️ Siguiente", use_container_width=True):
            nuevo_ejercicio()
            st.rerun()

    if st.session_state.respondido and st.session_state.resultado is not None:
        if st.session_state.resultado:
            st.markdown('<div class="ok">🎉 ¡Muy bien! ¡Correcto!</div>', unsafe_allow_html=True)
            st.balloons()
        else:
            st.markdown(
                f'<div class="err">❌ Casi... La respuesta era: <b>{ej["objetivo"]}</b></div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        if st.session_state.sesion_inicio is not None:
            mins        = round((time.time() - st.session_state.sesion_inicio) / 60, 1)
            total_sesion = sum(st.session_state.sesion_ej.values())
            st.caption(f"⏱ Sesión activa · {mins} min · {total_sesion} ejercicios completados")
    with col_b:
        if st.session_state.sesion_inicio is not None:
            if st.button("💾 Finalizar sesión", use_container_width=True):
                finalizar_sesion()
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CALENDARIO & PROGRESO
# ══════════════════════════════════════════════════════════════════════════════
with tab_cal:
    # Navegación de mes
    col_prev, col_mes, col_next = st.columns([1, 4, 1])
    with col_prev:
        if st.button("◀", use_container_width=True, key="cal_prev"):
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with col_mes:
        MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        st.markdown(
            f'<h4 style="text-align:center;margin:6px 0">'
            f'{MESES[st.session_state.cal_month]} {st.session_state.cal_year}</h4>',
            unsafe_allow_html=True,
        )
    with col_next:
        if st.button("▶", use_container_width=True, key="cal_next"):
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    st.markdown(
        render_calendario_html(st.session_state.cal_year, st.session_state.cal_month, progreso),
        unsafe_allow_html=True,
    )

    # Racha
    st.markdown("")
    racha = get_racha(progreso)
    if racha > 0:
        st.markdown(
            f'<div class="racha-box">🔥 Racha actual: {racha} día{"s" if racha > 1 else ""} seguido{"s" if racha > 1 else ""}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("¡Practica hoy para empezar una racha!")

    # Detalle de sesión
    st.markdown("---")
    st.subheader("📋 Detalle de una sesión")
    fechas_disponibles = sorted(progreso.keys(), reverse=True)

    if not fechas_disponibles:
        st.info("Aún no hay sesiones registradas. ¡Completa tu primera sesión!")
    else:
        hoy   = date.today().isoformat()
        ayer  = (date.today() - timedelta(1)).isoformat()

        def fmt_fecha(f):
            if f == hoy:   return f"{f}  (hoy)"
            if f == ayer:  return f"{f}  (ayer)"
            return f

        fecha_sel = st.selectbox(
            "Selecciona un día con sesión:",
            fechas_disponibles,
            format_func=fmt_fecha,
        )
        d = progreso[fecha_sel]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Aciertos",   f"{d.get('porcentaje_aciertos', 0):.1f}%")
        col2.metric("Estrellas",  "⭐" * d.get("estrellas", 0))
        col3.metric("Duración",   f"{d.get('duracion_minutos', 0)} min")
        col4.metric("Velocidad",  f"{d.get('velocidad_lectora', 0):.1f} wpm")

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
        st.info("Aún no hay datos. Completa algunas sesiones de ejercicios y vuelve aquí.")
    else:
        resumen = get_resumen_semanal(progreso)
        racha   = get_racha(progreso)

        # KPIs superiores
        col1, col2, col3 = st.columns(3)
        col1.metric("🔥 Racha",              f"{racha} día{'s' if racha != 1 else ''}")
        col2.metric("📅 Días esta semana",    f"{resumen['dias_practicados']}/7")
        col3.metric("📖 Palabras esta semana", resumen["total_palabras"])

        st.markdown("---")

        # Gráfica velocidad lectora
        serie_vel = get_velocidad_serie(progreso)
        if serie_vel:
            st.subheader("📈 Velocidad lectora (palabras / min)")
            df_vel = pd.DataFrame(serie_vel, columns=["Fecha", "WPM"]).set_index("Fecha")
            st.line_chart(df_vel)
        else:
            st.info("La velocidad lectora se registra cuando completas ejercicios de **Leer palabras**.")

        # Gráfica aciertos por área (esta semana vs anterior)
        st.subheader("📊 Aciertos por área — Esta semana vs. semana anterior")
        areas_act = resumen["areas_actual"]
        areas_ant = resumen["areas_anterior"]

        filas = []
        for area in AREAS:
            t_act = areas_act[area]["total"]
            a_act = areas_act[area]["aciertos"]
            t_ant = areas_ant[area]["total"]
            a_ant = areas_ant[area]["aciertos"]
            filas.append({
                "Área":           AREA_NOMBRES[area],
                "Esta semana %":  round(a_act / t_act * 100 if t_act > 0 else 0, 1),
                "Semana anterior %": round(a_ant / t_ant * 100 if t_ant > 0 else 0, 1),
            })

        df_areas = pd.DataFrame(filas).set_index("Área")
        if df_areas[["Esta semana %", "Semana anterior %"]].sum().sum() > 0:
            st.bar_chart(df_areas)
        else:
            st.info("Completa ejercicios esta semana para ver la comparativa.")

        # Comparativa detallada
        st.markdown("---")
        st.subheader("📅 Comparativa semanal detallada")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Esta semana:**")
            for area in AREAS:
                t = areas_act[area]["total"]
                a = areas_act[area]["aciertos"]
                if t > 0:
                    st.write(f"• {AREA_NOMBRES[area]}: {a}/{t} ({round(a/t*100)}%)")
        with col2:
            st.markdown("**Semana anterior:**")
            for area in AREAS:
                t = areas_ant[area]["total"]
                a = areas_ant[area]["aciertos"]
                if t > 0:
                    st.write(f"• {AREA_NOMBRES[area]}: {a}/{t} ({round(a/t*100)}%)")

        # Resumen semanal
        st.markdown("---")
        st.subheader("🏆 Resumen de la semana")

        if resumen["mejor_area"] != "—" or resumen["peor_area"] != "—":
            col1, col2 = st.columns(2)
            if resumen["mejor_area"] != "—":
                col1.success(f"✅ **Mejor área:** {resumen['mejor_area']}")
            if resumen["peor_area"] != "—":
                col2.warning(f"💪 **A reforzar:** {resumen['peor_area']}")

        if date.today().weekday() == 0 and resumen["dias_practicados"] == 0:
            st.info("🗓 ¡Es lunes! Aquí tienes el resumen de la semana pasada. ¡A por otra semana genial!")

        st.markdown(
            f'<div class="msg-box">{resumen["mensaje"]}</div>',
            unsafe_allow_html=True,
        )

# ── Pie de página ─────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("App educativa para Eric basada en el Método Glifing · Aprendizaje de la lectura paso a paso 🐢")
