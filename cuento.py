"""Une todos los componentes: texto -> imágenes -> sonido -> voz, y guarda el resultado."""

import gc
import json
import time
from datetime import datetime

import torch

import config
import imagenes
import sonido
import voz
from historia import generar_historia


def revisar_modelos():
    """Verifica que los modelos locales estén descargados antes de empezar."""
    faltantes = [
        str(ruta) for ruta in (config.MODELO_IMAGEN, config.MODELO_SONIDO, config.MODELO_VOZ)
        if not ruta.exists()
    ]
    if faltantes:
        raise FileNotFoundError(
            "Faltan modelos: " + ", ".join(faltantes) + ". Ejecute primero: python descargar_modelos.py"
        )


def liberar_memoria():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def crear_cuento(idea, genero, avance=lambda valor, texto: None):
    """Genera el cuento completo. 'avance' recibe (valor de 0 a 1, mensaje) para la barra de progreso."""
    revisar_modelos()
    carpeta = config.CARPETA_SALIDAS / datetime.now().strftime("%Y%m%d_%H%M%S")
    carpeta.mkdir(parents=True, exist_ok=True)
    n = config.NUM_ESCENAS
    tiempos = {}

    # 1. Texto
    inicio = time.time()
    avance(0.0, "Escribiendo la historia...")
    historia = generar_historia(idea, genero)
    tiempos["historia"] = round(time.time() - inicio, 1)

    # 2. Imágenes (se carga el modelo una sola vez para las 5 escenas)
    inicio = time.time()
    avance(0.2, "Cargando el modelo de imagen...")
    pipe = imagenes.cargar_modelo()
    prompts = []
    for i in range(1, n + 1):
        avance(0.2 + 0.4 * (i - 1) / n, f"Ilustrando la escena {i} de {n}...")
        prompt = imagenes.armar_prompt(historia, genero, i)
        imagenes.generar_imagen(pipe, prompt, imagenes.semilla_escena(i), carpeta / f"escena_{i}.png")
        prompts.append(prompt)
    del pipe
    liberar_memoria()
    tiempos["imagenes"] = round(time.time() - inicio, 1)

    # 3. Sonido ambiente
    inicio = time.time()
    avance(0.6, "Cargando el modelo de sonido...")
    pipe = sonido.cargar_modelo()
    for i, escena in enumerate(historia["escenas"], start=1):
        avance(0.6 + 0.3 * (i - 1) / n, f"Generando el sonido de la escena {i} de {n}...")
        sonido.generar_sonido(pipe, escena["sonido"], carpeta / f"sonido_{i}.wav")
    del pipe
    liberar_memoria()
    tiempos["sonidos"] = round(time.time() - inicio, 1)

    # 4. Voz
    inicio = time.time()
    avance(0.9, "Generando la narración...")
    narrador = voz.cargar_modelo()
    for i, escena in enumerate(historia["escenas"], start=1):
        voz.generar_voz(narrador, escena["texto"], carpeta / f"voz_{i}.wav")
    tiempos["voz"] = round(time.time() - inicio, 1)
    tiempos["total"] = round(sum(tiempos.values()), 1)
    avance(1.0, "Listo")

    # Registro de la prueba: entrada, parámetros, resultado y tiempos
    registro = {
        "idea": idea,
        "genero": genero,
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "configuracion": {
            "modelo_texto": config.MODELO_TEXTO,
            "temperatura": config.TEMPERATURA,
            "modelo_imagen": config.MODELO_IMAGEN.name,
            "pasos_imagen": config.PASOS_IMAGEN,
            "estrategia_consistencia": config.ESTRATEGIA_CONSISTENCIA,
            "semilla": config.SEMILLA,
            "modelo_sonido": config.MODELO_SONIDO.name,
            "pasos_sonido": config.PASOS_SONIDO,
            "modelo_voz": config.MODELO_VOZ.name,
            "dispositivo": imagenes.dispositivo()[0],
        },
        "historia": historia,
        "prompts_imagen": prompts,
        "tiempos_segundos": tiempos,
    }
    with open(carpeta / "cuento.json", "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, ensure_ascii=False, indent=2)

    return carpeta, registro
