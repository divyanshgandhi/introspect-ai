#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt

# Start the API server in the background
cd api
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for API server to start..."
sleep 5

# Run the test script
cd ..
python3 test_api.py

# Kill the server process
kill $SERVER_PID 