#!/bin/bash

echo "🚀 Setting up yt-dlp Test Service locally..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the service:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "🌐 Then open: http://localhost:8000"
echo ""
echo "🧪 Quick test commands:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/ytdlp-info" 