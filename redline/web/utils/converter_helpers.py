"""
Helper utilities for converter operations.
"""

import os
import shutil
import logging
import pandas as pd
from typing import List, Dict, Optional, Union, Tuple

logger = logging.getLogger(__name__)

# System files to exclude from conversion operations
SYSTEM_FILES = {
    'usage_data.duckdb',
    'redline_data.duckdb',
    'data_config.ini',
    'config.ini',
    'api_keys.json',      # API keys configuration (sensitive)
    'custom_apis.json',    # Custom API configurations (sensitive)
    'licenses.json'        # License information (sensitive)
}

def is_system_file(filename: str) -> bool:
    """
    Check if a filename is a system file that should be excluded.
    
    Args:
        filename: Name of the file to check
    
    Returns:
        True if the file is a system file, False otherwise
    """
    return filename in SYSTEM_FILES

def find_input_file_path(input_file, data_dir=None):
    """
    Find the input file path, handling both absolute and relative paths.
    
    Args:
        input_file: File path (absolute or relative)
        data_dir: Base data directory (defaults to cwd/data)
    
    Returns:
        Absolute path to the input file, or None if not found or is a system file
    """
    if data_dir is None:
        data_dir = os.path.join(os.getcwd(), 'data')
    
    # Check if this is a system file
    filename = os.path.basename(input_file)
    if is_system_file(filename):
        logger.warning(f"Attempted to access system file: {filename}")
        return None
    
    input_path = None
    
    # Check if input_file is an absolute path (from file browser)
    if os.path.isabs(input_file) and os.path.exists(input_file):
        # Copy file to data/downloaded/ directory
        downloaded_dir = os.path.join(data_dir, 'downloaded')
        os.makedirs(downloaded_dir, exist_ok=True)
        
        dest_filename = os.path.basename(input_file)
        dest_path = os.path.join(downloaded_dir, dest_filename)
        
        # Copy file (using shutil.copy2 to preserve metadata)
        shutil.copy2(input_file, dest_path)
        logger.info(f"Copied {input_file} to {dest_path}")
        
        input_path = dest_path
    else:
        # Existing logic for relative paths
        # Check in root data directory first
        root_path = os.path.join(data_dir, input_file)
        if os.path.exists(root_path):
            input_path = root_path
        else:
            # Check in downloaded directory
            downloaded_path = os.path.join(data_dir, 'downloaded', input_file)
            if os.path.exists(downloaded_path):
                input_path = downloaded_path
            else:
                # Check in stooq directory (for Stooq downloads)
                stooq_path = os.path.join(data_dir, 'stooq', input_file)
                if os.path.exists(stooq_path):
                    input_path = stooq_path
    
    return input_path

def adjust_output_filename(output_filename, output_format):
    """
    Ensure output filename has the correct extension for the output format.
    
    Args:
        output_filename: Original filename
        output_format: Target format (csv, json, parquet, etc.)
    
    Returns:
        Adjusted filename with correct extension
    """
    format_extensions = {
        'csv': '.csv',
        'json': '.json',
        'parquet': '.parquet',
        'feather': '.feather',
        'duckdb': '.duckdb',
        'txt': '.txt',
        'tensorflow': '.npz',
        'npz': '.npz',
        'keras': '.h5',
        'h5': '.h5',
        'pyarrow': '.arrow',
        'arrow': '.arrow'
    }
    
    # Get the expected extension for the output format
    expected_ext = format_extensions.get(output_format, '')
    
    # Check if filename already has an extension
    output_base, output_ext = os.path.splitext(output_filename)
    
    # If the extension doesn't match the expected format, add/change it
    if output_ext != expected_ext and expected_ext:
        output_filename = output_base + expected_ext
        logger.info(f"Adjusted output filename to: {output_filename}")
    
    return output_filename

def align_columns_for_merge(dataframes: List[pd.DataFrame], 
                             preferred_order: Optional[List[str]] = None) -> List[str]:
    """
    Get union of all columns from multiple DataFrames, with optional preferred order.
    
    Args:
        dataframes: List of DataFrames to merge
        preferred_order: Optional list of column names in desired order
    
    Returns:
        List of all unique column names in preferred order (if provided), 
        otherwise preserving order from first file, with additional columns appended
    """
    if not dataframes:
        return []
    
    # Get all unique columns across all DataFrames
    all_columns_set = set()
    for df in dataframes:
        if isinstance(df, pd.DataFrame):
            all_columns_set.update(df.columns)
    
    if preferred_order:
        # Use preferred order, add missing columns at end
        ordered = [col for col in preferred_order if col in all_columns_set]
        remaining = sorted([col for col in all_columns_set if col not in preferred_order])
        return ordered + remaining
    else:
        # Default: preserve order from first file
        first_df = dataframes[0]
        if not isinstance(first_df, pd.DataFrame):
            return []
        
        ordered_columns = list(first_df.columns)
        all_columns_set = set(ordered_columns)
        
        # Add any additional columns from other DataFrames
        for df in dataframes[1:]:
            if isinstance(df, pd.DataFrame):
                for col in df.columns:
                    if col not in all_columns_set:
                        ordered_columns.append(col)
                        all_columns_set.add(col)
        
        return ordered_columns

