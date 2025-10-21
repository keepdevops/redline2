FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Install system dependencies for web app
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
    && rm -rf /var/lib/apt/lists/*

# Download and install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    $CONDA_DIR/bin/conda clean -afy

# Initialize conda
RUN $CONDA_DIR/bin/conda init bash

# Set working directory
WORKDIR /app

# Copy REDLINE files
COPY . /app/

# Create conda environment optimized for web app
RUN $CONDA_DIR/bin/conda create -n redline-web python=3.11 -y && \
    $CONDA_DIR/bin/conda activate redline-web && \
    $CONDA_DIR/bin/conda install -n redline-web -c conda-forge \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scipy \
    scikit-learn \
    requests \
    pyarrow \
    duckdb \
    python-dateutil \
    pytz \
    -y

# Install web-specific packages via pip
RUN $CONDA_DIR/bin/conda run -n redline-web pip install \
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

# Create web app startup script
RUN echo '#!/bin/bash' > /app/start_web.sh && \
    echo 'source /opt/conda/bin/activate redline-web' >> /app/start_web.sh && \
    echo 'cd /app' >> /app/start_web.sh && \
    echo 'export FLASK_APP=web_app.py' >> /app/start_web.sh && \
    echo 'export FLASK_ENV=production' >> /app/start_web.sh && \
    echo 'export FLASK_RUN_HOST=0.0.0.0' >> /app/start_web.sh && \
    echo 'export FLASK_RUN_PORT=5000' >> /app/start_web.sh && \
    echo 'python web_app.py' >> /app/start_web.sh && \
    chmod +x /app/start_web.sh

# Create production startup script with Gunicorn
RUN echo '#!/bin/bash' > /app/start_production.sh && \
    echo 'source /opt/conda/bin/activate redline-web' >> /app/start_production.sh && \
    echo 'cd /app' >> /app/start_production.sh && \
    echo 'export FLASK_APP=web_app.py' >> /app/start_production.sh && \
    echo 'export FLASK_ENV=production' >> /app/start_production.sh && \
    echo 'gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class gevent --worker-connections 1000 web_app:app' >> /app/start_production.sh && \
    chmod +x /app/start_production.sh

# Create web app test script
RUN echo '#!/bin/bash' > /app/test_web.sh && \
    echo 'source /opt/conda/bin/activate redline-web' >> /app/test_web.sh && \
    echo 'cd /app' >> /app/test_web.sh && \
    echo 'python -c "import flask; print(\"Flask version:\", flask.__version__)"' >> /app/test_web.sh && \
    echo 'python -c "from redline.web import create_app; app = create_app(); print(\"Web app created successfully\")"' >> /app/test_web.sh && \
    echo 'python -c "from redline.core.data_loader import DataLoader; print(\"DataLoader imported successfully\")"' >> /app/test_web.sh && \
    chmod +x /app/test_web.sh

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
CMD ["/app/start_production.sh"]
