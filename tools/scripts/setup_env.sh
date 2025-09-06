#!/bin/bash
# @fileoverview Environment setup script for monorepo development
# @author Dr. Sarah Chen & Alex Novak
# @description Sets up Python paths and environment for development

# Get the root directory of the monorepo
MONOREPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🔧 Setting up AI Orchestration Platform development environment..."
echo "📁 Monorepo root: $MONOREPO_ROOT"

# Export PYTHONPATH to include all necessary directories
export PYTHONPATH="$MONOREPO_ROOT:$MONOREPO_ROOT/libs:$MONOREPO_ROOT/apps:$PYTHONPATH"
echo "✅ PYTHONPATH configured"

# Set NODE_PATH for TypeScript imports
export NODE_PATH="$MONOREPO_ROOT/node_modules:$MONOREPO_ROOT/libs"
echo "✅ NODE_PATH configured"

# Create Python virtual environment if it doesn't exist
if [ ! -d "$MONOREPO_ROOT/.venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv "$MONOREPO_ROOT/.venv"
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source "$MONOREPO_ROOT/.venv/Scripts/activate" 2>/dev/null || source "$MONOREPO_ROOT/.venv/bin/activate"
echo "✅ Virtual environment activated"

# Install Python dependencies in development mode
echo "📦 Installing Python packages in development mode..."
cd "$MONOREPO_ROOT"
pip install -e . --quiet
echo "✅ Python packages installed"

# Install git hooks for governance
echo "🛡️ Installing git pre-commit hooks..."
python "$MONOREPO_ROOT/tools/scripts/install_git_hooks.py" --force
echo "✅ Git hooks installed"

# Function to run backend
run_backend() {
    echo "🚀 Starting FastAPI backend..."
    cd "$MONOREPO_ROOT/apps/api"
    python main.py
}

# Function to run frontend
run_frontend() {
    echo "🚀 Starting Angular frontend..."
    cd "$MONOREPO_ROOT/apps/web"
    npm start
}

# Function to run tests
run_tests() {
    echo "🧪 Running tests..."
    cd "$MONOREPO_ROOT"
    pytest tests/ -xvs
}

# Export functions for use in terminal
export -f run_backend
export -f run_frontend
export -f run_tests

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "Available commands:"
echo "  run_backend  - Start the FastAPI backend"
echo "  run_frontend - Start the Angular frontend"
echo "  run_tests    - Run all tests"
echo ""
echo "Dr. Sarah Chen: 'The Three Questions Framework is active'"
echo "Alex Novak: 'All systems defensive and ready'"