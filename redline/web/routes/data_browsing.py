"""
Data browsing routes for VarioSync Web GUI.
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

    # Pre-validation with if-else
    if not data_dir:
        logger.error("Data directory path is empty")
        return jsonify({'error': 'Data directory not configured', 'code': 'DATA_DIR_EMPTY'}), 500

    try:
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

    except PermissionError as e:
        logger.error(f"Permission denied listing files in {data_dir}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error listing files in {data_dir}: {str(e)}")
        return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing file attribute: {str(e)}")
        return jsonify({'error': f'File attribute error: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error listing files: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500


@data_browsing_bp.route('/db-stats')
def get_database_stats():
    """Get database performance statistics."""
    try:
        stats = optimized_db.get_performance_stats()
        return jsonify(stats)
    except AttributeError as e:
        logger.error(f"Database method not found: {str(e)}")
        return jsonify({'error': 'Database operation failed', 'code': 'ATTRIBUTE_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error getting database stats: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500


@data_browsing_bp.route('/browse')
def browse_filesystem():
    """Browse file system - list directories and files."""
    path = request.args.get('path', os.path.expanduser('~'))

    # Pre-validation with if-else
    if not path:
        logger.error("Path parameter is empty")
        return jsonify({'error': 'Path is required', 'code': 'PATH_EMPTY'}), 400

    if not isinstance(path, str):
        logger.error(f"Path must be a string, got {type(path)}")
        return jsonify({'error': 'Invalid path type', 'code': 'INVALID_PATH_TYPE'}), 400

    # Security check - prevent directory traversal
    if not os.path.exists(path):
        logger.warning(f"Path does not exist: {path}")
        return jsonify({'error': 'Path does not exist', 'code': 'PATH_NOT_FOUND'}), 404

    if not os.path.isdir(path):
        logger.warning(f"Path is not a directory: {path}")
        return jsonify({'error': 'Path is not a directory', 'code': 'NOT_DIRECTORY'}), 400

    try:
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

        # List directory contents - Note: Directory listing requires try-except
        try:
            for item_name in sorted(os.listdir(abs_path)):
                item_path = os.path.join(abs_path, item_name)

                # Skip hidden files/folders
                if item_name.startswith('.'):
                    continue

                # Note: File stat requires try-except for permission errors
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
                except (OSError, PermissionError) as e:
                    logger.debug(f"Skipping inaccessible item {item_path}: {str(e)}")
                    continue

        except PermissionError as e:
            logger.error(f"Permission denied listing directory {abs_path}: {str(e)}")
            return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
        except OSError as e:
            logger.error(f"OS error listing directory {abs_path}: {str(e)}")
            return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500

        return jsonify({
            'path': abs_path,
            'items': items,
            'parent': os.path.dirname(abs_path) if abs_path != '/' else None
        })

    except Exception as e:
        logger.error(f"Unexpected error browsing filesystem at {path}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500


@data_browsing_bp.route('/download/<path:file_path>')
def download_file(file_path):
    """Download a file from the system."""
    # Pre-validation with if-else
    if not file_path:
        logger.error("File path is empty")
        return jsonify({'error': 'File path is required', 'code': 'FILE_PATH_EMPTY'}), 400

    if not isinstance(file_path, str):
        logger.error(f"File path must be a string, got {type(file_path)}")
        return jsonify({'error': 'Invalid file path type', 'code': 'INVALID_PATH_TYPE'}), 400

    try:
        # Security check
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            logger.warning(f"File not found: {abs_path}")
            return jsonify({'error': 'File not found', 'code': 'FILE_NOT_FOUND'}), 404

        if not os.path.isfile(abs_path):
            logger.warning(f"Path is not a file: {abs_path}")
            return jsonify({'error': 'Path is not a file', 'code': 'NOT_FILE'}), 400

        return send_file(abs_path, as_attachment=True)

    except PermissionError as e:
        logger.error(f"Permission denied downloading file {file_path}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error downloading file {file_path}: {str(e)}")
        return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error downloading file {file_path}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

