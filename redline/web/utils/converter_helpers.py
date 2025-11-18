"""
Helper utilities for converter operations.
"""

import os
import shutil
import logging

logger = logging.getLogger(__name__)

def find_input_file_path(input_file, data_dir=None):
    """
    Find the input file path, handling both absolute and relative paths.
    
    Args:
        input_file: File path (absolute or relative)
        data_dir: Base data directory (defaults to cwd/data)
    
    Returns:
        Absolute path to the input file, or None if not found
    """
    if data_dir is None:
        data_dir = os.path.join(os.getcwd(), 'data')
    
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
        'txt': '.txt'
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

