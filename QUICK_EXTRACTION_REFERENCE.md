# REDLINE USB Package - Quick Extraction Reference

## 🚀 Quick Commands by Platform

### macOS
```bash
cd /Volumes/REDLINE
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz
```

### Windows (PowerShell/CMD)
```cmd
cd E:\
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz
```

### Ubuntu/Linux
```bash
cd /media/username/REDLINE
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz
```

### Android (Termux)
```bash
cd /storage/usbotg
tar -xzf REDLINE-1.0.0-USB-Test-Package.tar.gz
```

## 📁 After Extraction

```bash
cd usb-package
ls -la                    # Check contents
cat README.txt           # Read instructions
cat PACKAGE_INFO.txt     # Package details
```

## 🔍 Verify Extraction

Expected structure:
```
usb-package/
├── macOS/           # macOS app bundles
├── Windows/         # Windows installers
├── Ubuntu/          # Ubuntu DEB packages
├── Documentation/   # Security guides
├── README.txt       # Main instructions
└── PACKAGE_INFO.txt # Package details
```

## ⚠️ Troubleshooting

- **"tar: command not found"**: Install tar utility
- **"Permission denied"**: Use `sudo` (Linux/macOS)
- **"No space"**: Free disk space or extract elsewhere
- **Wrong drive letter**: Adjust path (E:\, F:\, etc.)

## 📞 Need Help?

See `USB_EXTRACTION_GUIDE.md` for detailed instructions.
