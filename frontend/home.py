import streamlit as st
import requests
import time
from app.config import settings

st.set_page_config(page_title="Fyndly", layout="wide")
BACKEND_URL = f"http://{settings.api_server}:{settings.api_port}"

pages = {
    "Menu": [
        st.Page("chat.py", title="Chat with AI agent"),
        st.Page("search.py", title="Search your documents"),
    ],
    "Admin": [
        st.Page("admin.py", title="Admin Dashboard"),
    ],
}
pg = st.navigation(pages)
pg.run()

