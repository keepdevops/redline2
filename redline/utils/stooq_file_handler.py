#!/usr/bin/env python3
"""
Stooq File Handler
Handles downloading, extracting, and organizing Stooq files in REDLINE data directory.
"""

import os
import zipfile
import shutil
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

def get_stooq_data_dir() -> str:
    """Get the Stooq data directory path within REDLINE data directory."""
    base_dir = os.getcwd()
    data_dir = os.path.join(base_dir, 'data', 'stooq')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def extract_zip_file(zip_path: str, extract_to: Optional[str] = None) -> List[str]:
    """
    Extract a ZIP file to the REDLINE data directory.
    
    Args:
        zip_path: Path to the ZIP file
        extract_to: Optional destination directory (defaults to data/stooq)
        
    Returns:
        List of extracted file paths
    """
    try:
        if extract_to is None:
            extract_to = get_stooq_data_dir()
        
        os.makedirs(extract_to, exist_ok=True)
        
        extracted_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of files in the ZIP
            file_list = zip_ref.namelist()
            
            # Extract all files
            zip_ref.extractall(extract_to)
            
            # Move extracted files and get their paths
            for file_name in file_list:
                # Skip directory entries
                if file_name.endswith('/'):
                    continue
                
                extracted_path = os.path.join(extract_to, file_name)
                
                # If file was extracted to a subdirectory, move it to the main stooq directory
                if os.path.dirname(file_name):
                    # Get just the filename
                    filename = os.path.basename(file_name)
                    new_path = os.path.join(extract_to, filename)
                    
                    # Move file if it's in a subdirectory
                    if extracted_path != new_path:
                        if os.path.exists(extracted_path):
                            shutil.move(extracted_path, new_path)
                            extracted_files.append(new_path)
                    else:
                        extracted_files.append(extracted_path)
                else:
                    extracted_files.append(extracted_path)
            
            logger.info(f"Extracted {len(extracted_files)} files from {zip_path} to {extract_to}")
        
        # Clean up the ZIP file after extraction (optional)
        # os.remove(zip_path)
        
        return extracted_files
        
    except zipfile.BadZipFile:
        logger.error(f"Invalid ZIP file: {zip_path}")
        return []
    except Exception as e:
        logger.error(f"Error extracting ZIP file {zip_path}: {str(e)}")
        return []

def move_file_to_stooq_dir(file_path: str, new_filename: Optional[str] = None) -> str:
    """
    Move a downloaded file to the REDLINE data/stooq directory.
    
    Args:
        file_path: Path to the file to move
        new_filename: Optional new filename (defaults to original filename)
        
    Returns:
        New file path in data/stooq directory
    """
    try:
        stooq_dir = get_stooq_data_dir()
        
        if new_filename is None:
            new_filename = os.path.basename(file_path)
        
        new_path = os.path.join(stooq_dir, new_filename)
        
        # Move or copy the file
        if os.path.exists(file_path):
            if file_path != new_path:
                shutil.move(file_path, new_path)
                logger.info(f"Moved {file_path} to {new_path}")
            else:
                logger.info(f"File already in correct location: {new_path}")
        
        return new_path
        
    except Exception as e:
        logger.error(f"Error moving file to Stooq directory: {str(e)}")
        return file_path

def is_stooq_file(filename: str) -> bool:
    """
    Check if a filename looks like a Stooq file.
    
    Stooq files typically have patterns like:
    - data_h.txt, data_d.txt, data_m.txt (hourly, daily, monthly)
    - m_*.txt, d_*.txt, h_*.txt, w_*.txt
    - Files with 'stooq' in the name
    """
    filename_lower = filename.lower()
    
    # Common Stooq file patterns
    stooq_patterns = [
        filename_lower.startswith('data_'),
        filename_lower.startswith('m_'),  # Monthly
        filename_lower.startswith('d_'),  # Daily
        filename_lower.startswith('h_'),  # Hourly
        filename_lower.startswith('w_'),  # Weekly
        'stooq' in filename_lower,
    ]
    
    # Check if it's a text or CSV file with Stooq patterns
    is_text_or_csv = filename_lower.endswith('.txt') or filename_lower.endswith('.csv')
    
    return is_text_or_csv and any(stooq_patterns)

def handle_stooq_download(file_path: str) -> str:
    """
    Handle a downloaded Stooq file - extract if ZIP, move to data directory.
    
    Args:
        file_path: Path to the downloaded file
        
    Returns:
        Path to the file(s) in the data/stooq directory
    """
    try:
        filename = os.path.basename(file_path)
        
        # Check if it's a ZIP file
        if zipfile.is_zipfile(file_path):
            logger.info(f"Detected ZIP file: {file_path}")
            extracted_files = extract_zip_file(file_path)
            
            if extracted_files:
                # Return the first extracted file (or list of files)
                return extracted_files[0] if len(extracted_files) == 1 else extracted_files
            else:
                logger.warning(f"ZIP extraction returned no files: {file_path}")
                return file_path
        else:
            # Just move the file to the data directory
            return move_file_to_stooq_dir(file_path)
            
    except Exception as e:
        logger.error(f"Error handling Stooq download {file_path}: {str(e)}")
        return file_path

