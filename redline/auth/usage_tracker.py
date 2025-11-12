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
        self.check_interval = float(os.environ.get('USAGE_CHECK_INTERVAL', '300'))  # 5 minutes default
        
    def start_session(self, license_key: str, user_id: Optional[str] = None) -> str:
        """Start a new usage session"""
        session_id = f"{license_key}_{int(time.time())}"
        
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
        
        logger.info(f"Started usage session {session_id} for license {license_key}")
        return session_id
    
    def update_session(self, session_id: str) -> Optional[Dict]:
        """Update session and check if hours need to be deducted"""
        with self.session_lock:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            now = datetime.now()
            time_since_check = (now - session['last_check']).total_seconds()
            
            # Only check if enough time has passed
            if time_since_check < self.check_interval:
                return session
            
            # Calculate hours used since last check
            hours_used = time_since_check / 3600.0  # Convert seconds to hours
            session['total_seconds'] += time_since_check
            session['last_check'] = now
            
            # Deduct hours if significant time has passed (at least 1 minute)
            if hours_used >= (1.0 / 60.0):  # At least 1 minute
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

