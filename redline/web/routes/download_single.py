"""
Single ticker download route.
Handles downloading data for a single ticker from various sources.
"""

import os
from flask import Blueprint, request, jsonify, g
import logging
from datetime import datetime, timedelta

from redline.web.utils.download_helpers import (
    get_default_date_range,
    save_downloaded_data
)
from redline.downloaders.exceptions import RateLimitError

download_single_bp = Blueprint('download_single', __name__)
logger = logging.getLogger(__name__)

@download_single_bp.route('/download', methods=['POST'])
def download_data():
    """Download data from specified source."""
    # Get authenticated user (optional - allow guest downloads)
    user_id = getattr(g, 'user_id', None)
    
    # Log whether user is authenticated or using guest access
    if user_id:
        logger.info(f"Download request from authenticated user: {user_id}")
    else:
        logger.info("Download request from guest user (no authentication)")

    # Get and validate request data
    user_label = user_id or "guest"
    data = request.get_json()

    if not data:
        logger.warning(f"Download request from {user_label} with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Download request from {user_id} with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate ticker
    ticker = data.get('ticker')

    if not ticker:
        logger.warning(f"Download request from {user_label} missing ticker field")
        return jsonify({'error': 'Ticker symbol is required'}), 400

    if not isinstance(ticker, str):
        logger.error(f"Download request from {user_label} has invalid ticker type: {type(ticker)}")
        return jsonify({'error': 'Ticker must be a string'}), 400

    ticker = ticker.strip().upper()

    if len(ticker) == 0:
        logger.warning(f"Download request from {user_label} with empty ticker")
        return jsonify({'error': 'Ticker symbol cannot be empty'}), 400

    if len(ticker) > 20:
        logger.warning(f"Download request from {user_label} with unusually long ticker: {ticker}")
        return jsonify({'error': 'Ticker symbol too long (max 20 characters)'}), 400

    # Validate source
    source = data.get('source', 'yahoo')

    if not isinstance(source, str):
        logger.error(f"Download request from {user_label} has invalid source type: {type(source)}")
        return jsonify({'error': 'Source must be a string'}), 400

    valid_sources = ['yahoo', 'stooq', 'alpha_vantage', 'finnhub', 'massive']
    if source not in valid_sources:
        logger.warning(f"Download request from {user_label} has invalid source: {source}")
        return jsonify({'error': f'Invalid source. Must be one of: {", ".join(valid_sources)}'}), 400

    # Get date parameters
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    interval = data.get('interval', '1d')

    # Set default date range if not provided
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
        logger.debug(f"Using default end_date: {end_date}")

    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        logger.debug(f"Using default start_date: {start_date}")

    # Validate dates format
    for date_str, date_name in [(start_date, 'start_date'), (end_date, 'end_date')]:
        if not isinstance(date_str, str):
            logger.error(f"Download request from {user_label} has invalid {date_name} type: {type(date_str)}")
            return jsonify({'error': f'{date_name} must be a string'}), 400

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            logger.warning(f"Download request from {user_label} has invalid {date_name} format: {date_str}")
            return jsonify({'error': f'Invalid {date_name} format. Use YYYY-MM-DD'}), 400

    logger.info(f"Processing download request from {user_label}: ticker={ticker}, source={source}, dates={start_date} to {end_date}")

    try:
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
            # Use VarioSync data directory for Stooq downloads
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
                except FileNotFoundError:
                    logger.debug(f"API keys file not found: {api_keys_file}")
                except PermissionError as e:
                    logger.warning(f"Permission denied reading API keys file: {e}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON in API keys file: {e}")
                except KeyError as e:
                    logger.debug(f"Missing key in API keys file: {e}")
                except Exception as e:
                    logger.debug(f"Unexpected error loading saved API keys: {e}")
            
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
            except ImportError as e:
                logger.error(f"Import error initializing Massive.com downloader: {str(e)}")
                return jsonify({'error': f'Massive.com import error: {str(e)}', 'code': 'IMPORT_ERROR'}), 500
            except ValueError as e:
                logger.error(f"Invalid parameter for Massive.com downloader: {str(e)}")
                return jsonify({'error': f'Massive.com configuration error: {str(e)}', 'code': 'VALUE_ERROR'}), 400
            except Exception as e:
                logger.error(f"Unexpected error with Massive.com downloader: {str(e)}")
                return jsonify({'error': f'Massive.com error: {str(e)}', 'code': 'MASSIVE_ERROR'}), 400
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
            except ImportError as e:
                logger.error(f"Import error initializing custom API downloader: {str(e)}")
                return jsonify({'error': f'Custom API import error: {str(e)}', 'code': 'IMPORT_ERROR'}), 500
            except KeyError as e:
                logger.error(f"Missing configuration key for custom API: {str(e)}")
                return jsonify({'error': f'Custom API configuration missing key: {str(e)}', 'code': 'KEY_ERROR'}), 400
            except ValueError as e:
                logger.error(f"Invalid configuration for custom API: {str(e)}")
                return jsonify({'error': f'Custom API configuration error: {str(e)}', 'code': 'VALUE_ERROR'}), 400
            except Exception as e:
                logger.error(f"Unexpected error with custom API downloader: {str(e)}")
                return jsonify({'error': f'Custom API error: {str(e)}', 'code': 'CUSTOM_API_ERROR'}), 400
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
            'source': e.source or source,
            'code': 'RATE_LIMIT_ERROR'
        }), 429

    except ImportError as e:
        logger.error(f"Import error downloading {ticker}: {str(e)}")
        return jsonify({
            'error': f'Module import error: {str(e)}',
            'ticker': ticker,
            'source': source,
            'code': 'IMPORT_ERROR'
        }), 500

    except PermissionError as e:
        logger.error(f"Permission denied downloading {ticker}: {str(e)}")
        return jsonify({
            'error': 'Permission denied',
            'ticker': ticker,
            'source': source,
            'code': 'PERMISSION_DENIED'
        }), 403

    except OSError as e:
        logger.error(f"OS error downloading {ticker}: {str(e)}")
        return jsonify({
            'error': f'File system error: {str(e)}',
            'ticker': ticker,
            'source': source,
            'code': 'OS_ERROR'
        }), 500

    except KeyError as e:
        logger.error(f"Missing key downloading {ticker}: {str(e)}")
        return jsonify({
            'error': f'Configuration error: missing key {str(e)}',
            'ticker': ticker,
            'source': source,
            'code': 'KEY_ERROR'
        }), 500

    except ValueError as e:
        logger.error(f"Value error downloading {ticker}: {str(e)}")
        return jsonify({
            'error': f'Invalid parameter: {str(e)}',
            'ticker': ticker,
            'source': source,
            'code': 'VALUE_ERROR'
        }), 400

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error downloading data for {ticker}: {error_msg}")
        
        # Check if exception indicates rate limiting (fallback for other error types)
        error_lower = error_msg.lower()
        if 'rate limit' in error_lower or 'too many requests' in error_lower or '429' in error_lower:
            return jsonify({
                'error': f'Rate limit exceeded for {source}. Please wait a few minutes before trying again. You can also try a different data source.',
                'retry_after': 300,  # Suggest 5 minutes
                'ticker': ticker,
                'source': source,
                'code': 'RATE_LIMIT_DETECTED'
            }), 429

        # Check for Stooq bandwidth limit errors
        if source.lower() == 'stooq' and ('bandwidth' in error_lower and 'limit' in error_lower):
            return jsonify({
                'error': 'Stooq daily bandwidth limit exceeded. Please try again tomorrow or use manual download. Files downloaded to your Downloads folder will automatically appear in Data View.',
                'ticker': ticker,
                'source': 'stooq',
                'suggestion': 'Use manual download from Stooq website - files will auto-copy from Downloads folder',
                'code': 'STOOQ_BANDWIDTH_LIMIT'
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
                'suggestion': 'Try using Stooq as an alternative data source, or wait a few moments and try again.',
                'code': 'YAHOO_CONNECTION_ERROR'
            }), 503  # Service Unavailable - temporary issue

        return jsonify({
            'error': error_msg,
            'ticker': ticker,
            'source': source,
            'code': 'INTERNAL_ERROR'
        }), 500

