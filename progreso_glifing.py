import random
import calendar
import streamlit as st
from datetime import date, timedelta, datetime, timezone

AREAS = ["silabas", "palabras", "dictado", "discriminacion", "completar", "frases"]

AREA_NOMBRES = {
    "silabas":        "Sílabas",
    "palabras":       "Palabras",
    "dictado":        "Dictado",
    "discriminacion": "Discriminar letras",
    "completar":      "Completar sílaba",
    "frases":         "Frases y Trabalenguas",
}

MENSAJES = [
    "¡Eric, eres increíble! Cada día que practicas te haces más fuerte. 💪",
    "¡Semana fantástica! El esfuerzo siempre tiene recompensa. 🏆",
    "¡Lo estás haciendo genial! Sigue así y verás cómo mejoras. 🚀",
    "¡Bravo, Eric! Cada ejercicio te acerca más a tu objetivo. ⭐",
    "¡Eres un campeón de la lectura! No pares, vas muy bien. 🎯",
    "¡Qué semana tan buena! Tus letras y sílabas ya te conocen. 📖",
    "¡Increíble progreso! Tu cerebro está aprendiendo cosas nuevas. 🧠",
]

# ── Conexión Supabase (cacheada por instancia de app) ────────────────────────

_SB_URL = "https://hzgkmkacundgxbwcuekk.supabase.co"
_SB_KEY = "sb_publishable_CgQGi0YCQ_JXuJxi8npMbQ_snp3Paes"

@st.cache_resource(show_spinner=False)
def _supabase_client():
    """Devuelve el cliente Supabase o None si no está disponible."""
    try:
        from supabase import create_client
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        except Exception:
            url, key = _SB_URL, _SB_KEY
        return create_client(url, key)
    except Exception:
        return None


def get_db_status() -> bool:
    return _supabase_client() is not None

# ── Caché de sesión (fallback cuando no hay BD) ───────────────────────────────

def _cache_get() -> dict:
    return dict(st.session_state.get("_progreso_cache", {}))


def _cache_set(fecha: str, datos: dict):
    if "_progreso_cache" not in st.session_state:
        st.session_state["_progreso_cache"] = {}
    st.session_state["_progreso_cache"][fecha] = datos

# ── API pública ───────────────────────────────────────────────────────────────

def cargar_progreso() -> dict:
    """Lee todo el historial: Supabase si disponible, sesión si no."""
    sb = _supabase_client()
    if sb:
        try:
            resp = sb.table("eric_progreso").select("fecha, datos").execute()
            data = {row["fecha"]: row["datos"] for row in resp.data}
            # Sincroniza el caché de sesión con lo que hay en BD
            st.session_state["_progreso_cache"] = data
            return data
        except Exception:
            pass
    return _cache_get()


def calcular_estrellas(pct: float) -> int:
    if pct >= 90: return 5
    if pct >= 75: return 4
    if pct >= 60: return 3
    if pct >= 40: return 2
    return 1


