"""
Helper functions for download routes.
"""

import os
import logging
from datetime import datetime, timedelta
from flask import request, jsonify
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Initialize auth manager
try:
    from redline.auth.supabase_auth import supabase_auth_manager
    AUTH_AVAILABLE = True
except ImportError:
    logger.warning("Supabase auth not available")
    AUTH_AVAILABLE = False
    supabase_auth_manager = None


def extract_jwt_token() -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Returns:
        JWT token string or None if not found
    """
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.replace('Bearer ', '').strip()
    return None


def verify_jwt_auth() -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[Dict, int]]]:
    """
    Verify JWT authentication and return user info or error response.
    
    Returns:
        Tuple of (user_payload, error_response)
        - user_payload: Decoded JWT payload with user info, or None if invalid
        - error_response: Flask response tuple (jsonify(...), status_code) if auth failed, or None if successful
    """
    if not AUTH_AVAILABLE or not supabase_auth_manager:
        logger.error("JWT authentication not available")
        return None, (jsonify({
            'error': 'Authentication not configured',
            'message': 'JWT authentication is not available'
        }), 503)
    
    token = extract_jwt_token()
    if not token:
        return None, (jsonify({
            'error': 'Authentication required',
            'message': 'Please provide a JWT token in Authorization header (Bearer token)'
        }), 401)
    
    user = supabase_auth_manager.verify_jwt_token(token)
    if not user:
        return None, (jsonify({
            'error': 'Invalid authentication',
            'message': 'JWT token is invalid or expired'
        }), 401)
    
    return user, None


def get_user_id_from_request() -> Optional[str]:
    """
    Extract user ID from JWT token in request.
    
    Returns:
        User ID string or None if not authenticated
    """
    user, _ = verify_jwt_auth()
    if user:
        return user.get('sub')
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

