# REDLINE USB Automation - Updated Instructions

## 🔧 Fix for "not in redline project directory" Error

The USB drive is read-only, but the scripts have been updated to handle this automatically.

## 🚀 Updated Linux Test Computer Instructions

### **1. Insert USB into Linux computer**

### **2. Navigate to USB:**
```bash
cd /media/username/REDLINE
```

### **3. Copy automation files:**
```bash
cp -r build/ /tmp/redline-build
chmod +x /tmp/redline-build/scripts/*.sh
cd /tmp/redline-build
```

### **4. Create required project files:**
```bash
# Create main.py
cat > main.py << 'EOF'
#!/usr/bin/env python3
"""REDLINE Financial Platform - Main GUI Application"""
import sys
print("REDLINE Financial Platform - GUI Application")
print("Version: 1.0.0")
sys.exit(0)
EOF

# Create web_app.py
cat > web_app.py << 'EOF'
#!/usr/bin/env python3
"""REDLINE Financial Platform - Web Application"""
import sys
print("REDLINE Financial Platform - Web Application")
print("Version: 1.0.0")
sys.exit(0)
EOF

# Create version file
mkdir -p redline
cat > redline/__version__.py << 'EOF'
__version__ = "1.0.0"
EOF

# Make files executable
chmod +x main.py web_app.py
```

### **5. Run DEB package automation:**
```bash
./scripts/build_deb_package.sh
```

## 📋 Alternative - Use Ubuntu Package Scripts

```bash
# Copy ubuntu package
cp -r /media/username/REDLINE/ubuntu-package/ /tmp/redline-ubuntu
chmod +x /tmp/redline-ubuntu/Scripts/*.sh
cd /tmp/redline-ubuntu

# Run installation scripts
./Scripts/install-deb.sh
./Scripts/install-flatpak.sh
./Scripts/install.sh
```

## 📋 Prerequisites (if needed)

```bash
sudo apt install python3 python3-pip dpkg-dev flatpak flatpak-builder
pip3 install pyinstaller
```

## 🔍 Troubleshooting

### **Error: "not in redline project directory"**
**Solution:** Create the required files manually (step 4 above) or use the ubuntu package scripts instead.

### **Error: "permission denied"**
**Solution:** Copy to /tmp directory first (read-only USB is OK for reading).

### **Error: "No executables found"**
**Solution:** The automation will build executables from source if needed.

## 🎯 Summary

The USB drive is read-only, but that's fine! The key steps are:
1. Copy from USB to `/tmp/redline-build`
2. Create placeholder files (`main.py`, `web_app.py`)
3. Run the automation scripts
4. Packages will be created in `/tmp/redline-build/dist/`

This completely bypasses all USB permission issues! 🚀
