"""
File listing routes for converter operations.
Handles listing available files and converted files.
"""

from flask import Blueprint, jsonify
import logging
import os

converter_browsing_list_bp = Blueprint('converter_browsing_list', __name__)
logger = logging.getLogger(__name__)

# System files to exclude from user-facing file lists
SYSTEM_FILES = {
    'usage_data.duckdb',
    'redline_data.duckdb',
    'data_config.ini',
    'config.ini',
    'api_keys.json',      # API keys configuration (sensitive)
    'custom_apis.json',    # Custom API configurations (sensitive)
    'licenses.json'        # License information (sensitive)
}

@converter_browsing_list_bp.route('/files')
def list_available_files():
    """List files available for conversion. Matches /api/files endpoint format."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # Get files from main data directory (no extension filter - match data view)
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
                        'path': file_path,
                        'storage': 'local',
                        'location': 'root'
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
                        'storage': 'local',
                        'location': 'downloaded'
                    })
        
        # Get files from uploads directory
        uploads_dir = os.path.join(data_dir, 'uploads')
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                # Skip system files
                if filename in SYSTEM_FILES:
                    continue
                file_path = os.path.join(uploads_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path,
                        'storage': 'local',
                        'location': 'uploads'
                    })
        
        # Get files from stooq directory (recursively including all subdirectories)
        # Stooq data often comes in nested structures like: stooq/5min/subfolder1/data.txt
        stooq_dir = os.path.join(data_dir, 'stooq')
        if os.path.exists(stooq_dir):
            try:
                # Recursively search all subdirectories in stooq/
                for root, dirs, filenames in os.walk(stooq_dir):
                    for filename in filenames:
                        # Skip system files
                        if filename in SYSTEM_FILES:
                            continue
                        if not filename.startswith('.'):
                            file_path = os.path.join(root, filename)
                            if os.path.isfile(file_path):
                                file_stat = os.stat(file_path)
                                # Get relative path from data_dir for detailed location
                                rel_path = os.path.relpath(file_path, data_dir)
                                # Also get relative path from stooq_dir for cleaner display
                                stooq_rel_path = os.path.relpath(file_path, stooq_dir)
                                
                                files.append({
                                    'name': filename,
                                    'size': file_stat.st_size,
                                    'modified': file_stat.st_mtime,
                                    'path': file_path,
                                    'storage': 'local',
                                    'location': rel_path,  # Full path: stooq/5min/folder/file.txt
                                    'stooq_path': stooq_rel_path  # Relative to stooq: 5min/folder/file.txt
                                })
            except Exception as e:
                logger.warning(f"Error reading stooq directory: {str(e)}")
        
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
                                'storage': 'local',
                                'location': rel_path
                            })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.get('modified', 0), reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_browsing_list_bp.route('/converted-files')
def list_converted_files():
    """List previously converted files."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        converted_dir = os.path.join(data_dir, 'converted')
        files = []
        
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
                                'path': file_path,
                                'size': file_stat.st_size,
                                'modified': file_stat.st_mtime,
                                'location': rel_path
                            })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing converted files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_browsing_list_bp.route('/home')
def get_home_directory():
    """Get user home directory path."""
    try:
        home_dir = os.path.expanduser('~')
        return jsonify({
            'home': home_dir,
            'downloads': os.path.join(home_dir, 'Downloads')
        })
    except Exception as e:
        logger.error(f"Error getting home directory: {str(e)}")
        return jsonify({'error': str(e)}), 500

