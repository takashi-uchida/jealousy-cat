#!/bin/bash

echo "🚀 Starting Environment Setup for Jealousy.sys..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating python virtual environment in .venv..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
python3 -m pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Install additional required packages for macOS control
echo "🍺 Checking Homebrew dependencies (portaudio is required for pyaudio)..."
if command -v brew &> /dev/null; then
    brew install portaudio
else
    echo "⚠️ Homebrew is not installed. Please install Homebrew or portaudio manually to use audio features."
fi

echo "📥 Installing macOS specific dependencies (pyobjc, pyautogui, pyaudio)..."
pip install pyobjc pyautogui pyaudio

echo "🌐 Installing Playwright Chromium for computer-use-preview..."
playwright install chromium

echo "🔍 Checking macOS Permissions..."
python3 permissions_check.py

echo "✅ Environment setup complete!"
echo "👉 To activate the environment in your shell, run: source .venv/bin/activate"
