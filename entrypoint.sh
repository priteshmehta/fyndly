#!/bin/bash

# Run FastAPI backend
source .env
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run Streamlit frontend
#streamlit run app/ui.py --server.port 8501 --server.address 0.0.0.0

# Keep container alive
wait
