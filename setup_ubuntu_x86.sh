#!/bin/bash

# REDLINE Quick Setup Script for Ubuntu x86
# Simple one-command setup for Dell x86 Ubuntu systems

set -e

echo "🚀 REDLINE Ubuntu x86 Quick Setup"
echo "=================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -y

# Install essential packages
echo "🔧 Installing essential packages..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-tk \
    python3-venv \
    python3-dev \
    build-essential \
    curl \
    wget \
    git

# Install Miniconda if not present
if ! command -v conda &> /dev/null; then
    echo "📥 Installing Miniconda..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p "$HOME/miniconda3"
    echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/miniconda3/bin:$PATH"
    rm miniconda.sh
fi

# Setup conda environment
echo "🐍 Setting up Python environment..."
export PATH="$HOME/miniconda3/bin:$PATH"

# Create or activate stock environment
if conda env list | grep -q "stock"; then
    echo "✅ Using existing 'stock' environment"
    conda activate stock
else
    echo "🆕 Creating 'stock' environment..."
    conda create -n stock python=3.11 -y
    conda activate stock
    
    # Install core dependencies
    conda install -y \
        pandas \
        numpy \
        matplotlib \
        seaborn \
        scipy \
        scikit-learn \
        pyarrow \
        duckdb \
        polars \
        requests \
        beautifulsoup4 \
        lxml \
        openpyxl \
        xlrd
fi

# Set environment variables
echo "⚙️ Configuring environment..."
export PYTHONPATH="$(pwd):$PYTHONPATH"
export MPLBACKEND=TkAgg
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Verify installation
echo "🔍 Verifying installation..."
python -c "import pandas, numpy, pyarrow, duckdb, polars, tkinter; print('✅ All dependencies available')"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run REDLINE:"
echo "  ./run_ubuntu_x86.sh"
echo ""
echo "Or manually:"
echo "  conda activate stock"
echo "  python main.py --task=gui"
echo ""
