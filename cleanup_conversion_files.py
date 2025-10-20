#!/usr/bin/env python3
"""
REDLINE Conversion Cleanup Script
Cleans up temporary files and leftover conversion artifacts
"""

import os
import shutil
import glob
import logging
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_temp_files():
    """Clean up temporary files from conversion processes."""
    logger.info("Cleaning up temporary files...")
    
    # Common temporary file patterns
    temp_patterns = [
        '*.tmp',
        '*.temp',
        'temp_*',
        '*_temp.*',
        '*.lock',
        '*.pid',
        '.DS_Store',
        'Thumbs.db'
    ]
    
    data_dir = Path('data')
    converted_dir = data_dir / 'converted'
    
    cleaned_files = 0
    
    # Clean up in data directory
    if data_dir.exists():
        for pattern in temp_patterns:
            for temp_file in data_dir.glob(pattern):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                        logger.info(f"Removed temporary file: {temp_file}")
                        cleaned_files += 1
                except Exception as e:
                    logger.warning(f"Failed to remove {temp_file}: {e}")
    
    # Clean up in converted directory
    if converted_dir.exists():
        for pattern in temp_patterns:
            for temp_file in converted_dir.glob(pattern):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                        logger.info(f"Removed temporary file: {temp_file}")
                        cleaned_files += 1
                except Exception as e:
                    logger.warning(f"Failed to remove {temp_file}: {e}")
    
    logger.info(f"Cleaned up {cleaned_files} temporary files")
    return cleaned_files

def cleanup_incomplete_conversions():
    """Clean up incomplete conversion files."""
    logger.info("Cleaning up incomplete conversion files...")
    
    converted_dir = Path('data') / 'converted'
    cleaned_files = 0
    
    if converted_dir.exists():
        # Look for files that might be incomplete (0 bytes or very small)
        for file_path in converted_dir.iterdir():
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    # Remove files that are 0 bytes or incorrect extensions
                    if file_size == 0:
                        file_path.unlink()
                        logger.info(f"Removed incomplete file: {file_path}")
                        cleaned_files += 1
                    elif file_path.suffix in ['.tmp', '.temp', '.lock']:
                        file_path.unlink()
                        logger.info(f"Removed temporary file: {file_path}")
                        cleaned_files += 1
                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {e}")
    
    logger.info(f"Cleaned up {cleaned_files} incomplete conversion files")
    return cleaned_files

def cleanup_old_conversions(days_old=7):
    """Clean up old conversion files."""
    logger.info(f"Cleaning up conversion files older than {days_old} days...")
    
    import time
    cutoff_time = time.time() - (days_old * 24 * 60 * 60)
    cleaned_files = 0
    
    converted_dir = Path('data') / 'converted'
    
    if converted_dir.exists():
        for file_path in converted_dir.iterdir():
            if file_path.is_file():
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        logger.info(f"Removed old file: {file_path}")
                        cleaned_files += 1
                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {e}")
    
    logger.info(f"Cleaned up {cleaned_files} old conversion files")
    return cleaned_files

def cleanup_database_locks():
    """Clean up database lock files."""
    logger.info("Cleaning up database lock files...")
    
    lock_patterns = [
        '*.duckdb.wal',
        '*.duckdb.lock',
        '*.db.lock',
        '*.sqlite.lock'
    ]
    
    data_dir = Path('data')
    cleaned_files = 0
    
    for pattern in lock_patterns:
        for lock_file in data_dir.glob(pattern):
            try:
                if lock_file.is_file():
                    lock_file.unlink()
                    logger.info(f"Removed database lock: {lock_file}")
                    cleaned_files += 1
            except Exception as e:
                logger.warning(f"Failed to remove {lock_file}: {e}")
    
    logger.info(f"Cleaned up {cleaned_files} database lock files")
    return cleaned_files

def cleanup_empty_directories():
    """Clean up empty directories."""
    logger.info("Cleaning up empty directories...")
    
    data_dir = Path('data')
    cleaned_dirs = 0
    
    if data_dir.exists():
        # Walk through directories bottom-up to remove empty ones
        for dir_path in sorted(data_dir.rglob('*'), reverse=True):
            if dir_path.is_dir() and dir_path != data_dir:
                try:
                    if not any(dir_path.iterdir()):  # Directory is empty
                        dir_path.rmdir()
                        logger.info(f"Removed empty directory: {dir_path}")
                        cleaned_dirs += 1
                except Exception as e:
                    logger.warning(f"Failed to remove {dir_path}: {e}")
    
    logger.info(f"Cleaned up {cleaned_dirs} empty directories")
    return cleaned_dirs

def main():
    parser = argparse.ArgumentParser(description='Clean up REDLINE conversion files')
    parser.add_argument('--days', type=int, default=7, 
                       help='Remove conversion files older than this many days (default: 7)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be cleaned without actually cleaning')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No files will be deleted")
    
    logger.info("Starting REDLINE conversion cleanup...")
    
    total_cleaned = 0
    
    if not args.dry_run:
        total_cleaned += cleanup_temp_files()
        total_cleaned += cleanup_incomplete_conversions()
        total_cleaned += cleanup_old_conversions(args.days)
        total_cleaned += cleanup_database_locks()
        total_cleaned += cleanup_empty_directories()
    else:
        logger.info("Dry run mode - would clean up files but not actually deleting them")
    
    logger.info(f"Cleanup completed. Total files/directories cleaned: {total_cleaned}")

if __name__ == '__main__':
    main()
