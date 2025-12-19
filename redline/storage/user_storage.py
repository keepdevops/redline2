#!/usr/bin/env python3
"""
User Data Storage Module (Supabase)
Handles user-specific data storage with Supabase Storage and PostgreSQL
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

# Import Supabase
try:
    from redline.storage.supabase_storage import supabase_storage
    from redline.auth.supabase_config import supabase_admin
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    supabase_storage = None
    supabase_admin = None

class UserStorage:
    """Manages user-specific data storage with Supabase Storage and PostgreSQL"""

    def __init__(self):
        """Initialize user storage with Supabase"""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase not available - user storage disabled")
            return

        self.storage = supabase_storage
        self.db = supabase_admin
        logger.info("User storage initialized with Supabase")

    def save_file(self, user_id: str, file_data: bytes, filename: str,
                 file_type: str = None, metadata: Dict = None) -> Dict:
        """Save a file for a user"""
        if not SUPABASE_AVAILABLE:
            raise Exception("Supabase not available")

        try:
            file_size = len(file_data)

            # Upload to Supabase Storage
            supabase_url = self.storage.upload_file(user_id, filename, file_data)

            # Record in database
            result = self.db.table('user_files').insert({
                'user_id': user_id,
                'filename': filename,
                'original_filename': filename,
                'file_type': file_type,
                'format': file_type,
                'size_bytes': file_size,
                'supabase_url': supabase_url,
                'metadata': metadata or {}
            }).execute()

            file_id = result.data[0]['id'] if result.data else None

            return {
                'file_id': file_id,
                'filename': filename,
                'size': file_size,
                'url': supabase_url,
                'saved_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise

    def list_files(self, user_id: str, file_type: str = None) -> List[Dict]:
        """List all files for a user"""
        if not SUPABASE_AVAILABLE:
            return []

        try:
            query = self.db.table('user_files').select('*').eq('user_id', user_id)

            if file_type:
                query = query.eq('file_type', file_type)

            result = query.order('uploaded_at', desc=True).execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return []

    def get_file(self, user_id: str, file_id: int) -> Optional[Dict]:
        """Get file information"""
        if not SUPABASE_AVAILABLE:
            return None

        try:
            result = self.db.table('user_files').select('*').eq('user_id', user_id).eq('id', file_id).execute()

            if result.data:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"Error getting file: {str(e)}")
            return None

    def save_converted_file(self, user_id: str, original_file_id: int,
                           output_filename: str, output_format: str,
                           file_data: bytes, metadata: Dict = None) -> Dict:
        """Save a converted file"""
        if not SUPABASE_AVAILABLE:
            raise Exception("Supabase not available")

        try:
            # Save file
            file_info = self.save_file(user_id, file_data, output_filename,
                                     file_type=output_format, metadata=metadata)

            # Record conversion
            self.db.table('converted_files').insert({
                'user_id': user_id,
                'original_file_id': original_file_id,
                'output_format': output_format,
                'output_filename': output_filename,
                'size_bytes': len(file_data),
                'supabase_url': file_info.get('url'),
                'metadata': metadata or {}
            }).execute()

            return file_info

        except Exception as e:
            logger.error(f"Error saving converted file: {str(e)}")
            raise

    def save_data_table(self, user_id: str, table_name: str, ticker: str = None,
                       format: str = None, row_count: int = 0, columns: List[str] = None,
                       metadata: Dict = None):
        """Save data table metadata"""
        if not SUPABASE_AVAILABLE:
            return

        try:
            # Check if exists
            existing = self.db.table('user_data_tables').select('id').eq('user_id', user_id).eq('table_name', table_name).execute()

            data = {
                'user_id': user_id,
                'table_name': table_name,
                'ticker': ticker,
                'format': format,
                'row_count': row_count,
                'columns': columns or [],
                'last_accessed': datetime.now().isoformat(),
                'metadata': metadata or {}
            }

            if existing.data:
                # Update
                self.db.table('user_data_tables').update(data).eq('user_id', user_id).eq('table_name', table_name).execute()
            else:
                # Insert
                self.db.table('user_data_tables').insert(data).execute()

        except Exception as e:
            logger.error(f"Error saving data table: {str(e)}")
            raise

    def list_data_tables(self, user_id: str) -> List[Dict]:
        """List all data tables for a user"""
        if not SUPABASE_AVAILABLE:
            return []

        try:
            result = self.db.table('user_data_tables').select('*').eq('user_id', user_id).order('last_accessed', desc=True).execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Error listing data tables: {str(e)}")
            return []

    def get_storage_stats(self, user_id: str) -> Dict:
        """Get storage statistics for a user"""
        if not SUPABASE_AVAILABLE:
            return {'total_files': 0, 'total_size': 0, 'total_tables': 0}

        try:
            # File stats
            files_result = self.db.table('user_files').select('size_bytes').eq('user_id', user_id).execute()
            files = files_result.data or []

            total_files = len(files)
            total_size = sum(f.get('size_bytes', 0) or 0 for f in files)

            # Table stats
            tables_result = self.db.table('user_data_tables').select('id', count='exact').eq('user_id', user_id).execute()
            total_tables = tables_result.count or 0

            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_tables': total_tables
            }

        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {'error': str(e)}

# Global user storage instance
user_storage = UserStorage()
