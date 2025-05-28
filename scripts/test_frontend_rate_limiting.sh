#!/bin/bash

echo "🧪 Testing Frontend Rate Limiting Integration..."

# Function to cleanup processes
cleanup() {
    echo "🛑 Cleaning up processes..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Start backend
echo "🚀 Starting backend API server..."
cd backend

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Install dependencies
pip install -r requirements.txt > /dev/null 2>&1

# Start the API server in the background
cd api
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "✅ Backend started successfully"

# Start frontend
echo "🚀 Starting frontend development server..."
cd ../../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "📦 Installing frontend dependencies..."
  npm install > /dev/null 2>&1
fi

# Set environment variable for development
export VITE_API_URL=http://localhost:8000

# Start the frontend server in the background
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if ! curl -s http://localhost:5173 > /dev/null; then
    echo "❌ Frontend failed to start"
    exit 1
fi

echo "✅ Frontend started successfully"
echo ""
echo "🌐 Application is now running:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   Rate Limit Status: http://localhost:8000/api/rate-limit-status"
echo ""
echo "🧪 Test the rate limiting by:"
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. Try processing content multiple times"
echo "   3. Observe the rate limit counter below the button"
echo "   4. After 5 requests, you should see the rate limit message"
echo ""
echo "🛑 Press Ctrl+C to stop both servers"

# Keep the script running
wait 