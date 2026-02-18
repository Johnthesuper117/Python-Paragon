#!/bin/bash
# Setup script for PythonParagon

echo "=========================================="
echo "  PythonParagon Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version

if [ $? -ne 0 ]; then
    echo "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment (optional)
echo ""
read -p "Do you want to create a virtual environment? (recommended) [y/N]: " create_venv

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python -m venv venv
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Virtual environment created and activated."
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Run PythonParagon with:"
    echo "  python main.py"
    echo ""
    echo "Or try the demo:"
    echo "  ./demo.sh"
    echo ""
else
    echo ""
    echo "Error: Failed to install dependencies."
    exit 1
fi
