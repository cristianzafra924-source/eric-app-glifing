import random

SILABAS = ["ma", "me", "mi", "mo", "mu",
           "pa", "pe", "pi", "po", "pu",
           "sa", "se", "si", "so", "su",
           "la", "le", "li", "lo", "lu",
           "ta", "te", "ti", "to", "tu",
           "na", "ne", "ni", "no", "nu",
           "da", "de", "di", "do", "du",
           "ra", "re", "ri", "ro", "ru",
           "ca", "co", "cu", "que", "qui",
           "ga", "go", "gu", "gue", "gui"]

PALABRAS = {
    "fácil": ["mama", "papa", "puma", "mapa", "pipa", "sopa", "luna", "mano", "pino", "dedo"],
    "medio": ["pelota", "camino", "paloma", "maleta", "tomate", "bonito", "sabana", "cometa", "policia", "camisa"],
    "difícil": ["mariposa", "castillo", "princesa", "dinosaurio", "computadora", "biblioteca", "paraguas", "calamar", "almendra", "elefante"],
}

LETRAS = list("abcdefghijklmnopqrstuvwxyz")

PARES_SIMILARES = [
    ("b", "d"), ("p", "q"), ("m", "n"), ("u", "n"),
    ("a", "e"), ("i", "l"), ("c", "e"), ("o", "a"),
]


def ejercicio_silabas(nivel=1):
    """Devuelve una sílaba aleatoria para que el niño la lea o escriba."""
    silaba = random.choice(SILABAS)
    opciones = random.sample([s for s in SILABAS if s != silaba], 3)
    opciones.append(silaba)
    random.shuffle(opciones)
    return {
        "tipo": "silaba",
        "pregunta": f"¿Cuál es esta sílaba?",
        "objetivo": silaba,
        "opciones": opciones,
    }


def ejercicio_palabra(dificultad="fácil"):
    """Devuelve una palabra para leer según la dificultad."""
    lista = PALABRAS.get(dificultad, PALABRAS["fácil"])
    palabra = random.choice(lista)
    return {
        "tipo": "palabra",
        "pregunta": f"Lee esta palabra:",
        "objetivo": palabra,
        "silabas": dividir_silabas(palabra),
    }


def ejercicio_dictado(dificultad="fácil"):
    """Devuelve una palabra para que el niño la escriba (dictado)."""
    lista = PALABRAS.get(dificultad, PALABRAS["fácil"])
    palabra = random.choice(lista)
    return {
        "tipo": "dictado",
        "pregunta": "Escribe la palabra que escuchas:",
        "objetivo": palabra,
    }


def ejercicio_discriminacion_letras():
    """Ejercicio para distinguir letras parecidas (b/d, p/q, etc.)."""
    par = random.choice(PARES_SIMILARES)
    letra_correcta = random.choice(par)
    letra_falsa = par[1] if letra_correcta == par[0] else par[0]

    # Mostrar la letra y pedir cuál es
    return {
        "tipo": "discriminacion",
        "pregunta": f"¿Esta letra es una '{letra_correcta}' o una '{letra_falsa}'?",
        "objetivo": letra_correcta,
        "opciones": list(par),
    }


def ejercicio_completar_silaba():
    """El niño debe completar la sílaba que falta en una palabra."""
    dificultad = random.choice(["fácil", "medio"])
    lista = PALABRAS[dificultad]
    palabra = random.choice(lista)
    silabas = dividir_silabas(palabra)

    if len(silabas) < 2:
        return ejercicio_completar_silaba()

    pos = random.randint(0, len(silabas) - 1)
    silaba_oculta = silabas[pos]
    silabas_con_hueco = silabas.copy()
    silabas_con_hueco[pos] = "___"

    opciones = [silaba_oculta] + random.sample(
        [s for s in SILABAS if s != silaba_oculta], 3
    )
    random.shuffle(opciones)

    return {
        "tipo": "completar",
        "pregunta": "Completa la sílaba que falta:",
        "palabra_con_hueco": " - ".join(silabas_con_hueco),
        "objetivo": silaba_oculta,
        "opciones": opciones,
        "palabra_completa": palabra,
    }


def dividir_silabas(palabra):
    """División silábica simple (aproximada para palabras del vocabulario básico)."""
    vocales = "aeiouáéíóú"
    silabas = []
    silaba_actual = ""

    i = 0
    while i < len(palabra):
        silaba_actual += palabra[i]
        if palabra[i] in vocales:
            # Mira hacia adelante para decidir si cortar
            if i + 1 < len(palabra):
                siguiente = palabra[i + 1]
                if siguiente not in vocales:
                    if i + 2 < len(palabra) and palabra[i + 2] not in vocales:
                        silabas.append(silaba_actual)
                        silaba_actual = ""
                    elif i + 2 >= len(palabra):
                        pass  # Última consonante va con esta sílaba
                else:
                    silabas.append(silaba_actual)
                    silaba_actual = ""
        i += 1

    if silaba_actual:
        silabas.append(silaba_actual)

    return silabas if silabas else [palabra]


def verificar_respuesta(ejercicio, respuesta):
    """Comprueba si la respuesta del niño es correcta."""
    objetivo = ejercicio.get("objetivo", "")
    return respuesta.strip().lower() == objetivo.strip().lower()


def get_ejercicio_aleatorio(dificultad="fácil"):
    """Devuelve un ejercicio aleatorio entre los disponibles."""
    opciones = [
        lambda: ejercicio_silabas(),
        lambda: ejercicio_palabra(dificultad),
        lambda: ejercicio_discriminacion_letras(),
        lambda: ejercicio_completar_silaba(),
    ]
    return random.choice(opciones)()
