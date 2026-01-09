#!/usr/bin/env python3
"""
Usage Storage Module
Persistent storage for user access data, usage history, and payment records
"""

import os
import logging
import duckdb
from datetime import datetime
from typing import Dict, List, Optional
from threading import Lock

logger = logging.getLogger(__name__)

class UsageStorage:
    """Persistent storage for usage and access data"""
    
    def __init__(self, db_path: str = None):
        """Initialize usage storage database"""
        if db_path is None:
            db_path = os.path.join(os.getcwd(), 'data', 'usage_data.duckdb')
        
        self.db_path = db_path
        self.lock = Lock()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database schema
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create database tables if they don't exist"""
        # Pre-validation with if-else
        if not self.db_path:
            logger.error("Database path is empty, cannot initialize schema")
            raise ValueError("Database path cannot be empty")

        if not isinstance(self.db_path, str):
            logger.error(f"Database path must be a string, got {type(self.db_path)}")
            raise TypeError(f"Database path must be a string, got {type(self.db_path)}")

        # Ensure parent directory exists
        parent_dir = os.path.dirname(self.db_path)
        if parent_dir and not os.path.exists(parent_dir):
            logger.error(f"Parent directory does not exist: {parent_dir}")
            raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

        try:
            conn = duckdb.connect(self.db_path)
            
            # Usage sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_sessions (
                    session_id VARCHAR PRIMARY KEY,
                    license_key VARCHAR NOT NULL,
                    user_id VARCHAR,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    total_hours DOUBLE,
                    total_seconds DOUBLE,
                    api_endpoints TEXT[],
                    status VARCHAR DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Usage history table (detailed log of hour deductions)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_history (
                    id INTEGER PRIMARY KEY,
                    license_key VARCHAR NOT NULL,
                    session_id VARCHAR,
                    hours_deducted DOUBLE NOT NULL,
                    deduction_time TIMESTAMP NOT NULL,
                    hours_remaining_before DOUBLE,
                    hours_remaining_after DOUBLE,
                    api_endpoint VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sequence for auto-increment (DuckDB doesn't support AUTO_INCREMENT)
            conn.execute("CREATE SEQUENCE IF NOT EXISTS usage_history_id_seq START 1")
            
            # Payment history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payment_history (
                    id INTEGER PRIMARY KEY,
                    license_key VARCHAR NOT NULL,
                    stripe_session_id VARCHAR,
                    payment_id VARCHAR,
                    hours_purchased DOUBLE NOT NULL,
                    amount_paid DOUBLE NOT NULL,
                    currency VARCHAR DEFAULT 'usd',
                    payment_status VARCHAR,
                    payment_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sequence for auto-increment
            conn.execute("CREATE SEQUENCE IF NOT EXISTS payment_history_id_seq START 1")
            
            # Access logs table (API access tracking)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY,
                    license_key VARCHAR NOT NULL,
                    session_id VARCHAR,
                    endpoint VARCHAR NOT NULL,
                    method VARCHAR NOT NULL,
                    ip_address VARCHAR,
                    user_agent VARCHAR,
                    response_status INTEGER,
                    response_time_ms INTEGER,
                    access_time TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sequence for auto-increment
            conn.execute("CREATE SEQUENCE IF NOT EXISTS access_logs_id_seq START 1")
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_sessions_license ON usage_sessions(license_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_sessions_start ON usage_sessions(start_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_history_license ON usage_history(license_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_history_time ON usage_history(deduction_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_payment_history_license ON payment_history(license_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_logs_license ON access_logs(license_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_logs_time ON access_logs(access_time)")
            
            conn.close()
            logger.info(f"Usage storage database initialized: {self.db_path}")

        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error initializing usage storage: {str(e)}")
            raise
        except duckdb.CatalogException as e:
            logger.error(f"Database catalog error initializing usage storage: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error initializing usage storage: {str(e)}")
            raise
    
    def log_session_start(self, session_id: str, license_key: str, user_id: Optional[str] = None):
        """Log the start of a usage session"""
        # Pre-validation with if-else
        if not session_id:
            logger.error("Session ID is required for logging session start")
            return
        
        if not license_key:
            logger.error("License key is required for logging session start")
            return
        
        if not isinstance(session_id, str) or not isinstance(license_key, str):
            logger.error("Session ID and license key must be strings")
            return
        
        if not os.path.exists(os.path.dirname(self.db_path)):
            logger.error(f"Database directory does not exist: {os.path.dirname(self.db_path)}")
            return
        
        conn = None
        try:
            conn = duckdb.connect(self.db_path)
            # Check if session exists first (DuckDB doesn't support ON CONFLICT reliably)
            existing = conn.execute("""
                SELECT session_id FROM usage_sessions WHERE session_id = ?
            """, [session_id]).fetchone()
            
            if existing:
                # Update existing session (duplicate detected, update instead)
                conn.execute("""
                    UPDATE usage_sessions
                    SET start_time = ?, status = 'active', license_key = ?, user_id = ?
                    WHERE session_id = ?
                """, [datetime.now(), license_key, user_id, session_id])
                logger.debug(f"Updated existing session: {session_id}")
            else:
                # Insert new session
                conn.execute("""
                    INSERT INTO usage_sessions (session_id, license_key, user_id, start_time, status)
                    VALUES (?, ?, ?, ?, 'active')
                """, [session_id, license_key, user_id, datetime.now()])
                logger.debug(f"Logged session start: {session_id}")
        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error logging session start: {str(e)}")
        except duckdb.DataError as e:
            logger.error(f"Data error logging session start for {session_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error logging session start: {str(e)}")
            # Don't raise - allow session to continue even if logging fails
        finally:
            if conn:
                conn.close()
    
    def log_session_end(self, session_id: str, total_hours: float, total_seconds: float):
        """Log the end of a usage session"""
        # Pre-validation with if-else
        if not session_id:
            logger.error("Session ID is required for logging session end")
            return
        
        if not isinstance(session_id, str):
            logger.error("Session ID must be a string")
            return
        
        if total_hours is None or not isinstance(total_hours, (int, float)):
            logger.warning(f"Invalid total_hours value: {total_hours}, defaulting to 0")
            total_hours = 0.0
        
        if total_seconds is None or not isinstance(total_seconds, (int, float)):
            logger.warning(f"Invalid total_seconds value: {total_seconds}, defaulting to 0")
            total_seconds = 0.0
        
        conn = None
        try:
            conn = duckdb.connect(self.db_path)
            conn.execute("""
                UPDATE usage_sessions
                SET end_time = ?, total_hours = ?, total_seconds = ?, status = 'completed'
                WHERE session_id = ?
            """, [datetime.now(), total_hours, total_seconds, session_id])
            logger.debug(f"Logged session end: {session_id}, hours: {total_hours}")
        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error logging session end: {str(e)}")
        except Exception as e:
            logger.error(f"Error logging session end: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def log_hour_deduction(self, license_key: str, hours: float, session_id: Optional[str] = None,
                          hours_before: Optional[float] = None, hours_after: Optional[float] = None,
                          api_endpoint: Optional[str] = None):
        """Log an hour deduction event"""
        # Pre-validation with if-else
        if not license_key:
            logger.error("License key is required for logging hour deduction")
            return
        
        if not isinstance(license_key, str):
            logger.error("License key must be a string")
            return
        
        if hours is None or not isinstance(hours, (int, float)):
            logger.warning(f"Invalid hours value: {hours}, defaulting to 0")
            hours = 0.0
        
        if hours < 0:
            logger.warning(f"Negative hours value: {hours}, using absolute value")
            hours = abs(hours)
        
        conn = None
        try:
            conn = duckdb.connect(self.db_path)
            # Get next ID from sequence
            next_id = conn.execute("SELECT nextval('usage_history_id_seq')").fetchone()[0]
            conn.execute("""
                INSERT INTO usage_history 
                (id, license_key, session_id, hours_deducted, deduction_time, 
                 hours_remaining_before, hours_remaining_after, api_endpoint)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [next_id, license_key, session_id, hours, datetime.now(), 
                  hours_before, hours_after, api_endpoint])
            # Mask license key in logs (show only first 4 and last 4 chars)
            masked_key = f"{license_key[:4]}...{license_key[-4:]}" if len(license_key) > 8 else "***"
            logger.debug(f"Logged hour deduction: {masked_key}, {hours} hours")
        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error logging hour deduction: {str(e)}")
        except Exception as e:
            logger.error(f"Error logging hour deduction: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def log_payment(self, license_key: str, hours_purchased: float, amount_paid: float,
                   stripe_session_id: Optional[str] = None, payment_id: Optional[str] = None,
                   payment_status: str = 'completed', currency: str = 'usd'):
        """Log a payment transaction"""
        # Pre-validation with if-else
        if not license_key:
            logger.error("License key is required for logging payment")
            return
        
        if not isinstance(license_key, str):
            logger.error("License key must be a string")
            return
        
        if hours_purchased is None or not isinstance(hours_purchased, (int, float)):
            logger.error(f"Invalid hours_purchased value: {hours_purchased}")
            return
        
        if hours_purchased <= 0:
            logger.warning(f"Non-positive hours_purchased value: {hours_purchased}")
        
        if amount_paid is None or not isinstance(amount_paid, (int, float)):
            logger.error(f"Invalid amount_paid value: {amount_paid}")
            return
        
        if amount_paid < 0:
            logger.warning(f"Negative amount_paid value: {amount_paid}")
        
        # Validate currency
        valid_currencies = ['usd', 'eur', 'gbp', 'cad', 'aud']
        if currency and currency.lower() not in valid_currencies:
            logger.warning(f"Unknown currency: {currency}, using 'usd'")
            currency = 'usd'
        
        conn = None
        try:
            conn = duckdb.connect(self.db_path)
            # Get next ID from sequence
            next_id = conn.execute("SELECT nextval('payment_history_id_seq')").fetchone()[0]
            conn.execute("""
                INSERT INTO payment_history 
                (id, license_key, stripe_session_id, payment_id, hours_purchased, 
                 amount_paid, currency, payment_status, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [next_id, license_key, stripe_session_id, payment_id, hours_purchased,
                  amount_paid, currency, payment_status, datetime.now()])
            # Mask license key in logs (show only first 4 and last 4 chars)
            masked_key = f"{license_key[:4]}...{license_key[-4:]}" if len(license_key) > 8 else "***"
            logger.info(f"Logged payment: {masked_key}, {hours_purchased} hours, ${amount_paid}")
        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error logging payment: {str(e)}")
        except Exception as e:
            logger.error(f"Error logging payment: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def log_access(self, license_key: str, endpoint: str, method: str,
                  session_id: Optional[str] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None, response_status: Optional[int] = None,
                  response_time_ms: Optional[int] = None):
        """Log an API access event"""
        # Pre-validation with if-else
        if not license_key:
            logger.debug("License key is empty for access log, skipping")
            return
        
        if not endpoint:
            logger.debug("Endpoint is empty for access log, skipping")
            return
        
        if not method:
            logger.debug("Method is empty for access log, skipping")
            return
        
        # Validate method
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if method.upper() not in valid_methods:
            logger.warning(f"Unknown HTTP method: {method}")
        
        # Validate response status if provided
        if response_status is not None:
            if not isinstance(response_status, int) or response_status < 100 or response_status > 599:
                logger.warning(f"Invalid response status: {response_status}")
                response_status = None
        
        conn = None
        try:
            conn = duckdb.connect(self.db_path)
            # Get next ID from sequence
            next_id = conn.execute("SELECT nextval('access_logs_id_seq')").fetchone()[0]
            conn.execute("""
                INSERT INTO access_logs 
                (id, license_key, session_id, endpoint, method, ip_address, 
                 user_agent, response_status, response_time_ms, access_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [next_id, license_key, session_id, endpoint, method, ip_address,
                  user_agent, response_status, response_time_ms, datetime.now()])
        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error logging access: {str(e)}")
        except Exception as e:
            logger.error(f"Error logging access: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def get_usage_history(self, license_key: str, limit: int = 100) -> List[Dict]:
        """Get usage history for a license"""
        # Pre-validation with if-else
        if not license_key:
            logger.warning("License key is required for getting usage history")
            return []
        
        if not isinstance(license_key, str):
            logger.warning("License key must be a string")
            return []
        
        if not isinstance(limit, int) or limit < 1:
            logger.warning(f"Invalid limit value: {limit}, using default 100")
            limit = 100
        
        if limit > 10000:
            logger.warning(f"Limit {limit} is too large, capping at 10000")
            limit = 10000
        
        conn = None
        try:
            conn = duckdb.connect(self.db_path)
            result = conn.execute("""
                SELECT * FROM usage_history
                WHERE license_key = ?
                ORDER BY deduction_time DESC
                LIMIT ?
            """, [license_key, limit]).fetchall()
            
            columns = ['id', 'license_key', 'session_id', 'hours_deducted', 'deduction_time',
                      'hours_remaining_before', 'hours_remaining_after', 'api_endpoint', 'created_at']
            
            history = []
            for row in result:
                history.append(dict(zip(columns, row)))
            
            return history
        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error getting usage history: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting usage history: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_payment_history(self, license_key: str, limit: int = 50) -> List[Dict]:
        """Get payment history for a license"""
        try:
            conn = duckdb.connect(self.db_path)
            result = conn.execute("""
                SELECT * FROM payment_history
                WHERE license_key = ?
                ORDER BY payment_date DESC
                LIMIT ?
            """, [license_key, limit]).fetchall()
            
            columns = ['id', 'license_key', 'stripe_session_id', 'payment_id', 'hours_purchased',
                      'amount_paid', 'currency', 'payment_status', 'payment_date', 'created_at']
            
            history = []
            for row in result:
                history.append(dict(zip(columns, row)))
            
            conn.close()
            return history
        except Exception as e:
            logger.error(f"Error getting payment history: {str(e)}")
            return []
    
    def get_session_history(self, license_key: str, limit: int = 50) -> List[Dict]:
        """Get session history for a license"""
        try:
            conn = duckdb.connect(self.db_path)
            result = conn.execute("""
                SELECT * FROM usage_sessions
                WHERE license_key = ?
                ORDER BY start_time DESC
                LIMIT ?
            """, [license_key, limit]).fetchall()
            
            columns = ['session_id', 'license_key', 'user_id', 'start_time', 'end_time',
                      'total_hours', 'total_seconds', 'api_endpoints', 'status', 'created_at']
            
            sessions = []
            for row in result:
                sessions.append(dict(zip(columns, row)))
            
            conn.close()
            return sessions
        except Exception as e:
            logger.error(f"Error getting session history: {str(e)}")
            return []
    
    def get_access_stats(self, license_key: str, days: int = 30) -> Dict:
        """Get access statistics for a license"""
        try:
            conn = duckdb.connect(self.db_path)
            
            # Total API calls (DuckDB doesn't support parameterized INTERVAL, use string formatting)
            total_calls = conn.execute(f"""
                SELECT COUNT(*) FROM access_logs
                WHERE license_key = ? AND access_time >= CURRENT_TIMESTAMP - INTERVAL '{days}' DAYS
            """, [license_key]).fetchone()[0]
            
            # Total hours used
            total_hours = conn.execute(f"""
                SELECT COALESCE(SUM(hours_deducted), 0) FROM usage_history
                WHERE license_key = ? AND deduction_time >= CURRENT_TIMESTAMP - INTERVAL '{days}' DAYS
            """, [license_key]).fetchone()[0]
            
            # Most used endpoints
            top_endpoints = conn.execute(f"""
                SELECT endpoint, COUNT(*) as count
                FROM access_logs
                WHERE license_key = ? AND access_time >= CURRENT_TIMESTAMP - INTERVAL '{days}' DAYS
                GROUP BY endpoint
                ORDER BY count DESC
                LIMIT 10
            """, [license_key]).fetchall()
            
            conn.close()
            
            return {
                'total_api_calls': total_calls,
                'total_hours_used': total_hours or 0.0,
                'top_endpoints': [{'endpoint': ep[0], 'count': ep[1]} for ep in top_endpoints],
                'period_days': days
            }
        except Exception as e:
            logger.error(f"Error getting access stats: {str(e)}")
            return {}

# Global usage storage instance
usage_storage = UsageStorage()

