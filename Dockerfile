
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Python
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    curl \
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
    --break-system-packages

# Set working directory
WORKDIR /app

# Copy application files into the container
COPY data_module.py data_config.ini ./

# Default command to run the module
CMD ["python3", "-m", "data_module", "--task=load"]

