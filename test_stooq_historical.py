#!/usr/bin/env python3
"""
Quick test script for Stooq historical data download
"""

from stooq_historical_data_downloader import StooqHistoricalDownloader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_stooq_historical():
    """Test Stooq historical data download"""
    downloader = StooqHistoricalDownloader()
    
    # Test with a single ticker first
    ticker = "AAPL"
    print(f"🧪 Testing Stooq historical data download for {ticker}...")
    
    try:
        data = downloader.download_historical_data(ticker)
        
        if data is not None and not data.empty:
            print(f"✅ Success! Downloaded {len(data)} records for {ticker}")
            print(f"📊 Columns: {list(data.columns)}")
            print(f"📅 Date range: {data['<DATE>'].min()} to {data['<DATE>'].max()}")
            print("\n📋 Sample data:")
            print(data.head())
            
            # Save test data
            filename = f"test_{ticker}_historical.csv"
            data.to_csv(filename, index=False)
            print(f"\n💾 Test data saved to: {filename}")
            
            return True
        else:
            print(f"❌ Failed to download data for {ticker}")
            print("💡 This is expected - Stooq blocks automated access")
            print("💡 Use manual download or Yahoo Finance instead")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_stooq_historical()
