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
        elif source.startswith('custom_'):
            # Custom API - load configuration
            from redline.downloaders.generic_api_downloader import GenericAPIDownloader
            import json
            
            # Get custom API ID (remove 'custom_' prefix)
            custom_api_id = source.replace('custom_', '')
            
            # Load custom API configurations
            custom_apis_file = 'data/custom_apis.json'
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
            # Check if it's a rate limiting issue
            error_msg = f'No data found for {ticker}'
            if source == 'yahoo':
                error_msg += '. This might be due to rate limiting. Please try again in a few minutes.'
            return jsonify({'error': error_msg}), 429  # Use 429 for rate limiting
            
    except Exception as e:
        logger.error(f"Error downloading data for {ticker}: {str(e)}")
        return jsonify({'error': str(e)}), 500

