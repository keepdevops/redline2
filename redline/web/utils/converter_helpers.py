"""
Helper utilities for converter operations.
"""

import os
import shutil
import logging
import pandas as pd
from typing import List, Dict, Optional, Union

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

