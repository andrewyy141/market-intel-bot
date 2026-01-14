#!/bin/bash

# Market Intelligence Bot - Setup Script
# Run this script to automatically set up the bot

set -e  # Exit on any error

echo "🚀 Market Intelligence Bot - Setup"
echo "=================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
}

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || {
    echo "❌ Failed to activate virtual environment"
    exit 1
}

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
echo "📥 Downloading spaCy language model..."
python -m spacy download en_core_web_sm || {
    echo "⚠️  spaCy model download failed (non-critical)"
}

# Create directories
echo "📁 Creating directories..."
mkdir -p data logs
mkdir -p config database ingestion processing signals discord_bot

# Create __init__.py files
echo "📝 Creating package files..."
touch config/__init__.py
touch database/__init__.py
touch ingestion/__init__.py
touch processing/__init__.py
touch signals/__init__.py
touch discord_bot/__init__.py

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env file with your Discord bot token and API keys!"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   - DISCORD_BOT_TOKEN (from Discord Developer Portal)"
echo "   - ALERT_CHANNEL_ID (right-click channel → Copy ID)"
echo "   - FRED_API_KEY (from fred.stlouisfed.org)"
echo ""
echo "2. Run the bot:"
echo "   source venv/bin/activate"
echo "   python bot.py"
echo ""
echo "📖 See SETUP_GUIDE.md for detailed instructions"
echo ""