def guardar_sesion(datos: dict):
    """Fusiona los datos de la sesión con el historial y los persiste."""
    progreso = cargar_progreso()
    fecha    = datos.get("fecha", date.today().isoformat())

    if fecha in progreso:
        ex = progreso[fecha]
        for area in AREAS:
            for clave in ("ejercicios_completados", "aciertos", "errores"):
                ex[clave][area] = ex[clave].get(area, 0) + datos[clave].get(area, 0)
        total    = sum(ex["ejercicios_completados"].values())
        aciertos = sum(ex["aciertos"].values())
        ex["porcentaje_aciertos"] = round(aciertos / total * 100 if total else 0, 1)
        ex["estrellas"]           = calcular_estrellas(ex["porcentaje_aciertos"])
        ex["duracion_minutos"]    = round(
            ex.get("duracion_minutos", 0) + datos.get("duracion_minutos", 0), 1
        )
        v_old = ex.get("velocidad_lectora", 0)
        v_new = datos.get("velocidad_lectora", 0)
        if v_old > 0 and v_new > 0:
            ex["velocidad_lectora"] = round((v_old + v_new) / 2, 1)
        elif v_new > 0:
            ex["velocidad_lectora"] = v_new
        datos_finales = ex
    else:
        datos_finales = datos

    # Intenta guardar en Supabase; si falla, guarda en sesión
    sb = _supabase_client()
    if sb:
        try:
            sb.table("eric_progreso").upsert({
                "fecha":      fecha,
                "datos":      datos_finales,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
            _cache_set(fecha, datos_finales)
            return
        except Exception:
            pass
    _cache_set(fecha, datos_finales)

# ── Funciones de análisis (no tocan la BD) ────────────────────────────────────

def get_racha(progreso: dict) -> int:
    if not progreso:
        return 0
    racha   = 0
    current = date.today()
    while current.isoformat() in progreso:
        racha   += 1
        current -= timedelta(days=1)
    return racha


def get_semana_datos(progreso: dict, offset: int = 0):
    today = date.today()
    lunes = today - timedelta(days=today.weekday()) - timedelta(weeks=offset)
    datos = {}
    for i in range(7):
        ds = (lunes + timedelta(days=i)).isoformat()
        if ds in progreso:
            datos[ds] = progreso[ds]
    return datos, lunes


def get_aciertos_por_area(datos_semana: dict) -> dict:
    totales = {a: {"aciertos": 0, "total": 0} for a in AREAS}
    for d in datos_semana.values():
        for a in AREAS:
            totales[a]["aciertos"] += d.get("aciertos", {}).get(a, 0)
            totales[a]["total"]    += d.get("ejercicios_completados", {}).get(a, 0)
    return totales


def get_velocidad_serie(progreso: dict) -> list:
    return [
        (f, progreso[f].get("velocidad_lectora", 0))
        for f in sorted(progreso.keys())
        if progreso[f].get("velocidad_lectora", 0) > 0
    ]


def get_resumen_semanal(progreso: dict) -> dict:
    datos_actual,   _ = get_semana_datos(progreso, 0)
    datos_anterior, _ = get_semana_datos(progreso, 1)

    areas_actual   = get_aciertos_por_area(datos_actual)
    areas_anterior = get_aciertos_por_area(datos_anterior)

    total_palabras = sum(
        d.get("ejercicios_completados", {}).get("palabras", 0) +
        d.get("ejercicios_completados", {}).get("dictado",  0)
        for d in datos_actual.values()
    )

    pct = {
        a: areas_actual[a]["aciertos"] / areas_actual[a]["total"] * 100
        if areas_actual[a]["total"] > 0 else None
        for a in AREAS
    }
    con_datos = {a: v for a, v in pct.items() if v is not None}
    mejor = AREA_NOMBRES.get(max(con_datos, key=con_datos.get), "—") if con_datos else "—"
    peor  = AREA_NOMBRES.get(min(con_datos, key=con_datos.get), "—") if con_datos else "—"

    return {
        "dias_practicados": len(datos_actual),
        "total_palabras":   total_palabras,
        "mejor_area":       mejor,
        "peor_area":        peor,
        "mensaje":          random.choice(MENSAJES),
        "areas_actual":     areas_actual,
        "areas_anterior":   areas_anterior,
    }

# ── Render calendario HTML ────────────────────────────────────────────────────

def render_calendario_html(year: int, month: int, progreso: dict) -> str:
    today_str  = date.today().isoformat()
    cal_matrix = calendar.monthcalendar(year, month)

    css = """
<style>
.eric-cal{font-family:'Segoe UI',sans-serif;width:100%}
.eric-cal table{width:100%;border-collapse:separate;border-spacing:4px}
.eric-cal th{background:#7F77DD;color:#fff;padding:8px 4px;text-align:center;
             font-size:.8rem;border-radius:6px}
.eric-cal td{padding:3px}
.dc{border-radius:10px;padding:6px 3px;font-size:.82rem;line-height:1.25;
    min-height:46px;display:flex;flex-direction:column;
    align-items:center;justify-content:center;font-weight:600}
.df{background:#3a3a3a;color:#888}
.dh{background:#1a7a1a;color:#fff}
.dok{background:#3a6b3a;color:#c8f0c8}
.dm{background:#6b2a2a;color:#ffb3b3}
.de{background:transparent}
.dt{outline:3px solid #7F77DD;outline-offset:-3px}
.leyenda{display:flex;gap:10px;margin-top:8px;font-size:.75rem;flex-wrap:wrap}
.badge{border-radius:4px;padding:1px 7px}
</style>
"""

    dias_hdr = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    html = css + '<div class="eric-cal"><table><tr>'
    for d in dias_hdr:
        html += f"<th>{d}</th>"
    html += "</tr>"

    for week in cal_matrix:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += '<td><div class="dc de"> </div></td>'
                continue
            ds      = f"{year}-{month:02d}-{day:02d}"
            today_c = " dt" if ds == today_str else ""
            if ds > today_str:
                html += f'<td><div class="dc df{today_c}">{day}</div></td>'
            elif ds in progreso:
                pct   = progreso[ds].get("porcentaje_aciertos", 0)
                stars = "⭐" * progreso[ds].get("estrellas", 1)
                cls   = "dh" if pct >= 80 else "dok"
                html += f'<td><div class="dc {cls}{today_c}">{day}<br><span style="font-size:.65rem">{stars}</span></div></td>'
            else:
                html += f'<td><div class="dc dm{today_c}">{day}</div></td>'
        html += "</tr>"

    html += """</table>
<div class="leyenda">
  <span><span class="badge" style="background:#1a7a1a;color:#fff">■</span> &gt;80% aciertos</span>
  <span><span class="badge" style="background:#3a6b3a;color:#c8f0c8">■</span> Sesión OK</span>
  <span><span class="badge" style="background:#6b2a2a;color:#ffb3b3">■</span> Sin práctica</span>
  <span><span class="badge" style="background:#3a3a3a;color:#888">■</span> Día futuro</span>
</div></div>"""
    return html
