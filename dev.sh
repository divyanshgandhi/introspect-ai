#!/bin/bash

# Start the backend API server
echo "Starting backend API server..."
cd backend
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Start the backend server
echo "Starting backend server..."
cd api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Go back to root directory
cd ../..

# Start the frontend development server
echo "Starting frontend development server..."
cd frontend

# Install npm dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

# Set environment variable for development
export VITE_API_URL=http://localhost:8000

# Start the frontend server
npm run dev &
FRONTEND_PID=$!

# Function to handle script termination
function cleanup {
  echo "Shutting down servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}

# Register the cleanup function for when script is terminated
trap cleanup SIGINT SIGTERM

echo "Development environment is running!"
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both servers."

# Keep the script running
wait 