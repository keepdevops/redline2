#!/usr/bin/env python3
"""
License validation helpers for web routes.
Updated to use Supabase instead of external license server.
"""

import os
import logging
from flask import request, jsonify
from typing import Optional, Tuple, Dict

logger = logging.getLogger(__name__)

# Try to use Supabase-based access control
try:
    from redline.auth.supabase_access_control import (
        validate_license_key_supabase,
        check_hours_supabase,
        supabase_access_controller
    )
    USE_SUPABASE = True
except ImportError:
    USE_SUPABASE = False
    # Fallback to old system
    try:
        from redline.auth.access_control import access_controller
        USE_SUPABASE = False
    except ImportError:
        access_controller = None


def extract_license_key() -> Optional[str]:
    """
    Extract license key from headers, query params, or JSON body.
    
    Returns:
        License key string or None
    """
    license_key = (
        request.headers.get('X-License-Key') or
        request.headers.get('Authorization', '').replace('Bearer ', '') or
        request.args.get('license_key') or
        None
    )
    
    # Also check in JSON body if available
    if not license_key:
        try:
            data = request.get_json() or {}
            license_key = data.get('license_key') or data.get('licenseKey')
        except Exception:
            pass
    
    return license_key


def validate_license_key(license_key: Optional[str] = None) -> Optional[Tuple[Dict, int]]:
    """
    Validate license key and return error response if invalid.
    Uses Supabase if available, falls back to old license server.
    
    Args:
        license_key: Optional license key (will extract from request if not provided)
        
    Returns:
        None if valid, otherwise (error_response, status_code) tuple
    """
    if not license_key:
        license_key = extract_license_key()
    
    if not license_key:
        return jsonify({
            'error': 'License key is required',
            'message': 'Please provide a license key in X-License-Key header, Authorization header, license_key query parameter, or JSON body'
        }), 401
    
    # Use Supabase if available
    if USE_SUPABASE:
        try:
            is_valid, error_msg, license_info = validate_license_key_supabase(license_key)
            
            if not is_valid:
                return jsonify({
                    'error': error_msg or 'License validation failed',
                    'license_info': license_info
                }), 403
            
            # Store license info in request context for later use
            request.license_info = license_info
            request.license_key = license_key
            
            return None  # Valid
            
        except Exception as e:
            logger.error(f"Error validating license with Supabase: {e}")
            # Fall through to old system if Supabase fails
    
    # Fallback to old license server system
    if not USE_SUPABASE and access_controller:
        try:
            is_valid, error_msg, license_info = access_controller.validate_access(license_key)
            
            if not is_valid:
                return jsonify({
                    'error': error_msg or 'License validation failed',
                    'license_info': license_info
                }), 403
            
            request.license_info = license_info
            request.license_key = license_key
            
            return None  # Valid
            
        except Exception as e:
            logger.error(f"Error validating license with old system: {e}")
    
    # If no validation system available, check if we should fail open
    if os.environ.get('REQUIRE_LICENSE_VALIDATION', 'false').lower() != 'true':
        logger.warning("No license validation available, allowing access (development mode)")
        request.license_info = {'development_mode': True}
        request.license_key = license_key
        return None  # Allow access in dev mode
    
    return jsonify({
        'error': 'License validation unavailable',
        'message': 'License validation system is not configured'
    }), 503


def get_remaining_hours(license_key: Optional[str] = None) -> Optional[float]:
    """
    Get remaining hours for a license key.
    
    Args:
        license_key: Optional license key (will extract from request if not provided)
        
    Returns:
        Hours remaining or None if error
    """
    if not license_key:
        license_key = extract_license_key()
    
    if not license_key:
        return None
    
    # Use Supabase if available
    if USE_SUPABASE:
        try:
            return check_hours_supabase(license_key)
        except Exception as e:
            logger.error(f"Error checking hours with Supabase: {e}")
    
    # Fallback to old system
    if not USE_SUPABASE and access_controller:
        try:
            return access_controller.check_hours_remaining(license_key)
        except Exception as e:
            logger.error(f"Error checking hours with old system: {e}")
    
    return None


def require_license_key(f):
    """
    Decorator to require license key validation on a route.
    
    Usage:
        @app.route('/api/data')
        @require_license_key
        def get_data():
            # License is validated, use request.license_info
            pass
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        error_response = validate_license_key()
        if error_response:
            return error_response[0], error_response[1]
        return f(*args, **kwargs)
    
    return decorated_function
