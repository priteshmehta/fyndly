import streamlit as st
import requests
import time
from app.config import settings

BACKEND_URL = f"http://{settings.api_server}:{settings.api_port}"

st.title("💬 Ask Questions from Your Docs")
question = st.text_area("Question", placeholder="What is the main product offered on this site?", value="What is the main product offered on this site?")
st.write("backend_url:", BACKEND_URL)  # Debugging line
col1, col2 = st.columns(2)
with col1:
    if st.button("Ask"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(f"{BACKEND_URL}/ask", json={"question": question})
                print(res.status_code, question)  # Debugging line
                answer = res.json().get("answer", "No response")
                st.success(f"Answer: {answer}")
            except Exception as e:
                st.error(f"Failed: {str(e)}")
with col2:
    if st.button("RAG Ask"):    
        with st.spinner("Thinking..."):
            try:
                res = requests.post(f"{BACKEND_URL}/rag", json={"question": question})
                print(res.status_code, question)  # Debugging line
                answer = res.json().get("answer", "No response")
                st.success(f"Answer: {answer}")
            except Exception as e:
                st.error(f"Failed: {str(e)}")
