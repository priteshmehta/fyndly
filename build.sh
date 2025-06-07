#!/bin/bash

# Build docker images
docker network inspect app_network >/dev/null 2>&1 || docker network create app_network
docker build -t fyndly-app .
docker build -t fyndly-app-frontend -f Dockerfile.frontend .