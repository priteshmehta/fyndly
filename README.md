# fyndly

# 🧠 Fyndly

Ask questions directly about a specific website using GPT-4o — powered by periodic crawling, Chroma vector search, and hallucination-resistant guardrails.

---



             ┌──────────────┐
             │ Input Docs   │
             └────┬─────────┘
                  ↓
        ┌─────────────────────┐
        │ Chunking & Cleaning │
        └────┬────────────────┘
             ↓
    ┌──────────────────────┐
    │OpenAI Embeddings API │   <-- Expensive but excellent quality
    └────┬─────────────────┘
         ↓
   ┌────────────────┐
   │ ChromaDB (local)│  <-- Local storage, indexed
   └────┬────────────┘
        ↓
     Top-k context
        ↓
  ┌────────────────────┐
  │ LLM (e.g., Ollama/chatGPT) │ <-- Local model for reasoning/generation
  └────────────────────┘


## 🚀 Features

- 🔁 Periodic async crawling of any website (only your domain)
- 💾 Stores data as embeddings using **Chroma DB**
- 💬 GPT-4o answers only using retrieved content (via tool call)
- 🛡️ Validated responses with **Guardrails-AI**
- 🖥️ Streamlit frontend + FastAPI backend in a single Docker container

---

## 📦 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI GPT-4o](https://platform.openai.com/)
- [Chroma Vector DB](https://www.trychroma.com/)
- [LangChain](https://www.langchain.com/)
- [Guardrails-AI](https://www.guardrailsai.com/)
- [Streamlit](https://streamlit.io/)
- [Render](https://render.com/) for hosting

---

## 📁 Project Structure

### Secrets
1. Rename `.env.example` to `.env`
2. update `.env` file with OpenAI Api Key

### Local Dev Dev setup for Python 3.11
```sh
brew install pyenv
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -U langchain-community

streamlit run app/ui.py --server.port 8501 # run frontend app 
```
### Docker Setup
Build & Run Docker Image
```sh
./build.sh
./run_docker_backend.sh 
./run_docker_frontend.sh
./stop.sh  # shutdown
```
App Server
```sh
Frontend: http://localhost:8501
Backend: http://localhost:8000
```
