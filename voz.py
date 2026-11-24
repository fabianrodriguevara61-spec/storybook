"""Narración de cada escena con Piper (texto a voz local)."""

import wave

from piper import PiperVoice

import config


def cargar_modelo():
    # Piper busca el archivo de configuración .onnx.json junto al modelo .onnx
    return PiperVoice.load(str(config.MODELO_VOZ))


def generar_voz(voz, texto, ruta):
    with wave.open(str(ruta), "wb") as archivo:
        voz.synthesize_wav(texto, archivo)
