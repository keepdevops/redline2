"""
Helper functions for download routes.
"""

import os
import logging
from datetime import datetime, timedelta
from flask import request

logger = logging.getLogger(__name__)

# Import S3 manager for cloud storage
try:
    from redline.storage.s3_manager import s3_manager
    S3_AVAILABLE = s3_manager.is_available()
except ImportError:
    s3_manager = None
    S3_AVAILABLE = False


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


def save_downloaded_data(result, ticker, source, start_date, end_date, user_id=None):
    """
    Save downloaded data to file and optionally upload to S3.

    Args:
        result: DataFrame with downloaded data
        ticker: Ticker symbol
        source: Data source name
        start_date: Start date string
        end_date: End date string
        user_id: Optional user ID for S3 storage (uses user-specific path)

    Returns:
        tuple: (filename, filepath, s3_uri) - s3_uri is None if S3 upload failed or not available
    """
    filename = f"{ticker}_{source}_{start_date}_to_{end_date}.csv"
    downloaded_dir = get_download_directory(source)

    # Ensure downloaded directory exists
    os.makedirs(downloaded_dir, exist_ok=True)

    filepath = os.path.join(downloaded_dir, filename)
    result.to_csv(filepath, index=True)

    # Upload to S3 if available
    s3_uri = None
    if S3_AVAILABLE and s3_manager:
        try:
            # Determine S3 path based on user_id
            if user_id:
                # User-specific path: users/{user_id}/downloads/{filename}
                s3_key = s3_manager.get_file_path(user_id, filename, folder='downloads')
            else:
                # Guest/public path: public/downloads/{filename}
                s3_key = f"public/downloads/{filename}"

            # Upload to S3
            s3_uri = s3_manager.upload_file(filepath, s3_key)

            if s3_uri:
                logger.info(f"Uploaded {filename} to S3: {s3_uri}")
            else:
                logger.warning(f"S3 upload failed for {filename}")

        except Exception as e:
            logger.error(f"Error uploading {filename} to S3: {str(e)}")
            s3_uri = None

    return filename, filepath, s3_uri

