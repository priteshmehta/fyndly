#!/bin/bash

# Run Frontend
docker run --env-file .env -p 8501:8501 --network app_network -e API_SERVER=backend -e API_PORT=8000 fyndly-app-frontend
