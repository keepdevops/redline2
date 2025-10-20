#!/usr/bin/env python3
"""
REDLINE Data Loading Service
Centralized data loading functionality to eliminate duplication across modules.
"""

import os
import logging
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import glob

from .schema import EXT_TO_FORMAT, REQUIRED_COLUMNS
from .data_validator import DataValidator
from .data_cleaner import DataCleaner
from .format_converter import FormatConverter
from ..utils.logging_mixin import LoggingMixin
from ..utils.error_handling import handle_errors, handle_file_errors

logger = logging.getLogger(__name__)

class DataLoadingService(LoggingMixin):
    """
    Centralized data loading service to eliminate duplication across modules.
    
    This service consolidates all data loading functionality that was previously
    duplicated across 16 different files. Provides consistent behavior,
    error handling, and logging for all data loading operations.
    """
    
    def __init__(self):
        """Initialize the data loading service."""
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
        self.converter = FormatConverter()
        
        # Configuration
        self.max_file_size_mb = 50  # 50MB threshold for chunked loading
        self.chunk_size = 10000     # Rows per chunk for large files
        self.supported_formats = ['csv', 'json', 'parquet', 'feather', 'duckdb', 'txt']
    
    @handle_file_errors(default_return=pd.DataFrame())
    def load_file(self, file_path: str, format_type: Optional[str] = None) -> pd.DataFrame:
        """
        Load a single file with automatic format detection and validation.
        
        Args:
            file_path: Path to the file to load
            format_type: Expected format (auto-detected if None)
            
        Returns:
            Loaded DataFrame or empty DataFrame if loading fails
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return pd.DataFrame()
            
            # Auto-detect format if not specified
            if format_type is None:
                format_type = self.detect_format(file_path)
            
            # Check if this is a large file requiring chunked loading
            file_size = os.path.getsize(file_path)
            is_large_file = file_size > (self.max_file_size_mb * 1024 * 1024)
            
            # Load data based on file size and format
            if is_large_file and format_type in ['csv', 'txt']:
                data = self._load_large_file_chunked(file_path, format_type)
            else:
                data = self.converter.load_file_by_type(file_path, format_type)
            
            # Validate loaded data
            if not data.empty:
                validation_errors = self.validator.validate_data_integrity(data)
                if validation_errors:
                    self.logger.warning(f"Data validation warnings for {file_path}: {validation_errors}")
                
                self.logger.info(f"Successfully loaded {file_path} ({len(data)} rows)")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {str(e)}")
            return pd.DataFrame()
    
    def load_multiple_files(self, file_paths: List[str], 
                           format_type: Optional[str] = None,
                           combine: bool = True) -> Union[List[pd.DataFrame], pd.DataFrame]:
        """
        Load multiple files with optional combination.
        
        Args:
            file_paths: List of file paths to load
            format_type: Expected format for all files (auto-detected if None)
            combine: Whether to combine all DataFrames into one
            
        Returns:
            List of DataFrames or single combined DataFrame
        """
        loaded_data = []
        skipped_files = []
        
        for file_path in file_paths:
            try:
                data = self.load_file(file_path, format_type)
                if not data.empty:
                    loaded_data.append(data)
                else:
                    skipped_files.append(file_path)
                    
            except Exception as e:
                self.logger.error(f"Failed to load {file_path}: {str(e)}")
                skipped_files.append(file_path)
        
        # Log summary
        self.logger.info(f"Loaded {len(loaded_data)} files successfully, skipped {len(skipped_files)} files")
        if skipped_files:
            self.logger.warning(f"Skipped files: {skipped_files}")
        
        if combine and loaded_data:
            try:
                combined_data = pd.concat(loaded_data, ignore_index=True)
                self.logger.info(f"Combined {len(loaded_data)} files into {len(combined_data)} rows")
                return combined_data
            except Exception as e:
                self.logger.error(f"Error combining files: {str(e)}")
                return loaded_data
        
        return loaded_data
    
    def load_directory(self, directory_path: str, 
                      format_type: Optional[str] = None,
                      recursive: bool = False) -> Union[List[pd.DataFrame], pd.DataFrame]:
        """
        Load all files from a directory.
        
        Args:
            directory_path: Path to directory containing files
            format_type: Expected format (auto-detected if None)
            recursive: Whether to search subdirectories
            
        Returns:
            List of DataFrames or single combined DataFrame
        """
        if not os.path.exists(directory_path):
            self.logger.error(f"Directory not found: {directory_path}")
            return pd.DataFrame()
        
        # Find files based on format
        if format_type:
            pattern = f"*.{format_type}"
            if recursive:
                file_paths = glob.glob(os.path.join(directory_path, "**", pattern), recursive=True)
            else:
                file_paths = glob.glob(os.path.join(directory_path, pattern))
        else:
            # Find all supported format files
            patterns = [f"*.{fmt}" for fmt in self.supported_formats]
            file_paths = []
            for pattern in patterns:
                if recursive:
                    file_paths.extend(glob.glob(os.path.join(directory_path, "**", pattern), recursive=True))
                else:
                    file_paths.extend(glob.glob(os.path.join(directory_path, pattern)))
        
        if not file_paths:
            self.logger.warning(f"No files found in directory: {directory_path}")
            return pd.DataFrame()
        
        return self.load_multiple_files(file_paths, format_type, combine=True)
    
    def detect_format(self, file_path: str) -> str:
        """
        Detect file format from file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected format type
        """
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        return EXT_TO_FORMAT.get(ext, 'csv')
    
    def _load_large_file_chunked(self, file_path: str, format_type: str) -> pd.DataFrame:
        """
        Load large files in chunks to prevent memory issues.
        
        Args:
            file_path: Path to the file
            format_type: File format type
            
        Returns:
            Combined DataFrame from all chunks
        """
        self.logger.info(f"Loading large file {file_path} in chunks of {self.chunk_size} rows")
        
        try:
            if format_type == 'csv':
                chunks = []
                for chunk in pd.read_csv(file_path, chunksize=self.chunk_size):
                    chunks.append(chunk)
                    if len(chunks) >= 10:  # Limit memory usage
                        combined = pd.concat(chunks, ignore_index=True)
                        chunks = [combined]
                
                if chunks:
                    return pd.concat(chunks, ignore_index=True)
                else:
                    return pd.DataFrame()
            
            elif format_type == 'txt':
                # For text files, try to detect if it's Stooq format
                try:
                    with open(file_path, 'r') as f:
                        first_line = f.readline().strip()
                    
                    if '<TICKER>' in first_line:
                        # Stooq format - load in chunks
                        chunks = []
                        for chunk in pd.read_csv(file_path, chunksize=self.chunk_size, sep=','):
                            chunks.append(chunk)
                            if len(chunks) >= 10:
                                combined = pd.concat(chunks, ignore_index=True)
                                chunks = [combined]
                        
                        if chunks:
                            return pd.concat(chunks, ignore_index=True)
                        else:
                            return pd.DataFrame()
                    else:
                        # Regular text file
                        return pd.read_csv(file_path, sep='\t')
                except Exception as e:
                    self.logger.error(f"Error loading text file {file_path}: {str(e)}")
                    return pd.DataFrame()
            
            else:
                # For other formats, use regular loading
                return self.converter.load_file_by_type(file_path, format_type)
                
        except Exception as e:
            self.logger.error(f"Error in chunked loading of {file_path}: {str(e)}")
            return pd.DataFrame()
    
    def validate_file_before_loading(self, file_path: str, format_type: str) -> bool:
        """
        Validate file before attempting to load.
        
        Args:
            file_path: Path to the file
            format_type: Expected format
            
        Returns:
            True if file is valid for loading
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File does not exist: {file_path}")
                return False
            
            if not os.path.isfile(file_path):
                self.logger.error(f"Path is not a file: {file_path}")
                return False
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                self.logger.warning(f"File is empty: {file_path}")
                return False
            
            # Use validator to check format
            return self.validator.validate_data(file_path, format_type)
            
        except Exception as e:
            self.logger.error(f"Error validating file {file_path}: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            if not os.path.exists(file_path):
                return {'error': 'File not found'}
            
            stat = os.stat(file_path)
            format_type = self.detect_format(file_path)
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size_bytes': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified_time': stat.st_mtime,
                'format': format_type,
                'is_large_file': stat.st_size > (self.max_file_size_mb * 1024 * 1024),
                'is_valid': self.validate_file_before_loading(file_path, format_type)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return {'error': str(e)}
    
    def load_with_fallback(self, file_path: str, format_type: Optional[str] = None) -> pd.DataFrame:
        """
        Load file with fallback strategies for different formats.
        
        Args:
            file_path: Path to the file
            format_type: Primary format to try
            
        Returns:
            Loaded DataFrame or empty DataFrame if all attempts fail
        """
        # Try primary format first
        if format_type:
            data = self.load_file(file_path, format_type)
            if not data.empty:
                return data
        
        # Try auto-detected format
        detected_format = self.detect_format(file_path)
        if detected_format != format_type:
            data = self.load_file(file_path, detected_format)
            if not data.empty:
                return data
        
        # Try common formats as fallback
        fallback_formats = ['csv', 'json', 'txt']
        for fmt in fallback_formats:
            if fmt != format_type and fmt != detected_format:
                try:
                    data = self.load_file(file_path, fmt)
                    if not data.empty:
                        self.logger.info(f"Successfully loaded {file_path} using fallback format: {fmt}")
                        return data
                except Exception as e:
                    self.logger.debug(f"Fallback format {fmt} failed for {file_path}: {str(e)}")
                    continue
        
        self.logger.error(f"All loading attempts failed for {file_path}")
        return pd.DataFrame()
