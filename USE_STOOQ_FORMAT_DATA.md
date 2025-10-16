# Using Stooq Format Data with REDLINE

## Problem Solved ✅

The error "Missing columns: <DATE>, <TIME>, <CLOSE>" has been resolved! Your data is now in the correct Stooq format that REDLINE expects.

## Available Data Files

You now have properly formatted Stooq data files in the `data/stooq_format/` directory:

- `custom_tickers_yahoo_stooq_format.csv` - Multiple tickers (AAPL, MSFT, TSLA, GOOGL, AMZN)
- `AAPL_yahoo_data_stooq_format.csv` - Apple stock data
- `MSFT_yahoo_data_stooq_format.csv` - Microsoft stock data

## Data Format

The converted files now have the exact columns REDLINE expects:

```
<TICKER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>
AAPL,20241016,000000,230.52713995218937,231.04472016362837,228.77528327315235,230.706298828125,34082200
```

## How to Use

### Option 1: Use the Converted Files Directly
```bash
# Copy the Stooq format file to your main data directory
cp data/stooq_format/custom_tickers_yahoo_stooq_format.csv data/custom_tickers_stooq.csv

# Run REDLINE
python main.py
```

### Option 2: Update Your Data Configuration
Update your `data_config.ini` to point to the Stooq format files:
```ini
[data_sources]
stooq_files = data/stooq_format/custom_tickers_yahoo_stooq_format.csv
```

### Option 3: Use the Converter for New Data
```bash
# Convert any new downloaded data to Stooq format
python convert_to_stooq_format.py --input data/new_file.csv --output data/new_file_stooq.csv

# Or convert all CSV files in a directory
python convert_to_stooq_format.py --batch
```

## Future Downloads

The `yahoo_data_downloader.py` has been updated to output in Stooq format directly. When Yahoo Finance rate limits are lifted, you can download new data:

```python
from yahoo_data_downloader import YahooDataDownloader
downloader = YahooDataDownloader()
data = downloader.download_ticker_data('AAPL', period='1y')
```

## Data Sources Available

1. **Yahoo Finance** (Updated to Stooq format) - Reliable, no authentication needed
2. **Stooq Manual Download** - Use `stooq_manual_downloader.py` for manual authentication
3. **Universal GUI** - Use `universal_gui_downloader.py` to choose between sources

## Next Steps

1. Try running `python main.py` with the converted data
2. If you need more recent data, wait for Yahoo rate limits to reset (usually 15-60 minutes)
3. For real-time Stooq data, use the manual downloader GUI

The missing columns error should now be resolved! 🎉
