FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
ENV DISPLAY=:0

# Install system dependencies for GUI
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    # Tkinter GUI dependencies
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

# Copy REDLINE files
COPY . /app/

# Create conda environment optimized for GUI
RUN $CONDA_DIR/bin/conda create -n redline-gui python=3.11 -y && \
    $CONDA_DIR/bin/conda run -n redline-gui conda install -c conda-forge \
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

# Install GUI-specific packages via pip
RUN $CONDA_DIR/bin/conda run -n redline-gui pip install \
    yfinance \
    polars \
    openpyxl \
    xlsxwriter \
    psutil \
    configparser \
    urllib3

# Create GUI startup script
RUN echo '#!/bin/bash' > /app/start_gui.sh && \
    echo 'source /opt/conda/bin/activate redline-gui' >> /app/start_gui.sh && \
    echo 'cd /app' >> /app/start_gui.sh && \
    echo 'export DISPLAY=${DISPLAY:-:0}' >> /app/start_gui.sh && \
    echo 'python main.py' >> /app/start_gui.sh && \
    chmod +x /app/start_gui.sh

# Create GUI test script
RUN echo '#!/bin/bash' > /app/test_gui.sh && \
    echo 'source /opt/conda/bin/activate redline-gui' >> /app/test_gui.sh && \
    echo 'cd /app' >> /app/test_gui.sh && \
    echo 'export DISPLAY=${DISPLAY:-:0}' >> /app/test_gui.sh && \
    echo 'python -c "import tkinter; print(\"Tkinter version:\", tkinter.TkVersion)"' >> /app/test_gui.sh && \
    echo 'python -c "from redline.gui.main_window import StockAnalyzerGUI; print(\"GUI module imported successfully\")"' >> /app/test_gui.sh && \
    chmod +x /app/test_gui.sh

# Default command
CMD ["/bin/bash"]
