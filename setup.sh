#!/bin/bash
echo "Setting up virtual environment..."
python -m venv venv
source venv/Scripts/activate

echo "Installing dependencies..."
pip install flask python-dotenv pandas google-generativeai

echo "Starting Flask server..."
export FLASK_APP=app.py
flask run
