#!/bin/bash
# nvdi Setup Script
# Author: Supun Hewagamage (@supunhg)

set -e

echo "🔧 Setting up nvdi..."

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install nvdi in editable mode
echo "🚀 Installing nvdi..."
pip install -e .

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your NVD API key"
    echo "   Get your API key from: https://nvd.nist.gov/developers/request-an-api-key"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. (Optional) Add your NVD API key to .env"
echo "  3. Run: nvdi --help"
echo ""
echo "Example commands:"
echo "  nvdi get cve CVE-2021-44228"
echo "  nvdi search keyword log4j --limit 5"
echo "  nvdi monitor add nginx"
echo "  nvdi stats show"
