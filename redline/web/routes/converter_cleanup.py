"""
Cleanup utilities for converter operations.
Handles temporary file and resource cleanup.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import shutil
import atexit
import signal
import sys

converter_cleanup_bp = Blueprint('converter_cleanup', __name__)
logger = logging.getLogger(__name__)

# Global cleanup tracking
_temp_files = set()
_temp_dirs = set()
_active_connections = set()

def cleanup_resources():
    """Clean up all temporary resources."""
    logger.info("Starting cleanup of conversion resources...")
    
    # Clean up temporary files
    for temp_file in list(_temp_files):
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                logger.info(f"Cleaned up temporary file: {temp_file}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {temp_file}: {e}")
        finally:
            _temp_files.discard(temp_file)
    
    # Clean up temporary directories
    for temp_dir in list(_temp_dirs):
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
        finally:
            _temp_dirs.discard(temp_dir)
    
    # Close active database connections
    for conn in list(_active_connections):
        try:
            if hasattr(conn, 'close'):
                conn.close()
                logger.info("Closed database connection")
        except Exception as e:
            logger.warning(f"Failed to close database connection: {e}")
        finally:
            _active_connections.discard(conn)
    
    logger.info("Cleanup completed")

def register_cleanup():
    """Register cleanup functions."""
    atexit.register(cleanup_resources)
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, cleaning up...")
        cleanup_resources()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

# Register cleanup on module load
register_cleanup()

@converter_cleanup_bp.route('/cleanup', methods=['POST'])
def manual_cleanup():
    """Manually trigger cleanup of conversion resources."""
    try:
        cleanup_resources()
        return jsonify({
            'message': 'Cleanup completed successfully',
            'cleaned_files': len(_temp_files),
            'cleaned_dirs': len(_temp_dirs),
            'closed_connections': len(_active_connections)
        })
    except Exception as e:
        logger.error(f"Error during manual cleanup: {str(e)}")
        return jsonify({'error': str(e)}), 500

