import streamlit as st
import requests

st.set_page_config(page_title="Fyndly", layout="centered")

st.title("📘 Ask a Website")

url = st.text_input("Website URL", placeholder="https://lycheethings.com", value="https://lycheethings.com")
question = st.text_area("Your Question", placeholder="What is the main product offered on this site?", value="What is the main product offered on this site?")

if st.button("Ask"):
    with st.spinner("Thinking..."):
        try:
            res = requests.post("http://127.0.0.1:8000/ask", json={"url": url, "question": question})
            print(res.status_code, question)  # Debugging line
            answer = res.json().get("answer", "No response")
            st.success("Answer:")
            st.write(answer)
        except Exception as e:
            st.error(f"Failed: {str(e)}")
