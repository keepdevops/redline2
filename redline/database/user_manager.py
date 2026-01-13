#!/usr/bin/env python3
"""
DuckDB User Management
Stores user profiles in DuckDB while using Supabase Auth for authentication.
This is the "middle ground" approach: Supabase Auth + DuckDB storage.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    duckdb = None

logger = logging.getLogger(__name__)


class DuckDBUserManager:
    """Manages user profiles in DuckDB (authentication handled by Supabase Auth)"""
    
    def __init__(self, db_path: str = None):
        """Initialize DuckDB user manager"""
        if db_path is None:
            db_path = os.path.join(os.getcwd(), 'variosync_data.duckdb')
        self.db_path = db_path
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create users table if it doesn't exist"""
        if not DUCKDB_AVAILABLE:
            logger.warning("DuckDB not available - cannot initialize user schema")
            return
        
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(self.db_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            conn = duckdb.connect(self.db_path)
            
            # Create users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR PRIMARY KEY,
                    email VARCHAR NOT NULL UNIQUE,
                    name VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    email_verified BOOLEAN DEFAULT FALSE,
                    metadata JSON
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            
            conn.close()
            logger.debug(f"User schema initialized in DuckDB: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing user schema: {str(e)}")
            raise
    
    def create_or_update_user(
        self,
        user_id: str,
        email: str,
        name: Optional[str] = None,
        email_verified: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create or update user in DuckDB (sync from Supabase Auth)
        
        Args:
            user_id: User ID from Supabase Auth (UUID)
            email: User email
            name: User name (optional)
            email_verified: Whether email is verified
            metadata: Additional metadata (optional)
        
        Returns:
            True if successful, False otherwise
        """
        if not DUCKDB_AVAILABLE:
            logger.error("DuckDB not available - cannot create/update user")
            return False
        
        if not user_id or not email:
            logger.error("User ID and email are required")
            return False
        
        try:
            conn = duckdb.connect(self.db_path)
            
            # Check if user exists
            result = conn.execute(
                "SELECT id FROM users WHERE id = ?",
                [user_id]
            ).fetchone()
            
            if result:
                # Update existing user
                update_sql = """
                    UPDATE users 
                    SET email = ?,
                        name = ?,
                        email_verified = ?,
                        metadata = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                conn.execute(update_sql, [
                    email,
                    name,
                    email_verified,
                    str(metadata) if metadata else None,
                    user_id
                ])
                logger.debug(f"Updated user in DuckDB: {user_id}")
            else:
                # Create new user
                insert_sql = """
                    INSERT INTO users (id, email, name, email_verified, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """
                conn.execute(insert_sql, [
                    user_id,
                    email,
                    name,
                    email_verified,
                    str(metadata) if metadata else None
                ])
                logger.debug(f"Created user in DuckDB: {user_id}")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating/updating user {user_id}: {str(e)}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID from DuckDB
        
        Args:
            user_id: User ID from Supabase Auth
        
        Returns:
            User dict or None if not found
        """
        if not DUCKDB_AVAILABLE:
            logger.warning("DuckDB not available - cannot get user")
            return None
        
        if not user_id:
            logger.error("User ID is required")
            return None
        
        try:
            conn = duckdb.connect(self.db_path)
            
            result = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                [user_id]
            ).fetchone()
            
            conn.close()
            
            if not result:
                logger.debug(f"User not found in DuckDB: {user_id}")
                return None
            
            # Convert to dict
            columns = ['id', 'email', 'name', 'created_at', 'updated_at', 
                      'last_login', 'email_verified', 'metadata']
            user = dict(zip(columns, result))
            
            # Parse JSON metadata if present
            if user.get('metadata') and isinstance(user['metadata'], str):
                try:
                    import json
                    user['metadata'] = json.loads(user['metadata'])
                except Exception:
                    pass
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email from DuckDB
        
        Args:
            email: User email
        
        Returns:
            User dict or None if not found
        """
        if not DUCKDB_AVAILABLE:
            logger.warning("DuckDB not available - cannot get user")
            return None
        
        if not email:
            logger.error("Email is required")
            return None
        
        try:
            conn = duckdb.connect(self.db_path)
            
            result = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                [email]
            ).fetchone()
            
            conn.close()
            
            if not result:
                logger.debug(f"User not found in DuckDB: {email}")
                return None
            
            # Convert to dict
            columns = ['id', 'email', 'name', 'created_at', 'updated_at', 
                      'last_login', 'email_verified', 'metadata']
            user = dict(zip(columns, result))
            
            # Parse JSON metadata if present
            if user.get('metadata') and isinstance(user['metadata'], str):
                try:
                    import json
                    user['metadata'] = json.loads(user['metadata'])
                except Exception:
                    pass
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    def update_last_login(self, user_id: str) -> bool:
        """Update last login timestamp"""
        if not DUCKDB_AVAILABLE:
            return False
        
        if not user_id:
            return False
        
        try:
            conn = duckdb.connect(self.db_path)
            conn.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                [user_id]
            )
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating last login for {user_id}: {str(e)}")
            return False
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update user fields in DuckDB
        
        Args:
            user_id: User ID
            updates: Dictionary of fields to update
        
        Returns:
            True if successful, False otherwise
        """
        if not DUCKDB_AVAILABLE:
            return False
        
        if not user_id or not updates:
            return False
        
        try:
            conn = duckdb.connect(self.db_path)
            
            # Build UPDATE statement dynamically
            set_clauses = []
            values = []
            
            allowed_fields = ['name', 'email_verified', 'metadata']
            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    values.append(value)
            
            if not set_clauses:
                logger.warning(f"No valid fields to update for user {user_id}")
                conn.close()
                return False
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)
            
            update_sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
            conn.execute(update_sql, values)
            conn.close()
            
            logger.debug(f"Updated user {user_id} with fields: {list(updates.keys())}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return False


# Global instance
user_manager = DuckDBUserManager()
