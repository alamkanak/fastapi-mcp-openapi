#!/bin/bash

# Setup script for fastapi-mcp-openapi development

echo "Setting up fastapi-mcp-openapi development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install package in development mode
echo "Installing package in development mode..."
pip install -e .

echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "source venv/bin/activate"
echo ""
echo "To run the basic example:"
echo "python examples/basic_example.py"
echo ""
echo "To run the advanced example:"
echo "python examples/advanced_example.py"
echo ""
echo "To run tests:"
echo "python tests/test_basic.py"
