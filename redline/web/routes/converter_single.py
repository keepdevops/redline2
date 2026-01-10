"""
Single file conversion routes for VarioSync Web GUI.
Handles individual file format conversion operations.
"""

from flask import Blueprint, request, jsonify, g
import logging
import os
import pandas as pd
import traceback
from ..utils.converter_helpers import find_input_file_path, adjust_output_filename, validate_file_before_conversion
from redline.auth.supabase_auth import auth_manager

converter_single_bp = Blueprint('converter_single', __name__)
logger = logging.getLogger(__name__)

@converter_single_bp.route('/convert', methods=['POST'])
@auth_manager.require_auth
def convert_file():
    """Convert a single file format. Requires JWT authentication."""
    # Get authenticated user from g (set by @require_auth decorator)
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    """Convert file between formats - redirects to batch conversion."""
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Convert request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Convert request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate required fields
    input_file = data.get('input_file')
    output_format = data.get('output_format')
    output_filename = data.get('output_filename')
    overwrite = data.get('overwrite', False)

    if not input_file:
        logger.warning("Convert request missing input_file field")
        return jsonify({'error': 'input_file is required'}), 400

    if not output_format:
        logger.warning(f"Convert request missing output_format field for {input_file}")
        return jsonify({'error': 'output_format is required'}), 400

    if not output_filename:
        logger.warning(f"Convert request missing output_filename field for {input_file}")
        return jsonify({'error': 'output_filename is required'}), 400

    # Validate field types
    if not isinstance(input_file, str):
        logger.error(f"Convert request input_file has invalid type: {type(input_file)}")
        return jsonify({'error': 'input_file must be a string'}), 400

    if not isinstance(output_format, str):
        logger.error(f"Convert request output_format has invalid type: {type(output_format)}")
        return jsonify({'error': 'output_format must be a string'}), 400

    if not isinstance(output_filename, str):
        logger.error(f"Convert request output_filename has invalid type: {type(output_filename)}")
        return jsonify({'error': 'output_filename must be a string'}), 400

    # Validate output format
    valid_formats = ['csv', 'json', 'parquet', 'feather', 'excel', 'txt', 'duckdb']
    if output_format not in valid_formats:
        logger.warning(f"Convert request has invalid output_format: {output_format}")
        return jsonify({
            'error': f'Invalid output_format. Must be one of: {", ".join(valid_formats)}'
        }), 400

    # Security check: prevent path traversal
    for filename, field_name in [(input_file, 'input_file'), (output_filename, 'output_filename')]:
        if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
            logger.warning(f"Convert request with suspicious {field_name}: {filename}")
            return jsonify({'error': f'Invalid {field_name} format'}), 400

    logger.info(f"Processing convert request: input={input_file}, format={output_format}, output={output_filename}, overwrite={overwrite}")

    # Redirect single file conversion to batch conversion
    # Convert single file request to batch format
    try:
        from .converter_batch import batch_convert

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

    except ImportError as e:
        logger.error(f"Failed to import batch converter: {str(e)}")
        return jsonify({'error': 'Batch converter not available', 'code': 'IMPORT_ERROR'}), 500
    except PermissionError as e:
        logger.error(f"Permission denied during conversion: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error during conversion: {str(e)}")
        return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing key during conversion: {str(e)}")
        return jsonify({'error': f'Missing data: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except ValueError as e:
        logger.error(f"Value error during conversion: {str(e)}")
        return jsonify({'error': f'Invalid data: {str(e)}', 'code': 'VALUE_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error during conversion: {str(e)}")
        logger.debug(f"Exception traceback:\n{traceback.format_exc()}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

