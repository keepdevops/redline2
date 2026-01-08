"""
Data filtering routes for VarioSync Web GUI
Handles data filtering and export operations
"""

from flask import Blueprint, request, jsonify
import logging
import os
from ..utils.file_loading import (
    rate_limit,
    detect_format_from_path as _detect_format_from_path,
    load_file_by_format as _load_file_by_format,
    save_file_by_format as _save_file_by_format,
    apply_filters as _apply_filters
)

data_filtering_filter_bp = Blueprint('data_filtering_filter', __name__)
logger = logging.getLogger(__name__)

@data_filtering_filter_bp.route('/filter', methods=['POST'])
@rate_limit("60 per minute")
def filter_file_data():
    """Apply filters to loaded data."""
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Filter request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Filter request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate filename
    filename = data.get('filename')

    if not filename:
        logger.warning("Filter request missing filename field")
        return jsonify({'error': 'Filename is required'}), 400

    if not isinstance(filename, str):
        logger.error(f"Filter request filename has invalid type: {type(filename)}")
        return jsonify({'error': 'Filename must be a string'}), 400

    if len(filename) == 0:
        logger.warning("Filter request with empty filename")
        return jsonify({'error': 'Filename cannot be empty'}), 400

    # Security check: prevent path traversal
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        logger.warning(f"Filter request with suspicious filename: {filename}")
        return jsonify({'error': 'Invalid filename format'}), 400

    # Validate filters
    filters = data.get('filters', {})

    if not isinstance(filters, dict):
        logger.error(f"Filter request filters field has invalid type: {type(filters)}")
        return jsonify({'error': 'Filters must be an object'}), 400

    logger.info(f"Processing filter request for filename: {filename}, filters: {len(filters)} filter(s)")

    # Validate data directory
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return jsonify({'error': 'Data directory not configured'}), 500

    # Find file path
    root_path = os.path.join(data_dir, filename)
    downloaded_path = os.path.join(data_dir, 'downloaded', filename)

    file_path = None
    if os.path.exists(root_path):
        file_path = root_path
        logger.debug(f"Found file at root: {root_path}")
    elif os.path.exists(downloaded_path):
        file_path = downloaded_path
        logger.debug(f"Found file in downloaded: {downloaded_path}")

    if not file_path:
        logger.warning(f"File not found: {filename}")
        return jsonify({'error': 'File not found', 'filename': filename}), 404

    # Detect file format
    format_type = _detect_format_from_path(file_path)

    if not format_type:
        logger.error(f"Could not detect format for file: {file_path}")
        return jsonify({'error': 'Unknown file format'}), 400

    logger.debug(f"Detected format: {format_type}")

    # Load file data
    df = _load_file_by_format(file_path, format_type)

    # Validate loaded data
    if df is None:
        logger.error(f"File loading returned None for {filename}")
        return jsonify({'error': 'Failed to load file'}), 500

    if not hasattr(df, 'empty'):
        logger.error(f"Loaded data is not a DataFrame for {filename}: {type(df)}")
        return jsonify({'error': 'Failed to load file'}), 500

    if df.empty:
        logger.warning(f"Loaded DataFrame is empty for {filename}")
        return jsonify({'error': 'File contains no data'}), 404

    original_rows = len(df)
    logger.debug(f"Loaded DataFrame with {original_rows} rows")

    # Apply filters
    filtered_df = _apply_filters(df, filters)

    # Validate filtered result
    if filtered_df is None:
        logger.error(f"Filter operation returned None for {filename}")
        return jsonify({'error': 'Filter operation failed'}), 500

    if not hasattr(filtered_df, 'empty'):
        logger.error(f"Filtered data is not a DataFrame: {type(filtered_df)}")
        return jsonify({'error': 'Filter operation failed'}), 500

    filtered_rows = len(filtered_df)
    logger.info(f"Filter applied successfully: {original_rows} -> {filtered_rows} rows")

    return jsonify({
        'data': filtered_df.to_dict('records'),
        'columns': list(filtered_df.columns),
        'total_rows': filtered_rows,
        'original_rows': original_rows
    })

