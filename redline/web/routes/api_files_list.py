"""
API file listing routes for REDLINE Web GUI
Handles file listing and metadata
"""

from flask import Blueprint, jsonify
import logging
import os
from ..utils.api_helpers import rate_limit

api_files_list_bp = Blueprint('api_files_list', __name__)
logger = logging.getLogger(__name__)

# System files to exclude from user-facing file lists
SYSTEM_FILES = {
    'usage_data.duckdb',
    'redline_data.duckdb',
    # These files are now in ~/.redline/ and should not be listed
    # 'api_keys.json',
    # 'custom_apis.json',
    # 'licenses.json',
    'data_config.ini',
    'config.ini'
}

@api_files_list_bp.route('/files')
@rate_limit("200 per hour")  # More generous limit for file listing (read-only operation)
def api_list_files():
    """List available data files via API."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # Get files from main data directory
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                # Skip system files
                if filename in SYSTEM_FILES:
                    continue
                file_path = os.path.join(data_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path
                    })
        
        # Get files from downloaded directory
        downloaded_dir = os.path.join(data_dir, 'downloaded')
        if os.path.exists(downloaded_dir):
            for filename in os.listdir(downloaded_dir):
                # Skip system files
                if filename in SYSTEM_FILES:
                    continue
                file_path = os.path.join(downloaded_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path,
                        'location': 'downloaded'
                    })

        # Get files from converted/export directory (recursively including subdirectories)
        converted_dir = os.path.join(data_dir, 'converted')
        if os.path.exists(converted_dir):
            # Recursively search subdirectories in converted/ (duckdb/, parquet/, etc.)
            for root, dirs, filenames in os.walk(converted_dir):
                for filename in filenames:
                    # Skip system files
                    if filename in SYSTEM_FILES:
                        continue
                    if not filename.startswith('.'):
                        file_path = os.path.join(root, filename)
                        if os.path.isfile(file_path):
                            file_stat = os.stat(file_path)
                            # Get relative path for location
                            rel_path = os.path.relpath(file_path, data_dir)
                            files.append({
                                'name': filename,
                                'size': file_stat.st_size,
                                'modified': file_stat.st_mtime,
                                'path': file_path,
                                'location': rel_path
                            })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_files_list_bp.route('/files', methods=['GET'])
def list_files():
    """List available data files."""
    try:
        from ..utils.api_helpers import allowed_file
        
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        for filename in os.listdir(data_dir):
            if allowed_file(filename):
                file_path = os.path.join(data_dir, filename)
                file_stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime
                })
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

