#!/bin/bash

# Run Frontend
docker run --env-file .env -p 8501:8501 fyndly-app-frontend
