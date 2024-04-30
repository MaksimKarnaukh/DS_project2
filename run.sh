#!/bin/bash

podman-compose down

podman-compose up --build

sleep 3 
xdg-open http://127.0.0.1:5000

# # Prompt user to stop containers
# read -n 1 -s -r -p "Press any key to stop containers or Ctrl+C to exit"
# echo "Stopping containers..."


