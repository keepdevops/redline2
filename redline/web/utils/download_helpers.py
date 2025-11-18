"""
Helper functions for download routes.
"""

import os
from datetime import datetime, timedelta
from flask import request


def extract_license_key():
    """Extract license key from headers, query params, or JSON body."""
    license_key = (
        request.headers.get('X-License-Key') or
        request.args.get('license_key') or
        None
    )
    
    # Also check in JSON body if available
    data = request.get_json() or {}
    if not license_key and data:
        license_key = data.get('license_key')
    
    return license_key


def validate_license_key(license_key):
    """Validate license key and return error response if missing."""
    if not license_key:
        from flask import jsonify
        return jsonify({
            'error': 'License key is required',
            'message': 'Please provide a license key in X-License-Key header, license_key query parameter, or JSON body'
        }), 401
    return None


def get_default_date_range():
    """Get default date range (last year to today)."""
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    return start_date, end_date


def get_download_directory(source):
    """Get the appropriate download directory for a source."""
    if source == 'stooq':
        from redline.utils.stooq_file_handler import get_stooq_data_dir
        return get_stooq_data_dir()
    else:
        return "data/downloaded"


def save_downloaded_data(result, ticker, source, start_date, end_date):
    """Save downloaded data to file and return filepath."""
    filename = f"{ticker}_{source}_{start_date}_to_{end_date}.csv"
    downloaded_dir = get_download_directory(source)
    
    # Ensure downloaded directory exists
    os.makedirs(downloaded_dir, exist_ok=True)
    
    filepath = os.path.join(downloaded_dir, filename)
    result.to_csv(filepath, index=True)
    
    return filename, filepath

