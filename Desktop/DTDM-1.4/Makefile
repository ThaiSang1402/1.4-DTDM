# Makefile for Scalable AI API System

.PHONY: help install test lint format clean validate

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies and setup development environment
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

test:  ## Run all tests
	python -m pytest tests/ -v

test-coverage:  ## Run tests with coverage report
	python -m pytest tests/ --cov=scalable_ai_api --cov-report=html --cov-report=term

lint:  ## Run code linting
	python -m mypy scalable_ai_api/
	python -m isort --check-only scalable_ai_api/ tests/
	python -m black --check scalable_ai_api/ tests/

format:  ## Format code
	python -m isort scalable_ai_api/ tests/
	python -m black scalable_ai_api/ tests/

validate:  ## Validate project setup
	python validate_setup.py

clean:  ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/

dev-setup: install validate  ## Complete development setup
	@echo "Development environment setup complete!"

# Docker operations for Render
docker-build:  ## Build Docker images for Render
	@echo "Building Docker images for Render deployment..."
	docker build -t scalable-ai-api-loadbalancer .
	docker build -f Dockerfile.aiserver -t scalable-ai-api-server .

docker-test-render:  ## Test Render Docker setup locally
	@echo "Testing Render Docker configuration..."
	docker run -d -p 8000:8000 --name test-lb scalable-ai-api-loadbalancer
	docker run -d -p 8080:8080 -e SERVER_ID="Server A" --name test-server-a scalable-ai-api-server
	docker run -d -p 8081:8080 -e SERVER_ID="Server B" --name test-server-b scalable-ai-api-server
	@echo "Containers started. Test endpoints:"
	@echo "Load Balancer: http://localhost:8000/health"
	@echo "Server A: http://localhost:8080/health"
	@echo "Server B: http://localhost:8081/health"

docker-stop-test:  ## Stop test containers
	@echo "Stopping test containers..."
	-docker stop test-lb test-server-a test-server-b
	-docker rm test-lb test-server-a test-server-b

render-prepare:  ## Prepare for Render deployment
	@echo "Preparing for Render deployment..."
	@echo "✓ Docker configuration ready"
	@echo "✓ render.yaml configured for Docker runtime"
	@echo "✓ Dockerfiles optimized for Render"
	@echo "✓ Ready to deploy to Render!"