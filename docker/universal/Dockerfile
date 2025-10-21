FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
ENV DISPLAY=:0
ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# GTK and accessibility settings to prevent warnings
ENV GTK_MODULES=""
ENV QT_ACCESSIBILITY=0
ENV NO_AT_BRIDGE=1

# Install system dependencies for both GUI and web app
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    nginx \
    supervisor \
    # Tkinter GUI dependencies (architecture-agnostic)
    python3-tk \
    tk-dev \
    tcl-dev \
    # X11 forwarding for GUI
    x11-apps \
    xauth \
    xvfb \
    # Additional GUI libraries
    libx11-6 \
    libx11-dev \
    libxext6 \
    libxext-dev \
    libxrender1 \
    libxrender-dev \
    libxtst6 \
    libxtst-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install Miniconda (multi-platform)
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"; \
    elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    wget "$MINICONDA_URL" -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    $CONDA_DIR/bin/conda clean -afy

# Initialize conda and accept Terms of Service
RUN $CONDA_DIR/bin/conda init bash && \
    $CONDA_DIR/bin/conda config --set channel_priority strict && \
    $CONDA_DIR/bin/conda config --add channels conda-forge && \
    $CONDA_DIR/bin/conda config --set show_channel_urls true && \
    $CONDA_DIR/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    $CONDA_DIR/bin/conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# Set working directory
WORKDIR /app

# Copy essential REDLINE files only
COPY redline/ /app/redline/
COPY main.py /app/
COPY web_app.py /app/
COPY requirements*.txt /app/
COPY data_config.ini* /app/
COPY redline_template.json /app/
COPY api_keys.json /app/

# Create conda environment with all dependencies
RUN $CONDA_DIR/bin/conda create -n redline-universal python=3.11 -y && \
    $CONDA_DIR/bin/conda run -n redline-universal conda install -c conda-forge \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scipy \
    scikit-learn \
    requests \
    pyarrow \
    duckdb \
    pillow \
    python-dateutil \
    pytz \
    -y

# Install all packages via pip
RUN $CONDA_DIR/bin/conda run -n redline-universal pip install \
    flask \
    flask-socketio \
    flask-compress \
    gunicorn \
    celery \
    redis \
    yfinance \
    polars \
    openpyxl \
    xlsxwriter \
    psutil \
    configparser \
    urllib3 \
    gevent \
    gevent-websocket

# Create GUI startup script
RUN echo '#!/bin/bash' > /app/start_gui.sh && \
    echo 'source /opt/conda/bin/activate redline-universal' >> /app/start_gui.sh && \
    echo 'cd /app' >> /app/start_gui.sh && \
    echo 'export DISPLAY=${DISPLAY:-:0}' >> /app/start_gui.sh && \
    echo 'export GTK_MODULES=""' >> /app/start_gui.sh && \
    echo 'export QT_ACCESSIBILITY=0' >> /app/start_gui.sh && \
    echo 'export NO_AT_BRIDGE=1' >> /app/start_gui.sh && \
    echo 'python main.py' >> /app/start_gui.sh && \
    chmod +x /app/start_gui.sh

# Create web app startup script
RUN echo '#!/bin/bash' > /app/start_web.sh && \
    echo 'source /opt/conda/bin/activate redline-universal' >> /app/start_web.sh && \
    echo 'cd /app' >> /app/start_web.sh && \
    echo 'export FLASK_APP=web_app.py' >> /app/start_web.sh && \
    echo 'export FLASK_ENV=production' >> /app/start_web.sh && \
    echo 'export FLASK_RUN_HOST=0.0.0.0' >> /app/start_web.sh && \
    echo 'export FLASK_RUN_PORT=5000' >> /app/start_web.sh && \
    echo 'python web_app.py' >> /app/start_web.sh && \
    chmod +x /app/start_web.sh

# Create production web app startup script with Gunicorn
RUN echo '#!/bin/bash' > /app/start_production.sh && \
    echo 'source /opt/conda/bin/activate redline-universal' >> /app/start_production.sh && \
    echo 'cd /app' >> /app/start_production.sh && \
    echo 'export FLASK_APP=web_app.py' >> /app/start_production.sh && \
    echo 'export FLASK_ENV=production' >> /app/start_production.sh && \
    echo 'gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gevent --worker-connections 1000 web_app:app' >> /app/start_production.sh && \
    chmod +x /app/start_production.sh

# Create universal test script
RUN echo '#!/bin/bash' > /app/test_universal.sh && \
    echo 'source /opt/conda/bin/activate redline-universal' >> /app/test_universal.sh && \
    echo 'cd /app' >> /app/test_universal.sh && \
    echo 'echo "Testing GUI components..."' >> /app/test_universal.sh && \
    echo 'python -c "import tkinter; print(\"✅ Tkinter version:\", tkinter.TkVersion)"' >> /app/test_universal.sh && \
    echo 'python -c "from redline.gui.main_window import StockAnalyzerGUI; print(\"✅ GUI module imported successfully\")"' >> /app/test_universal.sh && \
    echo 'echo "Testing Web App components..."' >> /app/test_universal.sh && \
    echo 'python -c "import flask; print(\"✅ Flask version:\", flask.__version__)"' >> /app/test_universal.sh && \
    echo 'python -c "from redline.web import create_app; app = create_app(); print(\"✅ Web app created successfully\")"' >> /app/test_universal.sh && \
    echo 'echo "Testing Core components..."' >> /app/test_universal.sh && \
    echo 'python -c "from redline.core.data_loader import DataLoader; print(\"✅ DataLoader imported successfully\")"' >> /app/test_universal.sh && \
    echo 'python -c "from redline.database.connector import DatabaseConnector; print(\"✅ DatabaseConnector imported successfully\")"' >> /app/test_universal.sh && \
    echo 'echo "✅ All universal tests passed!"' >> /app/test_universal.sh && \
    chmod +x /app/test_universal.sh

# Create nginx configuration
RUN echo 'server {' > /etc/nginx/sites-available/redline && \
    echo '    listen 80;' >> /etc/nginx/sites-available/redline && \
    echo '    server_name localhost;' >> /etc/nginx/sites-available/redline && \
    echo '    location / {' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_pass http://127.0.0.1:5000;' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_set_header Host \$host;' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_set_header X-Real-IP \$remote_addr;' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;' >> /etc/nginx/sites-available/redline && \
    echo '        proxy_set_header X-Forwarded-Proto \$scheme;' >> /etc/nginx/sites-available/redline && \
    echo '    }' >> /etc/nginx/sites-available/redline && \
    echo '}' >> /etc/nginx/sites-available/redline

# Enable nginx site
RUN ln -s /etc/nginx/sites-available/redline /etc/nginx/sites-enabled/ && \
    rm /etc/nginx/sites-enabled/default

# Expose ports
EXPOSE 5000 80

# Default command
CMD ["/bin/bash"]
