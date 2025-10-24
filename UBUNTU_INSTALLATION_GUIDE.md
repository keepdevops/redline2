# REDLINE Ubuntu Installation Guide

## ✅ Working Solution for Ubuntu AMD64

### System Requirements
- Ubuntu (AMD64 architecture)
- Python 3.13+
- pip3 installed
- USB drive with REDLINE distribution

### Installation Steps

#### 1. Install REDLINE Package
```bash
pip3 install --user /media/bike/REDLINE/redline-distribution/packages/redline_financial-1.0.0-py3-none-any.whl
```

#### 2. Add to PATH
```bash
export PATH=$PATH:/home/bike/.local/bin
```

#### 3. Navigate to Home Directory
```bash
cd ~
```

#### 4. Start REDLINE Web Application
```bash
redline-web
```

### Access Points
- **Web Interface**: http://localhost:8080
- **CLI Tool**: `redline --help`
- **GUI Application**: `redline-gui`

## ⚠️ Critical Discovery

**MUST run `cd ~` before `redline-web`**

- Permission errors occur in other directories
- Home directory has proper write permissions
- REDLINE needs to create data files and logs

## Troubleshooting

### Architecture Issues
- **Problem**: ARM executables won't run on AMD64
- **Solution**: Use PyPI wheel package (cross-platform)

### Python Version Issues
- **Problem**: Python 3.13 compatibility
- **Solution**: PyPI package handles dependencies

### Permission Issues
- **Problem**: Permission denied errors
- **Solution**: Run from home directory (`cd ~`)

### PATH Issues
- **Problem**: Commands not found
- **Solution**: Add `/home/bike/.local/bin` to PATH

## Alternative Methods

### Virtual Environment
```bash
python3 -m venv redline-env
source redline-env/bin/activate
pip install /path/to/redline_financial-1.0.0-py3-none-any.whl
cd ~
redline-web
```

### System-wide Install (requires sudo)
```bash
sudo pip3 install /path/to/redline_financial-1.0.0-py3-none-any.whl
cd ~
redline-web
```

### Direct Python Run
```bash
cd ~
python3 -c "from redline.web import app; app.run(host='0.0.0.0', port=8080)"
```

## Testing

### Basic Functionality Test
1. Open browser to http://localhost:8080
2. Navigate interface
3. Download sample stock data (e.g., AAPL)
4. Verify data displays correctly

### CLI Test
```bash
redline --help
redline download AAPL
```

### GUI Test
```bash
redline-gui
```

## Success Criteria
- ✅ No error messages during installation
- ✅ `redline-web` command works
- ✅ Web interface loads at http://localhost:8080
- ✅ Data downloads successfully
- ✅ All features accessible

## Key Learnings
- PyPI packages work across architectures
- User install avoids permission issues
- Running from home directory fixes path problems
- `cd ~` is critical for proper operation

## Date Documented
December 2024

## Tested On
- Ubuntu AMD64
- Python 3.13
- User: bike
- USB mount: /media/bike/REDLINE