# REDLINE Local Environment Setup Guide

<div align="center">

![Local Setup](https://img.shields.io/badge/Local%20Setup-Complete-green?style=for-the-badge&logo=computer)

**Complete guide for setting up REDLINE in your local environment**

[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](README.md)
[![Conda](https://img.shields.io/badge/Conda-Supported-blue?logo=anaconda)](README.md)

</div>

---

## 🚀 **Quick Setup (5 Minutes)**

### **Prerequisites**
- **Python 3.11+** installed
- **Conda** or **Miniconda** installed
- **Git** (for cloning the repository)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/your-repo/redline.git
cd redline
```

### **Step 2: Choose Installation Method**

#### **Option A: Use Existing Stock Environment (Recommended)**
```bash
# Activate existing stock environment
conda activate stock

# Verify dependencies
python -c "import pandas, numpy, pyarrow, duckdb, polars; print('✅ All dependencies available')"

# Run REDLINE
python main.py
```

#### **Option B: Create New Conda Environment**
```bash
# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate redline

# Run REDLINE
python main.py
```

#### **Option B: Pip Installation**
```bash
# Install dependencies
pip install -r requirements.txt

# Run REDLINE
python main.py
```

#### **Option C: Manual Installation**
```bash
# Install core dependencies
conda install pandas numpy pyarrow polars duckdb yfinance -c conda-forge

# Install optional dependencies
conda install scikit-learn matplotlib seaborn -c conda-forge

# Run REDLINE
python main.py
```

---

## 📦 **Dependencies Overview**

### **Core Dependencies**
| Package | Purpose | Version |
|---------|---------|---------|
| **pandas** | Data manipulation | ≥2.0.0 |
| **numpy** | Numerical computing | ≥1.24.0 |
| **pyarrow** | Parquet support | ≥10.0.0 |
| **polars** | Fast data processing | ≥0.20.0 |
| **duckdb** | Embedded database | ≥0.8.0 |
| **yfinance** | Yahoo Finance data | ≥0.2.0 |

### **GUI Dependencies**
| Package | Purpose | Installation |
|---------|---------|--------------|
| **tkinter** | GUI framework | Built into Python |

### **Optional Dependencies**
| Package | Purpose | Installation |
|---------|---------|--------------|
| **scikit-learn** | Machine learning | `conda install scikit-learn` |
| **matplotlib** | Plotting | `conda install matplotlib` |
| **seaborn** | Statistical plots | `conda install seaborn` |

---

## 🧪 **Testing Your Installation**

### **Test 1: Verify Dependencies**
```bash
python -c "
import pandas as pd
import numpy as np
import pyarrow as pa
import polars as pl
import duckdb
import yfinance as yf
print('✅ All dependencies installed successfully!')
"
```

### **Test 2: Test Conversion Functionality**
```bash
python test_local_conversion.py
```

### **Test 3: Launch GUI**
```bash
python main.py --task=gui
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Issue: ImportError for pyarrow**
```bash
# Solution: Install pyarrow
conda install pyarrow -c conda-forge
# or
pip install pyarrow
```

#### **Issue: ImportError for duckdb**
```bash
# Solution: Install duckdb
conda install duckdb -c conda-forge
# or
pip install duckdb
```

#### **Issue: ImportError for polars**
```bash
# Solution: Install polars
conda install polars -c conda-forge
# or
pip install polars
```

#### **Issue: GUI won't start**
```bash
# Check Python version
python --version

# Ensure tkinter is available
python -c "import tkinter; print('✅ tkinter available')"

# Try alternative launch
python main.py --task=gui
```

### **Performance Issues**

#### **Slow Data Loading**
- Use **Parquet** format for large datasets
- Enable **virtual scrolling** in settings
- Close unused applications

#### **Memory Issues**
- Use **DuckDB** format for analysis
- Process data in chunks
- Monitor memory usage in status bar

---

## 📊 **Format Support Status**

### **✅ Fully Supported (Local Environment)**
| Format | Read | Write | Performance |
|--------|------|-------|-------------|
| **CSV** | ✅ | ✅ | Good |
| **JSON** | ✅ | ✅ | Good |
| **Parquet** | ✅ | ✅ | Excellent |
| **Feather** | ✅ | ✅ | Excellent |
| **DuckDB** | ✅ | ✅ | Excellent |

### **⚠️ Limited Support**
| Format | Read | Write | Notes |
|--------|------|-------|-------|
| **TXT** | ✅ | ❌ | Stooq format only |
| **Excel** | ❌ | ❌ | Future release |

---

## 🚀 **Performance Comparison**

### **Local vs Docker Environment**
| Feature | Local Environment | Docker Environment |
|---------|------------------|-------------------|
| **Startup Time** | ~2 seconds | ~10 seconds |
| **Memory Usage** | Lower | Higher |
| **File Access** | Direct | Containerized |
| **Dependencies** | System-wide | Isolated |
| **Performance** | Native | Virtualized |

### **Recommended Usage**
- **Local Environment**: Development, testing, small datasets
- **Docker Environment**: Production, large datasets, deployment

---

## 🔄 **Updating Dependencies**

### **Update Conda Environment**
```bash
# Update all packages
conda env update -f environment.yml

# Update specific package
conda update pyarrow -c conda-forge
```

### **Update Pip Packages**
```bash
# Update all packages
pip install -r requirements.txt --upgrade

# Update specific package
pip install --upgrade pandas
```

---

## 🎯 **Best Practices**

### **Environment Management**
1. **Use conda environments** for dependency isolation
2. **Pin package versions** for reproducible builds
3. **Regular updates** for security and performance
4. **Clean unused packages** periodically

### **Data Management**
1. **Use Parquet** for large datasets (10x smaller than CSV)
2. **Use DuckDB** for analysis and queries
3. **Use Feather** for fast Python/R workflows
4. **Use CSV** for compatibility

### **Performance Optimization**
1. **Enable virtual scrolling** for large datasets
2. **Monitor memory usage** in status bar
3. **Close unused tabs** to free memory
4. **Use batch operations** for multiple files

---

## 🆘 **Getting Help**

### **Local Environment Issues**
- **Check dependencies**: `python -c "import package_name"`
- **Test conversion**: `python test_local_conversion.py`
- **Check logs**: Look for error messages in console
- **Verify Python version**: `python --version`

### **Support Resources**
- **Documentation**: [README.md](README.md)
- **User Guide**: [REDLINE_USER_GUIDE.md](REDLINE_USER_GUIDE.md)
- **Troubleshooting**: [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md)
- **GitHub Issues**: Report bugs and feature requests

---

<div align="center">

**Your local REDLINE environment is now ready! 🎉**

[![Next Step](https://img.shields.io/badge/Next%20Step-User%20Guide-blue?style=for-the-badge&logo=book)](REDLINE_USER_GUIDE.md)

</div>
