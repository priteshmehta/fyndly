import streamlit as st
import requests
import time
from app.config import settings

st.title("📄 Upload PDF Document")
BACKEND_URL = f"http://{settings.api_server}:{settings.api_port}"

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Uploading and processing..."):
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        res = requests.post(f"{BACKEND_URL}/upload-pdf", files=files)
        if res.status_code == 200:
            st.success("File uploaded and indexed successfully!")
        else:
            st.error("Failed to upload PDF.")

# --- Section 4: Crawl & Maintenance ---
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