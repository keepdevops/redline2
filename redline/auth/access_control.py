#!/usr/bin/env python3
"""
Access Control Middleware
Validates licenses and blocks access when hours are insufficient
"""

import os
import logging
import requests
from flask import request, jsonify, g
from typing import Optional, Tuple, Dict

logger = logging.getLogger(__name__)

class AccessController:
    """Controls access based on license validation and hours remaining"""
    
    def __init__(self):
        self.license_server_url = os.environ.get('LICENSE_SERVER_URL', 'http://localhost:5001')
        self.enforce_payment = os.environ.get('ENFORCE_PAYMENT', 'true').lower() == 'true'
    
    def validate_access(self, license_key: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validate that a license key has sufficient hours for access
        
        Returns:
            (is_valid, error_message, license_info)
        """
        if not license_key:
            return False, "License key is required", None
        
        try:
            # Validate license with license server
            response = requests.post(
                f'{self.license_server_url}/api/licenses/{license_key}/validate',
                json={},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('valid'):
                    license_info = result.get('license', {})
                    hours_remaining = license_info.get('hours_remaining', 0.0)
                    
                    # Check if payment enforcement is enabled
                    if self.enforce_payment and hours_remaining <= 0:
                        return False, "No hours remaining. Please purchase hours to continue.", license_info
                    
                    return True, None, license_info
                else:
                    error = result.get('error', 'Invalid license')
                    return False, error, None
            else:
                return False, "License validation failed", None
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to license server at {self.license_server_url}")
            # If license server is down, allow access (fail open for development)
            # In production, you might want to fail closed
            if os.environ.get('REQUIRE_LICENSE_SERVER', 'false').lower() == 'true':
                return False, "License server unavailable", None
            return True, None, None  # Fail open for development
        except Exception as e:
            logger.error(f"Error validating license: {str(e)}")
            return False, f"License validation error: {str(e)}", None
    
    def check_hours_remaining(self, license_key: str) -> Optional[float]:
        """Check hours remaining for a license"""
        try:
            response = requests.get(
                f'{self.license_server_url}/api/licenses/{license_key}/hours',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('hours_remaining', 0.0)
            return None
        except Exception as e:
            logger.error(f"Error checking hours: {str(e)}")
            return None

# Global access controller instance
access_controller = AccessController()

