# Current Data Download Guide for REDLINE

## Overview

This guide explains how to download current historical financial data and process it with REDLINE. Due to Stooq's two-factor authentication requirements, we provide alternative methods using Yahoo Finance.

## Available Data Sources

### 1. Yahoo Finance (Recommended)
- **Pros**: No authentication required, reliable, fast
- **Cons**: Different data format than Stooq
- **Usage**: Use `yahoo_data_downloader.py`

### 2. Stooq (Limited)
- **Pros**: Original Stooq format
- **Cons**: Requires 2FA, connectivity issues
- **Usage**: Use `stooq_data_downloader.py` (may not work due to 2FA)

## Quick Start

### Download Current Data

```bash
# Download specific tickers
python yahoo_data_downloader.py --tickers AAPL MSFT GOOGL

# Download popular stocks
python yahoo_data_downloader.py --popular

# Download with custom date range
python yahoo_data_downloader.py --tickers AAPL --start-date 2024-01-01 --end-date 2024-12-31

# Download with different period
python yahoo_data_downloader.py --tickers AAPL --period 2y
```

### Process with REDLINE

1. **Start REDLINE**:
   ```bash
   python main.py
   ```

2. **Load Downloaded Data**:
   - Open REDLINE GUI
   - Go to "Data Loader" tab
   - Click "Browse Files"
   - Select the downloaded CSV files from `data/` directory
   - Choose "CSV" as input format
   - Choose desired output format (DuckDB, Parquet, etc.)
   - Click "Process Files"

## Data Format Compatibility

Both downloaders create data in REDLINE-compatible format:

```csv
ticker,timestamp,open,high,low,close,vol,openint,format
AAPL,2024-10-16 00:00:00-04:00,230.52,231.04,228.77,230.70,34082200,,yahoo_download
```

## Available Tickers

### Popular US Stocks (automatically downloaded with --popular flag)
- AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, BRK-B
- JPM, JNJ, V, PG, UNH, HD, MA, DIS, PYPL, ADBE
- CRM, NFLX, INTC, CMCSA, PFE, TMO, ABT, COST, WMT
- MRK, PEP, KO, AVGO, ACN, TXN, NKE, DHR, VZ, CSCO
- QCOM, T, LLY, WFC, RTX, SPGI, UNP, HON, UPS, LOW

### Custom Tickers
You can specify any ticker symbol supported by Yahoo Finance:
- US stocks: AAPL, MSFT, GOOGL, etc.
- International: ^GSPC (S&P 500), ^IXIC (NASDAQ), etc.
- ETFs: SPY, QQQ, etc.

## Date Ranges and Periods

### Date Range Options
```bash
--start-date 2024-01-01 --end-date 2024-12-31
```

### Period Options (if dates not specified)
- `1d` - 1 day
- `5d` - 5 days  
- `1mo` - 1 month
- `3mo` - 3 months
- `6mo` - 6 months
- `1y` - 1 year (default)
- `2y` - 2 years
- `5y` - 5 years
- `10y` - 10 years
- `ytd` - Year to date
- `max` - Maximum available

## Integration with REDLINE

### 1. Direct File Loading
1. Download data using the scripts
2. Open REDLINE GUI
3. Load files through Data Loader tab
4. Process and convert to desired format

### 2. Database Integration
1. Download data
2. Load into REDLINE
3. Save to DuckDB format
4. Use in other REDLINE sessions

### 3. Batch Processing
```bash
# Download multiple datasets
python yahoo_data_downloader.py --tickers AAPL MSFT GOOGL --period 2y
python yahoo_data_downloader.py --popular --period 1y

# Process all in REDLINE
python main.py
# Then load all CSV files from data/ directory
```

## Troubleshooting

### Yahoo Finance Issues
- **No data returned**: Check ticker symbol spelling
- **Connection timeout**: Try again, Yahoo Finance can be slow
- **Rate limiting**: Increase delay between requests

### REDLINE Integration Issues
- **File not recognized**: Ensure CSV files have proper headers
- **Column mismatch**: Use the standardized format from downloaders
- **Memory issues**: Process files in smaller batches

### Stooq Issues
- **2FA required**: Stooq now requires two-factor authentication
- **Connection timeouts**: Stooq servers may be slow or unavailable
- **Alternative**: Use Yahoo Finance downloader instead

## Example Workflows

### Workflow 1: Quick Data Update
```bash
# Download latest data for your portfolio
python yahoo_data_downloader.py --tickers AAPL MSFT GOOGL TSLA

# Process in REDLINE
python main.py
# Load the 4 CSV files from data/ directory
```

### Workflow 2: Historical Analysis
```bash
# Download 5 years of data for analysis
python yahoo_data_downloader.py --tickers AAPL --period 5y

# Process and save to DuckDB for analysis
python main.py
# Load AAPL_yahoo_data.csv, convert to DuckDB
```

### Workflow 3: Market Research
```bash
# Download popular stocks for market overview
python yahoo_data_downloader.py --popular --period 1y

# Process all stocks in REDLINE
python main.py
# Load popular_stocks_yahoo.csv, analyze market trends
```

## File Locations

- **Downloaded data**: `data/` directory
- **Individual tickers**: `data/{TICKER}_yahoo_data.csv`
- **Combined data**: `data/custom_tickers_yahoo.csv` or `data/popular_stocks_yahoo.csv`
- **REDLINE database**: `redline_data.duckdb` (created after processing)

## Next Steps

1. **Download current data** using the Yahoo Finance downloader
2. **Process data** through REDLINE GUI
3. **Convert to desired format** (DuckDB, Parquet, etc.)
4. **Use for analysis** or machine learning workflows

The downloaded data is fully compatible with REDLINE's processing pipeline and can be used for all the same purposes as traditional Stooq data files.
