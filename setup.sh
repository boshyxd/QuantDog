#!/bin/bash

echo "=== QuantDog Setup Script ==="

if ! command -v uv &> /dev/null; then
    echo "UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "Failed to install UV. Please install it manually from https://github.com/astral-sh/uv"
        exit 1
    fi
fi

echo "UV found: $(uv --version)"

echo "Installing dependencies with UV..."
uv sync --all-extras

if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
fi

echo "Running linter check..."
uv run ruff check . --fix

echo "Formatting code..."
uv run ruff format .

echo ""
echo "Setup complete!"
echo ""
echo "To start the app, run:"
echo "   uv run streamlit run app.py"
echo ""
echo "Or use the Makefile:"
echo "   make run"
echo ""
echo "Other useful commands:"
echo "   make test      # Run tests"
echo "   make lint      # Run linter"
echo "   make format    # Format code"