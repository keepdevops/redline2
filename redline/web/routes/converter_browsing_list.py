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
    """List files available for conversion."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # List files in main data directory
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                # Skip system files
                if filename in SYSTEM_FILES:
                    continue
                if filename.endswith(('.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb', '.npz', '.h5', '.arrow')):
                    file_path = os.path.join(data_dir, filename)
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'location': 'data'
                    })
        
        # List files in downloaded directory
        downloaded_dir = os.path.join(data_dir, 'downloaded')
        if os.path.exists(downloaded_dir):
            for filename in os.listdir(downloaded_dir):
                # Skip system files
                if filename in SYSTEM_FILES:
                    continue
                if filename.endswith(('.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb', '.npz', '.h5', '.arrow')):
                    file_path = os.path.join(downloaded_dir, filename)
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'location': 'data/downloaded'
                    })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_browsing_list_bp.route('/converted-files')
def list_converted_files():
    """List previously converted files."""
    try:
        converted_dir = os.path.join(os.getcwd(), 'data', 'converted')
        files = []
        
        if os.path.exists(converted_dir):
            for filename in os.listdir(converted_dir):
                # Skip system files
                if filename in SYSTEM_FILES:
                    continue
                if filename.endswith(('.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb', '.npz', '.h5', '.arrow')):
                    file_path = os.path.join(converted_dir, filename)
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'path': file_path,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'location': 'data/converted'
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

