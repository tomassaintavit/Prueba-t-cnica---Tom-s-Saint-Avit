import requests
import streamlit as st

API_URL = "http://localhost:8000/query"

st.set_page_config(page_title="Asistente de Soporte RAG", page_icon="💬")
st.title("Asistente de Soporte")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Escribe tu pregunta de soporte..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en la documentación..."):
            try:
                resp = requests.post(API_URL, json={"question": question}, timeout=60)
                answer = resp.json()["answer"]
            except Exception as e:
                answer = f"Error al conectar con la API: {e}"
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
