#!/bin/bash
# run.sh - Quick launcher for Ghost Kitchen AI Platform

echo "🍽️ Ghost Kitchen AI Platform Launcher"
echo "======================================"
echo ""
echo "Select option:"
echo "1) Validate setup"
echo "2) Run planning cycle (one-time)"
echo "3) Start API server"
echo "4) Test individual components"
echo "5) Start with Docker"
echo "6) Exit"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo "Validating setup..."
        python scripts/validate_setup.py
        ;;
    2)
        echo "Running planning cycle..."
        python scripts/start_platform.py
        ;;
    3)
        echo "Starting API server..."
        python main.py
        ;;
    4)
        echo "Testing components..."
        python scripts/test_components.py
        ;;
    5)
        echo "Starting with Docker..."
        docker-compose up -d
        echo "Server running at http://localhost:8000"
        echo "Check logs: docker-compose logs -f"
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac