"""
Converter tab routes for REDLINE Web GUI
Handles file format conversion operations with proper cleanup
"""

from flask import Blueprint, render_template, request, jsonify
import logging
import os
import pandas as pd
import tempfile
import shutil
import atexit
import signal
import sys

converter_bp = Blueprint('converter', __name__)
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

@converter_bp.route('/cleanup', methods=['POST'])
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

@converter_bp.route('/')
def converter_tab():
    """Converter tab main page."""
    return render_template('converter_tab.html')

@converter_bp.route('/formats')
def get_formats():
    """Get supported input and output formats."""
    try:
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        formats = converter.get_supported_formats()
        
        format_info = {
            'csv': {
                'name': 'CSV',
                'description': 'Comma-separated values',
                'extension': '.csv',
                'readable': True,
                'writable': True
            },
            'txt': {
                'name': 'TXT',
                'description': 'Text file (tab-separated or comma-separated)',
                'extension': '.txt',
                'readable': True,
                'writable': True
            },
            'json': {
                'name': 'JSON',
                'description': 'JavaScript Object Notation',
                'extension': '.json',
                'readable': True,
                'writable': True
            },
            'parquet': {
                'name': 'Parquet',
                'description': 'Columnar storage format',
                'extension': '.parquet',
                'readable': True,
                'writable': True
            },
            'feather': {
                'name': 'Feather',
                'description': 'Fast columnar storage',
                'extension': '.feather',
                'readable': True,
                'writable': True
            },
            'duckdb': {
                'name': 'DuckDB',
                'description': 'Embedded analytical database',
                'extension': '.duckdb',
                'readable': True,
                'writable': True
            }
        }
        
        return jsonify({
            'formats': format_info,
            'supported': formats
        })
        
    except Exception as e:
        logger.error(f"Error getting formats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_bp.route('/convert', methods=['POST'])
def convert_file():
    """Convert file between formats."""
    try:
        data = request.get_json()
        input_file = data.get('input_file')
        output_format = data.get('output_format')
        output_filename = data.get('output_filename')
        overwrite = data.get('overwrite', False)
        
        logger.info(f"Convert request: input_file={input_file}, output_format={output_format}, output_filename={output_filename}, overwrite={overwrite}")
        
        if not all([input_file, output_format, output_filename]):
            logger.error(f"Missing required parameters: input_file={input_file}, output_format={output_format}, output_filename={output_filename}")
            return jsonify({'error': 'Missing required parameters', 'details': {'input_file': input_file, 'output_format': output_format, 'output_filename': output_filename}}), 400
        
        # Ensure output filename has the correct extension for the output format
        format_extensions = {
            'csv': '.csv',
            'json': '.json',
            'parquet': '.parquet',
            'feather': '.feather',
            'duckdb': '.duckdb',
            'txt': '.txt'
        }
        
        # Get the expected extension for the output format
        expected_ext = format_extensions.get(output_format, '')
        
        # Check if filename already has an extension
        output_base, output_ext = os.path.splitext(output_filename)
        
        # If the extension doesn't match the expected format, add/change it
        if output_ext != expected_ext and expected_ext:
            output_filename = output_base + expected_ext
            logger.info(f"Adjusted output filename to: {output_filename}")
        
        # Check if output file exists and overwrite is not allowed
        output_path = os.path.join(os.getcwd(), 'data', 'converted', output_filename)
        
        if os.path.exists(output_path) and not overwrite:
            return jsonify({
                'error': 'Output file already exists',
                'output_file': output_filename,
                'suggestion': 'Set overwrite to true or choose a different filename'
            }), 400
        
        # Determine input file path - handle both absolute paths and relative paths
        data_dir = os.path.join(os.getcwd(), 'data')
        input_path = None
        
        # Check if input_file is an absolute path (from file browser)
        if os.path.isabs(input_file) and os.path.exists(input_file):
            # Copy file to data/downloaded/ directory
            downloaded_dir = os.path.join(data_dir, 'downloaded')
            os.makedirs(downloaded_dir, exist_ok=True)
            
            dest_filename = os.path.basename(input_file)
            dest_path = os.path.join(downloaded_dir, dest_filename)
            
            # Copy file (using shutil.copy2 to preserve metadata)
            shutil.copy2(input_file, dest_path)
            logger.info(f"Copied {input_file} to {dest_path}")
            
            input_path = dest_path
        else:
            # Existing logic for relative paths
            # Check in root data directory first
            root_path = os.path.join(data_dir, input_file)
            if os.path.exists(root_path):
                input_path = root_path
            else:
                # Check in downloaded directory
                downloaded_path = os.path.join(data_dir, 'downloaded', input_file)
                if os.path.exists(downloaded_path):
                    input_path = downloaded_path
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({'error': 'Input file not found'}), 404
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        # Load data
        logger.info(f"Loading data from {input_file}")
        from redline.core.schema import EXT_TO_FORMAT
        
        # Validate output format
        supported_formats = converter.get_supported_formats()
        logger.info(f"Supported formats: {supported_formats}")
        logger.info(f"Requested output format: {output_format}")
        
        if output_format not in supported_formats:
            logger.error(f"Unsupported output format: {output_format}")
            return jsonify({
                'error': 'Unsupported output format',
                'details': f'Format "{output_format}" is not supported. Supported formats: {", ".join(supported_formats)}',
                'supported_formats': supported_formats
            }), 400
        
        # Detect format from file extension
        ext = os.path.splitext(input_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        data_obj = converter.load_file_by_type(input_path, format_type)
        
        if data_obj is None or (hasattr(data_obj, 'empty') and data_obj.empty):
            logger.error(f"Failed to load data from {input_path}")
            return jsonify({
                'error': 'Failed to load input file',
                'details': f'Could not load data from {input_file} as {format_type} format'
            }), 400
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save in new format
        logger.info(f"Converting to {output_format} format")
        try:
            converter.save_file_by_type(data_obj, output_path, output_format)
        except Exception as save_error:
            logger.error(f"Failed to save converted file: {str(save_error)}")
            return jsonify({
                'error': 'Failed to save converted file',
                'details': str(save_error)
            }), 400
        
        # Get file info
        file_stat = os.stat(output_path)
        
        result = {
            'message': 'File converted successfully',
            'input_file': input_file,
            'output_file': output_filename,
            'output_format': output_format,
            'output_path': output_path,
            'file_size': file_stat.st_size,
            'records': len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error converting file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_bp.route('/batch-convert', methods=['POST'])
def batch_convert():
    """Convert multiple files in batch."""
    try:
        data = request.get_json()
        files = data.get('files', [])  # List of {input_file, output_format, output_filename}
        overwrite = data.get('overwrite', False)
        
        if not files:
            return jsonify({'error': 'No files provided for conversion'}), 400
        
        results = []
        errors = []
        
        for file_config in files:
            try:
                input_file = file_config.get('input_file')
                output_format = file_config.get('output_format')
                output_filename = file_config.get('output_filename')
                
                if not all([input_file, output_format, output_filename]):
                    errors.append({
                        'input_file': input_file,
                        'error': 'Missing required parameters'
                    })
                    continue
                
                # Check if output file exists
                output_path = os.path.join(os.getcwd(), 'data', 'converted', output_filename)
                
                if os.path.exists(output_path) and not overwrite:
                    errors.append({
                        'input_file': input_file,
                        'output_file': output_filename,
                        'error': 'Output file already exists'
                    })
                    continue
                
                # Determine input file path - handle both absolute paths and relative paths
                data_dir = os.path.join(os.getcwd(), 'data')
                input_path = None
                
                # Check if input_file is an absolute path (from file browser)
                if os.path.isabs(input_file) and os.path.exists(input_file):
                    # Copy file to data/downloaded/ directory
                    downloaded_dir = os.path.join(data_dir, 'downloaded')
                    os.makedirs(downloaded_dir, exist_ok=True)
                    
                    dest_filename = os.path.basename(input_file)
                    dest_path = os.path.join(downloaded_dir, dest_filename)
                    
                    # Copy file (using shutil.copy2 to preserve metadata)
                    shutil.copy2(input_file, dest_path)
                    logger.info(f"Copied {input_file} to {dest_path}")
                    
                    input_path = dest_path
                else:
                    # Existing logic for relative paths
                    # Check in root data directory first
                    root_path = os.path.join(data_dir, input_file)
                    if os.path.exists(root_path):
                        input_path = root_path
                    else:
                        # Check in downloaded directory
                        downloaded_path = os.path.join(data_dir, 'downloaded', input_file)
                        if os.path.exists(downloaded_path):
                            input_path = downloaded_path
                
                # Log debugging info
                logger.debug(f"Input file search: {input_file}")
                
                if not input_path or not os.path.exists(input_path):
                    error_msg = f'Input file not found: {input_file}'
                    logger.warning(error_msg)
                    errors.append({
                        'input_file': input_file,
                        'error': error_msg
                    })
                    continue
                
                from redline.core.format_converter import FormatConverter
                converter = FormatConverter()
                
                # Load and convert
                from redline.core.schema import EXT_TO_FORMAT
                
                # Detect format from file extension
                ext = os.path.splitext(input_path)[1].lower()
                format_type = EXT_TO_FORMAT.get(ext, 'csv')
                
                data_obj = converter.load_file_by_type(input_path, format_type)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                converter.save_file_by_type(data_obj, output_path, output_format)
                
                file_stat = os.stat(output_path)
                
                results.append({
                    'input_file': input_file,
                    'output_file': output_filename,
                    'output_format': output_format,
                    'file_size': file_stat.st_size,
                    'records': len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0,
                    'success': True
                })
                
            except Exception as e:
                errors.append({
                    'input_file': file_config.get('input_file', 'unknown'),
                    'error': str(e)
                })
        
        return jsonify({
            'message': f'Batch conversion completed. {len(results)} successful, {len(errors)} failed.',
            'results': results,
            'errors': errors,
            'total_files': len(files),
            'successful': len(results),
            'failed': len(errors)
        })
        
    except Exception as e:
        logger.error(f"Error in batch conversion: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_bp.route('/files')
def list_available_files():
    """List files available for conversion."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # List files in main data directory
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith(('.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb')):
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
                if filename.endswith(('.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb')):
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

@converter_bp.route('/converted-files')
def list_converted_files():
    """List previously converted files."""
    try:
        converted_dir = os.path.join(os.getcwd(), 'data', 'converted')
        files = []
        
        if os.path.exists(converted_dir):
            for filename in os.listdir(converted_dir):
                if filename.endswith(('.csv', '.txt', '.json', '.parquet', '.feather', '.duckdb')):
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

@converter_bp.route('/home')
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

@converter_bp.route('/browse')
def browse_filesystem():
    """Browse file system - list directories and files for file selection."""
    try:
        path = request.args.get('path', os.path.expanduser('~'))
        
        # Log for debugging
        logger.debug(f"Browsing path: {path}")
        
        # Security check - prevent directory traversal
        if not os.path.exists(path):
            logger.warning(f"Path does not exist: {path}")
            return jsonify({'error': f'Path does not exist: {path}'}), 400
            
        if not os.path.isdir(path):
            logger.warning(f"Path is not a directory: {path}")
            return jsonify({'error': f'Path is not a directory: {path}'}), 400
        
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
            dir_contents = os.listdir(abs_path)
            
            # If directory is empty, return empty list
            if not dir_contents:
                return jsonify({
                    'path': abs_path,
                    'items': []
                })
                
            for item_name in sorted(dir_contents):
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
                except (OSError, PermissionError) as e:
                    # Log but continue with other items
                    logger.debug(f"Cannot access {item_path}: {str(e)}")
                    continue
                    
        except PermissionError as e:
            logger.warning(f"Permission denied for directory {abs_path}: {str(e)}")
            return jsonify({
                'error': f'Permission denied: {str(e)}',
                'path': abs_path,
                'suggestion': 'Try a different directory or grant read permissions'
            }), 403
        
        return jsonify({
            'path': abs_path,
            'items': items
        })
        
    except Exception as e:
        logger.error(f"Error browsing filesystem: {str(e)}")
        return jsonify({'error': str(e)}), 500

@converter_bp.route('/preview/<filename>')
def preview_file(filename):
    """Preview file contents for conversion."""
    try:
        file_path = os.path.join(os.getcwd(), 'data', filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        from redline.core.schema import EXT_TO_FORMAT
        
        # Detect format from file extension
        ext = os.path.splitext(file_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        data = converter.load_file_by_type(file_path, format_type)
        
        if isinstance(data, pd.DataFrame):
            preview = {
                'type': 'dataframe',
                'columns': list(data.columns),
                'dtypes': data.dtypes.astype(str).to_dict(),
                'shape': {
                    'rows': int(data.shape[0]),
                    'columns': int(data.shape[1])
                },
                'sample_data': data.head(10).to_dict('records'),
                'null_counts': {k: int(v) for k, v in data.isnull().sum().to_dict().items()},
                'memory_usage': int(data.memory_usage(deep=True).sum())
            }
        else:
            preview = {
                'type': 'other',
                'content': str(data)[:1000],  # Truncate for large content
                'size': len(str(data))
            }
        
        return jsonify({
            'filename': filename,
            'preview': preview
        })
        
    except Exception as e:
        logger.error(f"Error previewing file {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500
