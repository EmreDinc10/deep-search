#!/bin/bash

# Start script for the backend server
echo "Starting Deep Search Backend..."

# Set Python path to include virtual environment
export PYTHONPATH="/Users/emredinc/projects/deep-search/backend/venv/lib/python3.13/site-packages:$PYTHONPATH"

# Copy environment variables
if [ ! -f ".env" ]; then
    echo "Copying environment template..."
    cp .env.example .env
    echo "Please update .env with your Azure OpenAI credentials"
fi

# Start the server
echo "Starting FastAPI server..."
/opt/homebrew/opt/python@3.13/bin/python3.13 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
