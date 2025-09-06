# AI Orchestration Platform - Makefile
# Authors: Dr. Sarah Chen & Alex Novak
# Description: Common development operations for the monorepo

.PHONY: help setup install install-hooks test clean run-backend run-frontend run-all lint format

# Default target
help:
	@echo "AI Orchestration Platform - Development Commands"
	@echo "================================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup       - Complete development environment setup"
	@echo "  make install     - Install all dependencies"
	@echo "  make install-hooks - Install git pre-commit hooks"
	@echo ""
	@echo "Development:"
	@echo "  make run-backend - Start FastAPI backend (port 8000)"
	@echo "  make run-frontend- Start Angular frontend (port 4200)"
	@echo "  make run-all     - Start all services"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test        - Run all tests with coverage"
	@echo "  make lint        - Run linters (Python & TypeScript)"
	@echo "  make format      - Auto-format code"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       - Clean temporary files and caches"
	@echo ""

# Setup development environment
setup:
	@echo "🔧 Setting up development environment..."
	@python -m venv .venv || true
	@.venv/Scripts/activate || source .venv/bin/activate
	@pip install -e . -q
	@cd apps/web && npm install
	@python tools/scripts/install_git_hooks.py --force
	@echo "✅ Setup complete!"

# Install git hooks
install-hooks:
	@echo "🛡️ Installing git pre-commit hooks..."
	@python tools/scripts/install_git_hooks.py
	@echo "✅ Git hooks installed!"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@pip install -r apps/api/requirements.txt
	@pip install -e .
	@cd apps/web && npm install
	@cd apps/desktop && npm install
	@echo "✅ Dependencies installed!"

# Run backend
run-backend:
	@echo "🚀 Starting FastAPI backend..."
	@cd apps/api && python main.py

# Run frontend
run-frontend:
	@echo "🚀 Starting Angular frontend..."
	@cd apps/web && npm start

# Run all services
run-all:
	@echo "🚀 Starting all services..."
	@start cmd /k "cd apps/api && python main.py"
	@start cmd /k "cd apps/web && npm start"

# Run tests
test:
	@echo "🧪 Running tests..."
	@pytest tests/unit/ -xvs --cov=apps --cov=libs --cov-report=term-missing
	@cd apps/web && npm test

# Lint code
lint:
	@echo "🔍 Running linters..."
	@flake8 apps/ libs/ --max-line-length=100 --ignore=E501,W503
	@cd apps/web && npm run lint

# Format code
format:
	@echo "✨ Formatting code..."
	@black apps/ libs/ tests/ --line-length=100
	@cd apps/web && npm run format

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ 2>/dev/null || true
	@rm -rf apps/web/dist 2>/dev/null || true
	@echo "✅ Cleaned!"