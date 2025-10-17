# REDLINE Quick Start Guide

<div align="center">

![Quick Start](https://img.shields.io/badge/Quick%20Start-5%20Minutes-green?style=for-the-badge&logo=rocket)

**Get up and running with REDLINE in 5 minutes**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](README.md)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](README.md)

</div>

---

## 🚀 **5-Minute Setup**

### **Step 1: Choose Your Method (1 minute)**

| Method | Best For | Command |
|--------|----------|---------|
| **Docker** | Beginners, no setup | `./run_gui.bash` |
| **Local** | Developers, customization | `pip install + python main.py` |
| **Test** | Troubleshooting | `./test_x11.bash` |

### **Step 2: Start REDLINE (1 minute)**

**🎯 Recommended: Docker Method**
```bash
# Clone the repository
git clone https://github.com/your-repo/redline.git
cd redline

# Run with Docker (includes all dependencies)
./run_gui.bash
```

**🔧 Alternative: Local Installation**
```bash
# Install Python dependencies
pip install pandas yfinance duckdb pyarrow polars tkinter

# Run the application
python main.py
```

### **Step 3: Download Your First Data (2 minutes)**

1. **Click the "Download" tab**
2. **Enter a ticker symbol**: `AAPL` (Apple)
3. **Select date range**: `2Y` (2 years)
4. **Click "Download"**
5. **Wait for completion** (progress bar will show)

### **Step 4: Load and Explore Data (1 minute)**

1. **Click the "Data" tab**
2. **Click "Load Data" button**
3. **Select your downloaded file** (usually in `data/downloaded/`)
4. **Explore the data** - scroll, filter, analyze!

---

## 🎯 **What You Just Did**

✅ **Downloaded real financial data** from Yahoo Finance  
✅ **Loaded data into REDLINE** for analysis  
✅ **Explored the interface** and data structure  
✅ **Set up your workspace** for future analysis  

---

## 🔥 **Next Steps**

### **Try These Features**

| Feature | Location | What to Try |
|---------|----------|-------------|
| **Filter Data** | Data tab → Filter button | Filter by date range or price |
| **Convert Format** | Converter tab | Convert CSV to Parquet |
| **Analyze Trends** | Analysis tab | View statistical analysis |
| **Download More** | Download tab | Try different tickers (MSFT, GOOGL) |

### **Pro Tips**

- **Use Parquet format** for large datasets (10x smaller than CSV)
- **Enable virtual scrolling** for 10M+ rows
- **Monitor memory usage** in the status bar
- **Save your work** regularly using the Data tab

---

## 🆘 **Need Help?**

### **Common Issues**

| Problem | Solution |
|---------|----------|
| **GUI won't start** | Run `./test_x11.bash` first |
| **Download fails** | Check internet connection |
| **Memory errors** | Use Parquet format, close other apps |
| **File not found** | Check file path in settings |

### **Getting Support**

- **Check logs**: `docker logs redline_gui`
- **Test installation**: `./test_x11.bash`
- **Report issues**: GitHub Issues with logs
- **Read full guide**: [REDLINE_USER_GUIDE.md](REDLINE_USER_GUIDE.md)

---

## 🎉 **Congratulations!**

You've successfully:
- ✅ Installed and started REDLINE
- ✅ Downloaded financial data
- ✅ Loaded and explored data
- ✅ Learned the basics

**You're now ready to use REDLINE for professional financial data analysis!**

---

<div align="center">

**Ready for more? Check out the [Complete User Guide](REDLINE_USER_GUIDE.md)**

[![Next Step](https://img.shields.io/badge/Next%20Step-User%20Guide-blue?style=for-the-badge&logo=book)](REDLINE_USER_GUIDE.md)

</div>
