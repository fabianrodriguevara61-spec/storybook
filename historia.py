"""Generación del texto del cuento con un modelo de lenguaje local (Ollama)."""

import json

import requests

import config

# Estructura que debe tener la respuesta del modelo.
# Ollama usa este esquema para obligar al modelo a responder con ese JSON.
ESQUEMA = {
    "type": "object",
    "properties": {
        "titulo": {"type": "string"},
        "personaje": {
            "type": "object",
            "properties": {
                "nombre": {"type": "string"},
                "descripcion_visual": {"type": "string"},
            },
            "required": ["nombre", "descripcion_visual"],
        },
        "escenario": {"type": "string"},
        "escenas": {
            "type": "array",
            "minItems": config.NUM_ESCENAS,
            "maxItems": config.NUM_ESCENAS,
            "items": {
                "type": "object",
                "properties": {
                    "texto": {"type": "string"},
                    "imagen": {"type": "string"},
                    "sonido": {"type": "string"},
                },
                "required": ["texto", "imagen", "sonido"],
            },
        },
    },
    "required": ["titulo", "personaje", "escenario", "escenas"],
}

INSTRUCCIONES = """Eres un escritor de cuentos. Con la idea y el género que te dan escribes un cuento corto dividido en exactamente 5 escenas.

Reglas:
- El título y el texto de las escenas van en español y respetan el género pedido.
- Escena 1: inicio, presenta al personaje principal y el lugar. Escenas 2, 3 y 4: desarrollo, aparece un problema que va creciendo. Escena 5: desenlace.
- Cada escena tiene entre 50 y 80 palabras y continúa lo que pasó en la anterior. El personaje principal, su nombre y los hechos importantes se mantienen en todo el cuento.
- "personaje.descripcion_visual": en inglés, rasgos físicos fijos del personaje principal (edad, cabello, ropa y colores). Máximo 20 palabras.
- "escenario": en inglés, el lugar principal de la historia. Máximo 10 palabras.
- "imagen": en inglés, lo que se ve en la escena (acción y lugar) sin volver a describir al personaje. Máximo 20 palabras.
- "sonido": en inglés, el sonido ambiente o efecto de la escena, sin voces ni música. Máximo 8 palabras. Ejemplo: "heavy rain and distant thunder".
Responde solo con el JSON."""


def historia_valida(historia):
    """Revisa que la historia tenga título, personaje, escenario y 5 escenas completas."""
    try:
        textos = [
            historia["titulo"],
            historia["personaje"]["nombre"],
            historia["personaje"]["descripcion_visual"],
            historia["escenario"],
        ]
        escenas = historia["escenas"]
        if len(escenas) != config.NUM_ESCENAS:
            return False
        for escena in escenas:
            textos += [escena["texto"], escena["imagen"], escena["sonido"]]
    except (KeyError, TypeError):
        return False
    return all(isinstance(t, str) and t.strip() for t in textos)


def generar_historia(idea, genero):
    """Pide la historia a Ollama. Si la respuesta no sirve, lo intenta de nuevo."""
    datos = {
        "model": config.MODELO_TEXTO,
        "messages": [
            {"role": "system", "content": INSTRUCCIONES},
            {"role": "user", "content": f"Idea: {idea}\nGénero: {genero}"},
        ],
        "format": ESQUEMA,
        "stream": False,
        "keep_alive": 0,  # libera la RAM apenas termina, porque luego se cargan los otros modelos
        "options": {"temperature": config.TEMPERATURA, "num_ctx": 4096},
    }

    for _ in range(config.INTENTOS_HISTORIA):
        try:
            respuesta = requests.post(config.OLLAMA_URL, json=datos, timeout=900)
        except requests.ConnectionError:
            raise RuntimeError("No se pudo conectar con Ollama. Verifique que Ollama esté abierto.")
        if respuesta.status_code == 404:
            raise RuntimeError(
                f"El modelo {config.MODELO_TEXTO} no está descargado. "
                f"Ejecute: ollama pull {config.MODELO_TEXTO}"
            )
        respuesta.raise_for_status()

        try:
            historia = json.loads(respuesta.json()["message"]["content"])
        except (json.JSONDecodeError, KeyError):
            continue
        if historia_valida(historia):
            return historia

    raise RuntimeError("El modelo no devolvió una historia válida. Intente de nuevo o cambie la idea.")
