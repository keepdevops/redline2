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
                    license_key VARCHAR,
                    user_id VARCHAR,
                    session_id VARCHAR,
                    hours_deducted DOUBLE NOT NULL,
                    deduction_time TIMESTAMP NOT NULL,
                    hours_remaining_before DOUBLE,
                    hours_remaining_after DOUBLE,
                    api_endpoint VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add user_id column if table exists but column doesn't (migration)
            try:
                conn.execute("ALTER TABLE usage_history ADD COLUMN IF NOT EXISTS user_id VARCHAR")
            except Exception:
                pass  # Column may already exist
            
            # Create sequence for auto-increment (DuckDB doesn't support AUTO_INCREMENT)
            conn.execute("CREATE SEQUENCE IF NOT EXISTS usage_history_id_seq START 1")
            
            # Payment history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payment_history (
                    id INTEGER PRIMARY KEY,
                    license_key VARCHAR,
                    user_id VARCHAR,
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
            
            # Add user_id column if table exists but column doesn't (migration)
            try:
                conn.execute("ALTER TABLE payment_history ADD COLUMN IF NOT EXISTS user_id VARCHAR")
            except Exception:
                pass  # Column may already exist
            
            # Create sequence for auto-increment
            conn.execute("CREATE SEQUENCE IF NOT EXISTS payment_history_id_seq START 1")
            
            # Access logs table (API access tracking)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY,
                    license_key VARCHAR,
                    user_id VARCHAR,
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
            
            # Add user_id column if table exists but column doesn't (migration)
            try:
                conn.execute("ALTER TABLE access_logs ADD COLUMN IF NOT EXISTS user_id VARCHAR")
            except Exception:
                pass  # Column may already exist
            
            # Create sequence for auto-increment
            conn.execute("CREATE SEQUENCE IF NOT EXISTS access_logs_id_seq START 1")
            
            # Create indexes for performance
            # Legacy license_key indexes (kept for migration period)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_sessions_license ON usage_sessions(license_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_history_license ON usage_history(license_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_payment_history_license ON payment_history(license_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_logs_license ON access_logs(license_key)")
            
            # New user_id indexes (primary for JWT authentication)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_sessions_user ON usage_sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_history_user ON usage_history(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_payment_history_user ON payment_history(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_logs_user ON access_logs(user_id)")
            
            # Time-based indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_sessions_start ON usage_sessions(start_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_history_time ON usage_history(deduction_time)")
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
    
    def log_session_start(self, session_id: str, user_id: str, license_key: Optional[str] = None):
        """Log the start of a usage session. Requires user_id from JWT token.
        
        Args:
            session_id: Unique session identifier
            user_id: User ID from JWT token (required)
            license_key: Legacy license key (optional, for migration period only)
        """
        # Pre-validation with if-else
        if not session_id:
            logger.error("Session ID is required for logging session start")
            return
        
        if not user_id:
            logger.error("User ID is required for logging session start")
            return
        
        if not isinstance(session_id, str) or not isinstance(user_id, str):
            logger.error("Session ID and user ID must be strings")
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
                    SET start_time = ?, status = 'active', user_id = ?, license_key = ?
                    WHERE session_id = ?
                """, [datetime.now(), user_id, license_key, session_id])
                logger.debug(f"Updated existing session: {session_id} for user {user_id}")
            else:
                # Insert new session
                conn.execute("""
                    INSERT INTO usage_sessions (session_id, user_id, license_key, start_time, status)
                    VALUES (?, ?, ?, ?, 'active')
                """, [session_id, user_id, license_key, datetime.now()])
                logger.debug(f"Logged session start: {session_id} for user {user_id}")
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
    
    def log_hour_deduction(self, user_id: str, hours: float, session_id: Optional[str] = None,
                          hours_before: Optional[float] = None, hours_after: Optional[float] = None,
                          api_endpoint: Optional[str] = None, license_key: Optional[str] = None):
        """Log an hour deduction event. Requires user_id from JWT token.
        
        Args:
            user_id: User ID from JWT token (required)
            hours: Hours to deduct
            session_id: Optional session identifier
            hours_before: Hours remaining before deduction
            hours_after: Hours remaining after deduction
            api_endpoint: Optional API endpoint name
            license_key: Legacy license key (optional, for migration period only)
        """
        # Pre-validation with if-else
        if not user_id:
            logger.error("User ID is required for logging hour deduction")
            return
        
        if not isinstance(user_id, str):
            logger.error("User ID must be a string")
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
                (id, user_id, license_key, session_id, hours_deducted, deduction_time, 
                 hours_remaining_before, hours_remaining_after, api_endpoint)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [next_id, user_id, license_key, session_id, hours, datetime.now(), 
                  hours_before, hours_after, api_endpoint])
            logger.debug(f"Logged hour deduction: user {user_id}, {hours} hours")
        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error logging hour deduction: {str(e)}")
        except Exception as e:
            logger.error(f"Error logging hour deduction: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def log_payment(self, user_id: str, hours_purchased: float, amount_paid: float,
                   stripe_session_id: Optional[str] = None, payment_id: Optional[str] = None,
                   payment_status: str = 'completed', currency: str = 'usd', license_key: Optional[str] = None):
        """Log a payment transaction. Requires user_id from JWT token.
        
        Args:
            user_id: User ID from JWT token (required)
            hours_purchased: Number of hours purchased
            amount_paid: Amount paid in currency
            stripe_session_id: Stripe checkout session ID
            payment_id: Stripe payment intent ID
            payment_status: Payment status (default: 'completed')
            currency: Currency code (default: 'usd')
            license_key: Legacy license key (optional, for migration period only)
        """
        # Pre-validation with if-else
        if not user_id:
            logger.error("User ID is required for logging payment")
            return
        
        if not isinstance(user_id, str):
            logger.error("User ID must be a string")
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
                (id, user_id, license_key, stripe_session_id, payment_id, hours_purchased, 
                 amount_paid, currency, payment_status, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [next_id, user_id, license_key, stripe_session_id, payment_id, hours_purchased,
                  amount_paid, currency, payment_status, datetime.now()])
            logger.info(f"Logged payment: user {user_id}, {hours_purchased} hours, ${amount_paid}")
        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error logging payment: {str(e)}")
        except Exception as e:
            logger.error(f"Error logging payment: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def log_access(self, user_id: str, endpoint: str, method: str,
                  session_id: Optional[str] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None, response_status: Optional[int] = None,
                  response_time_ms: Optional[int] = None, license_key: Optional[str] = None):
        """Log an API access event. Requires user_id from JWT token.
        
        Args:
            user_id: User ID from JWT token (required)
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            session_id: Optional session identifier
            ip_address: Client IP address
            user_agent: Client user agent string
            response_status: HTTP response status code
            response_time_ms: Response time in milliseconds
            license_key: Legacy license key (optional, for migration period only)
        """
        # Pre-validation with if-else
        if not user_id:
            logger.debug("User ID is empty for access log, skipping")
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
                (id, user_id, license_key, session_id, endpoint, method, ip_address, 
                 user_agent, response_status, response_time_ms, access_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [next_id, user_id, license_key, session_id, endpoint, method, ip_address,
                  user_agent, response_status, response_time_ms, datetime.now()])
        except duckdb.ConnectionException as e:
            logger.error(f"Database connection error logging access: {str(e)}")
        except Exception as e:
            logger.error(f"Error logging access: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def get_usage_history(self, user_id: str, limit: int = 100, license_key: Optional[str] = None) -> List[Dict]:
        """Get usage history for a user. Requires user_id from JWT token.
        
        Args:
            user_id: User ID from JWT token (required)
            limit: Maximum number of records to return (default: 100)
            license_key: Legacy license key (optional, for migration period only)
        
        Returns:
            List of usage history records
        """
        # Pre-validation with if-else
        if not user_id:
            logger.warning("User ID is required for getting usage history")
            return []
        
        if not isinstance(user_id, str):
            logger.warning("User ID must be a string")
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
            # Use user_id as primary identifier, fallback to license_key during migration
            if user_id:
                result = conn.execute("""
                    SELECT * FROM usage_history
                    WHERE user_id = ?
                    ORDER BY deduction_time DESC
                    LIMIT ?
                """, [user_id, limit]).fetchall()
            elif license_key:
                # Fallback for migration period
                logger.debug(f"Using license_key fallback for usage history query")
                result = conn.execute("""
                    SELECT * FROM usage_history
                    WHERE license_key = ?
                    ORDER BY deduction_time DESC
                    LIMIT ?
                """, [license_key, limit]).fetchall()
            else:
                logger.warning("Neither user_id nor license_key provided for usage history")
                return []
            
            columns = ['id', 'license_key', 'user_id', 'session_id', 'hours_deducted', 'deduction_time',
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
    
    def get_payment_history(self, user_id: str, limit: int = 50, license_key: Optional[str] = None) -> List[Dict]:
        """Get payment history for a user. Requires user_id from JWT token.
        
        Args:
            user_id: User ID from JWT token (required)
            limit: Maximum number of records to return (default: 50)
            license_key: Legacy license key (optional, for migration period only)
        
        Returns:
            List of payment history records
        """
        try:
            conn = duckdb.connect(self.db_path)
            # Use user_id as primary identifier, fallback to license_key during migration
            if user_id:
                result = conn.execute("""
                    SELECT * FROM payment_history
                    WHERE user_id = ?
                    ORDER BY payment_date DESC
                    LIMIT ?
                """, [user_id, limit]).fetchall()
            elif license_key:
                # Fallback for migration period
                logger.debug(f"Using license_key fallback for payment history query")
                result = conn.execute("""
                    SELECT * FROM payment_history
                    WHERE license_key = ?
                    ORDER BY payment_date DESC
                    LIMIT ?
                """, [license_key, limit]).fetchall()
            else:
                logger.warning("Neither user_id nor license_key provided for payment history")
                return []
            
            columns = ['id', 'license_key', 'user_id', 'stripe_session_id', 'payment_id', 'hours_purchased',
                      'amount_paid', 'currency', 'payment_status', 'payment_date', 'created_at']
            
            history = []
            for row in result:
                history.append(dict(zip(columns, row)))
            
            conn.close()
            return history
        except Exception as e:
            logger.error(f"Error getting payment history: {str(e)}")
            return []
    
    def get_session_history(self, user_id: str, limit: int = 50, license_key: Optional[str] = None) -> List[Dict]:
        """Get session history for a user. Requires user_id from JWT token.
        
        Args:
            user_id: User ID from JWT token (required)
            limit: Maximum number of records to return (default: 50)
            license_key: Legacy license key (optional, for migration period only)
        
        Returns:
            List of session history records
        """
        try:
            conn = duckdb.connect(self.db_path)
            # Use user_id as primary identifier, fallback to license_key during migration
            if user_id:
                result = conn.execute("""
                    SELECT * FROM usage_sessions
                    WHERE user_id = ?
                    ORDER BY start_time DESC
                    LIMIT ?
                """, [user_id, limit]).fetchall()
            elif license_key:
                # Fallback for migration period
                logger.debug(f"Using license_key fallback for session history query")
                result = conn.execute("""
                    SELECT * FROM usage_sessions
                    WHERE license_key = ?
                    ORDER BY start_time DESC
                    LIMIT ?
                """, [license_key, limit]).fetchall()
            else:
                logger.warning("Neither user_id nor license_key provided for session history")
                return []
            
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
    
    def get_access_stats(self, user_id: str, days: int = 30, license_key: Optional[str] = None) -> Dict:
        """Get access statistics for a user. Requires user_id from JWT token.
        
        Args:
            user_id: User ID from JWT token (required)
            days: Number of days to look back (default: 30)
            license_key: Legacy license key (optional, for migration period only)
        
        Returns:
            Dictionary with access statistics
        """
        try:
            conn = duckdb.connect(self.db_path)
            
            # Determine which identifier to use
            if not user_id and not license_key:
                logger.warning("Neither user_id nor license_key provided for access stats")
                return {}
            
            # Use user_id as primary identifier, fallback to license_key during migration
            identifier = user_id if user_id else license_key
            use_user_id = bool(user_id)
            
            # Total API calls (DuckDB doesn't support parameterized INTERVAL, use string formatting)
            if use_user_id:
                total_calls = conn.execute(f"""
                    SELECT COUNT(*) FROM access_logs
                    WHERE user_id = ? AND access_time >= CURRENT_TIMESTAMP - INTERVAL '{days}' DAYS
                """, [identifier]).fetchone()[0]
            else:
                logger.debug(f"Using license_key fallback for access stats query")
                total_calls = conn.execute(f"""
                    SELECT COUNT(*) FROM access_logs
                    WHERE license_key = ? AND access_time >= CURRENT_TIMESTAMP - INTERVAL '{days}' DAYS
                """, [identifier]).fetchone()[0]
            
            # Total hours used
            if use_user_id:
                total_hours = conn.execute(f"""
                    SELECT COALESCE(SUM(hours_deducted), 0) FROM usage_history
                    WHERE user_id = ? AND deduction_time >= CURRENT_TIMESTAMP - INTERVAL '{days}' DAYS
                """, [identifier]).fetchone()[0]
            else:
                total_hours = conn.execute(f"""
                    SELECT COALESCE(SUM(hours_deducted), 0) FROM usage_history
                    WHERE license_key = ? AND deduction_time >= CURRENT_TIMESTAMP - INTERVAL '{days}' DAYS
                """, [identifier]).fetchone()[0]
            
            # Most used endpoints
            if use_user_id:
                top_endpoints = conn.execute(f"""
                    SELECT endpoint, COUNT(*) as count
                    FROM access_logs
                    WHERE user_id = ? AND access_time >= CURRENT_TIMESTAMP - INTERVAL '{days}' DAYS
                    GROUP BY endpoint
                    ORDER BY count DESC
                    LIMIT 10
                """, [identifier]).fetchall()
            else:
                top_endpoints = conn.execute(f"""
                    SELECT endpoint, COUNT(*) as count
                    FROM access_logs
                    WHERE license_key = ? AND access_time >= CURRENT_TIMESTAMP - INTERVAL '{days}' DAYS
                    GROUP BY endpoint
                    ORDER BY count DESC
                    LIMIT 10
                """, [identifier]).fetchall()
            
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

