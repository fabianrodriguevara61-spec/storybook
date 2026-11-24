"""Descarga los modelos de imagen, sonido y voz en la carpeta modelos/.

Se ejecuta una sola vez y necesita Internet. Después la aplicación funciona sin conexión.
El modelo de texto se descarga aparte con Ollama.
"""

import shutil

from huggingface_hub import hf_hub_download, snapshot_download

import config

print("1/3 Descargando SD-Turbo (imágenes), unos 5 GB...")
snapshot_download(
    "stabilityai/sd-turbo",
    local_dir=config.MODELO_IMAGEN,
    ignore_patterns=["sd_turbo.safetensors", "*.fp16.safetensors", "*.png", "*.jpg"],
)

print("2/3 Descargando AudioLDM (sonido ambiente)...")
snapshot_download(
    "cvssp/audioldm-s-full-v2",
    local_dir=config.MODELO_SONIDO,
    ignore_patterns=["*.bin"],
)

print("3/3 Descargando la voz de Piper en español...")
config.MODELO_VOZ.parent.mkdir(parents=True, exist_ok=True)
for extension in [".onnx", ".onnx.json"]:
    ruta = hf_hub_download("rhasspy/piper-voices", f"es/es_MX/ald/medium/es_MX-ald-medium{extension}")
    shutil.copy(ruta, config.MODELO_VOZ.parent / f"es_MX-ald-medium{extension}")

print(f"Listo. Falta el modelo de texto: ollama pull {config.MODELO_TEXTO}")
