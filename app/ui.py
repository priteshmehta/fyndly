import streamlit as st
import requests
from config import settings

st.set_page_config(page_title="Fyndly", layout="centered")
backend_url = f"http://{settings.api_server}:{settings.api_port}"

st.title("📘 How can I help you?")

st.subheader(f"Website:{settings.web_site}")
if st.button("Crawl Now"):
    with st.spinner("Crawling..."):    
        try:
            res = requests.get(f"{backend_url}/crawl-now")
            print(res.status_code)
            if res.status_code == 200:
                st.success("Crawl completed successfully!")
            else:
                st.error(f"Failed to crawl: {res.text}")
        except Exception as e:
            st.error(f"Failed: {str(e)}")

question = st.text_area("Question", placeholder="What is the main product offered on this site?", value="What is the main product offered on this site?")
if st.button("Ask"):
    with st.spinner("Thinking..."):
        try:
            st.write("backend_url:", backend_url)  # Debugging line
            res = requests.post(f"{backend_url}/ask", json={"question": question})
            print(res.status_code, question)  # Debugging line
            answer = res.json().get("answer", "No response")
            st.success(f"Answer: {answer}")
        except Exception as e:
            st.error(f"Failed: {str(e)}")

if st.button("RAG Ask"):    
    with st.spinner("Thinking..."):
        try:
            res = requests.post(f"{backend_url}/rag", json={"question": question})
            print(res.status_code, question)  # Debugging line
            answer = res.json().get("answer", "No response")
            st.success(f"Answer: {answer}")
        except Exception as e:
            st.error(f"Failed: {str(e)}")


      
st.title("Upload PDF to ChromaDB")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    if st.button("Upload"):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{backend_url}/upload-pdf", files=files)
        if response.status_code == 200:
            st.success("✅ " + response.json().get("message"))
        else:
            st.error("❌ Upload failed: " + response.text)