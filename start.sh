#!/bin/bash

# Start backend in background
cd /app/backend
python run_api.py &

# Start frontend
cd /app/frontend
serve -s dist -l 8080 &

# Keep container running
wait 