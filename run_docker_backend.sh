#!/bin/bash

# Run Backend
docker run --env-file .env -p 8000:8000 --network app_network --hostname backend fyndly-app
