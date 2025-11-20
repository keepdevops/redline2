# Massive.com API Key Setup - Quick Start

## Quick Setup (Choose One)

### Option 1: Python Script (Recommended)

```bash
python3 setup_massive_api_key.py
```

Interactive script that:
- Prompts for your API key
- Saves to REDLINE config (for web UI)
- Saves to environment file (for command-line)
- Tests the connection
- Provides clear next steps

### Option 2: Shell Script

```bash
bash setup_massive_api_key.sh
```

Bash script with the same features as the Python version.

### Option 3: Manual Setup

#### For Web UI (Config File)

```bash
# Create config directory
mkdir -p ~/.redline

# Save API key
cat > ~/.redline/api_keys.json << EOF
{
  "massive": "YOUR_API_KEY_HERE"
}
EOF

# Set secure permissions
chmod 600 ~/.redline/api_keys.json
```

#### For Command-Line (Environment Variable)

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export MASSIVE_API_KEY="YOUR_API_KEY_HERE"' >> ~/.zshrc

# Reload shell
source ~/.zshrc
```

## Verify Setup

### Check Config File

```bash
cat ~/.redline/api_keys.json
```

Should show:
```json
{
  "massive": "your_api_key_here"
}
```

### Check Environment Variable

```bash
echo $MASSIVE_API_KEY
```

Should show your API key.

### Test Integration

```bash
python3 test_massive_integration.py
```

## Using in REDLINE

### Web UI

1. **Go to Settings → API Keys**
2. **Find "Massive.com"** in the API sources list
3. **Verify your API key** is saved (or enter it manually)
4. **Go to Download tab**
5. **Select "Massive.com"** as the data source
6. **Enter ticker** (e.g., AAPL)
7. **Select date range**
8. **Click Download**

### Command-Line / Python

```python
from redline.downloaders.massive_downloader import MassiveDownloader
import os

api_key = os.environ.get('MASSIVE_API_KEY')
downloader = MassiveDownloader(api_key=api_key)

# Download data
data = downloader.download_single_ticker('AAPL', '2024-01-01', '2024-12-31')
print(data.head())
```

## Troubleshooting

### "API key not found"

**Solution**: Run the setup script again or manually add to config file.

### "Massive.com client library not available"

**Solution**: This is optional. The downloader will use REST API instead.
```bash
pip install massive-client  # Optional
```

### "Rate limit exceeded"

**Solution**: Adjust rate limit delay:
```python
downloader.rate_limit_delay = 12.0  # For free tier (5 requests/minute)
```

## Get Your API Key

1. Visit [massive.com](https://massive.com)
2. Sign up for an account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key
6. Run the setup script

## Next Steps

- ✅ API key configured
- ✅ Tested connection
- ✅ Ready to use in REDLINE

Start downloading data with Massive.com!

