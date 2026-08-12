#!/usr/bin/env bash
set -e

echo "🚀 Starting AI Software Development Team Deployment..."

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker and try again."
    exit 1
fi

echo "📦 Building and launching containers via Docker Compose..."
docker-compose down
docker-compose up --build -d

echo "⏳ Waiting for PostgreSQL database to be healthy..."
docker-compose exec -T postgres pg_isready -U username -d ai_software_team

echo "🔄 Running Alembic Database Migrations..."
docker-compose exec -T backend python -m alembic upgrade head

echo "✅ Deployment successful!"
echo "🌐 Frontend available at: http://localhost"
echo "⚙️ Backend API available at: http://localhost:8000/docs"
