import streamlit as st
import requests
import time
from app.config import settings

st.title("💬 Chat with your AI assistent")
BACKEND_URL = f"http://{settings.api_server}:{settings.api_port}"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        thinking = st.empty()
        token_info = st.empty()
        thinking.markdown("⏳ Thinking...")
        placeholder = st.empty()
        full_response = ""
        try:
            response = requests.post(f"{BACKEND_URL}/chat", json={"question": question}, stream=True)
            #print(response.status_code, response)  # Debugging line
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    full_response += line
                    total_tokens += len(line.split()) 
                    placeholder.markdown(full_response)
                    token_info.caption(f"🔢 Estimated tokens: {total_tokens}")
            thinking.empty()
        except Exception as e:
            thinking.empty()
            placeholder.error("Failed to get answer. Backend not reachable?")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
