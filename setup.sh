#!/usr/bin/env bash

# Setup script for local Python venv
echo "Creating Python venv in .venv ..."
python3 -m venv .venv

echo "Activating venv ..."
source .venv/bin/activate

echo "Installing requirements ..."
pip install -r requirements.txt

echo "✅ Setup complete. Virtual environment activated."
echo
echo "Next time, just run:"
echo "source .venv/bin/activate"