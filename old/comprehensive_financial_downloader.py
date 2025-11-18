#!/usr/bin/env python3
"""
Comprehensive Financial Data Downloader
Downloads all types of financial data: Stocks, ETFs, Crypto, Forex, Commodities, Bonds, etc.
"""

import yfinance as yf
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveFinancialDownloader:
    """Download all types of financial data"""
    
    def __init__(self):
        # Comprehensive financial instruments database
        self.financial_data = {
            # US STOCKS
            'US_LARGE_CAP': self.get_us_large_cap(),
            'US_MID_CAP': self.get_us_mid_cap(),
            'US_SMALL_CAP': self.get_us_small_cap(),
            'US_GROWTH': self.get_us_growth_stocks(),
            'US_VALUE': self.get_us_value_stocks(),
            'US_DIVIDEND': self.get_us_dividend_stocks(),
            
            # INTERNATIONAL STOCKS
            'EUROPEAN': self.get_european_stocks(),
            'ASIAN': self.get_asian_stocks(),
            'EMERGING_MARKETS': self.get_emerging_market_stocks(),
            
            # SECTORS
            'TECHNOLOGY': self.get_technology_stocks(),
            'HEALTHCARE': self.get_healthcare_stocks(),
            'FINANCIAL': self.get_financial_stocks(),
            'ENERGY': self.get_energy_stocks(),
            'CONSUMER': self.get_consumer_stocks(),
            'INDUSTRIAL': self.get_industrial_stocks(),
            'MATERIALS': self.get_materials_stocks(),
            'REAL_ESTATE': self.get_real_estate_stocks(),
            'UTILITIES': self.get_utilities_stocks(),
            
            # ETFs
            'SP500_ETFS': self.get_sp500_etfs(),
            'SECTOR_ETFS': self.get_sector_etfs(),
            'INTERNATIONAL_ETFS': self.get_international_etfs(),
            'BOND_ETFS': self.get_bond_etfs(),
            'COMMODITY_ETFS': self.get_commodity_etfs(),
            
            # CRYPTOCURRENCIES
            'MAJOR_CRYPTO': self.get_major_cryptocurrencies(),
            'ALTCOINS': self.get_altcoins(),
            'DEFI_TOKENS': self.get_defi_tokens(),
            
            # FOREX
            'MAJOR_PAIRS': self.get_major_forex_pairs(),
            'MINOR_PAIRS': self.get_minor_forex_pairs(),
            'EXOTIC_PAIRS': self.get_exotic_forex_pairs(),
            
            # COMMODITIES
            'PRECIOUS_METALS': self.get_precious_metals(),
            'ENERGY_COMMODITIES': self.get_energy_commodities(),
            'AGRICULTURAL': self.get_agricultural_commodities(),
            'INDUSTRIAL_METALS': self.get_industrial_metals(),
            
            # BONDS
            'GOVERNMENT_BONDS': self.get_government_bonds(),
            'CORPORATE_BONDS': self.get_corporate_bonds(),
            'MUNICIPAL_BONDS': self.get_municipal_bonds(),
            
            # INDICES
            'STOCK_INDICES': self.get_stock_indices(),
            'COMMODITY_INDICES': self.get_commodity_indices(),
            'BOND_INDICES': self.get_bond_indices(),
            
            # CUSTOM
            'CUSTOM': []
        }

    # US STOCKS
    def get_us_large_cap(self) -> List[str]:
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B', 
               'UNH', 'JNJ', 'JPM', 'V', 'PG', 'HD', 'MA', 'PFE', 'ABBV', 'CVX', 
               'BAC', 'KO', 'AVGO', 'PEP', 'TMO', 'COST', 'WMT', 'DHR', 'ABT', 
               'ACN', 'VZ', 'NFLX', 'ADBE', 'TXN', 'NKE', 'CRM', 'RTX', 'QCOM',
               'PM', 'T', 'LIN', 'UNP', 'SPGI', 'HON', 'IBM', 'AMAT', 'GE', 'LOW']

    def get_us_mid_cap(self) -> List[str]:
        return ['AMD', 'INTC', 'PYPL', 'CMCSA', 'CSCO', 'AVGO', 'INTU', 'BKNG', 
               'ISRG', 'GILD', 'ADP', 'VRTX', 'REGN', 'MDLZ', 'FISV', 'CHTR', 
               'ATVI', 'ILMN', 'BIIB', 'CTSH', 'EXC', 'WBA', 'SBUX', 'KHC', 
               'CSX', 'TMUS', 'LRCX', 'AMGN', 'MRNA', 'XEL', 'NFLX', 'GOOGL']

    def get_us_small_cap(self) -> List[str]:
        return ['ZM', 'DOCU', 'SNOW', 'PLTR', 'ROKU', 'SQ', 'SHOP', 'CRWD', 
               'OKTA', 'NET', 'DDOG', 'TWLO', 'ESTC', 'SPOT', 'UBER', 'LYFT', 
               'PINS', 'SNAP', 'TWTR', 'WORK', 'ZM', 'DOCU', 'SNOW', 'PLTR']

    def get_us_growth_stocks(self) -> List[str]:
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 
               'ADBE', 'CRM', 'PYPL', 'SHOP', 'ZM', 'DOCU', 'SNOW', 'PLTR']

    def get_us_value_stocks(self) -> List[str]:
        return ['BRK-B', 'JPM', 'BAC', 'WFC', 'C', 'XOM', 'CVX', 'JNJ', 'PG', 
               'KO', 'PFE', 'WMT', 'HD', 'VZ', 'T', 'IBM', 'GE', 'F']

    def get_us_dividend_stocks(self) -> List[str]:
        return ['JNJ', 'PG', 'KO', 'PFE', 'WMT', 'HD', 'VZ', 'T', 'IBM', 'GE', 
               'F', 'XOM', 'CVX', 'JPM', 'BAC', 'WFC', 'C', 'ABBV', 'MRK']

    # INTERNATIONAL STOCKS
    def get_european_stocks(self) -> List[str]:
        return ['ASML', 'NVO', 'SAP', 'UL', 'RHHBY', 'TM', 'NVO', 'SAP', 'UL', 
               'RHHBY', 'TM', 'NVO', 'SAP', 'UL', 'RHHBY', 'TM']

    def get_asian_stocks(self) -> List[str]:
        return ['TM', 'HDB', 'TSM', 'BABA', 'JD', 'PDD', 'NIO', 'XPEV', 'LI', 
               'BILI', 'NTES', 'BIDU', 'VIPS', 'YMM', 'DIDI', 'GRAB']

    def get_emerging_market_stocks(self) -> List[str]:
        return ['BABA', 'JD', 'PDD', 'NIO', 'XPEV', 'LI', 'BILI', 'NTES', 'BIDU', 
               'VIPS', 'YMM', 'DIDI', 'GRAB', 'TM', 'HDB', 'TSM']

    # SECTORS
    def get_technology_stocks(self) -> List[str]:
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'NFLX', 'ADBE', 
               'CRM', 'ORCL', 'INTC', 'AMD', 'PYPL', 'CMCSA', 'TXN', 'QCOM', 
               'AMAT', 'CSCO', 'AVGO', 'INTU']

    def get_healthcare_stocks(self) -> List[str]:
        return ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 
               'LLY', 'GILD', 'AMGN', 'BIIB', 'VRTX', 'REGN', 'ILMN']

    def get_financial_stocks(self) -> List[str]:
        return ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC', 'TFC', 'BK', 
               'STT', 'NTRS', 'RF', 'HBAN', 'KEY', 'CFG']

    def get_energy_stocks(self) -> List[str]:
        return ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO', 'KMI', 
               'WMB', 'OKE', 'EPD', 'ENB', 'TRP', 'PPL', 'DUK']

    def get_consumer_stocks(self) -> List[str]:
        return ['AMZN', 'TSLA', 'HD', 'LOW', 'WMT', 'TGT', 'COST', 'SBUX', 'MCD', 
               'NKE', 'LULU', 'ROKU', 'NFLX', 'DIS', 'CMCSA']

    def get_industrial_stocks(self) -> List[str]:
        return ['BA', 'CAT', 'GE', 'HON', 'UPS', 'FDX', 'LMT', 'RTX', 'GD', 'NOC', 
               'MMM', 'EMR', 'ETN', 'ITW', 'PH', 'CMI']

    def get_materials_stocks(self) -> List[str]:
        return ['LIN', 'APD', 'SHW', 'ECL', 'DOW', 'DD', 'NEM', 'FCX', 'AA', 'X', 
               'CLF', 'STLD', 'NUE', 'RS', 'LYB']

    def get_real_estate_stocks(self) -> List[str]:
        return ['AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'WELL', 'AVB', 'EQR', 'MAA', 
               'UDR', 'EXR', 'CPT', 'ESS', 'AIV', 'BXP']

    def get_utilities_stocks(self) -> List[str]:
        return ['NEE', 'DUK', 'SO', 'D', 'EXC', 'AEP', 'XEL', 'ES', 'WEC', 'PPL', 
               'ED', 'ETR', 'FE', 'AEE', 'CNP']

    # ETFs
    def get_sp500_etfs(self) -> List[str]:
        return ['SPY', 'VOO', 'IVV', 'SPTM', 'SPLG', 'FXAIX', 'FZROX', 'SWPPX']

    def get_sector_etfs(self) -> List[str]:
        return ['XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'XLB', 'XLRE']

    def get_international_etfs(self) -> List[str]:
        return ['VEA', 'VWO', 'EFA', 'EEM', 'IEFA', 'IEMG', 'VXUS', 'IXUS']

    def get_bond_etfs(self) -> List[str]:
        return ['BND', 'AGG', 'TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'EMB']

    def get_commodity_etfs(self) -> List[str]:
        return ['GLD', 'SLV', 'USO', 'UNG', 'DBA', 'DJP', 'PDBC', 'GSG']

    # CRYPTOCURRENCIES
    def get_major_cryptocurrencies(self) -> List[str]:
        return ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'SOL-USD', 
               'DOT-USD', 'DOGE-USD', 'AVAX-USD', 'SHIB-USD']

    def get_altcoins(self) -> List[str]:
        return ['LINK-USD', 'UNI-USD', 'LTC-USD', 'BCH-USD', 'ATOM-USD', 'MATIC-USD', 
               'ALGO-USD', 'VET-USD', 'ICP-USD', 'FIL-USD']

    def get_defi_tokens(self) -> List[str]:
        return ['UNI-USD', 'AAVE-USD', 'COMP-USD', 'MKR-USD', 'SUSHI-USD', 'CRV-USD', 
               'YFI-USD', 'SNX-USD', 'BAL-USD', 'LRC-USD']

    # FOREX
    def get_major_forex_pairs(self) -> List[str]:
        return ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'USDCHF=X', 'AUDUSD=X', 'USDCAD=X', 
               'NZDUSD=X', 'EURGBP=X', 'EURJPY=X', 'GBPJPY=X']

    def get_minor_forex_pairs(self) -> List[str]:
        return ['EURAUD=X', 'EURCHF=X', 'EURCAD=X', 'EURNZD=X', 'GBPAUD=X', 'GBPCHF=X', 
               'GBPCAD=X', 'GBPNZD=X', 'AUDCHF=X', 'AUDCAD=X']

    def get_exotic_forex_pairs(self) -> List[str]:
        return ['USDTRY=X', 'USDZAR=X', 'USDMXN=X', 'USDPLN=X', 'USDCZK=X', 'USDHUF=X', 
               'USDSEK=X', 'USDNOK=X', 'USDDKK=X', 'USDSGD=X']

    # COMMODITIES
    def get_precious_metals(self) -> List[str]:
        return ['GC=F', 'SI=F', 'PL=F', 'PA=F', 'GLD', 'SLV', 'PPLT', 'PALL']

    def get_energy_commodities(self) -> List[str]:
        return ['CL=F', 'NG=F', 'RB=F', 'HO=F', 'USO', 'UNG', 'UCO', 'BNO']

    def get_agricultural_commodities(self) -> List[str]:
        return ['ZC=F', 'ZS=F', 'ZW=F', 'KC=F', 'CC=F', 'SB=F', 'CT=F', 'LB=F']

    def get_industrial_metals(self) -> List[str]:
        return ['HG=F', 'ALI=F', 'NID=F', 'PA=F', 'PL=F', 'SI=F']

    # BONDS
    def get_government_bonds(self) -> List[str]:
        return ['^TNX', '^FVX', '^IRX', 'TLT', 'IEF', 'SHY', 'GOVT', 'VGIT']

    def get_corporate_bonds(self) -> List[str]:
        return ['LQD', 'HYG', 'VCSH', 'VCIT', 'VCLT', 'VGSH', 'VGIT', 'VGLT']

    def get_municipal_bonds(self) -> List[str]:
        return ['MUB', 'HYD', 'VTEB', 'SHM', 'PZA', 'XMPT', 'VRD', 'MMIN']

    # INDICES
    def get_stock_indices(self) -> List[str]:
        return ['^GSPC', '^DJI', '^IXIC', '^RUT', '^VIX', '^TNX', '^FVX', '^IRX']

    def get_commodity_indices(self) -> List[str]:
        return ['DJP', 'GSG', 'PDBC', 'DBA', 'JJM', 'JJN', 'JJC', 'JJA']

    def get_bond_indices(self) -> List[str]:
        return ['^TNX', '^FVX', '^IRX', 'AGG', 'BND', 'TLT', 'IEF', 'SHY']

    def convert_to_stooq_format(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """Convert DataFrame to Stooq format"""
        try:
            # Handle timezone-aware timestamps
            if hasattr(df.index, 'tz') and df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            # Create Stooq format DataFrame
            df_stooq = pd.DataFrame({
                '<TICKER>': ticker,
                '<DATE>': df.index.strftime('%Y%m%d'),
                '<TIME>': '000000',
                '<OPEN>': df['Open'].values,
                '<HIGH>': df['High'].values,
                '<LOW>': df['Low'].values,
                '<CLOSE>': df['Close'].values,
                '<VOL>': df['Volume'].values
            })
            
            # Clean numeric data
            numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
            for col in numeric_cols:
                df_stooq[col] = pd.to_numeric(df_stooq[col], errors='coerce')
            
            # Remove rows with invalid data
            df_stooq = df_stooq.dropna()
            
            return df_stooq
            
        except Exception as e:
            logger.error(f"Error converting {ticker} to Stooq format: {str(e)}")
            return pd.DataFrame()

    def download_single_instrument(self, ticker: str, start_date: str = None, end_date: str = None, period: str = "2y") -> Optional[pd.DataFrame]:
        """Download data for a single financial instrument"""
        try:
            instrument = yf.Ticker(ticker)
            
            if start_date and end_date:
                data = instrument.history(start=start_date, end=end_date)
            else:
                data = instrument.history(period=period)
            
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return None
            
            return self.convert_to_stooq_format(data, ticker)
            
        except Exception as e:
            logger.error(f"Error downloading {ticker}: {str(e)}")
            return None

    def download_multiple_instruments(self, tickers: List[str], start_date: str = None, end_date: str = None, 
                                    period: str = "2y", max_workers: int = 5, delay: float = 0.1) -> Dict[str, pd.DataFrame]:
        """Download data for multiple financial instruments with threading"""
        results = {}
        failed_tickers = []
        
        def download_worker(ticker):
            """Worker function for downloading single instrument"""
            try:
                time.sleep(delay)  # Rate limiting
                data = self.download_single_instrument(ticker, start_date, end_date, period)
                return ticker, data
            except Exception as e:
                logger.error(f"Worker error for {ticker}: {str(e)}")
                return ticker, None
        
        logger.info(f"Starting bulk download for {len(tickers)} instruments...")
        logger.info(f"Using {max_workers} threads with {delay}s delay between requests")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_ticker = {executor.submit(download_worker, ticker): ticker for ticker in tickers}
            
            # Process completed downloads
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    ticker, data = future.result()
                    if data is not None and not data.empty:
                        results[ticker] = data
                        logger.info(f"✅ Downloaded {ticker}: {len(data)} records")
                    else:
                        failed_tickers.append(ticker)
                        logger.warning(f"❌ Failed {ticker}")
                except Exception as e:
                    failed_tickers.append(ticker)
                    logger.error(f"❌ Error processing {ticker}: {str(e)}")
        
        logger.info(f"Bulk download complete: {len(results)} successful, {len(failed_tickers)} failed")
        if failed_tickers:
            logger.warning(f"Failed tickers: {failed_tickers[:10]}...")  # Show first 10
        
        return results

class ComprehensiveFinancialGUI:
    """GUI for comprehensive financial data download"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Comprehensive Financial Data Downloader")
        self.root.geometry("1000x900")
        
        self.downloader = ComprehensiveFinancialDownloader()
        self.results = {}
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI"""
        # Title
        title_label = tk.Label(self.root, text="🌍 Comprehensive Financial Data Downloader", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=15)
        
        # Description
        desc_label = tk.Label(self.root, 
                             text="Download ALL types of financial data: Stocks, ETFs, Crypto, Forex, Commodities, Bonds, Indices\n" +
                                  "Complete financial market coverage",
                             justify=tk.CENTER, font=("Arial", 10))
        desc_label.pack(pady=5)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # STOCKS TAB
        stocks_frame = ttk.Frame(notebook)
        notebook.add(stocks_frame, text="📈 Stocks")
        self.setup_stocks_tab(stocks_frame)
        
        # ETFs TAB
        etfs_frame = ttk.Frame(notebook)
        notebook.add(etfs_frame, text="📊 ETFs")
        self.setup_etfs_tab(etfs_frame)
        
        # CRYPTO TAB
        crypto_frame = ttk.Frame(notebook)
        notebook.add(crypto_frame, text="₿ Crypto")
        self.setup_crypto_tab(crypto_frame)
        
        # FOREX TAB
        forex_frame = ttk.Frame(notebook)
        notebook.add(forex_frame, text="💱 Forex")
        self.setup_forex_tab(forex_frame)
        
        # COMMODITIES TAB
        commodities_frame = ttk.Frame(notebook)
        notebook.add(commodities_frame, text="🏭 Commodities")
        self.setup_commodities_tab(commodities_frame)
        
        # BONDS TAB
        bonds_frame = ttk.Frame(notebook)
        notebook.add(bonds_frame, text="🏛️ Bonds")
        self.setup_bonds_tab(bonds_frame)
        
        # INDICES TAB
        indices_frame = ttk.Frame(notebook)
        notebook.add(indices_frame, text="📊 Indices")
        self.setup_indices_tab(indices_frame)
        
        # CUSTOM TAB
        custom_frame = ttk.Frame(notebook)
        notebook.add(custom_frame, text="✏️ Custom")
        self.setup_custom_tab(custom_frame)
        
        # Settings and controls
        self.setup_controls()
    
    def setup_stocks_tab(self, parent):
        """Setup stocks tab"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="📈 STOCK MARKETS", font=("Arial", 14, "bold")).pack(pady=10)
        
        # US Stocks
        us_frame = tk.LabelFrame(frame, text="🇺🇸 US Stocks", font=("Arial", 12, "bold"))
        us_frame.pack(fill=tk.X, pady=10)
        
        us_options = [
            ("Large Cap (50 stocks)", "US_LARGE_CAP"),
            ("Mid Cap (30 stocks)", "US_MID_CAP"),
            ("Small Cap (25 stocks)", "US_SMALL_CAP"),
            ("Growth Stocks (16 stocks)", "US_GROWTH"),
            ("Value Stocks (19 stocks)", "US_VALUE"),
            ("Dividend Stocks (19 stocks)", "US_DIVIDEND")
        ]
        
        for text, value in us_options:
            btn = tk.Button(us_frame, text=text, width=25, height=2,
                           command=lambda v=value: self.select_category(v))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # International Stocks
        intl_frame = tk.LabelFrame(frame, text="🌍 International Stocks", font=("Arial", 12, "bold"))
        intl_frame.pack(fill=tk.X, pady=10)
        
        intl_options = [
            ("European Stocks (16 stocks)", "EUROPEAN"),
            ("Asian Stocks (16 stocks)", "ASIAN"),
            ("Emerging Markets (16 stocks)", "EMERGING_MARKETS")
        ]
        
        for text, value in intl_options:
            btn = tk.Button(intl_frame, text=text, width=25, height=2,
                           command=lambda v=value: self.select_category(v))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Sectors
        sector_frame = tk.LabelFrame(frame, text="🏢 Sectors", font=("Arial", 12, "bold"))
        sector_frame.pack(fill=tk.X, pady=10)
        
        sector_options = [
            ("Technology (20 stocks)", "TECHNOLOGY"),
            ("Healthcare (16 stocks)", "HEALTHCARE"),
            ("Financial (16 stocks)", "FINANCIAL"),
            ("Energy (16 stocks)", "ENERGY"),
            ("Consumer (15 stocks)", "CONSUMER"),
            ("Industrial (16 stocks)", "INDUSTRIAL"),
            ("Materials (15 stocks)", "MATERIALS"),
            ("Real Estate (15 stocks)", "REAL_ESTATE"),
            ("Utilities (15 stocks)", "UTILITIES")
        ]
        
        for i in range(0, len(sector_options), 3):
            row_frame = tk.Frame(sector_frame)
            row_frame.pack(fill=tk.X, pady=2)
            for j in range(3):
                if i + j < len(sector_options):
                    text, value = sector_options[i + j]
                    btn = tk.Button(row_frame, text=text, width=25, height=2,
                                   command=lambda v=value: self.select_category(v))
                    btn.pack(side=tk.LEFT, padx=5, pady=2)
    
    def setup_etfs_tab(self, parent):
        """Setup ETFs tab"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="📊 EXCHANGE TRADED FUNDS", font=("Arial", 14, "bold")).pack(pady=10)
        
        etf_options = [
            ("S&P 500 ETFs (8 ETFs)", "SP500_ETFS"),
            ("Sector ETFs (10 ETFs)", "SECTOR_ETFS"),
            ("International ETFs (8 ETFs)", "INTERNATIONAL_ETFS"),
            ("Bond ETFs (8 ETFs)", "BOND_ETFS"),
            ("Commodity ETFs (8 ETFs)", "COMMODITY_ETFS")
        ]
        
        for text, value in etf_options:
            btn = tk.Button(frame, text=text, width=30, height=3,
                           command=lambda v=value: self.select_category(v))
            btn.pack(pady=10)
    
    def setup_crypto_tab(self, parent):
        """Setup crypto tab"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="₿ CRYPTOCURRENCIES", font=("Arial", 14, "bold")).pack(pady=10)
        
        crypto_options = [
            ("Major Cryptocurrencies (10 coins)", "MAJOR_CRYPTO"),
            ("Altcoins (10 coins)", "ALTCOINS"),
            ("DeFi Tokens (10 tokens)", "DEFI_TOKENS")
        ]
        
        for text, value in crypto_options:
            btn = tk.Button(frame, text=text, width=30, height=3,
                           command=lambda v=value: self.select_category(v))
            btn.pack(pady=10)
    
    def setup_forex_tab(self, parent):
        """Setup forex tab"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="💱 FOREX MARKETS", font=("Arial", 14, "bold")).pack(pady=10)
        
        forex_options = [
            ("Major Forex Pairs (10 pairs)", "MAJOR_PAIRS"),
            ("Minor Forex Pairs (10 pairs)", "MINOR_PAIRS"),
            ("Exotic Forex Pairs (10 pairs)", "EXOTIC_PAIRS")
        ]
        
        for text, value in forex_options:
            btn = tk.Button(frame, text=text, width=30, height=3,
                           command=lambda v=value: self.select_category(v))
            btn.pack(pady=10)
    
    def setup_commodities_tab(self, parent):
        """Setup commodities tab"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="🏭 COMMODITIES", font=("Arial", 14, "bold")).pack(pady=10)
        
        commodity_options = [
            ("Precious Metals (8 metals)", "PRECIOUS_METALS"),
            ("Energy Commodities (8 commodities)", "ENERGY_COMMODITIES"),
            ("Agricultural (8 commodities)", "AGRICULTURAL"),
            ("Industrial Metals (6 metals)", "INDUSTRIAL_METALS")
        ]
        
        for text, value in commodity_options:
            btn = tk.Button(frame, text=text, width=30, height=3,
                           command=lambda v=value: self.select_category(v))
            btn.pack(pady=10)
    
    def setup_bonds_tab(self, parent):
        """Setup bonds tab"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="🏛️ BONDS", font=("Arial", 14, "bold")).pack(pady=10)
        
        bond_options = [
            ("Government Bonds (8 bonds)", "GOVERNMENT_BONDS"),
            ("Corporate Bonds (8 bonds)", "CORPORATE_BONDS"),
            ("Municipal Bonds (8 bonds)", "MUNICIPAL_BONDS")
        ]
        
        for text, value in bond_options:
            btn = tk.Button(frame, text=text, width=30, height=3,
                           command=lambda v=value: self.select_category(v))
            btn.pack(pady=10)
    
    def setup_indices_tab(self, parent):
        """Setup indices tab"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="📊 INDICES", font=("Arial", 14, "bold")).pack(pady=10)
        
        index_options = [
            ("Stock Indices (8 indices)", "STOCK_INDICES"),
            ("Commodity Indices (8 indices)", "COMMODITY_INDICES"),
            ("Bond Indices (8 indices)", "BOND_INDICES")
        ]
        
        for text, value in index_options:
            btn = tk.Button(frame, text=text, width=30, height=3,
                           command=lambda v=value: self.select_category(v))
            btn.pack(pady=10)
    
    def setup_custom_tab(self, parent):
        """Setup custom tab"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(frame, text="✏️ CUSTOM INSTRUMENTS", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(frame, text="Enter any ticker symbols (comma-separated):").pack(pady=10)
        self.custom_entry = tk.Entry(frame, width=80, font=("Arial", 10))
        self.custom_entry.insert(0, "AAPL,MSFT,GOOGL,BTC-USD,ETH-USD,GC=F,CL=F,EURUSD=X,^GSPC")
        self.custom_entry.pack(pady=10)
        
        custom_btn = tk.Button(frame, text="📊 Download Custom List", 
                              command=lambda: self.select_category("CUSTOM"), 
                              bg="#4caf50", fg="white", font=("Arial", 12))
        custom_btn.pack(pady=20)
    
    def setup_controls(self):
        """Setup download controls"""
        # Settings frame
        settings_frame = tk.LabelFrame(self.root, text="⚙️ Download Settings", font=("Arial", 12, "bold"))
        settings_frame.pack(pady=10, padx=20, fill=tk.X)
        
        settings_grid = tk.Frame(settings_frame)
        settings_grid.pack(pady=10)
        
        # Date range
        tk.Label(settings_grid, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5)
        self.start_date_entry = tk.Entry(settings_grid, width=15)
        self.start_date_entry.insert(0, "2020-01-01")
        self.start_date_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(settings_grid, text="End Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5)
        self.end_date_entry = tk.Entry(settings_grid, width=15)
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.end_date_entry.grid(row=0, column=3, padx=5)
        
        # Threading settings
        tk.Label(settings_grid, text="Max Threads:").grid(row=1, column=0, padx=5)
        self.threads_entry = tk.Entry(settings_grid, width=10)
        self.threads_entry.insert(0, "5")
        self.threads_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(settings_grid, text="Delay (seconds):").grid(row=1, column=2, padx=5)
        self.delay_entry = tk.Entry(settings_grid, width=10)
        self.delay_entry.insert(0, "0.1")
        self.delay_entry.grid(row=1, column=3, padx=5)
        
        # Download button
        download_btn = tk.Button(self.root, text="🚀 Start Comprehensive Download", 
                                command=self.start_comprehensive_download, 
                                bg="#4caf50", fg="white", font=("Arial", 14, "bold"))
        download_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=5, padx=20, fill=tk.X)
        
        # Progress label
        self.progress_label = tk.Label(self.root, text="Ready to download", font=("Arial", 10))
        self.progress_label.pack(pady=5)
        
        # Status text
        status_frame = tk.LabelFrame(self.root, text="📋 Download Status", font=("Arial", 12, "bold"))
        status_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=10, width=120, font=("Courier", 9))
        scrollbar = tk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Save button
        save_btn = tk.Button(self.root, text="💾 Save All Financial Data", 
                            command=self.save_all_data, 
                            bg="#ff9800", fg="white", font=("Arial", 12))
        save_btn.pack(pady=10)
        
        self.selected_category = None
    
    def select_category(self, category):
        """Select a financial category"""
        self.selected_category = category
        if category == "CUSTOM":
            custom_text = self.custom_entry.get().strip()
            if not custom_text:
                messagebox.showerror("Error", "Please enter custom tickers")
                return
            tickers = [ticker.strip().upper() for ticker in custom_text.split(',') if ticker.strip()]
        else:
            tickers = self.downloader.financial_data.get(category, [])
        
        self.log_status(f"📊 Selected: {category} ({len(tickers)} instruments)")
        self.log_status(f"🎯 Instruments: {', '.join(tickers[:10])}{'...' if len(tickers) > 10 else ''}")
    
    def log_status(self, message):
        """Log status message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def start_comprehensive_download(self):
        """Start comprehensive download"""
        if not self.selected_category:
            messagebox.showerror("Error", "Please select a financial category first")
            return
        
        if self.selected_category == "CUSTOM":
            custom_text = self.custom_entry.get().strip()
            if not custom_text:
                messagebox.showerror("Error", "Please enter custom tickers")
                return
            tickers = [ticker.strip().upper() for ticker in custom_text.split(',') if ticker.strip()]
        else:
            tickers = self.downloader.financial_data.get(self.selected_category, [])
        
        if not tickers:
            messagebox.showerror("Error", "No tickers found for selected category")
            return
        
        # Get settings
        start_date = self.start_date_entry.get().strip() or None
        end_date = self.end_date_entry.get().strip() or None
        max_workers = int(self.threads_entry.get() or 5)
        delay = float(self.delay_entry.get() or 0.1)
        
        # Start download in background thread
        self.progress.start()
        self.progress_label.config(text=f"Downloading {len(tickers)} financial instruments...")
        self.status_text.delete(1.0, tk.END)
        
        # Run download in separate thread
        thread = threading.Thread(target=self.comprehensive_download_worker, 
                                args=(tickers, start_date, end_date, max_workers, delay))
        thread.daemon = True
        thread.start()
    
    def comprehensive_download_worker(self, tickers, start_date, end_date, max_workers, delay):
        """Worker function for comprehensive download"""
        try:
            self.log_status(f"🌍 Starting comprehensive financial data download...")
            self.log_status(f"📊 Category: {self.selected_category}")
            self.log_status(f"🎯 Instruments: {len(tickers)}")
            self.log_status(f"📅 Date range: {start_date or 'N/A'} to {end_date or 'N/A'}")
            self.log_status(f"⚙️ Settings: {max_workers} threads, {delay}s delay")
            
            self.results = self.downloader.download_multiple_instruments(
                tickers, start_date, end_date, "2y", max_workers, delay
            )
            
            if self.results:
                total_records = sum(len(data) for data in self.results.values())
                self.log_status(f"\n🎉 Comprehensive download complete!")
                self.log_status(f"✅ Successfully downloaded: {len(self.results)} instruments")
                self.log_status(f"❌ Failed: {len(tickers) - len(self.results)} instruments")
                self.log_status(f"📊 Total records: {total_records:,}")
                
                # Show breakdown by type
                self.log_status(f"\n📈 Breakdown:")
                stock_count = len([t for t in self.results.keys() if not any(x in t for x in ['-USD', '=X', '=F', '^', '=F'])])
                crypto_count = len([t for t in self.results.keys() if '-USD' in t])
                forex_count = len([t for t in self.results.keys() if '=X' in t])
                commodity_count = len([t for t in self.results.keys() if '=F' in t])
                index_count = len([t for t in self.results.keys() if '^' in t])
                
                self.log_status(f"  📈 Stocks: {stock_count}")
                self.log_status(f"  ₿ Crypto: {crypto_count}")
                self.log_status(f"  💱 Forex: {forex_count}")
                self.log_status(f"  🏭 Commodities: {commodity_count}")
                self.log_status(f"  📊 Indices: {index_count}")
                
                self.log_status(f"\n💾 Click 'Save All Financial Data' to export")
            else:
                self.log_status(f"\n❌ No data downloaded. Check your internet connection.")
            
        except Exception as e:
            self.log_status(f"\n❌ Comprehensive download error: {str(e)}")
        finally:
            self.progress.stop()
            self.progress_label.config(text="Download complete")
    
    def save_all_data(self):
        """Save all downloaded financial data"""
        if not self.results:
            messagebox.showwarning("Warning", "No data to save. Please download data first.")
            return
        
        # Ask for directory
        directory = filedialog.askdirectory(title="Select directory to save financial data")
        if not directory:
            return
        
        try:
            # Create subdirectories by type
            subdirs = {
                'stocks': [],
                'crypto': [],
                'forex': [],
                'commodities': [],
                'indices': [],
                'etfs': [],
                'bonds': []
            }
            
            # Categorize files
            for ticker, data in self.results.items():
                if '-USD' in ticker:
                    subdirs['crypto'].append((ticker, data))
                elif '=X' in ticker:
                    subdirs['forex'].append((ticker, data))
                elif '=F' in ticker:
                    subdirs['commodities'].append((ticker, data))
                elif '^' in ticker:
                    subdirs['indices'].append((ticker, data))
                elif any(etf in ticker for etf in ['SPY', 'VOO', 'IVV', 'XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'XLB', 'XLRE', 'GLD', 'SLV', 'BND', 'AGG']):
                    subdirs['etfs'].append((ticker, data))
                elif any(bond in ticker for bond in ['TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'EMB']):
                    subdirs['bonds'].append((ticker, data))
                else:
                    subdirs['stocks'].append((ticker, data))
            
            saved_files = []
            
            # Save by category
            for category, files in subdirs.items():
                if files:
                    category_dir = os.path.join(directory, category)
                    os.makedirs(category_dir, exist_ok=True)
                    
                    for ticker, data in files:
                        filename = os.path.join(category_dir, f"{ticker}_financial_data.csv")
                        data.to_csv(filename, index=False)
                        saved_files.append(filename)
            
            # Save combined file
            all_data = pd.concat(list(self.results.values()), ignore_index=True)
            combined_filename = os.path.join(directory, f"comprehensive_financial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            all_data.to_csv(combined_filename, index=False)
            
            messagebox.showinfo("Success", f"Saved financial data organized by category to:\n{directory}")
            self.log_status(f"\n💾 Saved {len(saved_files)} individual files + 1 combined file")
            self.log_status(f"📁 Directory: {directory}")
            self.log_status(f"📊 Organized by: stocks, crypto, forex, commodities, indices, etfs, bonds")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
            self.log_status(f"\n❌ Save error: {str(e)}")

def main():
    """Main function"""
    app = ComprehensiveFinancialGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
