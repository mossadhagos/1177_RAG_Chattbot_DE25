# uv run streamlit run frontend/src/frontend/app.py
import streamlit as st
from frontend import api_client as api

HISTORY_TURNS = 6


def init_session_states():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def add_message(role: str, content: str, **extra):
    st.session_state.messages.append({"role": role, "content": content, **extra})


def display_message(message: dict):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for source in message.get("sources", []):
            st.markdown(f":material/link: [{source}]({source})")


def display_chat_messages():
    for message in st.session_state.messages:
        display_message(message)


def recent_history() -> list[dict]:
    return [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-HISTORY_TURNS:]
        if not m.get("error")
    ]


def handle_question(question: str):
    add_message("user", question)
    try:
        with st.spinner("Tänker..."):
            answer = api.ask_chat(recent_history())
        add_message("assistant", answer["answer"], sources=answer["sources"])
    except api.BackendError as error:
        add_message("assistant", f"Något gick fel: {error}", error=True)
    st.rerun()


def layout():
    st.title("VårdTolken")
    display_chat_messages()
    if question := st.chat_input("Skriv din fråga"):
        handle_question(question)


if __name__ == "__main__":
    init_session_states()
    layout()
