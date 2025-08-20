#!/bin/bash

# Setup script for the entire Deep Search application

echo "🔍 Setting up Deep Search Application..."

# Setup Backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️ Please update backend/.env with your Azure OpenAI credentials"
fi

cd ..

# Setup Frontend
echo "🌐 Setting up Next.js frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Copy environment file
if [ ! -f ".env.local" ]; then
    cp .env.local.example .env.local
    echo "📝 Frontend environment file created"
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your Azure OpenAI credentials"
echo "2. Start the backend: cd backend && ./start.sh"
echo "3. Start the frontend: cd frontend && npm run dev"
echo ""
echo "🌐 The application will be available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
