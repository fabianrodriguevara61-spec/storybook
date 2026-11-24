"""Interfaz de Storybook hecha con Streamlit.

Ejecutar con:  streamlit run app.py
"""

import streamlit as st

import config
from cuento import crear_cuento

st.set_page_config(page_title="Storybook")
st.title("Storybook")
st.write(
    "Escriba una idea y elija el tipo de historia. La aplicación crea un cuento de cinco escenas "
    "con ilustración, narración y sonido ambiente, todo generado en este equipo."
)


def cambiar_escena(paso):
    st.session_state.escena += paso


with st.form("entrada"):
    idea = st.text_area("Idea de la historia", placeholder="Ej: una niña encuentra un dragón pequeño herido en el bosque")
    genero = st.selectbox("Tipo de historia", list(config.GENEROS), index=None, placeholder="Seleccione un tipo")
    enviar = st.form_submit_button("Generar cuento")

if enviar:
    if not idea.strip():
        st.warning("Escriba la idea de la historia.")
    elif genero is None:
        st.warning("Seleccione el tipo de historia.")
    else:
        barra = st.progress(0.0, text="Iniciando...")
        try:
            carpeta, registro = crear_cuento(
                idea.strip(), genero, lambda valor, texto: barra.progress(valor, text=texto)
            )
        except Exception as error:
            barra.empty()
            st.error(f"No se pudo generar el cuento. {error}")
        else:
            barra.empty()
            st.session_state.cuento = registro
            st.session_state.carpeta = carpeta
            st.session_state.escena = 0

if "cuento" in st.session_state:
    registro = st.session_state.cuento
    carpeta = st.session_state.carpeta
    i = st.session_state.escena
    escena = registro["historia"]["escenas"][i]
    numero = i + 1

    st.divider()
    st.header(registro["historia"]["titulo"])
    st.caption(f"Escena {numero} de {config.NUM_ESCENAS}")
    st.image(str(carpeta / f"escena_{numero}.png"))
    st.write(escena["texto"])

    st.write("**Narración**")
    st.audio((carpeta / f"voz_{numero}.wav").read_bytes(), format="audio/wav", autoplay=True)
    st.write("**Sonido ambiente**")
    st.audio((carpeta / f"sonido_{numero}.wav").read_bytes(), format="audio/wav", loop=True, autoplay=True)

    anterior, siguiente = st.columns(2)
    anterior.button("Anterior", on_click=cambiar_escena, args=(-1,), disabled=i == 0, use_container_width=True)
    siguiente.button(
        "Siguiente", on_click=cambiar_escena, args=(1,),
        disabled=i == config.NUM_ESCENAS - 1, use_container_width=True,
    )

    st.caption(f"Tiempo total: {registro['tiempos_segundos']['total']} s. Archivos guardados en {carpeta}")
