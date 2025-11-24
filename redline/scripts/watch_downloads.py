#!/usr/bin/env python3
"""
File watcher that runs inside Docker container.
Monitors mounted Downloads folder and automatically copies files to data/stooq.
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/file_watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DOWNLOADS_DIR = Path('/app/data/downloads')
STOOQ_DIR = Path('/app/data/stooq')
COPIED_LOG = Path('/app/data/.copied_files.log')

# Ensure directories exist
STOOQ_DIR.mkdir(parents=True, exist_ok=True)
COPIED_LOG.touch(exist_ok=True)

# Track copied files
copied_files = set()

def load_copied_files():
    """Load list of already copied files."""
    global copied_files
    if COPIED_LOG.exists():
        try:
            with open(COPIED_LOG, 'r') as f:
                copied_files = set(line.strip() for line in f if line.strip())
            logger.info(f"Loaded {len(copied_files)} previously copied files")
        except Exception as e:
            logger.warning(f"Error loading copied files log: {e}")

def mark_as_copied(filename):
    """Mark file as copied."""
    global copied_files
    copied_files.add(filename)
    try:
        with open(COPIED_LOG, 'a') as f:
            f.write(f"{filename}\n")
    except Exception as e:
        logger.warning(f"Error writing to copied log: {e}")

def is_data_file(filename):
    """Check if file is a data file (CSV, TXT, ZIP)."""
    return filename.lower().endswith(('.csv', '.txt', '.zip'))

def wait_for_file_complete(filepath, max_wait=30):
    """Wait for file to finish downloading (size stabilizes)."""
    if not filepath.exists():
        return False
    
    prev_size = -1
    stable_count = 0
    wait_time = 0
    
    while wait_time < max_wait:
        try:
            current_size = filepath.stat().st_size
            if current_size == prev_size:
                stable_count += 1
                if stable_count >= 3:  # Stable for 3 checks
                    return True
            else:
                stable_count = 0
            prev_size = current_size
            time.sleep(1)
            wait_time += 1
        except Exception:
            return False
    
    return True

def copy_file_to_stooq(filepath):
    """Copy file from Downloads to stooq directory."""
    try:
        filename = filepath.name
        
        # Skip if already copied
        if filename in copied_files:
            logger.debug(f"Skipping already copied: {filename}")
            return False
        
        # Wait for file to complete
        logger.info(f"Waiting for {filename} to complete...")
        if not wait_for_file_complete(filepath):
            logger.warning(f"File {filename} may still be downloading")
        
        # Copy file
        dest_path = STOOQ_DIR / filename
        shutil.copy2(filepath, dest_path)
        
        # Mark as copied
        mark_as_copied(filename)
        
        logger.info(f"✅ Copied {filename} to {dest_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error copying {filepath}: {e}")
        return False

class DownloadsHandler(FileSystemEventHandler):
    """Handler for file system events in Downloads folder."""
    
    def on_created(self, event):
        """Handle file creation."""
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        if is_data_file(filepath.name):
            logger.info(f"New file detected: {filepath.name}")
            # Small delay to ensure file is writable
            time.sleep(1)
            copy_file_to_stooq(filepath)
    
    def on_modified(self, event):
        """Handle file modification (for files still downloading)."""
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        if is_data_file(filepath.name) and filepath.name not in copied_files:
            # File might still be downloading, will be handled by on_created
            pass

def scan_existing_files():
    """Scan Downloads folder for existing files and copy them."""
    logger.info("Scanning Downloads folder for existing files...")
    
    if not DOWNLOADS_DIR.exists():
        logger.warning(f"Downloads directory not found: {DOWNLOADS_DIR}")
        return
    
    copied_count = 0
    for filepath in DOWNLOADS_DIR.iterdir():
        if filepath.is_file() and is_data_file(filepath.name):
            if filepath.name not in copied_files:
                if copy_file_to_stooq(filepath):
                    copied_count += 1
    
    if copied_count > 0:
        logger.info(f"Copied {copied_count} existing file(s)")
    else:
        logger.info("No new files to copy")

def main():
    """Main function to start file watcher."""
    logger.info("=" * 70)
    logger.info("FILE WATCHER - AUTO-COPY FROM DOWNLOADS")
    logger.info("=" * 70)
    logger.info(f"Watching: {DOWNLOADS_DIR}")
    logger.info(f"Copying to: {STOOQ_DIR}")
    logger.info("")
    
    # Load previously copied files
    load_copied_files()
    
    # Check if Downloads directory is mounted
    if not DOWNLOADS_DIR.exists():
        logger.error(f"Downloads directory not mounted: {DOWNLOADS_DIR}")
        logger.error("Make sure docker-compose-dev.yml has Downloads folder mounted")
        sys.exit(1)
    
    # Scan existing files first
    scan_existing_files()
    
    # Set up file watcher
    event_handler = DownloadsHandler()
    observer = Observer()
    observer.schedule(event_handler, str(DOWNLOADS_DIR), recursive=False)
    observer.start()
    
    logger.info("✅ File watcher started - monitoring for new files...")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping file watcher...")
        observer.stop()
    
    observer.join()
    logger.info("File watcher stopped")

if __name__ == '__main__':
    main()

