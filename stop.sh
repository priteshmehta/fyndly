#!/bin/bash
# Stop and remove the Docker container for Fyndly app
docker ps -a  | grep fyndly-app* | awk '{print $1}' | xargs -r docker rm -f
