# REDLINE Subscription Service - Getting Started Guide

## 🚀 **Quick Start**

Get started with REDLINE in minutes - no installation required!

### **Step 1: Register for an Account**

1. **Visit** https://redfindat.com
2. **Click "Register"** in the navigation bar
3. **Fill in your information**:
   - Name
   - Email address
   - Company (optional)
4. **Submit registration**
5. **Check your email** for your license key

### **Step 2: Access REDLINE**

1. **Open your web browser** (Chrome, Firefox, Safari, or Edge)
2. **Navigate to** https://redfindat.com
3. **Enter your license key** when prompted
4. **Start using REDLINE** immediately

### **Step 3: Add Hours to Your Account**

1. **Go to Settings tab** or Payment page
2. **Choose a package**:
   - 5 hours
   - 10 hours
   - 20 hours
   - 50 hours
   - Custom hours
3. **Complete payment** via Stripe
4. **Hours are added** automatically to your account

---

## 🌐 **System Requirements**

### **Browser Requirements**

| Browser | Minimum Version | Recommended |
|---------|----------------|-------------|
| **Chrome** | 90+ | Latest |
| **Firefox** | 88+ | Latest |
| **Safari** | 14+ | Latest |
| **Edge** | 90+ | Latest |

### **Network Requirements**

- **Internet Connection**: Broadband connection required
- **Bandwidth**: Minimum 1 Mbps for optimal performance
- **HTTPS**: Secure connection required (HTTPS)

### **Device Requirements**

- **Screen Resolution**: Minimum 1280x720, recommended 1920x1080 or higher
- **JavaScript**: Must be enabled
- **Cookies**: Must be enabled for session management
- **Local Storage**: Required for theme preferences

---

## 📋 **Account Setup**

### **Registration Process**

1. **Visit Registration Page**: https://redfindat.com/register
2. **Enter Information**:
   - Full Name
   - Email Address (used for license key delivery)
   - Company Name (optional)
3. **Submit Registration**
4. **Receive License Key**: Check your email for your license key
5. **Login**: Use your license key to access the platform

### **License Key Format**

License keys follow this format:
```
RL-DEV-XXXXXXXX-XXXXXXXX-XXXXXXXX
```

Example:
```
RL-DEV-8dfdb2e7-c606053c-7d0c15f4
```

### **First Login**

1. **Enter License Key**: Paste your license key in the login prompt
2. **Access Granted**: You'll be redirected to the dashboard
3. **Check Balance**: View your remaining hours in Settings tab
4. **Start Using**: Begin downloading and analyzing data

---

## 💳 **Subscription & Payment**

### **Hour Packages**

REDLINE uses a time-based subscription model. Purchase hours to use the platform:

| Package | Hours | Price |
|---------|-------|-------|
| **Starter** | 5 hours | $X.XX |
| **Standard** | 10 hours | $X.XX |
| **Professional** | 20 hours | $X.XX |
| **Enterprise** | 50 hours | $X.XX |
| **Custom** | Any amount | Custom pricing |

### **Adding Hours**

1. **Navigate to Payment Tab** or Settings > Payment
2. **Select Package**: Choose from available packages or enter custom hours
3. **Click "Purchase"**: Redirected to Stripe checkout
4. **Complete Payment**: Secure payment via Stripe
5. **Hours Added**: Hours are automatically added to your account

### **Usage Tracking**

- **Session-based**: Hours are tracked per active session
- **Automatic Deduction**: Hours are deducted when you use the platform
- **Real-time Balance**: Check your balance anytime in Settings
- **Usage History**: View detailed usage history

### **Payment Methods**

- **Credit Cards**: Visa, Mastercard, American Express
- **Debit Cards**: Supported debit cards
- **Secure Processing**: All payments processed via Stripe

---

## 🔑 **API Key Configuration**

### **Built-in Data Sources**

REDLINE supports multiple data sources. Some require API keys:

#### **Yahoo Finance**
- ✅ **No API Key Required**: Free to use
- ✅ **Recommended**: Best for most users
- ✅ **Comprehensive**: Stocks, ETFs, indices, crypto

#### **Alpha Vantage**
- 🔑 **API Key Required**: Get free key at alphavantage.co
- ✅ **Real-time Data**: Live market data
- 📊 **Rate Limits**: Free tier: 5 calls/minute

#### **Finnhub**
- 🔑 **API Key Required**: Get free key at finnhub.io
- ✅ **Real-time Data**: Live market data
- 📊 **Rate Limits**: Free tier: 60 calls/minute

### **Configuring API Keys**

1. **Go to Settings Tab**
2. **Click "API Keys"** section
3. **Enter API Keys**:
   - Alpha Vantage API Key
   - Finnhub API Key
   - IEX Cloud API Key (optional)
