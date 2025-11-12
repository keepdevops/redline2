#!/usr/bin/env python3
"""
Utility script to move Stooq files from downloads directory to data/stooq directory.
Can also move files from user's Downloads folder if specified.
Run this to organize existing Stooq downloads.
"""

import os
import shutil
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def move_stooq_files_from_downloads(download_dir=None):
    """
    Move Stooq files from downloads directory to data/stooq directory.
    
    Args:
        download_dir: Optional directory to search (defaults to data/downloaded)
    """
    try:
        base_dir = os.getcwd()
        
        if download_dir is None:
            download_dir = os.path.join(base_dir, 'data', 'downloaded')
        else:
            # Expand user home directory if using ~
            download_dir = os.path.expanduser(download_dir)
        
        stooq_dir = os.path.join(base_dir, 'data', 'stooq')
        
        # Ensure stooq directory exists
        os.makedirs(stooq_dir, exist_ok=True)
        
        if not os.path.exists(download_dir):
            logger.info(f"No directory found at {download_dir}")
            return []
        
        moved_files = []
        
        # Find files that look like Stooq files
        for filename in os.listdir(download_dir):
            file_path = os.path.join(download_dir, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Check if it's a Stooq file
            # Stooq files are often named like: data_h.txt, m_*.txt, d_*.txt, etc.
            is_stooq_file = (
                'stooq' in filename.lower() or
                filename.lower().endswith('.txt') or
                (filename.lower().endswith('.csv') and ('stooq' in filename.lower() or any(pattern in filename.lower() for pattern in ['data_', 'm_', 'd_', 'h_', 'w_']))) or
                filename.startswith('data_') or
                filename.startswith('m_') or
                filename.startswith('d_') or
                filename.startswith('h_') or
                filename.startswith('w_')
            )
            
            if is_stooq_file:
                dest_path = os.path.join(stooq_dir, filename)
                
                # Avoid overwriting existing files
                if os.path.exists(dest_path):
                    logger.warning(f"File already exists in stooq directory: {filename}")
                    # Optionally add timestamp or increment
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(stooq_dir, new_filename)
                        counter += 1
                    logger.info(f"Renaming to: {os.path.basename(dest_path)}")
                
                shutil.move(file_path, dest_path)
                moved_files.append(dest_path)
                logger.info(f"Moved {filename} to {stooq_dir}")
        
        logger.info(f"Moved {len(moved_files)} Stooq file(s) to {stooq_dir}")
        return moved_files
        
    except PermissionError as e:
        logger.error(f"Permission denied accessing {download_dir}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error moving Stooq files: {str(e)}")
        return []

if __name__ == '__main__':
    # Check for command line argument (Downloads directory path)
    download_source = None
    if len(sys.argv) > 1:
        download_source = sys.argv[1]
    
    print("Moving Stooq files to data/stooq...")
    
    # First check data/downloaded
    print("\n1. Checking data/downloaded...")
    moved1 = move_stooq_files_from_downloads()
    
    # Then check user's Downloads folder if specified
    if download_source:
        print(f"\n2. Checking {download_source}...")
        moved2 = move_stooq_files_from_downloads(download_source)
        moved = moved1 + moved2
    else:
        moved = moved1
    
    print(f"\n✅ Moved {len(moved)} file(s) total")
    for file in moved:
        print(f"  - {file}")
