"""Generación del sonido ambiente de cada escena con AudioLDM de forma local."""

import wave

import numpy as np
import torch
from diffusers import AudioLDMPipeline

import config
from imagenes import dispositivo

FRECUENCIA = 16000  # AudioLDM entrega el audio a 16 kHz


def cargar_modelo():
    equipo, tipo = dispositivo()
    pipe = AudioLDMPipeline.from_pretrained(str(config.MODELO_SONIDO), torch_dtype=tipo)
    pipe.set_progress_bar_config(disable=True)
    return pipe.to(equipo)


def guardar_wav(ruta, audio, frecuencia):
    """Guarda un arreglo de numpy (valores entre -1 y 1) como WAV mono de 16 bits."""
    audio = np.clip(audio, -1.0, 1.0)
    datos = (audio * 32767).astype(np.int16)
    with wave.open(str(ruta), "wb") as archivo:
        archivo.setnchannels(1)
        archivo.setsampwidth(2)
        archivo.setframerate(frecuencia)
        archivo.writeframes(datos.tobytes())


def generar_sonido(pipe, descripcion, ruta):
    equipo, _ = dispositivo()
    generador = torch.Generator(equipo).manual_seed(config.SEMILLA)
    audio = pipe(
        prompt=f"{descripcion}, ambient sound effect, high quality",
        negative_prompt="speech, voice, talking, low quality",
        num_inference_steps=config.PASOS_SONIDO,
        audio_length_in_s=config.DURACION_SONIDO,
        generator=generador,
    ).audios[0]

    # Se baja el volumen para que el ambiente se distinga de la voz y no la tape
    audio = np.squeeze(audio)
    pico = np.abs(audio).max()
    if pico > 0:
        audio = audio / pico * config.VOLUMEN_SONIDO
    guardar_wav(ruta, audio, FRECUENCIA)
