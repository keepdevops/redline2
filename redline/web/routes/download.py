"""
Download tab routes for REDLINE Web GUI
Handles data downloading from various sources
"""

from flask import Blueprint, render_template, request, jsonify
import logging
from datetime import datetime, timedelta

download_bp = Blueprint('download', __name__)
logger = logging.getLogger(__name__)

@download_bp.route('/')
def download_tab():
    """Download tab main page."""
    return render_template('download_tab.html')

@download_bp.route('/sources')
def get_sources():
    """Get available data sources."""
    try:
        sources = {
            'yahoo': {
                'name': 'Yahoo Finance',
                'description': 'Free financial data from Yahoo Finance',
                'supported_tickers': 'US and international stocks, ETFs, indices',
                'data_types': ['OHLCV', 'dividends', 'splits'],
                'delay': '15-20 minutes for real-time data',
                'rate_limit': 'Rate limited - may fail frequently',
                'api_key_required': False
            },
            'stooq': {
                'name': 'Stooq',
                'description': 'Free historical financial data',
                'supported_tickers': 'Global stocks and indices',
                'data_types': ['OHLCV'],
                'delay': 'End of day',
                'rate_limit': 'May require 2FA',
                'api_key_required': False
            },
            'alpha_vantage': {
                'name': 'Alpha Vantage',
                'description': 'Professional financial data API',
                'supported_tickers': 'US and international stocks',
                'data_types': ['OHLCV', 'fundamentals', 'news'],
                'delay': 'Real-time',
                'rate_limit': '5 calls per minute (free tier)',
                'api_key_required': True,
                'api_key_url': 'https://www.alphavantage.co/support/#api-key'
            },
            'finnhub': {
                'name': 'Finnhub',
                'description': 'Global financial data API',
                'supported_tickers': 'Global stocks, forex, crypto',
                'data_types': ['OHLCV', 'fundamentals', 'news'],
                'delay': 'Real-time',
                'rate_limit': '60 calls per minute (free tier)',
                'api_key_required': True,
                'api_key_url': 'https://finnhub.io/register'
            },
            'csv': {
                'name': 'CSV Files',
                'description': 'Local CSV files and sample data',
                'supported_tickers': 'Any ticker (creates sample data)',
                'data_types': ['OHLCV'],
                'delay': 'Instant',
                'rate_limit': 'No limits',
                'api_key_required': False,
                'note': 'Uses existing CSV files or creates sample data'
            }
        }
        
        return jsonify({'sources': sources})
        
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        return jsonify({'error': str(e)}), 500

