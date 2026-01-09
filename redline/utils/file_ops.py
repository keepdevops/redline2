#!/usr/bin/env python3
"""
REDLINE File Operations
Common file I/O operations and utilities.
"""

import logging
import os
import shutil
import glob
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class FileOperations:
    """Handles common file operations for REDLINE."""
    
    def __init__(self):
        """Initialize file operations."""
        self.logger = logging.getLogger(__name__)
    
    def ensure_directory(self, directory_path: str) -> bool:
        """
        Ensure directory exists, create if necessary.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            True if directory exists or was created successfully
        """
        # Pre-validation with if-else
        if not directory_path:
            self.logger.error("Directory path cannot be empty")
            return False
        
        if not isinstance(directory_path, str):
            self.logger.error(f"Directory path must be a string, got {type(directory_path)}")
            return False
        
        # Check if already exists and is a directory
        if os.path.exists(directory_path):
            if os.path.isdir(directory_path):
                self.logger.debug(f"Directory already exists: {directory_path}")
                return True
            else:
                self.logger.error(f"Path exists but is not a directory: {directory_path}")
                return False
        
        # Check if parent directory is writable
        parent_dir = os.path.dirname(directory_path) or '.'
        if os.path.exists(parent_dir) and not os.access(parent_dir, os.W_OK):
            self.logger.error(f"Parent directory is not writable: {parent_dir}")
            return False
        
        try:
            os.makedirs(directory_path, exist_ok=True)
            self.logger.debug(f"Created directory: {directory_path}")
            return True
        except PermissionError as e:
            self.logger.error(f"Permission denied creating directory {directory_path}: {str(e)}")
            return False
        except OSError as e:
            self.logger.error(f"OS error creating directory {directory_path}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating directory {directory_path}: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        # Pre-validation with if-else
        if not file_path:
            self.logger.warning("File path is empty")
            return {'exists': False, 'error': 'File path is empty'}
        
        if not isinstance(file_path, str):
            self.logger.warning(f"File path must be a string, got {type(file_path)}")
            return {'exists': False, 'error': f'File path must be a string, got {type(file_path)}'}
        
        if not os.path.exists(file_path):
            self.logger.debug(f"File does not exist: {file_path}")
            return {'exists': False}
        
        try:
            stat = os.stat(file_path)
            path_obj = Path(file_path)
            
            return {
                'exists': True,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'extension': path_obj.suffix,
                'name': path_obj.name,
                'parent': str(path_obj.parent),
                'is_file': os.path.isfile(file_path),
                'is_directory': os.path.isdir(file_path)
            }
            
        except OSError as e:
            self.logger.error(f"OS error getting file info for {file_path}: {str(e)}")
            return {'exists': False, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error getting file info for {file_path}: {str(e)}")
            return {'exists': False, 'error': str(e)}
    
    def find_files(self, directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
        """
        Find files matching pattern in directory.
        
        Args:
            directory: Directory to search
            pattern: File pattern (e.g., "*.csv", "*.txt")
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        # Pre-validation with if-else
        if not directory:
            self.logger.warning("Directory path is empty")
            return []
        
        if not isinstance(directory, str):
            self.logger.warning(f"Directory must be a string, got {type(directory)}")
            return []
        
        if not os.path.exists(directory):
            self.logger.warning(f"Directory does not exist: {directory}")
            return []
        
        if not os.path.isdir(directory):
            self.logger.warning(f"Path is not a directory: {directory}")
            return []
        
        if not os.access(directory, os.R_OK):
            self.logger.warning(f"Directory is not readable: {directory}")
            return []
        
        try:
            if recursive:
                search_pattern = os.path.join(directory, "**", pattern)
                files = glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(directory, pattern)
                files = glob.glob(search_pattern)
            
            # Filter to only include files (not directories)
            files = [f for f in files if os.path.isfile(f)]
            
            return sorted(files)
            
        except OSError as e:
            self.logger.error(f"OS error finding files in {directory}: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error finding files in {directory}: {str(e)}")
            return []
    
    def copy_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Copy file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if copy was successful
        """
        # Pre-validation with if-else
        if not source:
            self.logger.error("Source path cannot be empty")
            return False
        
        if not destination:
            self.logger.error("Destination path cannot be empty")
            return False
        
        if not isinstance(source, str) or not isinstance(destination, str):
            self.logger.error("Source and destination must be strings")
            return False
        
        if not os.path.exists(source):
            self.logger.error(f"Source file does not exist: {source}")
            return False
        
        if not os.path.isfile(source):
            self.logger.error(f"Source is not a file: {source}")
            return False
        
        if not os.access(source, os.R_OK):
            self.logger.error(f"Source file is not readable: {source}")
            return False
        
        if os.path.exists(destination) and not overwrite:
            self.logger.error(f"Destination file exists and overwrite is False: {destination}")
            return False
        
        # Ensure destination directory exists
        dest_dir = os.path.dirname(destination)
        if dest_dir and not self.ensure_directory(dest_dir):
            return False
        
        try:
            shutil.copy2(source, destination)
            self.logger.info(f"Copied {source} to {destination}")
            return True
            
        except PermissionError as e:
            self.logger.error(f"Permission denied copying {source} to {destination}: {str(e)}")
            return False
        except shutil.SameFileError as e:
            self.logger.error(f"Source and destination are the same file: {str(e)}")
            return False
        except OSError as e:
            self.logger.error(f"OS error copying {source} to {destination}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error copying {source} to {destination}: {str(e)}")
            return False
    
    def move_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Move file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing files
            
        Returns:
            True if move was successful
        """
        # Pre-validation with if-else
        if not source:
            self.logger.error("Source path cannot be empty")
            return False
        
        if not destination:
            self.logger.error("Destination path cannot be empty")
            return False
        
        if not isinstance(source, str) or not isinstance(destination, str):
            self.logger.error("Source and destination must be strings")
            return False
        
        if not os.path.exists(source):
            self.logger.error(f"Source file does not exist: {source}")
            return False
        
        if not os.path.isfile(source):
            self.logger.error(f"Source is not a file: {source}")
            return False
        
        if not os.access(source, os.R_OK):
            self.logger.error(f"Source file is not readable: {source}")
            return False
        
        if os.path.exists(destination) and not overwrite:
            self.logger.error(f"Destination file exists and overwrite is False: {destination}")
            return False
        
        # Ensure destination directory exists
        dest_dir = os.path.dirname(destination)
        if dest_dir and not self.ensure_directory(dest_dir):
            return False
        
        try:
            shutil.move(source, destination)
            self.logger.info(f"Moved {source} to {destination}")
            return True
            
        except PermissionError as e:
            self.logger.error(f"Permission denied moving {source} to {destination}: {str(e)}")
            return False
        except shutil.Error as e:
            self.logger.error(f"Shutil error moving {source} to {destination}: {str(e)}")
            return False
        except OSError as e:
            self.logger.error(f"OS error moving {source} to {destination}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error moving {source} to {destination}: {str(e)}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deletion was successful
        """
        # Pre-validation with if-else
        if not file_path:
            self.logger.error("File path cannot be empty")
            return False
        
        if not isinstance(file_path, str):
            self.logger.error(f"File path must be a string, got {type(file_path)}")
            return False
        
        if not os.path.exists(file_path):
            self.logger.warning(f"File does not exist: {file_path}")
            return True  # Consider it successful if it doesn't exist
        
        if not os.path.isfile(file_path):
            self.logger.error(f"Path is not a file: {file_path}")
            return False
        
        # Check if file is writable (deletable)
        parent_dir = os.path.dirname(file_path) or '.'
        if not os.access(parent_dir, os.W_OK):
            self.logger.error(f"Cannot delete file - parent directory is not writable: {parent_dir}")
            return False
        
        try:
            os.remove(file_path)
            self.logger.info(f"Deleted file: {file_path}")
            return True
            
        except PermissionError as e:
            self.logger.error(f"Permission denied deleting file {file_path}: {str(e)}")
            return False
        except OSError as e:
            self.logger.error(f"OS error deleting file {file_path}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error deleting file {file_path}: {str(e)}")
            return False
    
    def backup_file(self, file_path: str, backup_suffix: str = None) -> Optional[str]:
        """
        Create backup of file.

        Args:
            file_path: Path to file to backup
            backup_suffix: Suffix for backup file

        Returns:
            Path to backup file or None if failed
        """
        # Pre-validation with if-else
        if not file_path:
            self.logger.error("File path cannot be empty")
            return None

        if not isinstance(file_path, str):
            self.logger.error(f"File path must be a string, got {type(file_path)}")
            return None

        if not os.path.exists(file_path):
            self.logger.error(f"File does not exist: {file_path}")
            return None

        if not os.path.isfile(file_path):
            self.logger.error(f"Path is not a file: {file_path}")
            return None

        if not os.access(file_path, os.R_OK):
            self.logger.error(f"File is not readable: {file_path}")
            return None

        if backup_suffix is None:
            from datetime import datetime
            backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')

        if backup_suffix and not isinstance(backup_suffix, str):
            self.logger.error(f"Backup suffix must be a string, got {type(backup_suffix)}")
            return None

        try:
            path_obj = Path(file_path)
            backup_path = f"{path_obj.stem}_{backup_suffix}{path_obj.suffix}"
            backup_full_path = path_obj.parent / backup_path

            if self.copy_file(file_path, str(backup_full_path)):
                self.logger.info(f"Created backup: {backup_full_path}")
                return str(backup_full_path)
            else:
                return None

        except Exception as e:
            self.logger.error(f"Unexpected error creating backup for {file_path}: {str(e)}")
            return None
    
    def get_directory_size(self, directory: str) -> Dict[str, Any]:
        """
        Get total size of directory and file count.

        Args:
            directory: Directory path

        Returns:
            Dictionary with size information
        """
        # Pre-validation with if-else
        if not directory:
            self.logger.warning("Directory path is empty")
            return {'size': 0, 'file_count': 0, 'directory_count': 0, 'error': 'Directory path is empty'}

        if not isinstance(directory, str):
            self.logger.warning(f"Directory must be a string, got {type(directory)}")
            return {'size': 0, 'file_count': 0, 'directory_count': 0, 'error': f'Directory must be a string, got {type(directory)}'}

        if not os.path.exists(directory):
            self.logger.debug(f"Directory does not exist: {directory}")
            return {'size': 0, 'file_count': 0, 'directory_count': 0}

        if not os.path.isdir(directory):
            self.logger.warning(f"Path is not a directory: {directory}")
            return {'size': 0, 'file_count': 0, 'directory_count': 0, 'error': 'Path is not a directory'}

        if not os.access(directory, os.R_OK):
            self.logger.warning(f"Directory is not readable: {directory}")
            return {'size': 0, 'file_count': 0, 'directory_count': 0, 'error': 'Directory is not readable'}

        try:
            total_size = 0
            file_count = 0
            directory_count = 0

            for dirpath, dirnames, filenames in os.walk(directory):
                directory_count += len(dirnames)
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
                        file_count += 1

            return {
                'size': total_size,
                'file_count': file_count,
                'directory_count': directory_count,
                'size_mb': total_size / (1024 * 1024)
            }

        except PermissionError as e:
            self.logger.error(f"Permission denied accessing directory {directory}: {str(e)}")
            return {'size': 0, 'file_count': 0, 'directory_count': 0, 'error': str(e)}
        except OSError as e:
            self.logger.error(f"OS error getting directory size for {directory}: {str(e)}")
            return {'size': 0, 'file_count': 0, 'directory_count': 0, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error getting directory size for {directory}: {str(e)}")
            return {'size': 0, 'file_count': 0, 'directory_count': 0, 'error': str(e)}
    
    def clean_directory(self, directory: str, pattern: str = "*", confirm: bool = False) -> int:
        """
        Clean directory by removing files matching pattern.

        Args:
            directory: Directory to clean
            pattern: File pattern to match
            confirm: Whether user has confirmed deletion

        Returns:
            Number of files deleted
        """
        # Pre-validation with if-else
        if not confirm:
            self.logger.warning("Clean operation requires confirmation")
            return 0

        if not directory:
            self.logger.error("Directory path cannot be empty")
            return 0

        if not isinstance(directory, str):
            self.logger.error(f"Directory must be a string, got {type(directory)}")
            return 0

        if not os.path.exists(directory):
            self.logger.error(f"Directory does not exist: {directory}")
            return 0

        if not os.path.isdir(directory):
            self.logger.error(f"Path is not a directory: {directory}")
            return 0

        if not os.access(directory, os.W_OK):
            self.logger.error(f"Directory is not writable: {directory}")
            return 0

        if not pattern or not isinstance(pattern, str):
            self.logger.warning("Invalid pattern, using default '*'")
            pattern = "*"

        try:
            files_to_delete = self.find_files(directory, pattern)
            deleted_count = 0

            for file_path in files_to_delete:
                if self.delete_file(file_path):
                    deleted_count += 1

            self.logger.info(f"Cleaned {deleted_count} files from {directory}")
            return deleted_count

        except Exception as e:
            self.logger.error(f"Unexpected error cleaning directory {directory}: {str(e)}")
            return 0
    
    def get_file_type(self, file_path: str) -> str:
        """
        Get file type based on extension.

        Args:
            file_path: Path to file

        Returns:
            File type string
        """
        # Pre-validation with if-else
        if not file_path:
            self.logger.warning("File path is empty")
            return 'unknown'

        if not isinstance(file_path, str):
            self.logger.warning(f"File path must be a string, got {type(file_path)}")
            return 'unknown'

        try:
            extension = Path(file_path).suffix.lower()

            type_mapping = {
                '.csv': 'csv',
                '.txt': 'text',
                '.json': 'json',
                '.parquet': 'parquet',
                '.feather': 'feather',
                '.h5': 'hdf5',
                '.hdf5': 'hdf5',
                '.duckdb': 'duckdb',
                '.db': 'database',
                '.sqlite': 'sqlite',
                '.xlsx': 'excel',
                '.xls': 'excel'
            }

            return type_mapping.get(extension, 'unknown')

        except Exception as e:
            self.logger.error(f"Unexpected error getting file type for {file_path}: {str(e)}")
            return 'unknown'
    
    def validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """
        Validate file path and check permissions.

        Args:
            file_path: Path to validate

        Returns:
            Dictionary with validation results
        """
        # Pre-validation with if-else
        if not file_path:
            self.logger.warning("File path is empty")
            return {
                'valid': False,
                'exists': False,
                'readable': False,
                'writable': False,
                'errors': ['File path is empty']
            }

        if not isinstance(file_path, str):
            self.logger.warning(f"File path must be a string, got {type(file_path)}")
            return {
                'valid': False,
                'exists': False,
                'readable': False,
                'writable': False,
                'errors': [f'File path must be a string, got {type(file_path)}']
            }

        try:
            result = {
                'valid': False,
                'exists': False,
                'readable': False,
                'writable': False,
                'errors': []
            }

            # Check if path exists
            result['exists'] = os.path.exists(file_path)

            if result['exists']:
                # Check readability
                result['readable'] = os.access(file_path, os.R_OK)
                if not result['readable']:
                    result['errors'].append("File is not readable")

                # Check writability (for files)
                if os.path.isfile(file_path):
                    result['writable'] = os.access(file_path, os.W_OK)
                    if not result['writable']:
                        result['errors'].append("File is not writable")

                # Check directory writability (for directories)
                elif os.path.isdir(file_path):
                    result['writable'] = os.access(file_path, os.W_OK)
                    if not result['writable']:
                        result['errors'].append("Directory is not writable")

                result['valid'] = len(result['errors']) == 0
            else:
                # Check if parent directory is writable for new files
                parent_dir = os.path.dirname(file_path)
                if parent_dir and os.path.exists(parent_dir):
                    result['writable'] = os.access(parent_dir, os.W_OK)
                    if result['writable']:
                        result['valid'] = True
                    else:
                        result['errors'].append("Parent directory is not writable")
                else:
                    result['errors'].append("Parent directory does not exist")

            return result

        except OSError as e:
            self.logger.error(f"OS error validating file path {file_path}: {str(e)}")
            return {
                'valid': False,
                'exists': False,
                'readable': False,
                'writable': False,
                'errors': [str(e)]
            }
        except Exception as e:
            self.logger.error(f"Unexpected error validating file path {file_path}: {str(e)}")
            return {
                'valid': False,
                'exists': False,
                'readable': False,
                'writable': False,
                'errors': [str(e)]
            }
