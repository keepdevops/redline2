# Starting REDLINE Services

## Quick Start

### Option 1: Start in Separate Terminals (Recommended)

**Terminal 1 - License Server:**
```bash
python3 licensing/server/license_server.py
```

**Terminal 2 - Web App:**
```bash
python3 web_app.py
```

**Terminal 3 - Run Tests:**
```bash
python3 test_payment_integration.py
```

### Option 2: Start in Background

**Start License Server:**
```bash
python3 licensing/server/license_server.py > license_server.log 2>&1 &
```

**Start Web App:**
```bash
python3 web_app.py > web_app.log 2>&1 &
```

**Check Status:**
```bash
./check_services.sh
```

**Stop Services:**
```bash
pkill -f license_server.py
pkill -f web_app.py
```

## Current Status

Run this to check:
```bash
./check_services.sh
```

## Expected Output

When both services are running:
- ✅ License Server: http://localhost:5001
- ✅ Web App: http://localhost:8080

## Test Endpoints

Once both services are running:

```bash
# Get packages
curl http://localhost:8080/payments/packages

# Check license server health
curl http://localhost:5001/api/health

# Run full test suite
python3 test_payment_integration.py
```

## Troubleshooting

**Port already in use:**
```bash
# Find process using port
lsof -Pi :8080 -sTCP:LISTEN
lsof -Pi :5001 -sTCP:LISTEN

# Kill process
kill -9 <PID>
```

**Services not starting:**
- Check logs: `tail -f license_server.log` or `tail -f web_app.log`
- Check dependencies: `pip3 install -r requirements.txt`

