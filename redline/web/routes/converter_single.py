"""
Single file conversion routes for REDLINE Web GUI.
Handles individual file format conversion operations.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
import traceback
from ..utils.converter_helpers import find_input_file_path, adjust_output_filename, validate_file_before_conversion

converter_single_bp = Blueprint('converter_single', __name__)
logger = logging.getLogger(__name__)

@converter_single_bp.route('/convert', methods=['POST'])
def convert_file():
    """Convert file between formats - redirects to batch conversion."""
    try:
        data = request.get_json()
        input_file = data.get('input_file')
        output_format = data.get('output_format')
        output_filename = data.get('output_filename')
        overwrite = data.get('overwrite', False)
        
        logger.info(f"Single file convert request redirected to batch: input_file={input_file}, output_format={output_format}, output_filename={output_filename}, overwrite={overwrite}")
        
        if not all([input_file, output_format, output_filename]):
            logger.error(f"Missing required parameters: input_file={input_file}, output_format={output_format}, output_filename={output_filename}")
            return jsonify({
                'error': 'Missing required parameters',
                'details': {
                    'input_file': input_file,
                    'output_format': output_format,
                    'output_filename': output_filename
                },
                'message': 'Single file conversion is no longer supported. Please use batch conversion instead.'
            }), 400
        
        # Redirect single file conversion to batch conversion
        # Convert single file request to batch format
        from .converter_batch import batch_convert
        from flask import Request
        
        # Create batch conversion request
        batch_data = {
            'files': [{
                'input_file': input_file,
                'output_format': output_format,
                'output_filename': output_filename
            }],
            'overwrite': overwrite,
            # Include data cleaning options if provided
            'remove_duplicates': data.get('remove_duplicates', False),
            'handle_missing': data.get('handle_missing', 'drop'),
            'clean_column_names': data.get('clean_column_names', False),
            'column_order': data.get('column_order')
        }
        
        # Call batch conversion with single file
        # Create a mock request object for batch_convert
        original_json = request.get_json
        request.get_json = lambda: batch_data
        
        try:
            result = batch_convert()
            return result
        finally:
            request.get_json = original_json
        
        # Ensure output filename has the correct extension
        output_filename = adjust_output_filename(output_filename, output_format)
        
        # Check if output file exists and overwrite is not allowed
        output_path = os.path.join(os.getcwd(), 'data', 'converted', output_filename)
        
        if os.path.exists(output_path) and not overwrite:
            return jsonify({
                'error': 'Output file already exists',
                'output_file': output_filename,
                'suggestion': 'Set overwrite to true or choose a different filename'
            }), 400
        
        # Find input file path
        data_dir = os.path.join(os.getcwd(), 'data')
        input_path = find_input_file_path(input_file, data_dir)
        
        if not input_path or not os.path.exists(input_path):
            # Check if it's a system file
            from ..utils.converter_helpers import is_system_file
            if is_system_file(os.path.basename(input_file)):
                logger.warning(f"Attempted to convert system file: {input_file}")
                return jsonify({
                    'error': 'System files cannot be converted',
                    'input_file': input_file
                }), 403
            logger.error(f"Input file not found: {input_file} (searched in: {data_dir})")
            return jsonify({
                'error': 'Input file not found',
                'input_file': input_file,
                'searched_paths': [
                    os.path.join(data_dir, input_file),
                    os.path.join(data_dir, 'downloaded', input_file),
                    os.path.join(data_dir, 'stooq', input_file)
                ]
            }), 404
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
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
        from redline.core.schema import EXT_TO_FORMAT
        ext = os.path.splitext(input_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Validate file before conversion attempt
        logger.info(f"Validating file {input_file} before conversion...")
        is_valid, validation_error, validation_details = validate_file_before_conversion(
            input_path, expected_format=format_type
        )
        
        if not is_valid:
            error_msg = validation_error or 'File validation failed'
            logger.error(f"File validation failed for {input_file}: {error_msg}")
            logger.debug(f"Validation details: {validation_details}")
            return jsonify({
                'error': error_msg,
                'input_file': input_file,
                'validation_details': validation_details
            }), 400
        
        # Log validation success with details
        if validation_details.get('file_size'):
            logger.info(f"File validation passed: {input_file} "
                      f"(size: {validation_details['file_size']} bytes, "
                      f"format: {format_type}, "
                      f"encoding: {validation_details.get('encoding', 'N/A')})")
        
        # Load data
        logger.info(f"Loading data from {input_file} as {format_type} format...")
        try:
            data_obj = converter.load_file_by_type(input_path, format_type)
        except Exception as load_error:
            error_msg = f"Error loading file: {str(load_error)}"
            logger.error(f"Failed to load {input_file}: {error_msg}")
            logger.debug(f"Load error traceback:\n{traceback.format_exc()}")
            return jsonify({
                'error': error_msg,
                'input_file': input_file,
                'format_attempted': format_type,
                'file_path': input_path,
                'file_size': validation_details.get('file_size', 'unknown')
            }), 400
        
        if data_obj is None:
            error_msg = f"File loaded but returned None: {input_file}"
            logger.error(error_msg)
            return jsonify({
                'error': error_msg,
                'input_file': input_file,
                'format_attempted': format_type,
                'file_path': input_path,
                'file_size': validation_details.get('file_size', 'unknown')
            }), 400
        
        if hasattr(data_obj, 'empty') and data_obj.empty:
            error_msg = f"File loaded but contains no data: {input_file}"
            logger.warning(error_msg)
            logger.debug(f"Data object type: {type(data_obj)}, shape: {getattr(data_obj, 'shape', 'N/A')}")
            return jsonify({
                'error': error_msg,
                'input_file': input_file,
                'format_attempted': format_type,
                'file_path': input_path,
                'file_size': validation_details.get('file_size', 'unknown')
            }), 400
        
        # Apply data cleaning options if provided
        remove_duplicates = data.get('remove_duplicates', False)
        handle_missing = data.get('handle_missing', 'none')
        clean_column_names = data.get('clean_column_names', False)
        column_order = data.get('column_order')
        
        original_rows = len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0
        cleaning_stats = {}
        
        if isinstance(data_obj, pd.DataFrame):
            # Remove duplicates
            if remove_duplicates:
                from redline.core.data_cleaner import DataCleaner
                cleaner = DataCleaner()
                df_before = len(data_obj)
                # Determine subset for duplicate detection (flexible column detection)
                from ..utils.analysis_helpers import detect_ticker_column, detect_timestamp_column
                ticker_col = detect_ticker_column(data_obj)
                timestamp_col = detect_timestamp_column(data_obj)
                
                # For Stooq format with separate DATE and TIME columns, include both
                subset = None
                if ticker_col and timestamp_col:
                    subset = [ticker_col, timestamp_col]
                    # Check if this is Stooq format with separate DATE and TIME
                    if '<DATE>' in data_obj.columns and '<TIME>' in data_obj.columns:
                        # Include TIME in duplicate detection to preserve all time-based rows
                        if '<TIME>' not in subset:
                            subset.append('<TIME>')
                        logger.info(f"Stooq format detected: using {subset} for duplicate detection")
                elif timestamp_col:
                    subset = [timestamp_col]
                    # For Stooq format, also include TIME
                    if '<DATE>' in data_obj.columns and '<TIME>' in data_obj.columns:
                        if '<TIME>' not in subset:
                            subset.append('<TIME>')
                elif '<DATE>' in data_obj.columns and '<TIME>' in data_obj.columns:
                    # Fallback: if no timestamp detected but Stooq format, use DATE+TIME
                    subset = ['<DATE>', '<TIME>']
                    if ticker_col:
                        subset.insert(0, ticker_col)
                    logger.info(f"Stooq format fallback: using {subset} for duplicate detection")
                
                data_obj = cleaner.remove_duplicates(data_obj, subset=subset)
                duplicates_removed = df_before - len(data_obj)
                cleaning_stats['duplicates_removed'] = duplicates_removed
                logger.info(f"Removed {duplicates_removed} duplicate rows")
            
            # Handle missing values
            if handle_missing and handle_missing != 'none':
                from redline.core.data_cleaner import DataCleaner
                cleaner = DataCleaner()
                df_before = len(data_obj)
                data_obj = cleaner.handle_missing_values(data_obj, strategy=handle_missing)
                missing_handled = df_before - len(data_obj)
                cleaning_stats['missing_handled'] = missing_handled
                logger.info(f"Handled missing values using {handle_missing} strategy, {missing_handled} rows affected")
            
            # Clean column names
            if clean_column_names:
                from redline.web.utils.data_helpers import clean_dataframe_columns
                data_obj = clean_dataframe_columns(data_obj)
                logger.info("Cleaned column names")
            
            # Reorder columns if specified
            if column_order:
                # Parse column_order if it's a string (comma-separated)
                if isinstance(column_order, str):
                    column_order = [col.strip() for col in column_order.split(',') if col.strip()]
                
                if column_order:
                    # Get all columns
                    all_columns = list(data_obj.columns)
                    # Use preferred order, add missing columns at end
                    ordered = [col for col in column_order if col in all_columns]
                    remaining = [col for col in all_columns if col not in column_order]
                    final_order = ordered + remaining
                    
                    # Reorder DataFrame columns
                    data_obj = data_obj[final_order]
                    logger.info(f"Reordered columns to: {final_order}")
        
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
        
        # Save to user storage if license key provided
        license_key = (
            request.headers.get('X-License-Key') or
            request.args.get('license_key') or
            data.get('license_key')
        )
        
        user_file_id = None
        if license_key:
            try:
                from redline.storage.user_storage import user_storage, STORAGE_AVAILABLE
                if STORAGE_AVAILABLE and user_storage:
                    # Read converted file
                    with open(output_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Save to user storage
                    file_info = user_storage.save_file(
                        license_key=license_key,
                        file_data=file_data,
                        filename=output_filename,
                        file_type=output_format,
                        metadata={
                            'converted_from': input_file,
                            'original_format': format_type,
                            'converted_via': 'web_converter',
                            'records': len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0
                        }
                    )
                    user_file_id = file_info.get('file_id')
                    logger.info(f"Saved converted file to user storage for license {license_key[:8]}...")
            except Exception as e:
                logger.warning(f"Failed to save to user storage: {str(e)}")
                # Don't fail the conversion if storage fails
        
        result = {
            'message': 'File converted successfully',
            'input_file': input_file,
            'output_file': output_filename,
            'output_format': output_format,
            'output_path': output_path,
            'file_size': file_stat.st_size,
            'records': len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0,
            'original_records': original_rows,
            'user_file_id': user_file_id,  # ID in user storage if saved
            'cleaning_applied': remove_duplicates or (handle_missing and handle_missing != 'none') or clean_column_names,
            'cleaning_stats': cleaning_stats
        }
        
        return jsonify(result)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error converting file: {error_msg}")
        logger.debug(f"Exception traceback:\n{traceback.format_exc()}")
        return jsonify({
            'error': error_msg,
            'exception_type': type(e).__name__
        }), 500

