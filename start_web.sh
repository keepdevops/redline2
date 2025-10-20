#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting REDLINE Web Interface..."

# Start the web app
source venv/bin/activate
export WEB_PORT=${WEB_PORT:-8080}
export FLASK_APP=web_app.py
export FLASK_ENV=production
python3 web_app.py
