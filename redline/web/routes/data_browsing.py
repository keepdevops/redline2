"""
Data browsing routes for REDLINE Web GUI.
Handles file listing, browsing, and database statistics.
"""

from flask import Blueprint, request, jsonify, send_file
import logging
import os
from ...database.optimized_connector import OptimizedDatabaseConnector

data_browsing_bp = Blueprint('data_browsing', __name__)
logger = logging.getLogger(__name__)

# Initialize optimized database connector
optimized_db = OptimizedDatabaseConnector(max_connections=8, cache_size=64, cache_ttl=300)


@data_browsing_bp.route('/files')
def list_files():
    """List available data files."""
    try:
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
        
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # Get files from root data directory
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
                        'location': 'downloaded'
                    })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500


@data_browsing_bp.route('/db-stats')
def get_database_stats():
    """Get database performance statistics."""
    try:
        stats = optimized_db.get_performance_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@data_browsing_bp.route('/browse')
def browse_filesystem():
    """Browse file system - list directories and files."""
    try:
        path = request.args.get('path', os.path.expanduser('~'))
        
        # Security check - prevent directory traversal
        if not os.path.exists(path) or not os.path.isdir(path):
            return jsonify({'error': 'Invalid path'}), 400
        
        # Get absolute path to prevent traversal attacks
        abs_path = os.path.abspath(path)
        
        items = []
        
        # Add parent directory if not at root
        if abs_path != os.path.abspath(os.path.expanduser('~')) and abs_path != '/':
            parent_path = os.path.dirname(abs_path)
            items.append({
                'name': '..',
                'type': 'directory',
                'path': parent_path,
                'size': 0,
                'modified': 0
            })
        
        # List directory contents
        try:
            for item_name in sorted(os.listdir(abs_path)):
                item_path = os.path.join(abs_path, item_name)
                
                # Skip hidden files/folders
                if item_name.startswith('.'):
                    continue
                
                try:
                    stat_info = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)
                    
                    items.append({
                        'name': item_name,
                        'type': 'directory' if is_dir else 'file',
                        'path': item_path,
                        'size': stat_info.st_size if not is_dir else 0,
                        'modified': stat_info.st_mtime,
                        'extension': os.path.splitext(item_name)[1].lower() if not is_dir else ''
                    })
                except (OSError, PermissionError):
                    continue
                    
        except PermissionError:
            return jsonify({'error': 'Permission denied'}), 403
        
        return jsonify({
            'path': abs_path,
            'items': items,
            'parent': os.path.dirname(abs_path) if abs_path != '/' else None
        })
        
    except Exception as e:
        logger.error(f"Error browsing filesystem: {str(e)}")
        return jsonify({'error': str(e)}), 500


@data_browsing_bp.route('/download/<path:file_path>')
def download_file(file_path):
    """Download a file from the system."""
    try:
        # Security check
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(abs_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

