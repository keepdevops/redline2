#!/usr/bin/env python3
"""
Usage Storage Module (Supabase PostgreSQL)
Persistent storage for user access data, usage history, and payment records
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from redline.auth.supabase_config import supabase_admin
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    supabase_admin = None

class UsageStorage:
    """Persistent storage for usage and access data using Supabase PostgreSQL"""

    def __init__(self):
        """Initialize usage storage with Supabase"""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase not available - usage storage disabled")
            return

        self.db = supabase_admin
        logger.info("Usage storage initialized with Supabase PostgreSQL")

    def log_session_start(self, session_id: str, user_id: str):
        """Log the start of a usage session"""
        if not SUPABASE_AVAILABLE:
            return

        try:
            # Check if session exists
            existing = self.db.table('usage_sessions').select('session_id').eq('session_id', session_id).execute()

            if existing.data:
                # Update existing session
                self.db.table('usage_sessions').update({
                    'start_time': datetime.now().isoformat(),
                    'status': 'active'
                }).eq('session_id', session_id).execute()
                logger.debug(f"Updated existing session: {session_id}")
            else:
                # Insert new session
                self.db.table('usage_sessions').insert({
                    'session_id': session_id,
                    'user_id': user_id,
                    'start_time': datetime.now().isoformat(),
                    'status': 'active'
                }).execute()
                logger.debug(f"Logged session start: {session_id}")
        except Exception as e:
            logger.error(f"Error logging session start: {str(e)}")

    def log_session_end(self, session_id: str, total_hours: float, total_seconds: float):
        """Log the end of a usage session"""
        if not SUPABASE_AVAILABLE:
            return

        try:
            self.db.table('usage_sessions').update({
                'end_time': datetime.now().isoformat(),
                'total_hours': total_hours,
                'total_seconds': total_seconds,
                'status': 'completed'
            }).eq('session_id', session_id).execute()
            logger.debug(f"Logged session end: {session_id}, hours: {total_hours}")
        except Exception as e:
            logger.error(f"Error logging session end: {str(e)}")

    def log_hour_deduction(self, user_id: str, hours: float, session_id: Optional[str] = None,
                          hours_before: Optional[float] = None, hours_after: Optional[float] = None,
                          api_endpoint: Optional[str] = None):
        """Log an hour deduction event"""
        if not SUPABASE_AVAILABLE:
            return

        try:
            self.db.table('usage_history').insert({
                'user_id': user_id,
                'session_id': session_id,
                'hours_deducted': hours,
                'deduction_time': datetime.now().isoformat(),
                'hours_remaining_before': hours_before,
                'hours_remaining_after': hours_after,
                'api_endpoint': api_endpoint
            }).execute()
            logger.debug(f"Logged hour deduction: {user_id}, {hours} hours")
        except Exception as e:
            logger.error(f"Error logging hour deduction: {str(e)}")

    def log_payment(self, user_id: str, hours_purchased: float, amount_paid: float,
                   stripe_session_id: Optional[str] = None, payment_id: Optional[str] = None,
                   payment_status: str = 'completed', currency: str = 'usd'):
        """Log a payment transaction"""
        if not SUPABASE_AVAILABLE:
            return

        try:
            self.db.table('payment_history').insert({
                'user_id': user_id,
                'stripe_session_id': stripe_session_id,
                'payment_id': payment_id,
                'hours_purchased': hours_purchased,
                'amount_paid': amount_paid,
                'currency': currency,
                'payment_status': payment_status,
                'payment_date': datetime.now().isoformat()
            }).execute()
            logger.info(f"Logged payment: {user_id}, {hours_purchased} hours, ${amount_paid}")
        except Exception as e:
            logger.error(f"Error logging payment: {str(e)}")

    def log_access(self, user_id: str, endpoint: str, method: str,
                  session_id: Optional[str] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None, response_status: Optional[int] = None,
                  response_time_ms: Optional[int] = None):
        """Log an API access event"""
        if not SUPABASE_AVAILABLE:
            return

        try:
            self.db.table('access_logs').insert({
                'user_id': user_id,
                'session_id': session_id,
                'endpoint': endpoint,
                'method': method,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'response_status': response_status,
                'response_time_ms': response_time_ms,
                'access_time': datetime.now().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Error logging access: {str(e)}")

    def get_usage_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get usage history for a user"""
        if not SUPABASE_AVAILABLE:
            return []

        try:
            result = self.db.table('usage_history').select('*').eq('user_id', user_id).order('deduction_time', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting usage history: {str(e)}")
            return []

    def get_payment_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get payment history for a user"""
        if not SUPABASE_AVAILABLE:
            return []

        try:
            result = self.db.table('payment_history').select('*').eq('user_id', user_id).order('payment_date', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting payment history: {str(e)}")
            return []

    def get_session_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get session history for a user"""
        if not SUPABASE_AVAILABLE:
            return []

        try:
            result = self.db.table('usage_sessions').select('*').eq('user_id', user_id).order('start_time', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error getting session history: {str(e)}")
            return []

    def get_access_stats(self, user_id: str, days: int = 30) -> Dict:
        """Get access statistics for a user"""
        if not SUPABASE_AVAILABLE:
            return {}

        try:
            # Calculate date threshold
            from datetime import timedelta
            threshold = (datetime.now() - timedelta(days=days)).isoformat()

            # Total API calls
            access_logs = self.db.table('access_logs').select('id', count='exact').eq('user_id', user_id).gte('access_time', threshold).execute()
            total_calls = access_logs.count or 0

            # Total hours used
            usage_history = self.db.table('usage_history').select('hours_deducted').eq('user_id', user_id).gte('deduction_time', threshold).execute()
            total_hours = sum(h.get('hours_deducted', 0) for h in (usage_history.data or []))

            # Most used endpoints
            endpoints_data = self.db.table('access_logs').select('endpoint').eq('user_id', user_id).gte('access_time', threshold).execute()
            endpoint_counts = {}
            for log in (endpoints_data.data or []):
                endpoint = log.get('endpoint')
                if endpoint:
                    endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1

            top_endpoints = sorted(
                [{'endpoint': ep, 'count': count} for ep, count in endpoint_counts.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:10]

            return {
                'total_api_calls': total_calls,
                'total_hours_used': total_hours or 0.0,
                'top_endpoints': top_endpoints,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"Error getting access stats: {str(e)}")
            return {}

# Global usage storage instance
usage_storage = UsageStorage()