@download_bp.route('/download', methods=['POST'])
def download_data():
    """Download data from specified source."""
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        source = data.get('source', 'yahoo')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        interval = data.get('interval', '1d')
        
        if not ticker:
            return jsonify({'error': 'Ticker symbol is required'}), 400
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        result = None
        downloader = None
        
        if source == 'yahoo':
            from redline.downloaders.yahoo_downloader import YahooDownloader
            downloader = YahooDownloader()
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        elif source == 'stooq':
            from redline.downloaders.stooq_downloader import StooqDownloader
            downloader = StooqDownloader()
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        elif source == 'alpha_vantage':
            from redline.downloaders.alpha_vantage_downloader import AlphaVantageDownloader
            downloader = AlphaVantageDownloader()
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        elif source == 'finnhub':
            from redline.downloaders.finnhub_downloader import FinnhubDownloader
            downloader = FinnhubDownloader()
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        elif source == 'csv':
            from redline.downloaders.csv_downloader import CSVDownloader
            downloader = CSVDownloader()
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        else:
            return jsonify({'error': f'Unsupported source: {source}'}), 400
        
        if result is not None and not result.empty:
            # Save the downloaded data
            import os
            filename = f"{ticker}_{source}_{start_date}_to_{end_date}.csv"
            downloaded_dir = "data/downloaded"
            
            # Ensure downloaded directory exists
            os.makedirs(downloaded_dir, exist_ok=True)
            
            filepath = os.path.join(downloaded_dir, filename)
            
            result.to_csv(filepath, index=True)
            
            return jsonify({
                'message': f'Successfully downloaded {len(result)} records for {ticker}',
                'ticker': ticker,
                'source': source,
                'records': len(result),
                'filename': filename,
                'filepath': filepath,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'columns': list(result.columns)
            })
        else:
            # Check if it's a rate limiting issue
            error_msg = f'No data found for {ticker}'
            if source == 'yahoo':
                error_msg += '. This might be due to rate limiting. Please try again in a few minutes.'
            return jsonify({'error': error_msg}), 429  # Use 429 for rate limiting
            
    except Exception as e:
        logger.error(f"Error downloading data for {ticker}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@download_bp.route('/batch-download', methods=['POST'])
def batch_download():
    """Download data for multiple tickers."""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        source = data.get('source', 'yahoo')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not tickers:
            return jsonify({'error': 'No tickers provided'}), 400
        
        results = []
        errors = []
        
        # Create a single downloader instance to share rate limiting
        downloader = None
        test_mode = data.get('test_mode', False)  # Allow test mode for demo purposes
        
        if test_mode:
            logger.info("Running in test mode - will create sample data")
        elif source == 'yahoo':
            from redline.downloaders.yahoo_downloader import YahooDownloader
            downloader = YahooDownloader()
        elif source == 'stooq':
            from redline.downloaders.stooq_downloader import StooqDownloader
            downloader = StooqDownloader()
        elif source == 'alpha_vantage':
            from redline.downloaders.alpha_vantage_downloader import AlphaVantageDownloader
            downloader = AlphaVantageDownloader()
        elif source == 'finnhub':
            from redline.downloaders.finnhub_downloader import FinnhubDownloader
            downloader = FinnhubDownloader()
        elif source == 'csv':
            from redline.downloaders.csv_downloader import CSVDownloader
            downloader = CSVDownloader()
        
        for i, ticker in enumerate(tickers):
            try:
                # Add longer delay between downloads to respect rate limits
                if i > 0 and downloader:
                    import time
                    delay = 10  # 10 second delay between downloads to avoid rate limiting
                    logger.info(f"Waiting {delay} seconds before downloading {ticker}...")
                    time.sleep(delay)
                
                if test_mode:
                    # Create sample data for testing
                    import pandas as pd
                    import numpy as np
                    from datetime import datetime, timedelta
                    
                    # Create sample data
                    dates = pd.date_range(start=start_date, end=end_date, freq='D')
                    np.random.seed(hash(ticker) % 2**32)  # Consistent random data per ticker
                    
                    result = pd.DataFrame({
                        'Open': 100 + np.random.randn(len(dates)).cumsum(),
                        'High': 105 + np.random.randn(len(dates)).cumsum(),
                        'Low': 95 + np.random.randn(len(dates)).cumsum(),
                        'Close': 100 + np.random.randn(len(dates)).cumsum(),
                        'Volume': np.random.randint(1000000, 10000000, len(dates))
                    }, index=dates)
                    
                    logger.info(f"Created sample data for {ticker} in test mode")
                    
                elif downloader:
                    result = downloader.download_single_ticker(
                        ticker=ticker,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    # If download failed due to rate limiting, try to use existing data
                    if result is None or result.empty:
                        logger.info(f"Download failed for {ticker}, checking for existing data...")
                        existing_file = f"data/{ticker}_yahoo_data.csv"
                        if os.path.exists(existing_file):
                            logger.info(f"Using existing data file for {ticker}")
                            import pandas as pd
                            result = pd.read_csv(existing_file, index_col=0, parse_dates=True)
                else:
                    result = None
                
                if result is not None and not result.empty:
                    filename = f"{ticker}_{source}_{start_date}_to_{end_date}.csv"
                    downloaded_dir = "data/downloaded"
                    
                    # Ensure downloaded directory exists
                    os.makedirs(downloaded_dir, exist_ok=True)
                    
                    filepath = os.path.join(downloaded_dir, filename)
                    result.to_csv(filepath, index=True)
                    
                    results.append({
                        'ticker': ticker,
                        'success': True,
                        'records': len(result),
                        'filename': filename
                    })
                else:
                    error_msg = 'No data found'
                    if source == 'yahoo':
                        error_msg += ' (possibly due to rate limiting)'
                    errors.append({
                        'ticker': ticker,
                        'error': error_msg
                    })
                    
            except Exception as e:
                error_msg = str(e)
                if "Too Many Requests" in error_msg or "rate limit" in error_msg.lower():
                    error_msg = f"Rate limited for {ticker}. Please wait before trying again."
                errors.append({
                    'ticker': ticker,
                    'error': error_msg
                })
        
        # Check if all failures are due to rate limiting
        rate_limit_count = sum(1 for error in errors if 'rate limit' in error['error'].lower())
        
        message = f'Batch download completed. {len(results)} successful, {len(errors)} failed.'
        if rate_limit_count > 0:
            message += f' {rate_limit_count} failures due to rate limiting. Please wait a few minutes before retrying.'
        
        return jsonify({
            'message': message,
            'results': results,
            'errors': errors,
            'total_requested': len(tickers),
            'successful': len(results),
            'failed': len(errors),
            'rate_limit_failures': rate_limit_count
        })
        
    except Exception as e:
        logger.error(f"Error in batch download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@download_bp.route('/history')
def get_download_history():
    """Get download history."""
    try:
        import os
        import glob
        
        download_dir = os.path.join(os.getcwd(), 'data', 'downloaded')
        
        if not os.path.exists(download_dir):
            return jsonify({'downloads': []})
        
        files = glob.glob(os.path.join(download_dir, '*.csv'))
        downloads = []
        
        for filepath in files:
            filename = os.path.basename(filepath)
            stat = os.stat(filepath)
            
            downloads.append({
                'filename': filename,
                'filepath': filepath,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime
            })
        
        # Sort by modification time (newest first)
        downloads.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'downloads': downloads})
        
    except Exception as e:
        logger.error(f"Error getting download history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@download_bp.route('/validate-ticker', methods=['POST'])
def validate_ticker():
    """Validate if a ticker symbol exists."""
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        source = data.get('source', 'yahoo')
        
        if not ticker:
            return jsonify({'error': 'Ticker symbol is required'}), 400
        
        # Try to download a small amount of data to validate
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        if source == 'yahoo':
            from redline.downloaders.yahoo_downloader import YahooDownloader
            downloader = YahooDownloader()
            result = downloader.download_data(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        else:
            result = None
        
        if result is not None and not result.empty:
            return jsonify({
                'valid': True,
                'ticker': ticker,
                'source': siurce,
                'sample_data': {
                    'columns': list(result.columns),
                    'records': len(result),
                    'date_range': {
                        'start': str(result.index.min()),
                        'end': str(result.index.max())
                    }
                }
            })
        else:
            return jsonify({
                'valid': False,
                'ticker': ticker,
                'source': source,
                'error': 'No data found for this ticker'
            })
            
    except Exception as e:
        logger.error(f"Error validating ticker {ticker}: {str(e)}")
        return jsonify({
            'valid': False,
            'ticker': ticker,
            'error': str(e)
        })
