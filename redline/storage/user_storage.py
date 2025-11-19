#!/usr/bin/env python3
"""
User Data Storage Module
Handles user-specific data storage, isolation, and cloud storage integration
"""

import os
import logging
import hashlib
import duckdb
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Cloud storage providers
try:
    import boto3
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    boto3 = None

class UserStorage:
    """Manages user-specific data storage and isolation"""
    
    def __init__(self, base_path: str = None, use_s3: bool = None, s3_config: Dict = None):
        """
        Initialize user storage
        
        Args:
            base_path: Base directory for local storage
            use_s3: Whether to use S3 for cloud storage (None = auto-detect from env)
            s3_config: S3 configuration dict with bucket, access_key, secret_key, region
        """
        if base_path is None:
            base_path = os.environ.get('USER_STORAGE_BASE_PATH', 
                                      os.path.join(os.getcwd(), 'data', 'users'))
        
        self.base_path = Path(base_path)
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
        
        # Auto-detect S3 usage from environment
        if use_s3 is None:
            use_s3 = os.environ.get('USE_S3_STORAGE', 'false').lower() == 'true'
        
        self.use_s3 = use_s3 and S3_AVAILABLE
        
        # Load S3/R2 config from environment if not provided
        if s3_config is None and self.use_s3:
            s3_config = {
                'bucket': os.environ.get('S3_BUCKET'),
                'access_key': os.environ.get('S3_ACCESS_KEY'),
                'secret_key': os.environ.get('S3_SECRET_KEY'),
                'region': os.environ.get('S3_REGION', 'us-east-1'),
                'endpoint_url': os.environ.get('S3_ENDPOINT_URL')  # For R2 or custom endpoints
            }
        
        self.s3_config = s3_config or {}
        
        if self.use_s3:
            self._init_s3()
    
    def _init_s3(self):
        """Initialize S3 client (supports AWS S3 and Cloudflare R2)"""
        try:
            # Get endpoint URL for R2 (Cloudflare R2 uses custom endpoint)
            endpoint_url = os.environ.get('S3_ENDPOINT_URL') or self.s3_config.get('endpoint_url')
            
            # Build client config
            client_config = {
                'aws_access_key_id': self.s3_config.get('access_key'),
                'aws_secret_access_key': self.s3_config.get('secret_key'),
                'region_name': self.s3_config.get('region', 'us-east-1')
            }
            
            # Add endpoint URL if provided (for R2 or other S3-compatible services)
            if endpoint_url:
                client_config['endpoint_url'] = endpoint_url
                logger.info(f"Using custom S3 endpoint: {endpoint_url}")
            
            self.s3_client = boto3.client('s3', **client_config)
            self.s3_bucket = self.s3_config.get('bucket')
            
            # Determine storage type for logging
            storage_type = "R2" if endpoint_url and 'r2.cloudflarestorage.com' in endpoint_url else "S3"
            logger.info(f"{storage_type} storage initialized: bucket={self.s3_bucket}")
        except Exception as e:
            logger.error(f"Failed to initialize S3/R2: {str(e)}")
            self.use_s3 = False
    
    def _get_user_path(self, license_key: str) -> Path:
        """Get storage path for a user (license key)"""
        # Hash license key for directory name (security)
        key_hash = hashlib.sha256(license_key.encode()).hexdigest()[:16]
        return self.base_path / key_hash
    
    def _get_user_db_path(self, license_key: str) -> str:
        """Get DuckDB path for a user"""
        user_path = self._get_user_path(license_key)
        user_path.mkdir(parents=True, exist_ok=True)
        return str(user_path / 'user_data.duckdb')
    
    def _get_user_files_path(self, license_key: str) -> Path:
        """Get files storage path for a user"""
        user_path = self._get_user_path(license_key)
        files_path = user_path / 'files'
        files_path.mkdir(parents=True, exist_ok=True)
        return files_path
    
    def _get_s3_prefix(self, license_key: str) -> str:
        """Get S3 prefix for a user"""
        key_hash = hashlib.sha256(license_key.encode()).hexdigest()[:16]
        return f"users/{key_hash}/"
    
    def initialize_user_storage(self, license_key: str):
        """Initialize storage for a new user"""
        try:
            # Create local directories
            user_path = self._get_user_path(license_key)
            user_path.mkdir(parents=True, exist_ok=True)
            (user_path / 'files').mkdir(exist_ok=True)
            
            # Initialize user database
            db_path = self._get_user_db_path(license_key)
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
    
    def save_file(self, license_key: str, file_data: bytes, filename: str, 
                 file_type: str = None, metadata: Dict = None) -> Dict:
        """Save a file for a user"""
        try:
            self.initialize_user_storage(license_key)
            
            # Save locally
            files_path = self._get_user_files_path(license_key)
            file_path = files_path / filename
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            file_size = len(file_data)
            
            # Save to S3 if enabled
            s3_key = None
            if self.use_s3:
                s3_key = f"{self._get_s3_prefix(license_key)}files/{filename}"
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=s3_key,
                    Body=file_data
                )
            
            # Record in database
            db_path = self._get_user_db_path(license_key)
            conn = duckdb.connect(db_path)
            
            conn.execute("""
                INSERT INTO user_files 
                (filename, original_filename, file_type, format, size_bytes, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [filename, filename, file_type, file_type, file_size, 
                  json.dumps(metadata or {})])
            
            file_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.close()
            
            return {
                'file_id': file_id,
                'filename': filename,
                'size': file_size,
                'local_path': str(file_path),
                's3_key': s3_key,
                'saved_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    def list_files(self, license_key: str, file_type: str = None) -> List[Dict]:
        """List all files for a user"""
        try:
            db_path = self._get_user_db_path(license_key)
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
    
    def get_file(self, license_key: str, file_id: int) -> Optional[Dict]:
        """Get file information and path"""
        try:
            db_path = self._get_user_db_path(license_key)
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
            
            # Get file path
            files_path = self._get_user_files_path(license_key)
            file_path = files_path / file_dict['filename']
            file_dict['local_path'] = str(file_path)
            file_dict['exists'] = os.path.exists(file_path)
            
            # Get S3 key if available
            if self.use_s3:
                file_dict['s3_key'] = f"{self._get_s3_prefix(license_key)}files/{file_dict['filename']}"
            
            conn.close()
            return file_dict
            
        except Exception as e:
            logger.error(f"Error getting file: {str(e)}")
            return None
    
    def save_converted_file(self, license_key: str, original_file_id: int,
                           output_filename: str, output_format: str,
                           file_data: bytes, metadata: Dict = None) -> Dict:
        """Save a converted file"""
        try:
            # Save file
            file_info = self.save_file(license_key, file_data, output_filename, 
                                     file_type=output_format, metadata=metadata)
            
            # Record conversion
            db_path = self._get_user_db_path(license_key)
            conn = duckdb.connect(db_path)
            
            conn.execute("""
                INSERT INTO converted_files 
                (original_file_id, output_format, output_filename, size_bytes, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, [original_file_id, output_format, output_filename, 
                  len(file_data), json.dumps(metadata or {})])
            
            conn.close()
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error saving converted file: {str(e)}")
            raise
    
    def save_data_table(self, license_key: str, table_name: str, ticker: str = None,
                       format: str = None, row_count: int = 0, columns: List[str] = None,
                       metadata: Dict = None):
        """Save data table metadata"""
        try:
            db_path = self._get_user_db_path(license_key)
            conn = duckdb.connect(db_path)
            
            conn.execute("""
                INSERT OR REPLACE INTO user_data_tables
                (table_name, ticker, format, row_count, columns, last_accessed, metadata)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            """, [table_name, ticker, format, row_count, columns or [], 
                  json.dumps(metadata or {})])
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving data table: {str(e)}")
            raise
    
    def list_data_tables(self, license_key: str) -> List[Dict]:
        """List all data tables for a user"""
        try:
            db_path = self._get_user_db_path(license_key)
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
            db_path = self._get_user_db_path(license_key)
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

# Global user storage instance
user_storage = UserStorage()

