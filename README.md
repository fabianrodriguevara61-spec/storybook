# Storybook: cuentos ilustrados generados localmente

Proyecto integrador de la electiva Inteligencia Artificial Generativa, Ingeniería de Sistemas, Universidad Santo Tomás, seccional Tunja.

Integrantes: Edward Fernando Ávila Ojeda y Fabián Rodríguez Guevara.

La aplicación recibe una idea y un tipo de historia y genera un cuento de cinco escenas. Cada escena tiene texto, una ilustración, narración con voz sintética y un sonido ambiente. Todo se genera en el computador, sin APIs de pago ni servicios en la nube.

| Parte | Herramienta | Modelo |
|---|---|---|
| Texto | Ollama | Llama 3.1 8B (o Llama 3.2 3B) |
| Imagen | diffusers | SD-Turbo (Stability AI) |
| Sonido ambiente | diffusers | AudioLDM S Full v2 |
| Voz | Piper | es_MX-ald-medium |
| Interfaz | Streamlit | — |

## Requisitos

- Windows 10/11, Linux o macOS.
- Python 3.11.
- [Ollama](https://ollama.com/download) 0.5 o superior.
- RAM: 16 GB recomendado. Con 8 GB se debe usar el modelo de texto `llama3.2:3b`.
- GPU NVIDIA opcional. Sin GPU funciona en CPU, pero es más lento.
- Unos 15 GB libres en disco para las dependencias y los modelos.

## Instalación

Estos pasos necesitan Internet solo la primera vez.

1. Clonar el repositorio:

   ```
   git clone https://github.com/SantiaGonzav/storybook.git
   cd storybook
   ```

2. Crear y activar un entorno virtual:

   ```
   py -3.11 -m venv .venv
   .venv\Scripts\activate
   ```

   En Linux o macOS: `python3.11 -m venv .venv` y `source .venv/bin/activate`.

3. (Solo si tiene GPU NVIDIA) instalar PyTorch con CUDA antes que lo demás:

   ```
   pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cu121
   ```

4. Instalar las dependencias:

   ```
   pip install -r requirements.txt
   ```

5. Descargar el modelo de texto con Ollama:

   ```
   ollama pull llama3.1:8b
   ```

   Si el equipo tiene 8 GB de RAM, descargar `llama3.2:3b` y cambiar `MODELO_TEXTO` en `config.py`.

6. Descargar los modelos de imagen, sonido y voz:

   ```
   python descargar_modelos.py
   ```

   Los modelos quedan en la carpeta `modelos/`:

   ```
   modelos/
   ├── sd-turbo/              (imagen)
   ├── audioldm-s-full-v2/    (sonido)
   └── voz/es_MX-ald-medium.onnx y .onnx.json
   ```

   Ollama guarda su modelo en su propia carpeta (`~/.ollama/models`).

Después de estos pasos la aplicación funciona sin conexión a Internet.

## Ejecución

Con Ollama abierto y el entorno virtual activado:

```
streamlit run app.py
```

Se abre el navegador en `http://localhost:8501`.

## Ejemplo de uso

1. En "Idea de la historia" escribir: `una niña encuentra un dragón pequeño herido en el bosque`.
2. En "Tipo de historia" elegir `Fantasía`.
3. Pulsar "Generar cuento" y esperar a que termine la barra de progreso.
4. Usar "Anterior" y "Siguiente" para recorrer las cinco escenas. En cada una se ve la imagen y el texto, y hay un reproductor para la narración y otro para el sonido ambiente.

Cada cuento se guarda en `salidas/AAAAMMDD_HHMMSS/` con las imágenes, los audios y un archivo `cuento.json` que registra la idea, el género, los parámetros usados, la historia, los prompts de imagen y los tiempos de cada etapa.

## Configuración

Todo se cambia en `config.py`:

| Variable | Qué hace | Valor por defecto |
|---|---|---|
| `MODELO_TEXTO` | Modelo de Ollama | `llama3.1:8b` |
| `TEMPERATURA` | Creatividad del texto | `0.8` |
| `PASOS_IMAGEN` | Pasos de difusión de SD-Turbo (1 a 4) | `2` |
| `ESTRATEGIA_CONSISTENCIA` | `ficha` o `simple` (ver documento técnico) | `ficha` |
| `SEMILLA` | Semilla para resultados reproducibles | `42` |
| `PASOS_SONIDO` | Pasos de difusión de AudioLDM | `20` |
| `DURACION_SONIDO` | Duración del ambiente en segundos | `6.0` |
| `VOLUMEN_SONIDO` | Volumen máximo del ambiente | `0.4` |

## Estructura del proyecto

```
storybook/
├── app.py                 interfaz (Streamlit)
├── cuento.py              une las etapas y guarda los resultados
├── historia.py            texto con Ollama
├── imagenes.py            ilustraciones con SD-Turbo
├── sonido.py              sonido ambiente con AudioLDM
├── voz.py                 narración con Piper
├── config.py              parámetros
├── descargar_modelos.py   descarga de modelos
├── requirements.txt
└── LICENSE
```

## Problemas comunes

- "No se pudo conectar con Ollama": abrir la aplicación Ollama o ejecutar `ollama serve`.
- "El modelo ... no está descargado": ejecutar `ollama pull` con el nombre del modelo.
- "Faltan modelos": ejecutar `python descargar_modelos.py`.
- El audio no arranca solo: algunos navegadores bloquean la reproducción automática; pulsar play en el reproductor.

## Licencias

El código de este repositorio está bajo licencia MIT. Los modelos no se incluyen en el repositorio y cada uno tiene su propia licencia:

- Llama 3.1: Llama 3.1 Community License (Meta).
- SD-Turbo: Stability AI Community License. Powered by Stability AI.
- AudioLDM S Full v2: CC BY-NC-SA 4.0.
- Voz es_MX-ald-medium (Piper): The Unlicense.
- Piper TTS: GPL-3.0.
