#!/usr/bin/env python3
"""
Simple file watcher that runs inside Docker container.
Uses polling instead of watchdog (no extra dependencies needed).
Monitors mounted Downloads folder and automatically copies files to data/stooq.
"""

import os
import sys
import time
import shutil
import logging
from pathlib import Path

# Configure logging - use a more robust setup
import sys

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove any existing handlers to avoid conflicts
logger.handlers.clear()

# File handler
try:
    file_handler = logging.FileHandler('/app/logs/file_watcher.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
except Exception as e:
    # If file handler fails, continue with just console
    print(f"Warning: Could not create file handler: {e}")

# Console handler (only if not in background)
try:
    if sys.stdout and sys.stdout.isatty():
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)
except Exception:
    # Ignore console handler errors
    pass

# Configuration
DOWNLOADS_DIR = Path('/app/data/downloads')
STOOQ_DIR = Path('/app/data/stooq')
COPIED_LOG = Path('/app/data/.copied_files.log')
POLL_INTERVAL = 5  # Check every 5 seconds

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
        
        # Skip if already copied (tracked in log)
        if filename in copied_files:
            return False
        
        # Check if destination already exists FIRST
        dest_path = STOOQ_DIR / filename
        if dest_path.exists():
            # Try to check if we can write to it
            try:
                # Try to remove existing file first
                dest_path.unlink()
            except (PermissionError, OSError) as e:
                # Can't remove - file exists with different permissions
                # Mark as copied to avoid repeated attempts
                mark_as_copied(filename)
                return False
        
        # Wait for file to complete
        if not wait_for_file_complete(filepath):
            logger.warning(f"File {filename} may still be downloading")
        
        # Copy file
        shutil.copy2(filepath, dest_path)
        
        # Ensure correct ownership (best effort)
        try:
            os.chown(dest_path, os.getuid(), os.getgid())
        except Exception:
            pass  # Ignore if chown fails
        
        # Mark as copied
        mark_as_copied(filename)
        
        logger.info(f"✅ Copied {filename} to {dest_path}")
        return True
        
    except PermissionError as e:
        # Permission error - file likely exists with wrong ownership
        # Mark to avoid repeated errors
        mark_as_copied(filepath.name)
        return False
    except Exception as e:
        logger.error(f"Error copying {filepath}: {e}")
        return False

def scan_and_copy():
    """Scan Downloads folder for new files and copy them."""
    if not DOWNLOADS_DIR.exists():
        return
    
    copied_count = 0
    for filepath in DOWNLOADS_DIR.iterdir():
        if filepath.is_file() and is_data_file(filepath.name):
            filename = filepath.name
            # Skip if already in copied_files set
            if filename in copied_files:
                continue
            
            # Check if file exists in stooq - if so, handle it
            dest_path = STOOQ_DIR / filename
            if dest_path.exists():
                # Try to remove it, if we can't, mark as copied and skip
                try:
                    dest_path.unlink()
                    # Successfully removed, can proceed with copy
                except Exception as e:
                    # Can't remove - file exists with different permissions
                    # Mark as copied to avoid repeated attempts (catch ALL exceptions)
                    if filename not in copied_files:
                        mark_as_copied(filename)
                    continue  # Skip this file entirely
            
            # File doesn't exist in stooq OR was successfully removed
            # Now try to copy
            if copy_file_to_stooq(filepath):
                copied_count += 1
    
    return copied_count

def main():
    """Main function to start file watcher."""
    logger.info("=" * 70)
    logger.info("FILE WATCHER - AUTO-COPY FROM DOWNLOADS (Simple Mode)")
    logger.info("=" * 70)
    logger.info(f"Watching: {DOWNLOADS_DIR}")
    logger.info(f"Copying to: {STOOQ_DIR}")
    logger.info(f"Poll interval: {POLL_INTERVAL} seconds")
    logger.info("")
    
    # Load previously copied files
    load_copied_files()
    
    # Check if Downloads directory is mounted
    if not DOWNLOADS_DIR.exists():
        logger.error(f"Downloads directory not mounted: {DOWNLOADS_DIR}")
        logger.error("Make sure docker-compose-dev.yml has Downloads folder mounted")
        sys.exit(1)
    
    # Scan existing files first
    logger.info("Scanning Downloads folder for existing files...")
    copied = scan_and_copy()
    if copied > 0:
        logger.info(f"Copied {copied} existing file(s)")
    else:
        logger.info("No new files to copy")
    
    logger.info("✅ File watcher started - monitoring for new files...")
    logger.info(f"Checking every {POLL_INTERVAL} seconds")
    logger.info("Press Ctrl+C to stop")
    logger.info("")
    
    try:
        while True:
            scan_and_copy()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Stopping file watcher...")
    except Exception as e:
        logger.error(f"Error in file watcher: {e}")
        sys.exit(1)
    
    logger.info("File watcher stopped")

if __name__ == '__main__':
    main()

