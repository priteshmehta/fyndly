#!/bin/bash

# Run Backend
docker run --env-file .env -p 8000:8000 -p 8501:8501 fyndly-app
