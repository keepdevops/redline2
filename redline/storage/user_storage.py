#!/usr/bin/env python3
"""
User Data Storage Module
Handles user-specific data storage, isolation, and cloud storage integration
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from .s3_operations import S3Operations, S3_AVAILABLE
from .local_operations import LocalOperations

logger = logging.getLogger(__name__)

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
        
        # Initialize local operations
        self.local_ops = LocalOperations(self.base_path)
        
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
        
        # Initialize S3 operations if enabled
        self.s3_ops = None
        if self.use_s3:
            try:
                self.s3_ops = S3Operations(self.s3_config)
            except Exception as e:
                logger.error(f"Failed to initialize S3/R2: {str(e)}")
                self.use_s3 = False
    
    def initialize_user_storage(self, license_key: str):
        """Initialize storage for a new user"""
        self.local_ops.initialize_user_storage(license_key)
    
    def save_file(self, license_key: str, file_data: bytes, filename: str, 
                 file_type: str = None, metadata: Dict = None) -> Dict:
        """Save a file for a user"""
        try:
            self.initialize_user_storage(license_key)
            
            # Save locally
            local_info = self.local_ops.save_file(license_key, file_data, filename)
            file_size = local_info['size']
            
            # Save to S3 if enabled
            s3_key = None
            if self.use_s3 and self.s3_ops:
                s3_key = self.s3_ops.upload_file(license_key, filename, file_data)
            
            # Record in database
            file_id = self.local_ops.record_file_in_db(
                license_key, filename, filename, file_type, file_size, metadata
            )
            
            return {
                'file_id': file_id,
                'filename': filename,
                'size': file_size,
                'local_path': local_info['local_path'],
                's3_key': s3_key,
                'saved_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    def list_files(self, license_key: str, file_type: str = None) -> List[Dict]:
        """List all files for a user"""
        return self.local_ops.list_files_from_db(license_key, file_type)
    
    def get_file(self, license_key: str, file_id: int) -> Optional[Dict]:
        """Get file information and path"""
        try:
            file_dict = self.local_ops.get_file_from_db(license_key, file_id)
            if not file_dict:
                return None
            
            # Get file path and existence
            file_path = self.local_ops.get_file_path(license_key, file_dict['filename'])
            file_dict['local_path'] = str(file_path)
            file_dict['exists'] = self.local_ops.file_exists(license_key, file_dict['filename'])
            
            # Get S3 key if available
            if self.use_s3 and self.s3_ops:
                file_dict['s3_key'] = f"{self.s3_ops.get_s3_prefix(license_key)}files/{file_dict['filename']}"
            
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
            self.local_ops.record_converted_file(
                license_key, original_file_id, output_filename, 
                output_format, len(file_data), metadata
            )
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error saving converted file: {str(e)}")
            raise
    
    def save_data_table(self, license_key: str, table_name: str, ticker: str = None,
                       format: str = None, row_count: int = 0, columns: List[str] = None,
                       metadata: Dict = None):
        """Save data table metadata"""
        self.local_ops.save_data_table(license_key, table_name, ticker, format, row_count, columns, metadata)
    
    def list_data_tables(self, license_key: str) -> List[Dict]:
        """List all data tables for a user"""
        return self.local_ops.list_data_tables(license_key)
    
    def get_storage_stats(self, license_key: str) -> Dict:
        """Get storage statistics for a user"""
        return self.local_ops.get_storage_stats(license_key)

# Global user storage instance
user_storage = UserStorage()

