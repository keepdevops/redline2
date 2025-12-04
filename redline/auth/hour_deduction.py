#!/usr/bin/env python3
"""
Hour Deduction Helper
Handles deducting hours from licenses via license server.
"""

import os
import logging
import requests
from typing import Optional

try:
    from redline.database.usage_storage import usage_storage
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    usage_storage = None

logger = logging.getLogger(__name__)


def deduct_hours(license_key: str, hours: float, license_server_url: str,
                 require_license_server: bool, session_id: Optional[str] = None,
                 local_licenses: dict = None) -> bool:
    """
    Deduct hours from license via license server.
    
    Args:
        license_key: The license key
        hours: Hours to deduct
        license_server_url: URL of the license server
        require_license_server: Whether license server is required
        session_id: Optional session ID for logging
        local_licenses: Optional dict to track hours locally if server unavailable
        
    Returns:
        True if deduction was successful, False otherwise
    """
    try:
        # Get current balance before deduction
        hours_before = None
        if STORAGE_AVAILABLE and usage_storage:
            try:
                balance_response = requests.get(
                    f'{license_server_url}/api/licenses/{license_key}/hours',
                    timeout=5
                )
                if balance_response.status_code == 200:
                    balance_data = balance_response.json()
                    hours_before = balance_data.get('hours_remaining', 0)
            except:
                pass
        
        response = requests.post(
            f'{license_server_url}/api/licenses/{license_key}/usage',
            json={'hours': hours},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            hours_after = result.get('hours_remaining', 0)
            
            # Log to persistent storage
            if STORAGE_AVAILABLE and usage_storage:
                try:
                    usage_storage.log_hour_deduction(
                        license_key, hours, session_id,
                        hours_before, hours_after
                    )
                except Exception as e:
                    logger.warning(f"Failed to log hour deduction to storage: {str(e)}")
            
            logger.info(f"Deducted {hours:.4f} hours from license {license_key}. Remaining: {hours_after}")
            return True
        else:
            logger.warning(f"Failed to deduct hours: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        # License server unavailable - use local tracking if not required
        if not require_license_server:
            logger.debug(f"License server unavailable, tracking hours locally for {license_key}")
            # Initialize local license if not exists
            if local_licenses is not None:
                if license_key not in local_licenses:
                    local_licenses[license_key] = {
                        'hours_remaining': 0.0,
                        'used_hours': 0.0
                    }
                
                # Track locally (don't actually deduct, just log)
                local_licenses[license_key]['used_hours'] += hours
                logger.debug(f"Tracked {hours:.4f} hours locally for {license_key}")
            return True
        else:
            logger.error(f"License server unavailable and REQUIRE_LICENSE_SERVER=true")
            return False
    except Exception as e:
        logger.error(f"Error deducting hours: {str(e)}")
        return False



