"""
Data cleaning routes for VarioSync Web GUI
Handles data cleaning operations
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
from ..utils.file_loading import (
    rate_limit,
    detect_format_from_path as _detect_format_from_path,
    load_file_by_format as _load_file_by_format,
    save_file_by_format as _save_file_by_format
)
from ..utils.data_helpers import clean_dataframe_columns

data_filtering_clean_bp = Blueprint('data_filtering_clean', __name__)
logger = logging.getLogger(__name__)

@data_filtering_clean_bp.route('/clean', methods=['POST'])
@rate_limit("10 per minute")
def clean_data():
    """Clean data: remove duplicates and handle missing values."""
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Clean data request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Clean data request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate filename
    filename = data.get('filename')

    if not filename:
        logger.warning("Clean data request missing filename field")
        return jsonify({'error': 'Filename is required'}), 400

    if not isinstance(filename, str):
        logger.error(f"Clean data request filename has invalid type: {type(filename)}")
        return jsonify({'error': 'Filename must be a string'}), 400

    if len(filename) == 0:
        logger.warning("Clean data request with empty filename")
        return jsonify({'error': 'Filename cannot be empty'}), 400

    # Security check: prevent path traversal
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        logger.warning(f"Clean data request with suspicious filename: {filename}")
        return jsonify({'error': 'Invalid filename format'}), 400

    # Validate remove_duplicates flag
    remove_duplicates = data.get('remove_duplicates', True)
    if not isinstance(remove_duplicates, bool):
        logger.warning(f"Clean data request has invalid remove_duplicates type: {type(remove_duplicates)}, defaulting to True")
        remove_duplicates = True

    # Validate handle_missing strategy
    handle_missing = data.get('handle_missing', 'drop')
    if not isinstance(handle_missing, str):
        logger.error(f"Clean data request has invalid handle_missing type: {type(handle_missing)}")
        return jsonify({'error': 'handle_missing must be a string'}), 400

    valid_strategies = ['drop', 'forward_fill', 'backward_fill', 'none']
    if handle_missing not in valid_strategies:
        logger.warning(f"Clean data request has invalid handle_missing strategy: {handle_missing}")
        return jsonify({'error': f'Invalid handle_missing strategy. Must be one of: {", ".join(valid_strategies)}'}), 400

    logger.info(f"Processing clean data request: filename={filename}, remove_duplicates={remove_duplicates}, handle_missing={handle_missing}")

    # Validate data directory
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return jsonify({'error': 'Data directory not configured'}), 500

    # Search for file in data directories
    file_path = None
    search_paths = [
        os.path.join(data_dir, filename),
        os.path.join(data_dir, 'downloaded', filename),
        os.path.join(data_dir, 'stooq', filename),
        os.path.join(data_dir, 'uploads', filename)
    ]

    # Search in converted directory recursively
    converted_dir = os.path.join(data_dir, 'converted')
    if os.path.exists(converted_dir):
        direct_path = os.path.join(converted_dir, filename)
        if os.path.exists(direct_path) and os.path.isfile(direct_path):
            search_paths.append(direct_path)
        else:
            for root, dirs, files in os.walk(converted_dir):
                if filename in files:
                    search_paths.append(os.path.join(root, filename))
                    break

    # Find the file
    for path in search_paths:
        if os.path.exists(path) and os.path.isfile(path):
            file_path = path
            logger.debug(f"Found file at: {file_path}")
            break

    if not file_path:
        logger.warning(f"File not found: {filename}")
        return jsonify({
            'error': 'File not found',
            'filename': filename,
            'message': f'File "{filename}" not found in data directories'
        }), 404

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
        return jsonify({
            'error': 'No data found',
            'message': f'The file "{filename}" contains no data'
        }), 404

    original_rows = len(df)
    logger.debug(f"Loaded DataFrame with {original_rows} rows")

    stats = {}

    # Initialize cleaner
    from redline.core.data_cleaner import DataCleaner
    cleaner = DataCleaner()

    # Remove duplicates
    if remove_duplicates:
        df_before = len(df)
        logger.debug(f"Removing duplicates from {df_before} rows")

        # Determine subset for duplicate detection (flexible column detection)
        from ..utils.analysis_helpers import detect_ticker_column, detect_timestamp_column
        ticker_col = detect_ticker_column(df)
        timestamp_col = detect_timestamp_column(df)

        subset = None
        if ticker_col and timestamp_col:
            subset = [ticker_col, timestamp_col]
            logger.debug(f"Using subset for duplicate detection: {subset}")
        elif timestamp_col:
            subset = [timestamp_col]
            logger.debug(f"Using timestamp column for duplicate detection: {subset}")

        df = cleaner.remove_duplicates(df, subset=subset)

        # Validate removal result
        if df is None:
            logger.error(f"Duplicate removal returned None for {filename}")
            return jsonify({'error': 'Duplicate removal failed'}), 500

        duplicates_removed = df_before - len(df)
        stats['duplicates_removed'] = duplicates_removed
        logger.info(f"Removed {duplicates_removed} duplicate rows")

    # Handle missing values
    if handle_missing and handle_missing != 'none':
        df_before = len(df)
        logger.debug(f"Handling missing values using {handle_missing} strategy")

        df = cleaner.handle_missing_values(df, strategy=handle_missing)

        # Validate result
        if df is None:
            logger.error(f"Missing value handling returned None for {filename}")
            return jsonify({'error': 'Missing value handling failed'}), 500

        missing_handled = df_before - len(df)
        stats['missing_handled'] = missing_handled
        logger.info(f"Handled missing values: {missing_handled} rows affected")

    # Clean column names
    logger.debug("Cleaning column names")
    df = clean_dataframe_columns(df)

    # Validate final DataFrame
    if df is None or df.empty:
        logger.error(f"Data cleaning resulted in empty DataFrame for {filename}")
        return jsonify({'error': 'Data cleaning resulted in no data'}), 500

    # Convert to JSON-serializable format (limit to 1000 rows for performance)
    preview_rows = min(1000, len(df))
    cleaned_data = df.head(preview_rows).to_dict('records')

    logger.info(f"Data cleaning completed: {original_rows} -> {len(df)} rows (preview: {preview_rows} rows)")

    return jsonify({
        'success': True,
        'filename': filename,
        'columns': list(df.columns),
        'data': cleaned_data,
        'total_rows': len(df),
        'original_rows': original_rows,
        'preview_rows': preview_rows,
        'stats': stats
    })

@data_filtering_clean_bp.route('/save-cleaned', methods=['POST'])
@rate_limit("10 per minute")
def save_cleaned_data():
    """Save cleaned data to a new file."""
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Save cleaned data request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Save cleaned data request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate filename
    filename = data.get('filename')

    if not filename:
        logger.warning("Save cleaned data request missing filename field")
        return jsonify({'error': 'Filename is required'}), 400

    if not isinstance(filename, str):
        logger.error(f"Save cleaned data request filename has invalid type: {type(filename)}")
        return jsonify({'error': 'Filename must be a string'}), 400

    if len(filename) == 0:
        logger.warning("Save cleaned data request with empty filename")
        return jsonify({'error': 'Filename cannot be empty'}), 400

    # Security check: prevent path traversal
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        logger.warning(f"Save cleaned data request with suspicious filename: {filename}")
        return jsonify({'error': 'Invalid filename format'}), 400

    # Validate cleaned_data
    cleaned_data = data.get('data')

    if not cleaned_data:
        logger.warning(f"Save cleaned data request for {filename} missing data field")
        return jsonify({'error': 'Data is required'}), 400

    if not isinstance(cleaned_data, list):
        logger.error(f"Save cleaned data request for {filename} has invalid data type: {type(cleaned_data)}")
        return jsonify({'error': 'Data must be an array'}), 400

    if len(cleaned_data) == 0:
        logger.warning(f"Save cleaned data request for {filename} with empty data array")
        return jsonify({'error': 'Data array cannot be empty'}), 400

    # Validate columns (optional)
    columns = data.get('columns', [])

    if columns and not isinstance(columns, list):
        logger.warning(f"Save cleaned data request for {filename} has invalid columns type: {type(columns)}, ignoring")
        columns = []

    logger.info(f"Processing save cleaned data request: filename={filename}, {len(cleaned_data)} rows, {len(columns) if columns else 'auto'} columns")

    # Create DataFrame from cleaned data
    try:
        df = pd.DataFrame(cleaned_data)
    except Exception as e:
        logger.error(f"Failed to create DataFrame from cleaned data for {filename}: {str(e)}")
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400

    # Validate DataFrame creation
    if df is None:
        logger.error(f"DataFrame creation returned None for {filename}")
        return jsonify({'error': 'Failed to create DataFrame from data'}), 500

    if df.empty:
        logger.warning(f"Created DataFrame is empty for {filename}")
        return jsonify({'error': 'Data resulted in empty DataFrame'}), 400

    logger.debug(f"Created DataFrame with shape: {df.shape}")

    # Ensure columns are in correct order if provided
    if columns and len(columns) == len(df.columns):
        try:
            df = df[columns]
            logger.debug(f"Reordered columns: {columns}")
        except KeyError as e:
            logger.warning(f"Could not reorder columns for {filename}: {str(e)}, using default order")

    # Validate data directory
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return jsonify({'error': 'Data directory not configured'}), 500

    # Determine save location
    save_dir = os.path.join(data_dir, 'converted')
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, filename)
    logger.debug(f"Save path: {save_path}")

    # Detect format from extension
    format_type = _detect_format_from_path(save_path)

    if not format_type:
        logger.error(f"Could not detect format for file: {save_path}")
        return jsonify({'error': 'Unknown file format'}), 400

    logger.debug(f"Detected save format: {format_type}")

    # Save file
    _save_file_by_format(df, save_path, format_type)

    # Verify save succeeded
    if not os.path.exists(save_path):
        logger.error(f"File was not created after save operation: {save_path}")
        return jsonify({'error': 'Failed to save file'}), 500

    file_size = os.path.getsize(save_path)
    logger.info(f"Successfully saved cleaned data to: {save_path} ({file_size} bytes, {len(df)} rows)")

    return jsonify({
        'success': True,
        'message': f'Cleaned data saved as "{filename}"',
        'filename': filename,
        'path': save_path,
        'rows': len(df),
        'file_size': file_size
    })

