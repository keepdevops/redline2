#!/bin/bash
echo "🧪 Testing REDLINE Web App Docker Installation"
echo "=============================================="

# Test if image exists
if docker images | grep -q redline-web; then
    echo "✅ Docker image exists: redline-web"
else
    echo "❌ Docker image not found: redline-web"
    exit 1
fi

# Test web app components
echo "Testing web app components..."
docker run --rm redline-web /bin/bash -c "
    source /opt/conda/bin/activate redline-web && \
    python -c 'import flask; print(\"✅ Flask version:\", flask.__version__)' && \
    python -c 'import flask_socketio; print(\"✅ Flask-SocketIO version:\", flask_socketio.__version__)' && \
    python -c 'import gunicorn; print(\"✅ Gunicorn version:\", gunicorn.__version__)' && \
    python -c 'from redline.web import create_app; app = create_app(); print(\"✅ REDLINE web app created successfully\")' && \
    python -c 'from redline.core.data_loader import DataLoader; print(\"✅ REDLINE core modules working\")' && \
    echo '✅ All web app tests passed!'
"

echo "Web app test complete!"