@data_filtering_filter_bp.route('/export', methods=['POST'])
def export_file_data():
    """Export filtered data to a file."""
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Export request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Export request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate filename
    filename = data.get('filename')

    if not filename:
        logger.warning("Export request missing filename field")
        return jsonify({'error': 'Filename is required'}), 400

    if not isinstance(filename, str):
        logger.error(f"Export request filename has invalid type: {type(filename)}")
        return jsonify({'error': 'Filename must be a string'}), 400

    # Security check: prevent path traversal
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        logger.warning(f"Export request with suspicious filename: {filename}")
        return jsonify({'error': 'Invalid filename format'}), 400

    # Validate export_filename
    export_filename = data.get('export_filename')

    if not export_filename:
        logger.warning(f"Export request from {filename} missing export_filename field")
        return jsonify({'error': 'Export filename is required'}), 400

    if not isinstance(export_filename, str):
        logger.error(f"Export request export_filename has invalid type: {type(export_filename)}")
        return jsonify({'error': 'Export filename must be a string'}), 400

    # Security check: prevent path traversal on export filename
    if '..' in export_filename or export_filename.startswith('/') or export_filename.startswith('\\'):
        logger.warning(f"Export request with suspicious export_filename: {export_filename}")
        return jsonify({'error': 'Invalid export filename format'}), 400

    # Validate format
    format_type = data.get('format', 'csv')

    if not isinstance(format_type, str):
        logger.error(f"Export request format has invalid type: {type(format_type)}")
        return jsonify({'error': 'Format must be a string'}), 400

    valid_formats = ['csv', 'json', 'parquet', 'feather', 'excel', 'txt']
    if format_type not in valid_formats:
        logger.warning(f"Export request has invalid format: {format_type}")
        return jsonify({'error': f'Invalid format. Must be one of: {", ".join(valid_formats)}'}), 400

    # Validate filters
    filters = data.get('filters', {})

    if not isinstance(filters, dict):
        logger.error(f"Export request filters field has invalid type: {type(filters)}")
        return jsonify({'error': 'Filters must be an object'}), 400

    logger.info(f"Processing export request: {filename} -> {export_filename} (format: {format_type}, filters: {len(filters)})")

    # Validate data directory
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return jsonify({'error': 'Data directory not configured'}), 500

    # Find file path
    root_path = os.path.join(data_dir, filename)
    downloaded_path = os.path.join(data_dir, 'downloaded', filename)

    file_path = None
    if os.path.exists(root_path):
        file_path = root_path
        logger.debug(f"Found file at root: {root_path}")
    elif os.path.exists(downloaded_path):
        file_path = downloaded_path
        logger.debug(f"Found file in downloaded: {downloaded_path}")

    if not file_path:
        logger.warning(f"File not found for export: {filename}")
        return jsonify({'error': 'File not found', 'filename': filename}), 404

    # Detect and load file
    original_format = _detect_format_from_path(file_path)

    if not original_format:
        logger.error(f"Could not detect format for file: {file_path}")
        return jsonify({'error': 'Unknown file format'}), 400

    logger.debug(f"Loading file with format: {original_format}")

    df = _load_file_by_format(file_path, original_format)

    # Validate loaded data
    if df is None:
        logger.error(f"File loading returned None for {filename}")
        return jsonify({'error': 'Failed to load file'}), 500

    if not hasattr(df, 'empty'):
        logger.error(f"Loaded data is not a DataFrame for {filename}: {type(df)}")
        return jsonify({'error': 'Failed to load file'}), 500

    if df.empty:
        logger.warning(f"Loaded DataFrame is empty for {filename}")
        return jsonify({'error': 'File contains no data'}), 404

    original_rows = len(df)
    logger.debug(f"Loaded {original_rows} rows")

    # Apply filters if any
    if filters:
        logger.debug(f"Applying {len(filters)} filter(s)")
        df = _apply_filters(df, filters)

        if df is None:
            logger.error(f"Filter operation returned None")
            return jsonify({'error': 'Filter operation failed'}), 500

        logger.info(f"Filters applied: {original_rows} -> {len(df)} rows")

    # Prepare export path
    export_path = os.path.join(data_dir, export_filename)
    logger.debug(f"Exporting to: {export_path}")

    # Save file
    _save_file_by_format(df, export_path, format_type)

    # Verify export
    if not os.path.exists(export_path):
        logger.error(f"Export file was not created: {export_path}")
        return jsonify({'error': 'Failed to export file'}), 500

    rows_exported = len(df)
    logger.info(f"Export successful: {rows_exported} rows saved to {export_filename}")

    return jsonify({
        'message': f'Data exported successfully to {export_filename}',
        'export_path': export_path,
        'rows_exported': rows_exported,
        'format': format_type
    })

