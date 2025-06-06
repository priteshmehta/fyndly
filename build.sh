#!/bin/bash

# Build docker images
docker build -t fyndly-app .
docker build -t fyndly-app-frontend -f Dockerfile.frontend .