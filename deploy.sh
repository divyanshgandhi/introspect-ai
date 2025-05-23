#!/bin/bash

echo "🚀 Deploying Introspect AI (Microservice Mode)..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy environment.example to .env and fill in your API keys:"
    echo "cp environment.example .env"
    echo "Then edit .env with your actual API keys."
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.prod.yml up --build -d

# Check if containers are running
echo "⏳ Waiting for containers to start..."
sleep 10

if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Introspect AI services are now running:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8000"
    echo ""
    echo "🔗 Configure your main website nginx to route:"
    echo "   www.divyanshgandhi.com/introspect → localhost:3000"
    echo "   www.divyanshgandhi.com/introspect/api → localhost:8000"
    echo ""
    echo "📊 Monitor logs with:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f"
    echo ""
    echo "🔧 To stop the application:"
    echo "   docker-compose -f docker-compose.prod.yml down"
else
    echo "❌ Deployment failed! Check logs:"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi 