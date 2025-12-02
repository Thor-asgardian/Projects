#!/bin/bash

# AI Transaction Categorizer - Setup Script
# Run this to set up the entire project

echo "AI Transaction Categorizer - Setup"
echo ""

# Check Python version
echo "→ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $python_version"

# Create virtual environment
echo ""
echo "→ Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "→ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "→ Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo ""
echo "→ Creating project directories..."
mkdir -p models
mkdir -p outputs
mkdir -p data
mkdir -p config

# Train the model
echo ""
echo "→ Training the model and generating config..."
# This script now handles data generation, config creation, and model training
python train.py

echo ""
echo "✓ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Run demo: streamlit run app.py"
echo "3. Test predictions: python predict.py"
echo ""