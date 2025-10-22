# REDLINE Web GUI Dockerfile
# Multi-platform Ubuntu 24.04 LTS with Python 3.11+ and modern features
FROM ubuntu:24.04

# Set environment variables for multi-platform compatibility
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHON_VERSION=3.11.14
ENV PLATFORM=multi-arch

# Set working directory
WORKDIR /opt/redline

# Install system dependencies and modern Ubuntu features
RUN apt-get update && apt-get install -y \
    # Add deadsnakes PPA for Python 3.11
    software-properties-common \
    curl \
    wget \
    git \
    build-essential \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update \
    && apt-get install -y \
    # Python 3.11 support (explicit version for HP compatibility)
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3.11-distutils \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    # Build tools
    gcc \
    g++ \
    make \
    cmake \
    # yfinance dependencies
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    # System utilities
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    tree \
    jq \
    # Network tools
    net-tools \
    iputils-ping \
    dnsutils \
    # Process management
    supervisor \
    systemd \
    # Security tools
    ufw \
    fail2ban \
    # Modern Ubuntu features
    snapd \
    flatpak \
    # Database tools
    sqlite3 \
    # Web server tools
    nginx \
    apache2-utils \
    # Monitoring tools
    htop \
    iotop \
    nethogs \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create non-root user for security
RUN groupadd -r redline && useradd -r -g redline -d /opt/redline -s /bin/bash redline

# Set up Python 3.11 virtual environment
RUN python3.11 -m venv /opt/redline/venv
ENV PATH="/opt/redline/venv/bin:$PATH"

# Upgrade pip and install essential tools for Python 3.11
RUN python3.11 -m pip install --upgrade pip setuptools wheel importlib-metadata

# Copy requirements first for better caching
COPY requirements.txt /opt/redline/

# Install Python dependencies using Python 3.11
# Install yfinance separately first (it has complex dependencies)
RUN python3.11 -m pip install --upgrade pip setuptools wheel && \
    python3.11 -m pip install yfinance --no-cache-dir && \
    python3.11 -m pip install -r requirements.txt --no-cache-dir

# Copy application code
COPY . /opt/redline/

# Create necessary directories
RUN mkdir -p /opt/redline/data \
    /opt/redline/logs \
    /opt/redline/uploads \
    /opt/redline/temp \
    /opt/redline/config \
    /var/log/redline \
    /var/run/redline

# Set proper permissions
RUN chown -R redline:redline /opt/redline \
    && chown -R redline:redline /var/log/redline \
    && chown -R redline:redline /var/run/redline \
    && chmod +x /opt/redline/scripts/*.sh

# Create systemd service file
RUN echo '[Unit]' > /etc/systemd/system/redline.service \
    && echo 'Description=REDLINE Web GUI' >> /etc/systemd/system/redline.service \
    && echo 'After=network.target' >> /etc/systemd/system/redline.service \
    && echo '' >> /etc/systemd/system/redline.service \
    && echo '[Service]' >> /etc/systemd/system/redline.service \
    && echo 'Type=simple' >> /etc/systemd/system/redline.service \
    && echo 'User=redline' >> /etc/systemd/system/redline.service \
    && echo 'Group=redline' >> /etc/systemd/system/redline.service \
    && echo 'WorkingDirectory=/opt/redline' >> /etc/systemd/system/redline.service \
    && echo 'ExecStart=/opt/redline/scripts/start.sh' >> /etc/systemd/system/redline.service \
    && echo 'ExecStop=/opt/redline/scripts/shutdown.sh' >> /etc/systemd/system/redline.service \
    && echo 'Restart=always' >> /etc/systemd/system/redline.service \
    && echo 'RestartSec=5' >> /etc/systemd/system/redline.service \
    && echo '' >> /etc/systemd/system/redline.service \
    && echo '[Install]' >> /etc/systemd/system/redline.service \
    && echo 'WantedBy=multi-user.target' >> /etc/systemd/system/redline.service

# Create nginx configuration
RUN echo 'server {' > /etc/nginx/sites-available/redline \
    && echo '    listen 80;' >> /etc/nginx/sites-available/redline \
    && echo '    server_name localhost;' >> /etc/nginx/sites-available/redline \
    && echo '' >> /etc/nginx/sites-available/redline \
    && echo '    location / {' >> /etc/nginx/sites-available/redline \
    && echo '        proxy_pass http://127.0.0.1:8080;' >> /etc/nginx/sites-available/redline \
    && echo '        proxy_set_header Host $host;' >> /etc/nginx/sites-available/redline \
    && echo '        proxy_set_header X-Real-IP $remote_addr;' >> /etc/nginx/sites-available/redline \
    && echo '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;' >> /etc/nginx/sites-available/redline \
    && echo '        proxy_set_header X-Forwarded-Proto $scheme;' >> /etc/nginx/sites-available/redline \
    && echo '    }' >> /etc/nginx/sites-available/redline \
    && echo '}' >> /etc/nginx/sites-available/redline \
    && ln -sf /etc/nginx/sites-available/redline /etc/nginx/sites-enabled/ \
    && rm -f /etc/nginx/sites-enabled/default

# Create supervisor configuration
RUN echo '[supervisord]' > /etc/supervisor/conf.d/redline.conf \
    && echo 'nodaemon=true' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'user=root' >> /etc/supervisor/conf.d/redline.conf \
    && echo '' >> /etc/supervisor/conf.d/redline.conf \
    && echo '[program:redline]' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'command=/opt/redline/scripts/start.sh' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'directory=/opt/redline' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'user=redline' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'autostart=true' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'autorestart=true' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'stderr_logfile=/var/log/redline/error.log' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'stdout_logfile=/var/log/redline/access.log' >> /etc/supervisor/conf.d/redline.conf \
    && echo '' >> /etc/supervisor/conf.d/redline.conf \
    && echo '[program:nginx]' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'command=nginx -g "daemon off;"' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'autostart=true' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'autorestart=true' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'stderr_logfile=/var/log/nginx/error.log' >> /etc/supervisor/conf.d/redline.conf \
    && echo 'stdout_logfile=/var/log/nginx/access.log' >> /etc/supervisor/conf.d/redline.conf

# Create health check script
RUN echo '#!/bin/bash' > /opt/redline/scripts/healthcheck.sh \
    && echo 'curl -f http://localhost:8080/health || exit 1' >> /opt/redline/scripts/healthcheck.sh \
    && chmod +x /opt/redline/scripts/healthcheck.sh

# Expose ports
EXPOSE 80 8080

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /opt/redline/scripts/healthcheck.sh

# Switch to non-root user
USER redline

# Set default command
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]