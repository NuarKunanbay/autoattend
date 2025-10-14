#!/bin/bash

# Auto Attendance Server Setup Script
# This script sets up the attendance server to run 24/7

set -e

echo "🚀 Setting up Auto Attendance Server..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if Chrome/Chromium is installed
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null && ! command -v chrome &> /dev/null; then
    echo "⚠️  Chrome/Chromium not found. Please install Google Chrome or Chromium."
    echo "   On macOS: brew install --cask google-chrome"
    echo "   On Ubuntu: sudo apt-get install google-chrome-stable"
    echo "   On CentOS/RHEL: sudo yum install google-chrome-stable"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if credentials are configured
echo "🔐 Checking credentials..."
if grep -q 'USERNAME = ""' main.py; then
    echo "⚠️  WARNING: Username is not configured in main.py"
    echo "   Please edit main.py and set your USERNAME and PASSWORD"
    echo "   Example:"
    echo "   USERNAME = \"your_username\""
    echo "   PASSWORD = \"your_password\""
fi

# Make the script executable
chmod +x setup.sh

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit main.py and configure your USERNAME and PASSWORD"
echo "2. Test the server: python main.py"
echo "3. For 24/7 operation, install as systemd service:"
echo "   sudo cp attendance-server.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable attendance-server"
echo "   sudo systemctl start attendance-server"
echo ""
echo "🌐 Server will be available at: http://localhost:5000"
echo "📊 Status endpoint: http://localhost:5000/status"
echo "❤️  Health check: http://localhost:5000/health"
