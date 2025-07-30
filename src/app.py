"""
The main application for the BitDogLab Chatbot.

This app handles the user's input (either an image or pseudocode) and runs the
appropriate agent to generate code or pseudocode. The app also displays the
generated code or pseudocode and allows the user to edit it.
"""

import streamlit as st

from coordinator import AgentCoordinator
from utils import split_code_fences

# --- Page Config ---
st.set_page_config(page_title="Assistente BitDogLab", layout="centered")
st.title("🐶 Assistente BitDogLab")


# --- Load Coordinator ---
@st.cache_resource(show_spinner="Iniciando agentes...")
def load_coordinator():
    """
    Loads the AgentCoordinator instance.

    The AgentCoordinator instance is cached to improve performance.

    Returns:
        The AgentCoordinator instance.
    """
    return AgentCoordinator()


coordinator = load_coordinator()

# --- Session State to track progress ---
if "pseudocode" not in st.session_state:
    st.session_state["pseudocode"] = ""
if "code" not in st.session_state:
    st.session_state["code"] = ""
if "image_path" not in st.session_state:
    st.session_state["image_path"] = None

# --- Inputs ---
uploaded_file = st.file_uploader(
    "Envie imagem de um fluxograma",
    type=["png", "jpg", "jpeg"],
)
st.markdown("**OU**")
pseudocode_input = st.text_area("Digite o pseudocódigo")

# --- Submit ---
if st.button("Enviar"):
    # Clear previous state
    st.session_state["pseudocode"] = ""
    st.session_state["pseudocode_preffix"] = None
    st.session_state["pseudocode_suffix"] = None
    st.session_state["code"] = ""
    st.session_state["image_path"] = None

    if uploaded_file:  # User uploaded an image
        with st.spinner("Analisando imagem...", show_time=True):
            response = coordinator.handle_input(uploaded_file, "")
        pc_preffix, pseudocode, pc_suffix = split_code_fences(response)
        st.session_state["pseudocode"] = pseudocode
        st.session_state["pseudocode_preffix"] = pc_preffix
        st.session_state["pseudocode_suffix"] = pc_suffix
        st.session_state["image_path"] = uploaded_file

    elif pseudocode_input.strip():  # User entered pseudocode
        with st.spinner("Gerando código...", show_time=True):
            code = coordinator.handle_input(None, pseudocode_input)
        st.session_state["code"] = code

    else:  # No input
        st.warning("Por favor, envie uma imagem ou insira o pseudocódigo.")

# --- Outputs ---
if st.session_state["pseudocode"] and st.session_state["image_path"]:
    st.subheader("📄 Pseudocódigo")
    if st.session_state["pseudocode_preffix"] is not None:
        st.markdown(st.session_state["pseudocode_preffix"])

    updated_pseudocode = st.text_area(
        "Pseudocódigo gerado",
        st.session_state["pseudocode"],
        height=120,
        key="pseudocode_display",
        label_visibility="collapsed",
    )

    if st.session_state["pseudocode_suffix"] is not None:
        st.markdown(st.session_state["pseudocode_suffix"])

    # Store any changes made by the user
    st.session_state["pseudocode"] = updated_pseudocode

    if st.button("✅ Validar e Gerar Código"):
        with st.spinner("Gerando código...", show_time=True):
            code = coordinator.generate_code(st.session_state["pseudocode"])
        st.session_state["code"] = code

if st.session_state["code"]:
    st.subheader("⌨️ Código Final")
    st.markdown(st.session_state["code"])
