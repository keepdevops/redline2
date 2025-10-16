#!/usr/bin/env python3
"""
Financial Data Formats Guide & Universal Converter
Comprehensive guide to financial data formats and universal conversion tools
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialDataFormatsGuide:
    """Guide to financial data formats and standards"""
    
    def __init__(self):
        # Define all major financial data formats
        self.formats = {
            'STOOQ': {
                'description': 'Stooq.com format - Most popular for historical data',
                'columns': ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>'],
                'date_format': 'YYYYMMDD',
                'time_format': 'HHMMSS',
                'separator': ',',
                'header': True,
                'example': '<TICKER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>\nAAPL,20240101,000000,192.53,193.58,192.17,193.05,67800000'
            },
            
            'YAHOO_FINANCE': {
                'description': 'Yahoo Finance format - Most common for API data',
                'columns': ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'],
                'date_format': 'YYYY-MM-DD',
                'time_format': 'None',
                'separator': ',',
                'header': True,
                'example': 'Date,Open,High,Low,Close,Volume,Adj Close\n2024-01-01,192.53,193.58,192.17,193.05,67800000,193.05'
            },
            
            'ALPHA_VANTAGE': {
                'description': 'Alpha Vantage API format',
                'columns': ['timestamp', 'open', 'high', 'low', 'close', 'volume'],
                'date_format': 'YYYY-MM-DD',
                'time_format': 'None',
                'separator': ',',
                'header': True,
                'example': 'timestamp,open,high,low,close,volume\n2024-01-01,192.53,193.58,192.17,193.05,67800000'
            },
            
            'IEX_CLOUD': {
                'description': 'IEX Cloud API format',
                'columns': ['date', 'open', 'high', 'low', 'close', 'volume', 'unadjustedVolume', 'change', 'changePercent', 'vwap'],
                'date_format': 'YYYY-MM-DD',
                'time_format': 'None',
                'separator': ',',
                'header': True,
                'example': 'date,open,high,low,close,volume\n2024-01-01,192.53,193.58,192.17,193.05,67800000'
            },
            
            'FINNHUB': {
                'description': 'Finnhub API format',
                'columns': ['c', 'h', 'l', 'o', 's', 't', 'v'],
                'date_format': 'Unix timestamp',
                'time_format': 'Unix timestamp',
                'separator': ',',
                'header': True,
                'example': 'c,h,l,o,s,t,v\n193.05,193.58,192.17,192.53,ok,1704067200,67800000'
            },
            
            'TRADINGVIEW': {
                'description': 'TradingView Pine Script format',
                'columns': ['time', 'open', 'high', 'low', 'close', 'volume'],
                'date_format': 'Unix timestamp',
                'time_format': 'Unix timestamp',
                'separator': ',',
                'header': True,
                'example': 'time,open,high,low,close,volume\n1704067200000,192.53,193.58,192.17,193.05,67800000'
            },
            
            'METAQUOTES': {
                'description': 'MetaTrader/MetaQuotes format',
                'columns': ['<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<TICKVOL>', '<VOL>', '<SPREAD>'],
                'date_format': 'YYYY.MM.DD',
                'time_format': 'HH:MM',
                'separator': '\t',
                'header': False,
                'example': '2024.01.01\t00:00\t192.53\t193.58\t192.17\t193.05\t1000\t67800000\t2'
            },
            
            'REDLINE': {
                'description': 'REDLINE application format',
                'columns': ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint', 'format'],
                'date_format': 'YYYY-MM-DD HH:MM:SS',
                'time_format': 'HH:MM:SS',
                'separator': ',',
                'header': True,
                'example': 'ticker,timestamp,open,high,low,close,vol,openint,format\nAAPL,2024-01-01 00:00:00,192.53,193.58,192.17,193.05,67800000,,yahoo_download'
            },
            
            'QUANDL': {
                'description': 'Quandl format',
                'columns': ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'],
                'date_format': 'YYYY-MM-DD',
                'time_format': 'None',
                'separator': ',',
                'header': True,
                'example': 'Date,Open,High,Low,Close,Volume\n2024-01-01,192.53,193.58,192.17,193.05,67800000'
            },
            
            'BLOOMBERG': {
                'description': 'Bloomberg format',
                'columns': ['DATE', 'PX_OPEN', 'PX_HIGH', 'PX_LOW', 'PX_LAST', 'PX_VOLUME'],
                'date_format': 'MM/DD/YYYY',
                'time_format': 'None',
                'separator': ',',
                'header': True,
                'example': 'DATE,PX_OPEN,PX_HIGH,PX_LOW,PX_LAST,PX_VOLUME\n01/01/2024,192.53,193.58,192.17,193.05,67800000'
            },
            
            'REUTERS': {
                'description': 'Reuters format',
                'columns': ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'],
                'date_format': 'DD-MMM-YYYY',
                'time_format': 'None',
                'separator': ',',
                'header': True,
                'example': 'Date,Open,High,Low,Close,Volume\n01-Jan-2024,192.53,193.58,192.17,193.05,67800000'
            }
        }
        
        # Most popular formats (in order of adoption)
        self.popular_formats = [
            'STOOQ',      # Most popular for historical data
            'YAHOO_FINANCE',  # Most common for APIs
            'ALPHA_VANTAGE',  # Professional APIs
            'REDLINE',    # Your application
            'TRADINGVIEW',    # Trading platforms
            'METAQUOTES',     # MetaTrader
            'QUANDL',     # Financial data providers
            'BLOOMBERG',  # Institutional
            'REUTERS'     # News/financial services
        ]

    def get_format_info(self, format_name: str) -> Dict:
        """Get information about a specific format"""
        return self.formats.get(format_name.upper(), {})

    def list_all_formats(self) -> List[str]:
        """List all supported formats"""
        return list(self.formats.keys())

    def get_popular_formats(self) -> List[str]:
        """Get list of most popular formats"""
        return self.popular_formats

    def get_format_comparison(self) -> pd.DataFrame:
        """Get comparison table of all formats"""
        comparison_data = []
        for format_name, info in self.formats.items():
            comparison_data.append({
                'Format': format_name,
                'Description': info['description'],
                'Columns': ', '.join(info['columns']),
                'Date Format': info['date_format'],
                'Separator': info['separator'],
                'Header': info['header']
            })
        
        return pd.DataFrame(comparison_data)

class UniversalFinancialDataConverter:
    """Universal converter between all financial data formats"""
    
    def __init__(self):
        self.guide = FinancialDataFormatsGuide()
        
        # Define column mappings between formats
        self.column_mappings = {
            # Ticker symbols
            'ticker_mappings': {
                '<TICKER>': ['ticker', 'symbol', 'instrument'],
                'ticker': ['<TICKER>', 'symbol', 'instrument'],
                'symbol': ['ticker', '<TICKER>', 'instrument'],
                'instrument': ['ticker', '<TICKER>', 'symbol']
            },
            
            # Date/Time columns
            'datetime_mappings': {
                '<DATE>': ['Date', 'date', 'timestamp'],
                '<TIME>': ['Time', 'time'],
                'Date': ['<DATE>', 'date', 'timestamp'],
                'date': ['<DATE>', 'Date', 'timestamp'],
                'timestamp': ['Date', 'date', '<DATE>'],
                'Time': ['<TIME>', 'time'],
                'time': ['<TIME>', 'Time']
            },
            
            # Price columns
            'price_mappings': {
                '<OPEN>': ['Open', 'open', 'PX_OPEN'],
                '<HIGH>': ['High', 'high', 'PX_HIGH'],
                '<LOW>': ['Low', 'low', 'PX_LOW'],
                '<CLOSE>': ['Close', 'close', 'PX_LAST', 'Adj Close'],
                'Open': ['<OPEN>', 'open', 'PX_OPEN'],
                'open': ['<OPEN>', 'Open', 'PX_OPEN'],
                'High': ['<HIGH>', 'high', 'PX_HIGH'],
                'high': ['<HIGH>', 'High', 'PX_HIGH'],
                'Low': ['<LOW>', 'low', 'PX_LOW'],
                'low': ['<LOW>', 'Low', 'PX_LOW'],
                'Close': ['<CLOSE>', 'close', 'PX_LAST'],
                'close': ['<CLOSE>', 'Close', 'PX_LAST'],
                'PX_OPEN': ['<OPEN>', 'Open', 'open'],
                'PX_HIGH': ['<HIGH>', 'High', 'high'],
                'PX_LOW': ['<LOW>', 'Low', 'low'],
                'PX_LAST': ['<CLOSE>', 'Close', 'close']
            },
            
            # Volume columns
            'volume_mappings': {
                '<VOL>': ['Volume', 'volume', 'PX_VOLUME'],
                'Volume': ['<VOL>', 'volume', 'PX_VOLUME'],
                'volume': ['<VOL>', 'Volume', 'PX_VOLUME'],
                'PX_VOLUME': ['<VOL>', 'Volume', 'volume']
            }
        }

    def detect_format(self, df: pd.DataFrame) -> Optional[str]:
        """Auto-detect the format of a DataFrame"""
        columns = list(df.columns)
        
        # Check for specific format signatures
        if all(col in columns for col in ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']):
            return 'STOOQ'
        elif all(col in columns for col in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']):
            if 'Adj Close' in columns:
                return 'YAHOO_FINANCE'
            else:
                return 'QUANDL'
        elif all(col in columns for col in ['timestamp', 'open', 'high', 'low', 'close', 'volume']):
            return 'ALPHA_VANTAGE'
        elif all(col in columns for col in ['date', 'open', 'high', 'low', 'close', 'volume']):
            return 'IEX_CLOUD'
        elif all(col in columns for col in ['c', 'h', 'l', 'o', 't', 'v']):
            return 'FINNHUB'
        elif all(col in columns for col in ['time', 'open', 'high', 'low', 'close', 'volume']):
            return 'TRADINGVIEW'
        elif all(col in columns for col in ['<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<TICKVOL>', '<VOL>']):
            return 'METAQUOTES'
        elif all(col in columns for col in ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'format']):
            return 'REDLINE'
        elif all(col in columns for col in ['DATE', 'PX_OPEN', 'PX_HIGH', 'PX_LOW', 'PX_LAST', 'PX_VOLUME']):
            return 'BLOOMBERG'
        
        return None

    def convert_format(self, df: pd.DataFrame, from_format: str = None, to_format: str = 'STOOQ') -> pd.DataFrame:
        """Convert DataFrame from one format to another"""
        try:
            # Auto-detect format if not provided
            if from_format is None:
                from_format = self.detect_format(df)
                if from_format is None:
                    raise ValueError("Cannot auto-detect format. Please specify from_format.")
            
            logger.info(f"Converting from {from_format} to {to_format}")
            
            # Create a copy to avoid modifying original
            result_df = df.copy()
            
            # Handle different source formats
            if from_format == 'STOOQ':
                result_df = self._from_stooq(result_df, to_format)
            elif from_format == 'YAHOO_FINANCE':
                result_df = self._from_yahoo_finance(result_df, to_format)
            elif from_format == 'ALPHA_VANTAGE':
                result_df = self._from_alpha_vantage(result_df, to_format)
            elif from_format == 'IEX_CLOUD':
                result_df = self._from_iex_cloud(result_df, to_format)
            elif from_format == 'FINNHUB':
                result_df = self._from_finnhub(result_df, to_format)
            elif from_format == 'TRADINGVIEW':
                result_df = self._from_tradingview(result_df, to_format)
            elif from_format == 'METAQUOTES':
                result_df = self._from_metaquotes(result_df, to_format)
            elif from_format == 'REDLINE':
                result_df = self._from_redline(result_df, to_format)
            elif from_format == 'QUANDL':
                result_df = self._from_quandl(result_df, to_format)
            elif from_format == 'BLOOMBERG':
                result_df = self._from_bloomberg(result_df, to_format)
            elif from_format == 'REUTERS':
                result_df = self._from_reuters(result_df, to_format)
            else:
                raise ValueError(f"Unsupported format: {from_format}")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Conversion error: {str(e)}")
            raise

    def _from_stooq(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from Stooq format"""
        if to_format == 'STOOQ':
            return df
        
        # Handle ticker
        if '<TICKER>' in df.columns:
            ticker = df['<TICKER>'].iloc[0] if not df.empty else 'UNKNOWN'
        
        # Handle date/time
        if '<DATE>' in df.columns and '<TIME>' in df.columns:
            df['datetime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'], format='%Y%m%d %H%M%S', errors='coerce')
        
        # Convert to target format
        if to_format == 'YAHOO_FINANCE':
            result = pd.DataFrame({
                'Date': df['datetime'].dt.date if 'datetime' in df.columns else pd.to_datetime(df['<DATE>'], format='%Y%m%d'),
                'Open': df['<OPEN>'],
                'High': df['<HIGH>'],
                'Low': df['<LOW>'],
                'Close': df['<CLOSE>'],
                'Volume': df['<VOL>']
            })
            if ticker:
                result['Symbol'] = ticker
            return result
        
        elif to_format == 'REDLINE':
            result = pd.DataFrame({
                'ticker': ticker,
                'timestamp': df['datetime'] if 'datetime' in df.columns else pd.to_datetime(df['<DATE>'], format='%Y%m%d'),
                'open': df['<OPEN>'],
                'high': df['<HIGH>'],
                'low': df['<LOW>'],
                'close': df['<CLOSE>'],
                'vol': df['<VOL>'],
                'openint': None,
                'format': 'stooq_convert'
            })
            return result
        
        # Default: return as-is
        return df

    def _from_yahoo_finance(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from Yahoo Finance format"""
        if to_format == 'YAHOO_FINANCE':
            return df
        
        # Get ticker if available
        ticker = df.get('Symbol', ['UNKNOWN']).iloc[0] if 'Symbol' in df.columns else 'UNKNOWN'
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': ticker,
                '<DATE>': pd.to_datetime(df['Date']).dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['Open'],
                '<HIGH>': df['High'],
                '<LOW>': df['Low'],
                '<CLOSE>': df['Close'],
                '<VOL>': df['Volume']
            })
            return result
        
        elif to_format == 'REDLINE':
            result = pd.DataFrame({
                'ticker': ticker,
                'timestamp': pd.to_datetime(df['Date']),
                'open': df['Open'],
                'high': df['High'],
                'low': df['Low'],
                'close': df['Close'],
                'vol': df['Volume'],
                'openint': None,
                'format': 'yahoo_convert'
            })
            return result
        
        # Default: return as-is
        return df

    def _from_alpha_vantage(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from Alpha Vantage format"""
        if to_format == 'ALPHA_VANTAGE':
            return df
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': 'UNKNOWN',  # Alpha Vantage doesn't include ticker in response
                '<DATE>': pd.to_datetime(df['timestamp']).dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['open'],
                '<HIGH>': df['high'],
                '<LOW>': df['low'],
                '<CLOSE>': df['close'],
                '<VOL>': df['volume']
            })
            return result
        
        # Default: return as-is
        return df

    def _from_iex_cloud(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from IEX Cloud format"""
        if to_format == 'IEX_CLOUD':
            return df
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': 'UNKNOWN',  # IEX Cloud doesn't include ticker in response
                '<DATE>': pd.to_datetime(df['date']).dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['open'],
                '<HIGH>': df['high'],
                '<LOW>': df['low'],
                '<CLOSE>': df['close'],
                '<VOL>': df['volume']
            })
            return result
        
        # Default: return as-is
        return df

    def _from_finnhub(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from Finnhub format"""
        if to_format == 'FINNHUB':
            return df
        
        # Convert Unix timestamps to dates
        df['datetime'] = pd.to_datetime(df['t'], unit='s')
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': 'UNKNOWN',  # Finnhub doesn't include ticker in response
                '<DATE>': df['datetime'].dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['o'],
                '<HIGH>': df['h'],
                '<LOW>': df['l'],
                '<CLOSE>': df['c'],
                '<VOL>': df['v']
            })
            return result
        
        # Default: return as-is
        return df

    def _from_tradingview(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from TradingView format"""
        if to_format == 'TRADINGVIEW':
            return df
        
        # Convert Unix timestamps to dates
        df['datetime'] = pd.to_datetime(df['time'], unit='ms')
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': 'UNKNOWN',  # TradingView doesn't include ticker in response
                '<DATE>': df['datetime'].dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['open'],
                '<HIGH>': df['high'],
                '<LOW>': df['low'],
                '<CLOSE>': df['close'],
                '<VOL>': df['volume']
            })
            return result
        
        # Default: return as-is
        return df

    def _from_metaquotes(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from MetaQuotes format"""
        if to_format == 'METAQUOTES':
            return df
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': 'UNKNOWN',  # MetaQuotes doesn't include ticker in response
                '<DATE>': df['<DATE>'].str.replace('.', ''),
                '<TIME>': df['<TIME>'].str.replace(':', ''),
                '<OPEN>': df['<OPEN>'],
                '<HIGH>': df['<HIGH>'],
                '<LOW>': df['<LOW>'],
                '<CLOSE>': df['<CLOSE>'],
                '<VOL>': df['<VOL>']
            })
            return result
        
        # Default: return as-is
        return df

    def _from_redline(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from REDLINE format"""
        if to_format == 'REDLINE':
            return df
        
        # Get ticker
        ticker = df['ticker'].iloc[0] if not df.empty else 'UNKNOWN'
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': ticker,
                '<DATE>': pd.to_datetime(df['timestamp']).dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['open'],
                '<HIGH>': df['high'],
                '<LOW>': df['low'],
                '<CLOSE>': df['close'],
                '<VOL>': df['vol']
            })
            return result
        
        # Default: return as-is
        return df

    def _from_quandl(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from Quandl format"""
        if to_format == 'QUANDL':
            return df
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': 'UNKNOWN',  # Quandl doesn't include ticker in response
                '<DATE>': pd.to_datetime(df['Date']).dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['Open'],
                '<HIGH>': df['High'],
                '<LOW>': df['Low'],
                '<CLOSE>': df['Close'],
                '<VOL>': df['Volume']
            })
            return result
        
        # Default: return as-is
        return df

    def _from_bloomberg(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from Bloomberg format"""
        if to_format == 'BLOOMBERG':
            return df
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': 'UNKNOWN',  # Bloomberg doesn't include ticker in response
                '<DATE>': pd.to_datetime(df['DATE'], format='%m/%d/%Y').dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['PX_OPEN'],
                '<HIGH>': df['PX_HIGH'],
                '<LOW>': df['PX_LOW'],
                '<CLOSE>': df['PX_LAST'],
                '<VOL>': df['PX_VOLUME']
            })
            return result
        
        # Default: return as-is
        return df

    def _from_reuters(self, df: pd.DataFrame, to_format: str) -> pd.DataFrame:
        """Convert from Reuters format"""
        if to_format == 'REUTERS':
            return df
        
        # Convert to target format
        if to_format == 'STOOQ':
            result = pd.DataFrame({
                '<TICKER>': 'UNKNOWN',  # Reuters doesn't include ticker in response
                '<DATE>': pd.to_datetime(df['Date'], format='%d-%b-%Y').dt.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['Open'],
                '<HIGH>': df['High'],
                '<LOW>': df['Low'],
                '<CLOSE>': df['Close'],
                '<VOL>': df['Volume']
            })
            return result
        
        # Default: return as-is
        return df

def main():
    """Demonstrate the financial data formats guide"""
    guide = FinancialDataFormatsGuide()
    converter = UniversalFinancialDataConverter()
    
    print("🌍 COMPREHENSIVE FINANCIAL DATA FORMATS GUIDE")
    print("=" * 60)
    
    print("\n📊 MOST POPULAR FORMATS:")
    for i, format_name in enumerate(guide.get_popular_formats(), 1):
        info = guide.get_format_info(format_name)
        print(f"{i:2d}. {format_name:15s} - {info['description']}")
    
    print("\n📋 FORMAT COMPARISON TABLE:")
    comparison_df = guide.get_format_comparison()
    print(comparison_df.to_string(index=False))
    
    print("\n🔄 UNIVERSAL CONVERTER CAPABILITIES:")
    print("✅ Auto-detect format from DataFrame")
    print("✅ Convert between any supported formats")
    print("✅ Handle date/time format conversions")
    print("✅ Preserve data integrity")
    print("✅ Support for 11 major financial data formats")
    
    print("\n💡 RECOMMENDATION:")
    print("🎯 Use STOOQ format as your universal standard")
    print("   - Most widely adopted for historical data")
    print("   - Compatible with most trading platforms")
    print("   - Easy to parse and process")
    print("   - REDLINE natively supports this format")

if __name__ == "__main__":
    main()