def apply_column_mappings(df: pd.DataFrame, column_mappings: Dict[str, str]) -> pd.DataFrame:
    """
    Apply column name mappings to a DataFrame.
    
    Args:
        df: DataFrame to rename columns
        column_mappings: Dictionary mapping old column names to new names
    
    Returns:
        DataFrame with renamed columns
    """
    if not column_mappings:
        return df
    
    # Only rename columns that exist in the DataFrame
    rename_map = {old: new for old, new in column_mappings.items() if old in df.columns}
    if rename_map:
        df = df.rename(columns=rename_map)
        logger.info(f"Renamed columns: {rename_map}")
    
    return df

def merge_dataframes(dataframes: List[pd.DataFrame], 
                     column_mappings: Optional[Dict[str, str]] = None,
                     column_order: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Merge multiple DataFrames into one, handling column alignment and mappings.
    
    Args:
        dataframes: List of DataFrames to merge
        column_mappings: Optional dictionary mapping old column names to new names
        column_order: Optional list of column names in desired order
    
    Returns:
        Combined DataFrame
    """
    if not dataframes:
        return pd.DataFrame()
    
    # Apply column mappings if provided
    if column_mappings:
        dataframes = [apply_column_mappings(df.copy(), column_mappings) for df in dataframes]
    
    # Get all unique columns (with preferred order if provided)
    all_columns = align_columns_for_merge(dataframes, preferred_order=column_order)
    
    # Align all DataFrames to have the same columns
    aligned_dfs = []
    for df in dataframes:
        if isinstance(df, pd.DataFrame):
            # Add missing columns with NaN values
            for col in all_columns:
                if col not in df.columns:
                    df[col] = None
            # Reorder columns to match
            df = df[all_columns]
            aligned_dfs.append(df)
    
    # Concatenate all DataFrames
    if aligned_dfs:
        merged_df = pd.concat(aligned_dfs, ignore_index=True)
        logger.info(f"Merged {len(dataframes)} files into {len(merged_df)} rows with {len(all_columns)} columns")
        return merged_df
    
    return pd.DataFrame()

def validate_file_before_conversion(file_path: str, expected_format: str = None) -> Tuple[bool, Optional[str], Dict[str, any]]:
    """
    Comprehensive file validation before conversion attempt.
    
    Args:
        file_path: Path to the file to validate
        expected_format: Expected file format (csv, parquet, etc.) for additional checks
    
    Returns:
        Tuple of (is_valid, error_message, validation_details)
        validation_details contains: file_size, is_readable, encoding_info, format_match, etc.
    """
    validation_details = {
        'file_path': file_path,
        'file_exists': False,
        'file_size': 0,
        'is_readable': False,
        'is_empty': False,
        'encoding': None,
        'format_match': None,
        'error_details': []
    }
    
    # Check 1: File exists
    if not os.path.exists(file_path):
        return False, f"File does not exist: {file_path}", validation_details
    
    validation_details['file_exists'] = True
    
    # Check 2: Is a file (not directory)
    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}", validation_details
    
    # Check 3: File size
    try:
        file_size = os.path.getsize(file_path)
        validation_details['file_size'] = file_size
        
        if file_size == 0:
            validation_details['is_empty'] = True
            return False, f"File is empty (0 bytes): {file_path}", validation_details
        
        # Warn about very large files (>1GB)
        if file_size > 1024 * 1024 * 1024:  # 1GB
            validation_details['error_details'].append(f"File is very large ({file_size / (1024**3):.2f} GB)")
    except OSError as e:
        return False, f"Cannot access file size: {str(e)}", validation_details
    
    # Check 4: File is readable
    try:
        with open(file_path, 'rb') as f:
            f.read(1)  # Try to read at least 1 byte
        validation_details['is_readable'] = True
    except PermissionError:
        return False, f"Permission denied: Cannot read file {file_path}", validation_details
    except Exception as e:
        return False, f"Cannot read file: {str(e)}", validation_details
    
    # Check 5: Encoding detection (for text files)
    if expected_format in ['csv', 'txt', 'json']:
        try:
            # Try common encodings
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
            encoding_found = None
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read(1024)  # Read first 1KB to test encoding
                    encoding_found = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if encoding_found:
                validation_details['encoding'] = encoding_found
            else:
                validation_details['error_details'].append("Could not detect valid text encoding")
        except Exception as e:
            validation_details['error_details'].append(f"Encoding check failed: {str(e)}")
    
    # Check 6: Format match (check file extension matches expected format)
    if expected_format:
        ext = os.path.splitext(file_path)[1].lower()
        format_extensions = {
            'csv': ['.csv'],
            'txt': ['.txt'],
            'json': ['.json'],
            'parquet': ['.parquet'],
            'feather': ['.feather'],
            'duckdb': ['.duckdb']
        }
        
        expected_exts = format_extensions.get(expected_format, [])
        if expected_exts and ext not in expected_exts:
            validation_details['format_match'] = False
            validation_details['error_details'].append(
                f"File extension ({ext}) does not match expected format ({expected_format})"
            )
        else:
            validation_details['format_match'] = True
    
    # Check 7: Quick content check for text files (check if file has actual content beyond whitespace)
    if expected_format in ['csv', 'txt', 'json']:
        try:
            with open(file_path, 'r', encoding=validation_details.get('encoding', 'utf-8'), errors='ignore') as f:
                first_chunk = f.read(1024)
                if not first_chunk.strip():
                    validation_details['is_empty'] = True
                    return False, f"File appears to contain only whitespace: {file_path}", validation_details
        except Exception as e:
            validation_details['error_details'].append(f"Content check failed: {str(e)}")
    
    # All checks passed
    if validation_details['error_details']:
        # Has warnings but not critical errors
        return True, None, validation_details
    
    return True, None, validation_details

