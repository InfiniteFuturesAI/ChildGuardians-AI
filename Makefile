# =============================================================================
# CHILD GUARDIANS - Makefile
# =============================================================================
# Common development and deployment tasks
# Usage: make <target>
# =============================================================================

.PHONY: help install dev test lint format type-check security build run clean docker-build docker-run

# Default target
help:
	@echo "CHILD GUARDIANS - Development Commands"
	@echo "======================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install      Install production dependencies"
	@echo "  make dev          Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test         Run all tests"
	@echo "  make test-cov     Run tests with coverage report"
	@echo "  make lint         Run linting (ruff)"
	@echo "  make format       Format code (black + ruff)"
	@echo "  make type-check   Run type checking (mypy)"
	@echo "  make security     Run security scan (bandit)"
	@echo "  make check        Run all checks (lint + type-check + test)"
	@echo ""
	@echo "Running:"
	@echo "  make run          Run development server"
	@echo "  make run-prod     Run production server"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build Build Docker image"
	@echo "  make docker-run   Run Docker container"
	@echo "  make docker-test  Run tests in Docker"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        Remove build artifacts"

# =============================================================================
# Setup
# =============================================================================

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

# =============================================================================
# Development
# =============================================================================

test:
	pytest -v tests/

test-cov:
	pytest --cov=child_guardians --cov-report=html --cov-report=term tests/
	@echo "Coverage report: htmlcov/index.html"

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

type-check:
	mypy src/

security:
	bandit -r src/ -ll

check: lint type-check test

# =============================================================================
# Running
# =============================================================================

run:
	uvicorn child_guardians.api.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uvicorn child_guardians.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# =============================================================================
# Docker
# =============================================================================

docker-build:
	docker build -t child-guardians:latest .

docker-run:
	docker run -p 8000:8000 child-guardians:latest

docker-test:
	docker build -f Dockerfile.dev -t child-guardians-test:latest .
	docker run child-guardians-test:latest pytest -v

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

# =============================================================================
# Cleanup
# =============================================================================

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
