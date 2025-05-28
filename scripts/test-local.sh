#!/bin/bash

echo "🧪 Testing Introspect AI (Microservice Mode) Locally..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating a test .env file with placeholder values..."
    cp environment.example .env
    echo ""
    echo "📝 Please edit .env with your actual API keys before production deployment."
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start containers for local testing
echo "🔨 Building and starting containers for local testing..."
docker-compose -f docker-compose.prod.yml up --build

echo ""
echo "🧪 Local testing complete!"
echo ""
echo "📍 Test your microservices directly at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   Health:   http://localhost:8000/health"
echo ""
echo "🔗 When integrated with your main website, access via:"
echo "   https://www.divyanshgandhi.com/introspect"
echo "   https://www.divyanshgandhi.com/introspect/api/health"
echo ""
echo "📋 See docs/change-request.md for main website integration steps"
echo ""
echo "🛑 Press Ctrl+C to stop the test environment" 