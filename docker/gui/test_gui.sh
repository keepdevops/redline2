#!/bin/bash
echo "🧪 Testing REDLINE GUI Docker Installation"
echo "=========================================="

# Test if image exists
if docker images | grep -q redline-gui; then
    echo "✅ Docker image exists: redline-gui"
else
    echo "❌ Docker image not found: redline-gui"
    exit 1
fi

# Test GUI components
echo "Testing GUI components..."
docker run --rm -e DISPLAY=$DISPLAY redline-gui /bin/bash -c "
    source /opt/conda/bin/activate redline-gui && \
    python -c 'import tkinter; print(\"✅ Tkinter version:\", tkinter.TkVersion)' && \
    python -c 'import pandas; print(\"✅ Pandas version:\", pandas.__version__)' && \
    python -c 'import matplotlib; print(\"✅ Matplotlib version:\", matplotlib.__version__)' && \
    python -c 'from redline.gui.main_window import StockAnalyzerGUI; print(\"✅ REDLINE GUI modules working\")' && \
    echo '✅ All GUI tests passed!'
"

echo "GUI test complete!"
