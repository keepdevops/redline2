FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Python
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-tk \
    build-essential \
    curl \
    git \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages using system pip with --break-system-packages
RUN python3 -m pip install \
    pandas \
    sqlalchemy \
    duckdb \
    configparser \
    pyarrow \
    polars \
    tensorflow \
    scikit-learn \
    yfinance \
    requests \
    psutil \
    --break-system-packages

# Set working directory
WORKDIR /app

# Copy the new modular application structure
COPY main.py data_config.ini ./
COPY redline/ ./redline/

# Create data directories
RUN mkdir -p data data/converted data/downloaded

# Expose port for web GUI (if needed)
EXPOSE 8080

# Default command to run the new main application
CMD ["python3", "main.py"]

