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