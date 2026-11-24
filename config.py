"""Configuración general del proyecto.

Aquí se cambian los modelos y los parámetros de generación sin tocar el resto del código.
"""

from pathlib import Path

CARPETA = Path(__file__).parent
CARPETA_MODELOS = CARPETA / "modelos"
CARPETA_SALIDAS = CARPETA / "salidas"

NUM_ESCENAS = 5
SEMILLA = 42

# --- Texto (Ollama, servidor local) ---
OLLAMA_URL = "http://localhost:11434/api/chat"
MODELO_TEXTO = "llama3.1:8b"  # con 8 GB de RAM usar "llama3.2:3b"
TEMPERATURA = 0.8
INTENTOS_HISTORIA = 3

# --- Imagen (SD-Turbo con diffusers) ---
MODELO_IMAGEN = CARPETA_MODELOS / "sd-turbo"
PASOS_IMAGEN = 2
TAMANO_IMAGEN = 512

# Estrategia de consistencia visual:
#   "ficha"  -> estilo del género + ficha del personaje + escenario en todos los prompts,
#               y la misma semilla en las cinco imágenes.
#   "simple" -> solo la descripción de la escena y una semilla distinta por escena.
ESTRATEGIA_CONSISTENCIA = "ficha"

# --- Sonido ambiente (AudioLDM con diffusers) ---
MODELO_SONIDO = CARPETA_MODELOS / "audioldm-s-full-v2"
PASOS_SONIDO = 20
DURACION_SONIDO = 6.0  # segundos
VOLUMEN_SONIDO = 0.4  # pico máximo, para que el ambiente no tape la voz

# --- Voz (Piper) ---
MODELO_VOZ = CARPETA_MODELOS / "voz" / "es_MX-ald-medium.onnx"

# Tipos de historia y el estilo visual (en inglés) que se usa para las imágenes.
GENEROS = {
    "Terror": "dark horror illustration, gloomy atmosphere, muted colors, dramatic shadows",
    "Fantasía": "fantasy storybook watercolor illustration, soft warm colors",
    "Misterio": "mystery noir illustration, foggy night, cold blue tones",
    "Aventura": "adventure comic illustration, vivid colors, dynamic scene",
    "Ciencia ficción": "science fiction digital art, futuristic, neon lights",
    "Infantil": "cute children's book illustration, pastel colors, simple shapes",
}
