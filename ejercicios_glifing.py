import random

# ── Vocabulario ────────────────────────────────────────────────────────────────
SILABAS = [
    "ma","me","mi","mo","mu","pa","pe","pi","po","pu",
    "sa","se","si","so","su","la","le","li","lo","lu",
    "ta","te","ti","to","tu","na","ne","ni","no","nu",
    "da","de","di","do","du","ra","re","ri","ro","ru",
    "ca","co","cu","que","qui","ga","go","gu","gue","gui",
    "fa","fe","fi","fo","fu","ba","be","bi","bo","bu",
    "cha","che","chi","cho","chu","lla","lle","lli","llo","llu",
    "bla","ble","bli","blo","blu","fra","fre","fri","fro","fru",
    "tra","tre","tri","tro","tru","pla","ple","pli","plo","plu",
]

PALABRAS = {
    "fácil": [
        "mama","papa","puma","mapa","pipa","sopa","luna","mano","pino","dedo",
        "pelo","bola","lago","mesa","nido","foca","roca","tela","vela","rosa",
        "loma","lupa","dato","moto","polo","palo","nube","lodo","sede","mole",
        "boca","capa","cola","duna","faro","gota","hoja","isla","jota","kilo",
        "lima","mono","nota","olla","pera","queso","rana","saco","taco","uva",
    ],
    "medio": [
        "pelota","camino","paloma","maleta","tomate","bonito","sabana","cometa",
        "camisa","botella","sandalia","patata","casita","barriga","familia",
        "planeta","ventana","jardín","ratón","balcón","canción","limón",
        "corazón","camión","botón","pantalón","jabón","salón","dragón",
        "lagarto","tortuga","cebolla","naranja","guitarra","murciélago",
        "estrella","conejo","gallina","palomita","velero","cohete","barco",
        "castillo","molino","colmena","cascada","sendero","pradera","almohada",
        "bufanda","paraguas","boligrafo","cuaderno","mochila","tijeras",
    ],
    "difícil": [
        "mariposa","castillo","princesa","dinosaurio","computadora","biblioteca",
        "almendra","elefante","chocolate","televisión","universo","galaxia",
        "aventura","misterio","transparente","extraordinario","protagonista",
        "diccionario","temperatura","electricidad","perseverancia","imaginación",
        "comunicación","experimento","laboratorio","matemáticas","geografía",
        "vocabulario","ortografía","gramática","silencioso","estudiante",
        "trabajador","inteligente","fantástico","increíble","maravilloso",
        "estupendo","incomprensible","irresponsable","biodiversidad","ecosistema",
        "transformación","procesamiento","investigación","descubrimiento","constelación",
        "fluorescente","arquitectura","estetoscopio","prehistórico","voluntariado",
    ],
}

FRASES = {
    "fácil": [
        "El sol brilla en el cielo azul.",
        "Mi mamá me quiere mucho.",
        "El perro corre por el patio.",
        "La luna sale de noche.",
        "El pato nada en el lago.",
        "Mi gato duerme en la cama.",
        "El niño come pan con miel.",
        "La rosa es roja y bonita.",
        "El pez nada en el río.",
        "La vaca da leche rica.",
        "El oso come miel dulce.",
        "Mi bici es azul y rápida.",
        "La nube es blanca y suave.",
        "El árbol tiene muchas hojas.",
        "El bebé ríe con su mamá.",
        "La pelota es grande y roja.",
        "El tren pasa muy deprisa.",
        "Mi amigo se llama Dani.",
        "El pájaro canta en el nido.",
        "La lluvia moja el jardín.",
    ],
    "medio": [
        "La mariposa vuela sobre las flores del jardín.",
        "El conejo corre muy rápido por el campo verde.",
        "Mi familia va de vacaciones a la playa en verano.",
        "El capitán navega con su barco por el mar azul.",
        "Los niños juegan al fútbol en el parque todos los días.",
        "La profesora explica la lección con mucha paciencia.",
        "El cocinero prepara una tortilla deliciosa para cenar.",
        "El cartero trae una carta muy importante esta mañana.",
        "La ballena vive en el océano profundo y oscuro.",
        "Los pájaros cantan alegres por las mañanas soleadas.",
        "El astronauta viaja por el espacio exterior con valentía.",
        "Mi abuelo me cuenta cuentos antes de ir a dormir.",
        "Los pingüinos viven en lugares muy fríos del planeta.",
        "La serpiente se arrastra despacio por la hierba mojada.",
        "El bombero apagó el incendio con mucho coraje.",
        "La abeja recoge el néctar de todas las flores del campo.",
        "El mago sacó un conejo blanco de su sombrero de copa.",
        "Los delfines saltan alegres en las olas del océano.",
        "El pintor mezcla los colores para crear nuevos tonos.",
        "La niña lee un libro muy interesante en la biblioteca.",
    ],
    "difícil": [
        "El explorador descubrió una cueva llena de estalactitas brillantes.",
        "La científica realizó un experimento con muchos ingredientes especiales.",
        "Los dinosaurios vivieron hace millones de años en la Tierra prehistórica.",
        "Los astronautas entrenaron durante años para viajar hasta la Luna.",
        "La biblioteca tiene miles de libros sobre todos los temas imaginables.",
        "El compositor escribió una sinfonía extraordinaria que emocionó al público.",
        "La expedición recorrió la selva amazónica durante tres semanas consecutivas.",
        "Los ingenieros construyeron un puente resistente sobre el río caudaloso.",
        "El detective investigó el misterio con inteligencia y perseverancia.",
        "La fotógrafa capturó imágenes de animales en peligro de extinción.",
        "El telescopio permite observar galaxias que están a millones de años luz.",
        "La inteligencia artificial está transformando la forma en que trabajamos.",
        "El submarino descendió hasta las profundidades más oscuras del océano.",
        "Los arqueólogos descubrieron una civilización desconocida bajo la arena.",
        "La energía renovable es fundamental para proteger el medioambiente.",
    ],
}

