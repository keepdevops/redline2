"""
Single ticker download route.
Handles downloading data for a single ticker from various sources.
"""

import os
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta

from redline.web.utils.download_helpers import (
    extract_license_key,
    validate_license_key,
    get_default_date_range,
    save_downloaded_data
)
from redline.downloaders.exceptions import RateLimitError

download_single_bp = Blueprint('download_single', __name__)
logger = logging.getLogger(__name__)

@download_single_bp.route('/download', methods=['POST'])
def download_data():
    """Download data from specified source."""
    try:
        # Extract and validate license key
        license_key = extract_license_key()
        error_response = validate_license_key(license_key)
        if error_response:
            return error_response
        
        data = request.get_json() or {}
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
            # Use REDLINE data directory for Stooq downloads
            data_dir = os.path.join(os.getcwd(), 'data', 'stooq')
            os.makedirs(data_dir, exist_ok=True)
            downloader = StooqDownloader(output_dir=data_dir)
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        elif source == 'alpha_vantage':
            from redline.downloaders.alpha_vantage_downloader import AlphaVantageDownloader
            # Get API key from request or environment
            api_key = data.get('api_key') or os.environ.get('ALPHA_VANTAGE_API_KEY')
            if not api_key:
                return jsonify({'error': 'Alpha Vantage API key is required. Please select an API key or set ALPHA_VANTAGE_API_KEY environment variable.'}), 400
            downloader = AlphaVantageDownloader(api_key=api_key)
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        elif source == 'finnhub':
            from redline.downloaders.finnhub_downloader import FinnhubDownloader
            # Get API key from request or environment
            api_key = data.get('api_key') or os.environ.get('FINNHUB_API_KEY')
            if not api_key:
                return jsonify({'error': 'Finnhub API key is required. Please select an API key or set FINNHUB_API_KEY environment variable.'}), 400
            downloader = FinnhubDownloader(api_key=api_key)
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        elif source == 'massive':
            from redline.downloaders.massive_downloader import MassiveDownloader
            # Get API key from request, saved config, or environment
            api_key = data.get('api_key')
            if not api_key:
                # Try to load from saved API keys
                try:
                    from ...utils.config_paths import get_api_keys_file
                    api_keys_file = str(get_api_keys_file())
                    if os.path.exists(api_keys_file):
                        import json
                        with open(api_keys_file, 'r') as f:
                            saved_keys = json.load(f)
                            api_key = saved_keys.get('massive')
                except Exception as e:
                    logger.debug(f"Could not load saved API keys: {e}")
            
            # Fallback to environment variable
            if not api_key:
                api_key = os.environ.get('MASSIVE_API_KEY')
            
            if not api_key:
                return jsonify({'error': 'Massive.com API key is required. Please configure it in Settings > API Keys or set MASSIVE_API_KEY environment variable.'}), 400
            try:
                downloader = MassiveDownloader(api_key=api_key)
                result = downloader.download_single_ticker(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date
                )
            except Exception as e:
                logger.error(f"Error initializing Massive.com downloader: {str(e)}")
                return jsonify({'error': f'Massive.com initialization error: {str(e)}'}), 400
        elif source.startswith('custom_'):
            # Custom API - load configuration
            from redline.downloaders.generic_api_downloader import GenericAPIDownloader
            import json
            
            # Get custom API ID (remove 'custom_' prefix)
            custom_api_id = source.replace('custom_', '')
            
            # Load custom API configurations
            from ...utils.config_paths import get_custom_apis_file
            custom_apis_file = str(get_custom_apis_file())
            if not os.path.exists(custom_apis_file):
                return jsonify({'error': 'No custom APIs configured. Please configure a custom API first.'}), 400
            
            with open(custom_apis_file, 'r') as f:
                custom_apis = json.load(f)
            
            if custom_api_id not in custom_apis:
                return jsonify({'error': f'Custom API "{custom_api_id}" not found. Please check your configuration.'}), 404
            
            api_config = custom_apis[custom_api_id]
            
            # Override API key if provided in request
            if data.get('api_key'):
                api_config['api_key'] = data.get('api_key')
            
            try:
                downloader = GenericAPIDownloader(api_config)
                result = downloader.download_single_ticker(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date
                )
            except Exception as e:
                logger.error(f"Error initializing custom API downloader: {str(e)}")
                return jsonify({'error': f'Custom API configuration error: {str(e)}'}), 400
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
            filename, filepath = save_downloaded_data(result, ticker, source, start_date, end_date)
            
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
            # No data found - return 404 with helpful message
            error_msg = f'No data found for {ticker}'
            # Provide more context based on source
            if source == 'yahoo':
                error_msg += '. Please verify the ticker symbol is correct. Yahoo Finance may not have data for this ticker, or it may be delisted.'
            elif source == 'stooq':
                error_msg += '. Please verify the ticker symbol is correct. Stooq may not have data for this ticker.'
            else:
                error_msg += '. Please verify the ticker symbol is correct and try a different data source if available.'
            
            return jsonify({
                'error': error_msg,
                'ticker': ticker,
                'source': source,
                'suggestion': 'Try checking the ticker symbol or using a different data source.'
            }), 404
            
    except RateLimitError as e:
        # Rate limit error from downloader - return proper 429 response
        logger.warning(f"Rate limit exceeded for {ticker} from {source}: {e.message}")
        retry_after = e.retry_after or 300  # Default to 5 minutes if not specified
        
        return jsonify({
            'error': f'Rate limit exceeded for {source}. {e.message}',
            'retry_after': retry_after,
            'source': e.source or source
        }), 429
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error downloading data for {ticker}: {error_msg}")
        
        # Check if exception indicates rate limiting (fallback for other error types)
        error_lower = error_msg.lower()
        if 'rate limit' in error_lower or 'too many requests' in error_lower or '429' in error_lower:
            return jsonify({
                'error': f'Rate limit exceeded for {source}. Please wait a few minutes before trying again. You can also try a different data source.',
                'retry_after': 300  # Suggest 5 minutes
            }), 429
        
        # Check for Stooq bandwidth limit errors
        if source.lower() == 'stooq' and ('bandwidth' in error_lower and 'limit' in error_lower):
            return jsonify({
                'error': 'Stooq daily bandwidth limit exceeded. Please try again tomorrow or use manual download. Files downloaded to your Downloads folder will automatically appear in Data View.',
                'source': 'stooq',
                'suggestion': 'Use manual download from Stooq website - files will auto-copy from Downloads folder'
            }), 429
        
        # Check if it's a yfinance/curl library error
        if ('yfinance' in error_lower or 'impersonating' in error_lower or 
            'curl' in error_lower or 'setopt' in error_lower or 'curl_cffi' in error_lower):
            # Provide helpful message about Yahoo Finance issues
            if 'temporary issue' in error_msg.lower() or 'try again' in error_msg.lower():
                # Error message already has helpful guidance
                helpful_msg = error_msg
            else:
                helpful_msg = f'Yahoo Finance connection error: {error_msg}. This may be a temporary issue with Yahoo Finance. Please try again in a few moments or use a different data source (e.g., Stooq).'
            
            return jsonify({
                'error': helpful_msg,
                'ticker': ticker,
                'source': source,
                'suggestion': 'Try using Stooq as an alternative data source, or wait a few moments and try again.'
            }), 503  # Service Unavailable - temporary issue
        
        return jsonify({
            'error': error_msg,
            'ticker': ticker,
            'source': source
        }), 500

