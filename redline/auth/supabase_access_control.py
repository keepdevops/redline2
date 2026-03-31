#!/usr/bin/env python3
"""
Supabase-based Access Control
Validates licenses and checks hours using Supabase instead of external license server.
"""

import os
import logging
from flask import request, jsonify, g
from typing import Optional, Tuple, Dict
from uuid import UUID

try:
    from redline.database.supabase_client import SupabaseClient, get_supabase_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    SupabaseClient = None

logger = logging.getLogger(__name__)


class SupabaseAccessController:
    """Controls access based on Supabase user subscriptions and hours remaining"""
    
    def __init__(self):
        """Initialize access controller with Supabase client."""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase client not available. Install with: pip install supabase")
            self.supabase = None
        else:
            try:
                self.supabase = get_supabase_client()
                logger.info("Supabase access controller initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.supabase = None
        
        # For development: allow access if Supabase is not configured
        self.fail_open = os.environ.get('REQUIRE_SUPABASE', 'false').lower() != 'true'
        self.enforce_payment = os.environ.get('ENFORCE_PAYMENT', 'true').lower() == 'true'
    
    def get_user_id_from_license_key(self, license_key: str) -> Optional[UUID]:
        """
        Map license key to Supabase user ID.
        
        In the refactored system, license keys can be:
        1. Supabase user IDs (UUID format)
        2. Email addresses (lookup user by email)
        3. Custom license keys (stored in a mapping table)
        
        Args:
            license_key: License key string
            
        Returns:
            User UUID if found, None otherwise
        """
        if not license_key or not self.supabase:
            return None
        
        try:
            # Try as UUID first
            try:
                user_id = UUID(license_key)
                # Verify user exists
                profile = self.supabase.get_user_profile(user_id)
                if profile:
                    return user_id
            except (ValueError, TypeError):
                pass
            
            # Try as email
            if '@' in license_key:
                # Lookup user by email in Supabase Auth
                # Note: This requires service role key, not anon key
                try:
                    response = self.supabase.client.auth.admin.list_users()
                    for user in response.users:
                        if user.email == license_key:
                            return UUID(user.id)
                except Exception as e:
                    logger.debug(f"Could not lookup user by email: {e}")
            
            # For now, return None if not found
            # In production, you might have a license_key -> user_id mapping table
            return None
            
        except Exception as e:
            logger.error(f"Error mapping license key to user ID: {e}")
            return None
    
    def validate_access(self, license_key: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validate that a license key has sufficient hours for access.
        
        Args:
            license_key: License key (can be user ID, email, or custom key)
            
        Returns:
            (is_valid, error_message, license_info)
        """
        if not license_key:
            return False, "License key is required", None
        
        # If Supabase is not available, fail open for development
        if not self.supabase:
            if self.fail_open:
                logger.warning("Supabase not available, allowing access (development mode)")
                return True, None, {'hours_remaining': 0.0, 'development_mode': True}
            return False, "License validation unavailable (Supabase not configured)", None
        
        try:
            # Get user ID from license key
            user_id = self.get_user_id_from_license_key(license_key)
            
            if not user_id:
                # If we can't map the license key, check if we should fail open
                if self.fail_open:
                    logger.warning(f"Could not map license key to user, allowing access (dev mode)")
                    return True, None, {'hours_remaining': 0.0, 'development_mode': True}
                return False, "Invalid license key", None
            
            # Check usage hours
            usage_check = self.supabase.check_usage_hours(user_id, required_hours=0.01)
            
            if not usage_check.has_sufficient_hours:
                if self.enforce_payment:
                    return False, f"No hours remaining ({usage_check.remaining_hours:.2f} hours). Please purchase hours to continue.", {
                        'hours_remaining': usage_check.remaining_hours,
                        'user_id': str(user_id)
                    }
                else:
                    # Payment enforcement disabled, allow access
                    logger.warning(f"User {user_id} has insufficient hours but payment enforcement is disabled")
                    return True, None, {
                        'hours_remaining': usage_check.remaining_hours,
                        'user_id': str(user_id)
                    }
            
            # Valid access
            return True, None, {
                'hours_remaining': usage_check.remaining_hours,
                'user_id': str(user_id),
                'valid': True
            }
            
        except Exception as e:
            logger.error(f"Error validating access: {str(e)}")
            if self.fail_open:
                logger.warning("Error during validation, allowing access (development mode)")
                return True, None, {'hours_remaining': 0.0, 'development_mode': True, 'error': str(e)}
            return False, f"License validation error: {str(e)}", None
    
    def check_hours_remaining(self, license_key: str) -> Optional[float]:
        """
        Check hours remaining for a license key.
        
        Args:
            license_key: License key string
            
        Returns:
            Hours remaining or None if error
        """
        if not license_key or not self.supabase:
            return None
        
        try:
            user_id = self.get_user_id_from_license_key(license_key)
            if not user_id:
                return None
            
            return self.supabase.get_remaining_hours(user_id)
            
        except Exception as e:
            logger.error(f"Error checking hours: {str(e)}")
            return None
    
    def deduct_hours_for_operation(self, license_key: str, hours: float) -> Tuple[bool, Optional[str]]:
        """
        Deduct hours for an operation.
        
        Args:
            license_key: License key string
            hours: Hours to deduct
            
        Returns:
            (success, error_message)
        """
        if not license_key or not self.supabase:
            return False, "License validation unavailable"
        
        try:
            user_id = self.get_user_id_from_license_key(license_key)
            if not user_id:
                return False, "Invalid license key"
            
            result = self.supabase.deduct_hours(user_id, hours)
            if result.success:
                return True, None
            else:
                return False, "Insufficient hours"
                
        except Exception as e:
            logger.error(f"Error deducting hours: {str(e)}")
            return False, str(e)


# Global access controller instance
supabase_access_controller = SupabaseAccessController()


def validate_license_key_supabase(license_key: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
    """
    Convenience function to validate license key using Supabase.
    
    Args:
        license_key: License key to validate
        
    Returns:
        (is_valid, error_message, license_info)
    """
    return supabase_access_controller.validate_access(license_key)


def check_hours_supabase(license_key: str) -> Optional[float]:
    """
    Convenience function to check hours remaining.
    
    Args:
        license_key: License key to check
        
    Returns:
        Hours remaining or None
    """
    return supabase_access_controller.check_hours_remaining(license_key)
