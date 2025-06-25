# REDLINE GUI Troubleshooting Guide for macOS

## Common X11 Forwarding Issues and Solutions

### Issue 1: "couldn't connect to display" Error
**Error Message:**
```
_tkinter.TclError: couldn't connect to display "host.docker.internal:0"
```

**Solution:**
1. Ensure XQuartz is installed and running:
   ```bash
   open -a XQuartz
   ```
2. Use the provided `run_gui.bash` script instead of manual Docker commands
3. If XQuartz preferences window opens, go to Security tab and enable "Allow connections from network clients"

### Issue 2: "Authorization required" Error
**Error Message:**
```
Authorization required, but no authorization protocol specified
```

**Solution:**
1. Run the xhost command to allow X11 connections:
   ```bash
   export DISPLAY=:0
   xhost + $(ifconfig en0 | grep inet | grep -v inet6 | awk '{print $2}')
   ```
2. This is automatically handled by the `run_gui.bash` script

### Issue 3: XQuartz Not Starting
**Symptoms:**
- XQuartz window doesn't appear
- X11 commands fail

**Solution:**
1. Check if XQuartz is installed:
   ```bash
   ls /Applications/Utilities/XQuartz.app
   ```
2. If not installed, download from: https://www.xquartz.org/
3. Restart your terminal after installation
4. Log out and log back in to macOS (sometimes required)

### Issue 4: Docker Container Can't Find Python File
**Error Message:**
```
python3: can't open file '/app/data_module_shared.py': [Errno 2] No such file or directory
```

**Solution:**
Use the provided scripts (`run_gui.bash` or `run_gui_socat.bash`) which mount the current directory correctly.

### Issue 5: Slow or Unresponsive GUI
**Symptoms:**
- GUI appears but is very slow
- Windows don't redraw properly

**Solutions:**
1. Try the socat approach:
   ```bash
   # Install socat first
   brew install socat
   # Then use the alternative script
   ./run_gui_socat.bash
   ```
2. Check your network connection (X11 forwarding uses network)
3. Close other applications using X11

### Issue 6: "Permission denied" for Scripts
**Error Message:**
```
bash: ./run_gui.bash: Permission denied
```

**Solution:**
```bash
chmod +x run_gui.bash
chmod +x run_gui_socat.bash
```

## Alternative Solutions

### Option 1: VNC Server (if X11 forwarding fails completely)
If X11 forwarding continues to fail, you can run a VNC server in the container:

```bash
# Install VNC in the Docker container
sudo apt-get update && sudo apt-get install -y x11vnc xvfb

# Start virtual display and VNC server
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
x11vnc -display :99 -bg -forever -nopw -quiet

# Connect with VNC viewer from macOS
```

### Option 2: Web-based Interface
Consider creating a web-based version of the interface using tools like:
- Streamlit
- Dash
- Flask with web forms

### Option 3: Command-line Mode
For data processing without GUI:
```bash
docker run -it --rm \
    -v $(pwd)/data:/app/data \
    -v $(pwd):/app/host \
    redline_arm \
    python3 /app/host/data_module_shared.py --task load
```

## Testing X11 Forwarding

### Test 1: Simple X11 Test
```bash
# In terminal (after running xhost +)
export DISPLAY=:0
xeyes  # Should show a pair of eyes that follow your cursor
```

### Test 2: Docker X11 Test
```bash
# Test X11 forwarding with a simple container
LOCAL_IP=$(ifconfig en0 | grep inet | grep -v inet6 | awk '{print $2}')
docker run -it --rm -e DISPLAY=$LOCAL_IP:0 redline_arm xeyes
```

## XQuartz Configuration

### Required XQuartz Settings:
1. Open XQuartz
2. Go to XQuartz > Preferences
3. Security tab:
   - ✅ "Allow connections from network clients"
   - ✅ "Authenticate connections" (recommended)
4. Restart XQuartz after changing settings

### Environment Variables:
```bash
# Add to your ~/.bashrc or ~/.zshrc
export DISPLAY=:0
```

## Network Issues

### Check Network Connectivity:
```bash
# Test if Docker can reach your IP
LOCAL_IP=$(ifconfig en0 | grep inet | grep -v inet6 | awk '{print $2}')
ping $LOCAL_IP

# Test X11 port
nc -z $LOCAL_IP 6000
```

### Firewall Issues:
If your firewall is blocking connections:
1. System Preferences > Security & Privacy > Firewall
2. Firewall Options > Allow XQuartz (if listed)
3. Or temporarily disable firewall for testing

## Docker-specific Issues

### Container Build Problems:
```bash
# Rebuild container if GUI libraries are missing
docker build -t redline_arm -f Dockerfile .
```

### Volume Mount Issues:
```bash
# Verify mounts work
docker run -it --rm -v $(pwd):/app/host redline_arm ls -la /app/host
```

## Getting Help

### Log Files to Check:
1. XQuartz logs: `~/Library/Logs/X11/`
2. Docker logs: `docker logs redline_gui`
3. REDLINE logs: `./redline.log`

### Useful Commands for Debugging:
```bash
# Check what's using X11
lsof -i :6000

# Check XQuartz process
ps aux | grep -i xquartz

# Check Docker containers
docker ps -a

# Check X11 environment
env | grep DISPLAY
```

### Contact Information:
For persistent issues, provide the following information:
1. macOS version: `sw_vers`
2. XQuartz version: `/Applications/Utilities/XQuartz.app/Contents/Info.plist`
3. Docker version: `docker --version`
4. Full error message and stack trace
5. Contents of `redline.log` 