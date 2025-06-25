# REDLINE2 - Enhanced Data Conversion Utility Dockerfile
# Supports ML/AI file formats, parallel processing, visualization, and plugin architecture

FROM ubuntu:24.04

# Set non-interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-tk \
    build-essential \
    curl \
    git \
    libpq-dev \
    libhdf5-dev \
    libgl1-mesa-glx \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (core + ML/AI + parallel + visualization)
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install \
    pandas \
    numpy \
    scipy \
    scikit-learn \
    matplotlib \
    seaborn \
    plotly \
    sqlalchemy \
    duckdb \
    configparser \
    pyarrow \
    polars \
    tensorflow \
    torch \
    dask[complete] \
    ray \
    h5py \
    pillow \
    opencv-python-headless \
    fastparquet \
    pyarrow \
    jupyter \
    ipywidgets \
    --break-system-packages

# Set working directory
WORKDIR /app

# Copy application code (modular structure)
COPY . /app

# Expose port for Jupyter or API if needed (optional)
# EXPOSE 8888

# Default command (can be overridden)
CMD ["python3", "-m", "data_module", "--task=gui"]

# For plugin support, users can mount a plugins directory at runtime
# Example: docker run -v $(pwd)/plugins:/app/plugins ... 