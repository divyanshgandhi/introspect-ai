#!/bin/bash

echo "🧪 Testing Rate Limiting Functionality..."

# Change to backend directory from scripts directory
cd ../backend

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt

# Start the API server in the background
cd api
echo "🚀 Starting API server..."
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for API server to start..."
sleep 5

# Run the rate limiting test
echo "🔬 Running rate limiting tests..."
cd ../tests
python3 test_rate_limiting.py

echo ""
echo "✅ Rate limiting tests completed!"
echo ""
echo "🛑 Stopping API server..."

# Kill the server process
kill $SERVER_PID

echo "✨ Done!" 