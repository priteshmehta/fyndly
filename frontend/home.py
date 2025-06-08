import streamlit as st
import requests
import time
from app.config import settings

st.set_page_config(page_title="Fyndly", layout="wide")
BACKEND_URL = f"http://{settings.api_server}:{settings.api_port}"

# Sidebar Navigation
st.sidebar.title("🧭 Navigation")
section = st.sidebar.radio("Go to", ["Chat", "Upload PDF", "Crawl & Maintenance"])

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Section 1: Chat Interface ---
if section == "Chat":
    st.title("💬 Ask Questions from Your Docs")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if question := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            thinking = st.empty()
            thinking.markdown("⏳ Thinking...")
            placeholder = st.empty()
            full_response = ""
            try:
                response = requests.post(f"{BACKEND_URL}/ask", json={"question": question}, stream=True)
                print(response.status_code, response)  # Debugging line
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        full_response += line
                        placeholder.markdown(full_response)
                thinking.empty()
            except Exception as e:
                thinking.empty()
                placeholder.error("Failed to get answer. Backend not reachable?")

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Section 2: Upload PDF ---
elif section == "Upload PDF":
    st.title("📄 Upload PDF Document")
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file:
        with st.spinner("Uploading and processing..."):
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            res = requests.post(f"{BACKEND_URL}/upload-pdf", files=files)
            if res.status_code == 200:
                st.success("File uploaded and indexed successfully!")
            else:
                st.error("Failed to upload PDF.")

# --- Section 3: Crawl & Maintenance ---
elif section == "Crawl & Maintenance":
    st.title("🛠️ Crawler and Maintenance")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Recrawl Website"):
            with st.spinner("Re-crawling in progress..."):
                res = requests.post(f"{BACKEND_URL}/crawl-now")
                st.success("Crawl complete!" if res.ok else "Failed to crawl.")

    with col2:
        if st.button("🧹 Flush DB"):
            with st.spinner("Flushing database..."):
                res = requests.post(f"{BACKEND_URL}/api/flush")
                st.success("Database flushed." if res.ok else "Flush failed.")

    # Optional: show indexed sources
    st.subheader("📚 Indexed Sources")
    try:
        res = requests.get(f"{BACKEND_URL}/debug/chroma")
        sources = res.json()
        st.write(sources)
    except:
        st.error("Couldn't fetch indexed sources.")
