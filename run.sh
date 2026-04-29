#!/bin/bash
set -e

echo "Starting SkinBudget Engine..."

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "1. Starting application stack via Docker Compose..."
docker compose up -d --build

echo "2. Application is starting..."
echo "Access the application at http://localhost:8000"