4. **Save Configuration**: API keys are securely stored and masked

### **Custom API Configuration**

1. **Click "Add Custom API"** in Settings > API Keys
2. **Configure Your API**:
   - **Name**: Display name for your API
   - **Base URL**: API base endpoint (e.g., `https://api.example.com`)
   - **Endpoint**: Data endpoint path (e.g., `/v1/data`)
   - **API Key**: Your API key (masked for security)
   - **Rate Limit**: Requests per minute
   - **Date Format**: Expected date format (YYYY-MM-DD, etc.)
   - **Parameter Names**: Ticker, date, API key parameter names
3. **Save Configuration**
4. **Use in Download Tab**: Your custom API will appear as a data source

---

## 🎨 **Theme Customization**

### **Available Themes**

REDLINE offers 8 color-blind friendly themes:

1. **Default** - Clean, professional theme
2. **High Contrast** - Maximum contrast for accessibility
3. **Ocean** - Blue color scheme
4. **Forest** - Green color scheme
5. **Sunset** - Orange/red color scheme
6. **Monochrome** - Grayscale theme
7. **Grayscale** - Black and white theme
8. **Dark** - Dark mode theme

### **Changing Themes**

1. **Click Theme Selector** in the navigation bar
2. **Select Theme**: Choose from available themes
3. **Theme Applied**: Changes are applied immediately
4. **Saved Automatically**: Your preference is saved

### **Color Customization**

1. **Go to Settings Tab**
2. **Click "Font Colors"** section
3. **Customize Colors**: Adjust colors for different UI elements
4. **Save Preferences**: Your custom colors are saved

---

## 📊 **Getting Started with Data**

### **First Data Download**

1. **Go to Download Tab**
2. **Select Data Source**: Choose Yahoo Finance (recommended)
3. **Enter Ticker**: Try `AAPL` (Apple)
4. **Select Date Range**: Choose `2Y` (2 years)
5. **Click "Download"**
6. **Wait for Completion**: Progress bar shows download status
7. **File Saved**: Data is saved to your account

### **Loading and Viewing Data**

1. **Go to Data Tab**
2. **Click "Load Data"**
3. **Select File**: Choose your downloaded file
4. **Data Loaded**: Data appears in virtual scrolling table
5. **Customize Display**: Use date format selector and column editor

### **Running Your First Analysis**

1. **Load Data**: Load a data file in Data tab
2. **Go to Analysis Tab**
3. **Select Analysis Type**: Choose "Basic Analysis"
4. **Click "Run Analysis"**
5. **View Results**: Analysis results are displayed
6. **Export Results**: Save results to CSV or JSON

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"License key missing" Error**
- **Cause**: License key not provided or expired
- **Solution**: Enter your license key in the login prompt or Settings tab
- **Check Balance**: Verify you have hours remaining in Settings

#### **"Failed to retrieve balance"**
- **Cause**: License server temporarily unavailable
- **Solution**: Check your internet connection and try again
- **Note**: The platform will continue to work with local tracking

#### **"API key invalid" Error**
- **Cause**: API key is incorrect or expired
- **Solution**: Update your API key in Settings > API Keys
- **Check**: Verify API key is correct and has sufficient quota

#### **Browser Compatibility Issues**
- **Cause**: Using an unsupported browser
- **Solution**: Update to the latest version of Chrome, Firefox, Safari, or Edge
- **Check**: Verify JavaScript and cookies are enabled

### **Performance Optimization**

#### **Large Datasets**
- Use virtual scrolling (automatic)
- Process data in chunks
- Consider using Parquet format for storage
- Close unused browser tabs

#### **Download Speed**
- Use Yahoo Finance for fastest downloads
- Download multiple tickers in batches
- Avoid peak market hours for better performance
- Check your internet connection speed

### **Getting Help**

#### **Support Resources**
- **Help Page**: Access comprehensive documentation at https://redfindat.com/help
- **Settings Tab**: View system information and logs
- **Email Support**: Contact support@redfindat.com

---

## 📚 **Additional Resources**

- **User Guide**: [REDLINE_USER_GUIDE.md](REDLINE_USER_GUIDE.md) - Complete user guide
- **API Reference**: [REDLINE_API_REFERENCE.md](REDLINE_API_REFERENCE.md) - API documentation
- **Comprehensive Documentation**: [REDLINE_COMPREHENSIVE_DOCUMENTATION.md](REDLINE_COMPREHENSIVE_DOCUMENTATION.md) - Full documentation

---

## 🆘 **Support**

For additional help or to report issues:
1. Check the troubleshooting section above
2. Review the Help page in the application
3. Contact support@redfindat.com
4. Ensure you're using a supported browser

---

**REDLINE: Professional-grade financial data analysis accessible through cloud subscription service.** 🚀
