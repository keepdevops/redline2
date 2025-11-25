#!/usr/bin/env python3
"""
REDLINE Local Storage Operations
Handles local file system operations for user data storage.
"""

import os
import logging
import hashlib
import duckdb
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LocalOperations:
    """Handles local file system operations."""
    
    def __init__(self, base_path: Path):
        """
        Initialize local operations.
        
        Args:
            base_path: Base directory for local storage
        """
        self.base_path = base_path
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            if e.errno == 28:  # No space left on device
                error_msg = (
                    f"Disk space exhausted. Cannot create directory: {self.base_path}\n"
                    f"Please free up disk space or configure S3 storage (USE_S3_STORAGE=true)."
                )
                logger.error(error_msg)
                raise OSError(error_msg) from e
            raise
    
    def get_user_path(self, license_key: str) -> Path:
        """Get storage path for a user (license key)"""
        # Hash license key for directory name (security)
        key_hash = hashlib.sha256(license_key.encode()).hexdigest()[:16]
        return self.base_path / key_hash
    
    def get_user_db_path(self, license_key: str) -> str:
        """Get DuckDB path for a user"""
        user_path = self.get_user_path(license_key)
        user_path.mkdir(parents=True, exist_ok=True)
        return str(user_path / 'user_data.duckdb')
    
    def get_user_files_path(self, license_key: str) -> Path:
        """Get files storage path for a user"""
        user_path = self.get_user_path(license_key)
        files_path = user_path / 'files'
        files_path.mkdir(parents=True, exist_ok=True)
        return files_path
    
    def initialize_user_storage(self, license_key: str):
        """Initialize storage for a new user"""
        try:
            # Create local directories
            user_path = self.get_user_path(license_key)
            user_path.mkdir(parents=True, exist_ok=True)
            (user_path / 'files').mkdir(exist_ok=True)
            
            # Initialize user database
            db_path = self.get_user_db_path(license_key)
            conn = duckdb.connect(db_path)
            
            # Create user data tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_files (
                    id INTEGER PRIMARY KEY,
                    filename VARCHAR NOT NULL,
                    original_filename VARCHAR,
                    file_type VARCHAR,
                    format VARCHAR,
                    size_bytes INTEGER,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    converted_from VARCHAR,
                    metadata JSON
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS converted_files (
                    id INTEGER PRIMARY KEY,
                    original_file_id INTEGER,
                    output_format VARCHAR NOT NULL,
                    output_filename VARCHAR NOT NULL,
                    size_bytes INTEGER,
                    converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON,
                    FOREIGN KEY (original_file_id) REFERENCES user_files(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_data_tables (
                    id INTEGER PRIMARY KEY,
                    table_name VARCHAR NOT NULL UNIQUE,
                    ticker VARCHAR,
                    format VARCHAR,
                    row_count INTEGER,
                    columns TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP,
                    metadata JSON
                )
            """)
            
            conn.close()
            logger.info(f"Initialized storage for user: {license_key[:8]}...")
            
        except Exception as e:
            logger.error(f"Error initializing user storage: {str(e)}")
            raise
    
    def save_file(self, license_key: str, file_data: bytes, filename: str) -> Dict:
        """
        Save a file locally.
        
        Args:
            license_key: User license key
            file_data: File data as bytes
            filename: Name of the file
            
        Returns:
            Dictionary with file information
        """
        files_path = self.get_user_files_path(license_key)
        file_path = files_path / filename
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        file_size = len(file_data)
        
        return {
            'filename': filename,
            'size': file_size,
            'local_path': str(file_path)
        }
    
    def get_file_path(self, license_key: str, filename: str) -> Path:
        """Get the local path for a file"""
        files_path = self.get_user_files_path(license_key)
        return files_path / filename
    
    def file_exists(self, license_key: str, filename: str) -> bool:
        """Check if a file exists locally"""
        file_path = self.get_file_path(license_key, filename)
        return os.path.exists(file_path)
    
    def record_file_in_db(self, license_key: str, filename: str, original_filename: str,
                          file_type: str, file_size: int, metadata: Dict = None) -> int:
        """
        Record a file in the database.
        
        Returns:
            File ID
        """
        db_path = self.get_user_db_path(license_key)
        conn = duckdb.connect(db_path)
        
        conn.execute("""
            INSERT INTO user_files 
            (filename, original_filename, file_type, format, size_bytes, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [filename, original_filename, file_type, file_type, file_size, 
              json.dumps(metadata or {})])
        
        file_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        
        return file_id
    
    def list_files_from_db(self, license_key: str, file_type: str = None) -> List[Dict]:
        """List all files for a user from database"""
        try:
            db_path = self.get_user_db_path(license_key)
            if not os.path.exists(db_path):
                return []
            
            conn = duckdb.connect(db_path)
            
            if file_type:
                result = conn.execute("""
                    SELECT id, filename, original_filename, file_type, format, 
                           size_bytes, uploaded_at, metadata
                    FROM user_files
                    WHERE file_type = ?
                    ORDER BY uploaded_at DESC
                """, [file_type]).fetchall()
            else:
                result = conn.execute("""
                    SELECT id, filename, original_filename, file_type, format, 
                           size_bytes, uploaded_at, metadata
                    FROM user_files
                    ORDER BY uploaded_at DESC
                """).fetchall()
            
            columns = ['id', 'filename', 'original_filename', 'file_type', 'format',
                      'size_bytes', 'uploaded_at', 'metadata']
            
            files = []
            for row in result:
                file_dict = dict(zip(columns, row))
                file_dict['metadata'] = json.loads(file_dict['metadata']) if file_dict['metadata'] else {}
                files.append(file_dict)
            
            conn.close()
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []
    
    def get_file_from_db(self, license_key: str, file_id: int) -> Optional[Dict]:
        """Get file information from database"""
        try:
            db_path = self.get_user_db_path(license_key)
            if not os.path.exists(db_path):
                return None
            
            conn = duckdb.connect(db_path)
            result = conn.execute("""
                SELECT id, filename, original_filename, file_type, format, 
                       size_bytes, uploaded_at, metadata
                FROM user_files
                WHERE id = ?
            """, [file_id]).fetchone()
            
            if not result:
                conn.close()
                return None
            
            columns = ['id', 'filename', 'original_filename', 'file_type', 'format',
                      'size_bytes', 'uploaded_at', 'metadata']
            file_dict = dict(zip(columns, result))
            file_dict['metadata'] = json.loads(file_dict['metadata']) if file_dict['metadata'] else {}
            
            conn.close()
            return file_dict
            
        except Exception as e:
            logger.error(f"Error getting file: {str(e)}")
            return None
    
    def record_converted_file(self, license_key: str, original_file_id: int,
                             output_filename: str, output_format: str,
                             file_size: int, metadata: Dict = None):
        """Record a converted file in the database"""
        db_path = self.get_user_db_path(license_key)
        conn = duckdb.connect(db_path)
        
        conn.execute("""
            INSERT INTO converted_files 
            (original_file_id, output_format, output_filename, size_bytes, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, [original_file_id, output_format, output_filename, 
              file_size, json.dumps(metadata or {})])
        
        conn.close()
    
    def save_data_table(self, license_key: str, table_name: str, ticker: str = None,
                       format: str = None, row_count: int = 0, columns: List[str] = None,
                       metadata: Dict = None):
        """Save data table metadata"""
        db_path = self.get_user_db_path(license_key)
        conn = duckdb.connect(db_path)
        
        conn.execute("""
            INSERT OR REPLACE INTO user_data_tables
            (table_name, ticker, format, row_count, columns, last_accessed, metadata)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        """, [table_name, ticker, format, row_count, columns or [], 
              json.dumps(metadata or {})])
        
        conn.close()
    
    def list_data_tables(self, license_key: str) -> List[Dict]:
        """List all data tables for a user"""
        try:
            db_path = self.get_user_db_path(license_key)
            if not os.path.exists(db_path):
                return []
            
            conn = duckdb.connect(db_path)
            result = conn.execute("""
                SELECT id, table_name, ticker, format, row_count, columns, 
                       created_at, last_accessed, metadata
                FROM user_data_tables
                ORDER BY last_accessed DESC
            """).fetchall()
            
            columns = ['id', 'table_name', 'ticker', 'format', 'row_count', 'columns',
                      'created_at', 'last_accessed', 'metadata']
            
            tables = []
            for row in result:
                table_dict = dict(zip(columns, row))
                table_dict['metadata'] = json.loads(table_dict['metadata']) if table_dict['metadata'] else {}
                tables.append(table_dict)
            
            conn.close()
            return tables
            
        except Exception as e:
            logger.error(f"Error listing data tables: {str(e)}")
            return []
    
    def get_storage_stats(self, license_key: str) -> Dict:
        """Get storage statistics for a user"""
        try:
            db_path = self.get_user_db_path(license_key)
            if not os.path.exists(db_path):
                return {'total_files': 0, 'total_size': 0, 'total_tables': 0}
            
            conn = duckdb.connect(db_path)
            
            # File stats
            file_stats = conn.execute("""
                SELECT COUNT(*) as count, COALESCE(SUM(size_bytes), 0) as total_size
                FROM user_files
            """).fetchone()
            
            # Table stats
            table_count = conn.execute("""
                SELECT COUNT(*) FROM user_data_tables
            """).fetchone()[0]
            
            conn.close()
            
            return {
                'total_files': file_stats[0] or 0,
                'total_size_bytes': file_stats[1] or 0,
                'total_size_mb': round((file_stats[1] or 0) / (1024 * 1024), 2),
                'total_tables': table_count or 0
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {'error': str(e)}

