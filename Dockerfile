# Multi-mode Dockerfile for REDLINE GUI on Ubuntu
# Supports: X11 forwarding, VNC server, headless mode, and web interface

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Build arguments for different modes
ARG MODE=auto
ARG VNC_PORT=5900
ARG WEB_PORT=8080

# Labels for metadata
LABEL maintainer="REDLINE Team"
LABEL description="REDLINE Data Analyzer with GUI support"
LABEL version="1.0.0"

# Install system dependencies for all modes
RUN apt-get update && \
    apt-get install -y \
    # Core system packages
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    curl \
    wget \
    git \
    # GUI and X11 packages
    python3-tk \
    tk-dev \
    tcl-dev \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxss1 \
    libgconf-2-4 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    # VNC and virtual display packages
    xvfb \
    x11vnc \
    fluxbox \
    # Web server packages (for future web interface)
    nginx \
    # Additional utilities
    procps \
    htop \
    nano \
    vim \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -s /bin/bash redline && \
    usermod -aG sudo redline

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements_docker.txt ./

# Install Python packages
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements_docker.txt

# Copy application files
COPY main.py data_config.ini ./
COPY redline/ ./redline/

# Create data directories with proper permissions
RUN mkdir -p data data/converted data/downloaded data/stooq_format && \
    chown -R redline:redline /app

# Copy entrypoint script
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Copy launch scripts
COPY scripts/ ./scripts/
RUN chmod +x scripts/*.sh

# Create VNC password file (default password: redline123)
RUN mkdir -p /home/redline/.vnc && \
    echo "redline123" | vncpasswd -f > /home/redline/.vnc/passwd && \
    chmod 600 /home/redline/.vnc/passwd && \
    chown -R redline:redline /home/redline/.vnc

# Switch to non-root user
USER redline

# Expose ports
EXPOSE ${VNC_PORT} ${WEB_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${WEB_PORT}/health || exit 1

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Default command
CMD ["--mode=auto"]