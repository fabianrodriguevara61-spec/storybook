"""Generación de las ilustraciones con SD-Turbo (Stable Diffusion) de forma local."""

import torch
from diffusers import AutoPipelineForText2Image

import config


def dispositivo():
    """Usa la GPU si hay una con CUDA; si no, la CPU."""
    if torch.cuda.is_available():
        return "cuda", torch.float16
    return "cpu", torch.float32


def cargar_modelo():
    equipo, tipo = dispositivo()
    pipe = AutoPipelineForText2Image.from_pretrained(str(config.MODELO_IMAGEN), torch_dtype=tipo)
    pipe.set_progress_bar_config(disable=True)
    return pipe.to(equipo)


def armar_prompt(historia, genero, numero):
    """Arma el prompt de la escena según la estrategia de consistencia elegida.

    CLIP solo lee unos 77 tokens, por eso lo más importante va primero.
    """
    escena = historia["escenas"][numero - 1]
    if config.ESTRATEGIA_CONSISTENCIA == "ficha":
        return ", ".join([
            config.GENEROS[genero],
            historia["personaje"]["descripcion_visual"],
            escena["imagen"],
            historia["escenario"],
        ])
    return escena["imagen"]


def semilla_escena(numero):
    if config.ESTRATEGIA_CONSISTENCIA == "ficha":
        return config.SEMILLA
    return config.SEMILLA + numero


def generar_imagen(pipe, prompt, semilla, ruta):
    equipo, _ = dispositivo()
    generador = torch.Generator(equipo).manual_seed(semilla)
    imagen = pipe(
        prompt=prompt,
        num_inference_steps=config.PASOS_IMAGEN,
        guidance_scale=0.0,  # SD-Turbo se usa sin guidance
        width=config.TAMANO_IMAGEN,
        height=config.TAMANO_IMAGEN,
        generator=generador,
    ).images[0]
    imagen.save(ruta)
