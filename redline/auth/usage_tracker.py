#!/usr/bin/env python3
"""
Usage Tracking Middleware
Tracks active sessions and deducts hours from licenses
"""

import os
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from threading import Lock

try:
    from redline.database.usage_storage import usage_storage
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    usage_storage = None

logger = logging.getLogger(__name__)

class UsageTracker:
    """Tracks user usage time and deducts hours from licenses"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.session_lock = Lock()
        self.license_server_url = os.environ.get('LICENSE_SERVER_URL', 'http://localhost:5001')
        self.require_license_server = os.environ.get('REQUIRE_LICENSE_SERVER', 'false').lower() == 'true'
        self.check_interval = float(os.environ.get('USAGE_CHECK_INTERVAL', '30'))  # 30 seconds default
        # Track last deduction time per license key (for session-independent tracking)
        self.last_deduction_time: Dict[str, datetime] = {}
        # Local license storage for development (when license server unavailable)
        self.local_licenses: Dict[str, Dict] = {}
        
    def start_session(self, license_key: str, user_id: Optional[str] = None) -> str:
        """Start a new usage session"""
        # Use microseconds and a small random component to ensure uniqueness
        import secrets
        timestamp = time.time()
        microsecond_component = int((timestamp - int(timestamp)) * 1000000)
        random_component = secrets.token_hex(2)  # 4 hex characters for uniqueness
        session_id = f"{license_key}_{int(timestamp)}_{microsecond_component}_{random_component}"
        
        with self.session_lock:
            self.active_sessions[session_id] = {
                'license_key': license_key,
                'user_id': user_id,
                'start_time': datetime.now(),
                'last_check': datetime.now(),
                'total_seconds': 0.0
            }
        
        # Log to persistent storage
        if STORAGE_AVAILABLE and usage_storage:
            try:
                usage_storage.log_session_start(session_id, license_key, user_id)
            except Exception as e:
                logger.warning(f"Failed to log session start to storage: {str(e)}")
        
        logger.debug(f"Started usage session {session_id} for license {license_key}")
        return session_id
    
    def update_session(self, session_id: str) -> Optional[Dict]:
        """Update session and check if hours need to be deducted"""
        with self.session_lock:
            if session_id not in self.active_sessions:
                # Session doesn't exist - might be from a previous server restart
                # Return None to indicate session not found
                return None
            
            session = self.active_sessions[session_id]
            now = datetime.now()
            time_since_check = (now - session['last_check']).total_seconds()
            
            # Always update last_check to current time
            session['last_check'] = now
            
            # Only deduct if enough time has passed since last check
            if time_since_check < self.check_interval:
                # Not enough time has passed, just update timestamp
                return session
            
            # Calculate hours used since last check
            hours_used = time_since_check / 3600.0  # Convert seconds to hours
            session['total_seconds'] += time_since_check
            
            # Deduct hours (no minimum threshold - deduct every check interval)
            # Since check_interval is 30 seconds, this will deduct every 30 seconds
            self._deduct_hours(session['license_key'], hours_used, session_id)
            
            return session
    
    def end_session(self, session_id: str) -> Optional[Dict]:
        """End a usage session and deduct final hours"""
        with self.session_lock:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            now = datetime.now()
            total_time = (now - session['start_time']).total_seconds()
            hours_used = total_time / 3600.0
            
            # Deduct remaining hours
            if hours_used > 0:
                self._deduct_hours(session['license_key'], hours_used)
            
            # Remove session
            del self.active_sessions[session_id]
            
            # Log to persistent storage
            if STORAGE_AVAILABLE and usage_storage:
                try:
                    usage_storage.log_session_end(session_id, hours_used, total_time)
                except Exception as e:
                    logger.warning(f"Failed to log session end to storage: {str(e)}")
            
            logger.info(f"Ended session {session_id}, used {hours_used:.4f} hours")
            
            return {
                'session_id': session_id,
                'total_hours': hours_used,
                'total_seconds': total_time
            }
    
    def _deduct_hours(self, license_key: str, hours: float, session_id: Optional[str] = None):
        """Deduct hours from license via license server"""
        try:
            # Get current balance before deduction
            hours_before = None
            if STORAGE_AVAILABLE and usage_storage:
                try:
                    balance_response = requests.get(
                        f'{self.license_server_url}/api/licenses/{license_key}/hours',
                        timeout=5
                    )
                    if balance_response.status_code == 200:
                        balance_data = balance_response.json()
                        hours_before = balance_data.get('hours_remaining', 0)
                except:
                    pass
            
            response = requests.post(
                f'{self.license_server_url}/api/licenses/{license_key}/usage',
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
            else:
                logger.warning(f"Failed to deduct hours: {response.text}")
                
        except requests.exceptions.ConnectionError:
            # License server unavailable - use local tracking if not required
            if not self.require_license_server:
                logger.debug(f"License server unavailable, tracking hours locally for {license_key}")
                # Initialize local license if not exists
                if license_key not in self.local_licenses:
                    self.local_licenses[license_key] = {
                        'hours_remaining': 0.0,
                        'used_hours': 0.0
                    }
                
                # Track locally (don't actually deduct, just log)
                self.local_licenses[license_key]['used_hours'] += hours
                logger.debug(f"Tracked {hours:.4f} hours locally for {license_key}")
            else:
                logger.error(f"License server unavailable and REQUIRE_LICENSE_SERVER=true")
        except Exception as e:
            logger.error(f"Error deducting hours: {str(e)}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about an active session"""
        with self.session_lock:
            return self.active_sessions.get(session_id)
    
    def cleanup_stale_sessions(self, max_age_hours: float = 24.0):
        """Clean up sessions older than max_age_hours"""
        with self.session_lock:
            now = datetime.now()
            stale_sessions = []
            
            for session_id, session in list(self.active_sessions.items()):
                age = (now - session['start_time']).total_seconds() / 3600.0
                if age > max_age_hours:
                    stale_sessions.append(session_id)
            
            for session_id in stale_sessions:
                self.end_session(session_id)
                logger.info(f"Cleaned up stale session {session_id}")

# Global usage tracker instance
usage_tracker = UsageTracker()

