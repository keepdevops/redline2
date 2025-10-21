#!/bin/bash
echo "🧪 Testing REDLINE Universal Docker Installation"
echo "================================================"

# Test if image exists
if docker images | grep -q redline-universal; then
    echo "✅ Docker image exists: redline-universal"
else
    echo "❌ Docker image not found: redline-universal"
    exit 1
fi

# Test universal components
echo "Testing universal components..."
docker run --rm redline-universal /bin/bash -c "
    source /opt/conda/bin/activate redline-universal && \
    echo 'Testing GUI components...' && \
    python -c 'import tkinter; print(\"✅ Tkinter version:\", tkinter.TkVersion)' && \
    python -c 'from redline.gui.main_window import StockAnalyzerGUI; print(\"✅ GUI module imported successfully\")' && \
    echo 'Testing Web App components...' && \
    python -c 'import flask; print(\"✅ Flask version:\", flask.__version__)' && \
    python -c 'from redline.web import create_app; app = create_app(); print(\"✅ Web app created successfully\")' && \
    echo 'Testing Core components...' && \
    python -c 'from redline.core.data_loader import DataLoader; print(\"✅ DataLoader imported successfully\")' && \
    python -c 'from redline.database.connector import DatabaseConnector; print(\"✅ DatabaseConnector imported successfully\")' && \
    echo '✅ All universal tests passed!'
"

echo "Universal test complete!"
