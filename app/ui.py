import streamlit as st
import requests
from config import settings

st.set_page_config(page_title="Fyndly", layout="centered")

st.title("📘 How can I help you?")

st.subheader(f"Website:{settings.web_site}")
question = st.text_area("Question", placeholder="What is the main product offered on this site?", value="What is the main product offered on this site?")

if st.button("Ask"):
    with st.spinner("Thinking..."):
        try:
            res = requests.post("http://127.0.0.1:8000/ask", json={"question": question})
            print(res.status_code, question)  # Debugging line
            answer = res.json().get("answer", "No response")
            st.success(f"Answer: {answer}")
        except Exception as e:
            st.error(f"Failed: {str(e)}")

if st.button("RAG Ask"):    
    with st.spinner("Thinking..."):
        try:
            res = requests.post("http://127.0.0.1:8000/rag", json={"question": question})
            print(res.status_code, question)  # Debugging line
            answer = res.json().get("answer", "No response")
            st.success(f"Answer: {answer}")
        except Exception as e:
            st.error(f"Failed: {str(e)}")
