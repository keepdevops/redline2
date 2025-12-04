"""
Batch download route.
Handles downloading data for multiple tickers.
"""

import os
import time
from flask import Blueprint, request, jsonify
import logging

from redline.web.utils.download_helpers import (
    extract_license_key,
    validate_license_key,
    get_download_directory,
    save_downloaded_data
)
from redline.downloaders.exceptions import RateLimitError

download_batch_bp = Blueprint('download_batch', __name__)
logger = logging.getLogger(__name__)

@download_batch_bp.route('/batch-download', methods=['POST'])
def batch_download():
    """Download data for multiple tickers."""
    try:
        # Extract and validate license key
        license_key = extract_license_key()
        error_response = validate_license_key(license_key)
        if error_response:
            return error_response
        
        data = request.get_json() or {}
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
        # Use environment variable for test mode instead of request parameter
        test_mode = os.environ.get('REDLINE_TEST_MODE', 'false').lower() == 'true'
        
        if test_mode:
            logger.info("Running in test mode - will create sample data")
        elif source == 'yahoo':
            from redline.downloaders.yahoo_downloader import YahooDownloader
            downloader = YahooDownloader()
        elif source == 'stooq':
            from redline.downloaders.stooq_downloader import StooqDownloader
            # Use REDLINE data directory for Stooq downloads
            data_dir = os.path.join(os.getcwd(), 'data', 'stooq')
            os.makedirs(data_dir, exist_ok=True)
            downloader = StooqDownloader(output_dir=data_dir)
        elif source == 'alpha_vantage':
            from redline.downloaders.alpha_vantage_downloader import AlphaVantageDownloader
            # Get API key from request or environment
            api_key = data.get('api_key') or os.environ.get('ALPHA_VANTAGE_API_KEY')
            if not api_key:
                errors.append({'ticker': 'ALL', 'error': 'Alpha Vantage API key is required. Please select an API key or set ALPHA_VANTAGE_API_KEY environment variable.'})
                return jsonify({
                    'success': False,
                    'results': [],
                    'errors': errors,
                    'success_count': 0,
                    'error_count': len(errors)
                }), 400
            downloader = AlphaVantageDownloader(api_key=api_key)
        elif source == 'finnhub':
            from redline.downloaders.finnhub_downloader import FinnhubDownloader
            # Get API key from request or environment
            api_key = data.get('api_key') or os.environ.get('FINNHUB_API_KEY')
            if not api_key:
                errors.append({'ticker': 'ALL', 'error': 'Finnhub API key is required. Please select an API key or set FINNHUB_API_KEY environment variable.'})
                return jsonify({
                    'success': False,
                    'results': [],
                    'errors': errors,
                    'success_count': 0,
                    'error_count': len(errors)
                }), 400
            downloader = FinnhubDownloader(api_key=api_key)
        elif source == 'massive':
            from redline.downloaders.massive_downloader import MassiveDownloader
            # Get API key from request or environment
            api_key = data.get('api_key') or os.environ.get('MASSIVE_API_KEY')
            if not api_key:
                errors.append({'ticker': 'ALL', 'error': 'Massive.com API key is required. Please select an API key or set MASSIVE_API_KEY environment variable.'})
                return jsonify({
                    'success': False,
                    'results': [],
                    'errors': errors,
                    'success_count': 0,
                    'error_count': len(errors)
                }), 400
            try:
                downloader = MassiveDownloader(api_key=api_key)
            except Exception as e:
                logger.error(f"Error initializing Massive.com downloader: {str(e)}")
                errors.append({'ticker': 'ALL', 'error': f'Massive.com initialization error: {str(e)}'})
                return jsonify({
                    'success': False,
                    'results': [],
                    'errors': errors,
                    'success_count': 0,
                    'error_count': len(errors)
                }), 400
        elif source.startswith('custom_'):
            # Custom API - load configuration
            from redline.downloaders.generic_api_downloader import GenericAPIDownloader
            import json
            
            custom_api_id = source.replace('custom_', '')
            from ...utils.config_paths import get_custom_apis_file
            custom_apis_file = str(get_custom_apis_file())
            
            if not os.path.exists(custom_apis_file):
                errors.append({'ticker': 'ALL', 'error': 'No custom APIs configured. Please configure a custom API first.'})
                return jsonify({
                    'success': False,
                    'results': [],
                    'errors': errors,
                    'success_count': 0,
                    'error_count': len(errors)
                }), 400
            
            with open(custom_apis_file, 'r') as f:
                custom_apis = json.load(f)
            
            if custom_api_id not in custom_apis:
                errors.append({'ticker': 'ALL', 'error': f'Custom API "{custom_api_id}" not found. Please check your configuration.'})
                return jsonify({
                    'success': False,
                    'results': [],
                    'errors': errors,
                    'success_count': 0,
                    'error_count': len(errors)
                }), 404
            
            api_config = custom_apis[custom_api_id].copy()
            if data.get('api_key'):
                api_config['api_key'] = data.get('api_key')
            
            try:
                downloader = GenericAPIDownloader(api_config)
            except Exception as e:
                logger.error(f"Error initializing custom API downloader: {str(e)}")
                errors.append({'ticker': 'ALL', 'error': f'Custom API configuration error: {str(e)}'})
                return jsonify({
                    'success': False,
                    'results': [],
                    'errors': errors,
                    'success_count': 0,
                    'error_count': len(errors)
                }), 400
        elif source == 'csv':
            from redline.downloaders.csv_downloader import CSVDownloader
            downloader = CSVDownloader()
        
        for i, ticker in enumerate(tickers):
            try:
                # Add longer delay between downloads to respect rate limits
                if i > 0 and downloader:
                    delay = 30  # 30 second delay between downloads to avoid rate limiting (increased from 10s)
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

                    # If download failed and source is Yahoo, try Stooq as fallback
                    if (result is None or result.empty) and source == 'yahoo':
                        logger.warning(f"Yahoo Finance failed for {ticker}, attempting Stooq fallback...")
                        try:
                            from redline.downloaders.stooq_downloader import StooqDownloader
                            stooq_data_dir = os.path.join(os.getcwd(), 'data', 'stooq')
                            os.makedirs(stooq_data_dir, exist_ok=True)
                            stooq_downloader = StooqDownloader(output_dir=stooq_data_dir)

                            result = stooq_downloader.download_single_ticker(
                                ticker=ticker,
                                start_date=start_date,
                                end_date=end_date
                            )

                            if result is not None and not result.empty:
                                logger.info(f"Successfully downloaded {ticker} from Stooq as fallback")
                                source = 'stooq'  # Update source for filename
                            else:
                                logger.info(f"Stooq fallback also failed for {ticker}, checking existing data...")
                        except Exception as stooq_error:
                            logger.error(f"Stooq fallback error for {ticker}: {str(stooq_error)}")

                    # If still no data, try to use existing data file
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
                    filename, filepath = save_downloaded_data(result, ticker, source, start_date, end_date)
                    
                    results.append({
                        'ticker': ticker,
                        'success': True,
                        'records': len(result),
                        'filename': filename
                    })
                else:
                    # No data found - not a rate limit issue
                    error_msg = 'No data found'
                    errors.append({
                        'ticker': ticker,
                        'error': error_msg
                    })
                    
            except RateLimitError as e:
                # Rate limit error from downloader
                logger.warning(f"Rate limited for {ticker} from {source}: {e.message}")
                retry_after = e.retry_after or 300
                error_msg = f"Rate limit exceeded. {e.message}"
                if retry_after:
                    minutes = retry_after // 60
                    if minutes > 0:
                        error_msg += f" Please wait {minutes} minute(s) before trying again."
                
                errors.append({
                    'ticker': ticker,
                    'error': error_msg,
                    'rate_limited': True,
                    'retry_after': retry_after
                })
                
                # If this is the first rate limit error in batch, we might want to stop
                # For now, continue with other tickers but log the issue
                if len([err for err in errors if err.get('rate_limited')]) == 1:
                    logger.warning(f"Rate limit encountered during batch download. Continuing with remaining tickers...")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error downloading {ticker}: {error_msg}")
                
                # Check if exception indicates rate limiting (fallback)
                if "Too Many Requests" in error_msg or "rate limit" in error_msg.lower():
                    error_msg = f"Rate limited for {ticker}. Please wait before trying again."
                    errors.append({
                        'ticker': ticker,
                        'error': error_msg,
                        'rate_limited': True
                    })
                else:
                    errors.append({
                        'ticker': ticker,
                        'error': error_msg
                    })
        
        # Check if failures are due to rate limiting
        rate_limit_count = sum(1 for error in errors if error.get('rate_limited') or 'rate limit' in error.get('error', '').lower())
        rate_limit_errors = [err for err in errors if err.get('rate_limited')]
        
        # Get retry_after from first rate limit error if available
        retry_after = None
        if rate_limit_errors:
            retry_after = rate_limit_errors[0].get('retry_after', 300)
        
        message = f'Batch download completed. {len(results)} successful, {len(errors)} failed.'
        if rate_limit_count > 0:
            if retry_after:
                minutes = retry_after // 60
                message += f' {rate_limit_count} failure(s) due to rate limiting. Please wait {minutes} minute(s) before retrying.'
            else:
                message += f' {rate_limit_count} failure(s) due to rate limiting. Please wait a few minutes before retrying.'
        
        response_data = {
            'message': message,
            'results': results,
            'errors': errors,
            'total_requested': len(tickers),
            'successful': len(results),
            'failed': len(errors),
            'rate_limit_failures': rate_limit_count
        }
        
        # Add retry_after if there are rate limit errors
        if retry_after:
            response_data['retry_after'] = retry_after
        
        # Return 429 if all failures are due to rate limiting, otherwise 200 with error details
        status_code = 429 if rate_limit_count > 0 and len(results) == 0 else 200
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Error in batch download: {str(e)}")
        return jsonify({'error': str(e)}), 500

