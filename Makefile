# Makefile - Ghost Kitchen AI Platform

.PHONY: help install validate run-cycle run-api test docker-up docker-down clean

help:
	@echo "Ghost Kitchen AI Platform - Commands"
	@echo "===================================="
	@echo "make install      - Install dependencies"
	@echo "make validate     - Validate setup and configuration"
	@echo "make run-cycle    - Run single planning cycle"
	@echo "make run-api      - Start API server"
	@echo "make test         - Test individual components"
	@echo "make docker-up    - Start with Docker"
	@echo "make docker-down  - Stop Docker containers"
	@echo "make clean        - Clean logs and cache"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	mkdir -p logs prompts/templates
	@echo "✅ Dependencies installed"

validate:
	python scripts/validate_setup.py

run-cycle:
	python scripts/start_platform.py

run-api:
	python main.py

test:
	python scripts/test_components.py

docker-up:
	docker-compose up -d
	@echo "✅ Platform running at http://localhost:8000"
	@echo "View logs: docker-compose logs -f"

docker-down:
	docker-compose down

clean:
	rm -rf logs/*.log
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache
	@echo "✅ Cleaned logs and cache"

# Development commands
dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

format:
	black .

lint:
	flake8 .

# Quick start (validates then runs)
start: validate run-cycle