TRABALENGUAS = [
    ("fácil",  "Pablito clavó un clavito. ¿Qué clavito clavó Pablito?"),
    ("fácil",  "Como poco coco como, poco coco compro."),
    ("fácil",  "Pepe Pecas pica papas con un pico."),
    ("medio",  "Tres tristes tigres tragan trigo en un trigal."),
    ("medio",  "Erre con erre cigarro, erre con erre barril."),
    ("medio",  "El perro de San Roque no tiene rabo porque Ramón Ramírez se lo cortó."),
    ("difícil","María Chucena techaba su choza. ¿Techas tu choza o techas la ajena, María Chucena?"),
    ("difícil","Pedro Pérez Prado pinta preciosos paisajes pintorescos para personas privilegiadas."),
    ("difícil","Si Pancha plancha con cuatro planchas, ¿con cuántas planchas plancha Pancha?"),
]

PARES_SIMILARES = [
    ("b","d"),("p","q"),("m","n"),("u","n"),
    ("a","e"),("i","l"),("c","e"),("o","a"),("d","b"),("q","p"),
]

MENSAJES_CORRECTO = [
    "¡BOOM! ¡Lo clavaste, campeón! 🚀",
    "¡Increíble! ¡Eres una máquina lectora! ⚡",
    "¡SUPER ERIC lo vuelve a hacer! 🌟",
    "¡Perfecto! ¡Eres el héroe de la lectura! 🏆",
    "¡Genial! ¡Cada vez eres más poderoso! 💥",
    "¡Wow! ¡Imparable! Sigue así, campeón! 🔥",
]

MENSAJES_INCORRECTO = [
    "¡Casi! Los héroes no se rinden. ¡Vamos! 💪",
    "¡Error superado! Los campeones aprenden de esto. 🛡️",
    "¡Inténtalo de nuevo! Tú puedes, SUPER ERIC! ⚡",
    "¡Sin miedo! Los héroes cometen errores y siguen. 🦸",
]

MENSAJES_BIENVENIDA = [
    "¡Hola, campeón! ¿Listo para entrenar tu superpoder? 🚀",
    "¡El héroe lector ha llegado! ¡A practicar! ⚡",
    "¡Tu misión de hoy: ser el mejor lector del universo! 🌟",
    "¡Cada ejercicio te hace más poderoso! ¡Vamos! 💥",
]


# ── Funciones de ejercicio ──────────────────────────────────────────────────

def ejercicio_silabas():
    silaba  = random.choice(SILABAS)
    opciones = random.sample([s for s in SILABAS if s != silaba], 3) + [silaba]
    random.shuffle(opciones)
    return {"tipo":"silaba","pregunta":"¿Cuál es esta sílaba?","objetivo":silaba,"opciones":opciones}


def ejercicio_palabra(dificultad="fácil"):
    lista  = PALABRAS.get(dificultad, PALABRAS["fácil"])
    palabra = random.choice(lista)
    return {"tipo":"palabra","pregunta":"Lee esta palabra:","objetivo":palabra,
            "silabas":dividir_silabas(palabra)}


def ejercicio_dictado(dificultad="fácil"):
    lista  = PALABRAS.get(dificultad, PALABRAS["fácil"])
    palabra = random.choice(lista)
    return {"tipo":"dictado","pregunta":"Escribe la palabra que escuchas:","objetivo":palabra}


def ejercicio_discriminacion_letras():
    par  = random.choice(PARES_SIMILARES)
    letra = random.choice(par)
    return {"tipo":"discriminacion",
            "pregunta":f"¿Esta letra es '{par[0]}' o '{par[1]}'?",
            "objetivo":letra,"opciones":list(par)}


def ejercicio_completar_silaba():
    dificultad = random.choice(["fácil","medio"])
    lista  = PALABRAS[dificultad]
    palabra = random.choice(lista)
    silabas = dividir_silabas(palabra)
    if len(silabas) < 2:
        return ejercicio_completar_silaba()
    pos          = random.randint(0, len(silabas) - 1)
    silaba_oculta = silabas[pos]
    con_hueco    = silabas.copy()
    con_hueco[pos] = "___"
    opciones = [silaba_oculta] + random.sample([s for s in SILABAS if s != silaba_oculta], 3)
    random.shuffle(opciones)
    return {"tipo":"completar","pregunta":"Completa la sílaba que falta:",
            "palabra_con_hueco":" · ".join(con_hueco),"objetivo":silaba_oculta,
            "opciones":opciones,"palabra_completa":palabra}


def ejercicio_frase(dificultad="fácil"):
    lista  = FRASES.get(dificultad, FRASES["fácil"])
    frase  = random.choice(lista)
    return {"tipo":"frase","pregunta":"Lee esta frase en voz alta:",
            "objetivo":frase,"num_palabras":len(frase.split())}


def ejercicio_trabalenguas(dificultad="medio"):
    filtrados = [t for nivel, t in TRABALENGUAS if nivel == dificultad]
    if not filtrados:
        filtrados = [t for _, t in TRABALENGUAS]
    tw = random.choice(filtrados)
    return {"tipo":"trabalenguas",
            "pregunta":"¡Lee este trabalenguas lo más rápido que puedas!",
            "objetivo":tw,"num_palabras":len(tw.split())}


def ejercicio_velocidad_bloque(n: int = 12, dificultad: str = "fácil") -> dict:
    lista = PALABRAS.get(dificultad, PALABRAS["fácil"])
    palabras = random.sample(lista, min(n, len(lista)))
    return {
        "tipo": "velocidad",
        "pregunta": f"¡Lee estas {len(palabras)} palabras lo más rápido que puedas!",
        "objetivo": " ".join(palabras),
        "palabras": palabras,
        "num_palabras": len(palabras),
    }


def get_ejercicio_aleatorio(dificultad="fácil"):
    opciones = [
        lambda: ejercicio_silabas(),
        lambda: ejercicio_palabra(dificultad),
        lambda: ejercicio_discriminacion_letras(),
        lambda: ejercicio_completar_silaba(),
        lambda: ejercicio_frase(dificultad),
    ]
    if dificultad in ("medio","difícil"):
        opciones.append(lambda: ejercicio_trabalenguas(dificultad))
    return random.choice(opciones)()


def verificar_respuesta(ejercicio, respuesta):
    return respuesta.strip().lower() == ejercicio.get("objetivo","").strip().lower()


def dividir_silabas(palabra):
    vocales = "aeiouáéíóú"
    silabas, actual = [], ""
    i = 0
    while i < len(palabra):
        actual += palabra[i]
        if palabra[i] in vocales:
            if i + 1 < len(palabra):
                sig = palabra[i + 1]
                if sig not in vocales:
                    if i + 2 < len(palabra) and palabra[i + 2] not in vocales:
                        silabas.append(actual); actual = ""
                else:
                    silabas.append(actual); actual = ""
        i += 1
    if actual:
        silabas.append(actual)
    return silabas if silabas else [palabra]


def tiempo_objetivo(tipo: str, dificultad: str) -> int:
    """Segundos límite para el modo cronometrado según tipo y dificultad."""
    tabla = {
        ("silaba",         "fácil"): 10, ("silaba",         "medio"): 8,  ("silaba",         "difícil"): 6,
        ("palabra",        "fácil"): 12, ("palabra",        "medio"): 9,  ("palabra",        "difícil"): 7,
        ("dictado",        "fácil"): 18, ("dictado",        "medio"): 14, ("dictado",        "difícil"): 10,
        ("discriminacion", "fácil"): 8,  ("discriminacion", "medio"): 6,  ("discriminacion", "difícil"): 5,
        ("completar",      "fácil"): 12, ("completar",      "medio"): 9,  ("completar",      "difícil"): 7,
        ("frase",          "fácil"): 20, ("frase",          "medio"): 16, ("frase",          "difícil"): 12,
        ("trabalenguas",   "fácil"): 15, ("trabalenguas",   "medio"): 12, ("trabalenguas",   "difícil"): 10,
    }
    return tabla.get((tipo, dificultad), 15)
