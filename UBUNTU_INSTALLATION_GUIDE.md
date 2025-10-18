# REDLINE Ubuntu x86 Installation Guide

## 🖥️ System Requirements

### Hardware
- **CPU**: Intel x86-64 processor (Dell x86 compatible)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space minimum
- **Display**: X11-compatible display (desktop or X11 forwarding)

### Software
- **OS**: Ubuntu 18.04 LTS or newer
- **Python**: 3.8+ (3.11 recommended)
- **Desktop Environment**: Any (GNOME, KDE, XFCE, etc.)
- **Display Server**: X11 (default on Ubuntu)

## 🚀 Quick Installation

### Option 1: Automated Setup (Recommended)
```bash
# Download and run the setup script
curl -O https://raw.githubusercontent.com/your-repo/redline/main/setup_ubuntu_x86.sh
chmod +x setup_ubuntu_x86.sh
./setup_ubuntu_x86.sh
```

### Option 2: Manual Setup
```bash
# 1. Update system
sudo apt-get update -y

# 2. Install dependencies
sudo apt-get install -y python3 python3-pip python3-tk python3-venv python3-dev build-essential curl wget git

# 3. Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/miniconda3/bin:$PATH"

# 4. Create environment
conda create -n stock python=3.11 -y
conda activate stock

# 5. Install Python packages
conda install -y pandas numpy matplotlib seaborn scipy scikit-learn pyarrow duckdb polars requests beautifulsoup4 lxml openpyxl xlrd

# 6. Set environment variables
export PYTHONPATH="$(pwd):$PYTHONPATH"
export MPLBACKEND=TkAgg
```

## 🎯 Running REDLINE

### Using the Launch Script
```bash
# Run REDLINE GUI
./run_ubuntu_x86.sh

# Install dependencies first (if needed)
./run_ubuntu_x86.sh --install

# Run diagnostics
./run_ubuntu_x86.sh --diagnose
```

### Manual Launch
```bash
# Activate environment
conda activate stock

# Set environment variables
export PYTHONPATH="$(pwd):$PYTHONPATH"
export MPLBACKEND=TkAgg

# Run REDLINE
python main.py --task=gui
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **"No module named 'tkinter'" Error**
```bash
# Install tkinter
sudo apt-get install -y python3-tk

# Or if using conda
conda install -y tk
```

#### 2. **Display/X11 Issues**
```bash
# Check display
echo $DISPLAY

# Set display if not set
export DISPLAY=:0

# Test X11
xdpyinfo
```

#### 3. **Permission Denied Errors**
```bash
# Make scripts executable
chmod +x run_ubuntu_x86.sh
chmod +x setup_ubuntu_x86.sh

# Fix conda permissions
sudo chown -R $USER:$USER $HOME/miniconda3
```

#### 4. **Python Version Issues**
```bash
# Check Python version
python3 --version

# Update Python if needed
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
```

#### 5. **Missing Dependencies**
```bash
# Install missing packages
conda install -y [package-name]

# Or using pip
pip install [package-name]
```

### Environment Issues

#### **Conda Environment Not Found**
```bash
# List environments
conda env list

# Create stock environment
conda create -n stock python=3.11 -y
conda activate stock
```

#### **PATH Issues**
```bash
# Add conda to PATH
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or manually export
export PATH="$HOME/miniconda3/bin:$PATH"
```

### Performance Issues

#### **Slow GUI Performance**
```bash
# Set environment variables for better performance
export QT_X11_NO_MITSHM=1
export OMP_NUM_THREADS=1
export MPLBACKEND=TkAgg
```

#### **Memory Issues**
```bash
# Monitor memory usage
free -h
htop

# Reduce memory usage
export OMP_NUM_THREADS=1
```

## 📊 System Diagnostics

### Run Full Diagnostics
```bash
./run_ubuntu_x86.sh --diagnose
```

### Manual System Check
```bash
# Check system info
uname -a
lsb_release -a

# Check Python
python3 --version
python3 -c "import sys; print(sys.executable)"

# Check packages
python3 -c "
import sys
packages = ['pandas', 'numpy', 'matplotlib', 'tkinter', 'pyarrow', 'duckdb', 'polars']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg}')
"

# Check display
echo "DISPLAY: $DISPLAY"
xdpyinfo
```

## 🐳 Docker Alternative

If you prefer Docker on Ubuntu:

```bash
# Install Docker
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER

# Run REDLINE in Docker
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $(pwd):/app \
    redline:latest
```

## 🔄 Updates and Maintenance

### Update REDLINE
```bash
# Pull latest changes
git pull origin main

# Update dependencies
conda activate stock
conda update --all
```

### Clean Installation
```bash
# Remove old environment
conda env remove -n stock

# Reinstall
./setup_ubuntu_x86.sh
```

## 📝 Environment Variables

### Required Variables
```bash
export PYTHONPATH="$(pwd):$PYTHONPATH"
export MPLBACKEND=TkAgg
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
```

### Optional Variables
```bash
# Performance tuning
export OMP_NUM_THREADS=1
export QT_X11_NO_MITSHM=1

# Debug mode
export REDLINE_DEBUG=1
export REDLINE_LOG_LEVEL=DEBUG
```

## 🎯 Desktop Environment Specific

### GNOME (Default Ubuntu)
```bash
# No additional setup needed
./run_ubuntu_x86.sh
```

### KDE
```bash
# May need additional packages
sudo apt-get install -y kde-baseapps
./run_ubuntu_x86.sh
```

### XFCE
```bash
# Lightweight setup
sudo apt-get install -y xfce4
./run_ubuntu_x86.sh
```

### Server/Headless (X11 Forwarding)
```bash
# For SSH X11 forwarding
ssh -X username@server
export DISPLAY=localhost:10.0
./run_ubuntu_x86.sh
```

## 🆘 Getting Help

### Log Files
```bash
# Check application logs
tail -f redline_ubuntu.log

# Check system logs
journalctl -f
```

### Support Resources
- **GitHub Issues**: [Report bugs and issues](https://github.com/your-repo/redline/issues)
- **Documentation**: [Full documentation](https://github.com/your-repo/redline/wiki)
- **Community**: [Discord/Slack community](https://discord.gg/your-invite)

## ✅ Verification Checklist

After installation, verify:

- [ ] Python 3.8+ installed
- [ ] Conda environment created
- [ ] All dependencies installed
- [ ] Display/X11 working
- [ ] REDLINE launches without errors
- [ ] GUI is responsive
- [ ] All tabs functional
- [ ] Help system works
- [ ] File operations work

## 🎉 Success!

If all checks pass, you're ready to use REDLINE on your Dell x86 Ubuntu system!

```bash
# Launch REDLINE
./run_ubuntu_x86.sh
```

Happy data analysis! 📊🚀
