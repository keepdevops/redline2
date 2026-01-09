"""
API routes for file conversion operations.
Handles format conversion between different file types.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
from ..utils.api_helpers import rate_limit

api_convert_bp = Blueprint('api_convert', __name__)
logger = logging.getLogger(__name__)


@api_convert_bp.route('/convert', methods=['POST'])
@rate_limit("20 per hour")
def convert_file():
    """Convert file between formats."""
    # Get request data
    data = request.get_json()

    # Pre-validation with if-else
    if not data:
        logger.warning("Convert request with empty body")
        return jsonify({'error': 'Request body is required', 'code': 'EMPTY_BODY'}), 400

    if not isinstance(data, dict):
        logger.error(f"Convert request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object', 'code': 'INVALID_BODY_TYPE'}), 400

    input_file = data.get('input_file')
    output_format = data.get('output_format')
    output_file = data.get('output_file')

    # Validate required parameters
    if not input_file:
        logger.warning("Convert request missing input_file")
        return jsonify({'error': 'input_file is required', 'code': 'MISSING_INPUT_FILE'}), 400

    if not output_format:
        logger.warning("Convert request missing output_format")
        return jsonify({'error': 'output_format is required', 'code': 'MISSING_OUTPUT_FORMAT'}), 400

    if not output_file:
        logger.warning("Convert request missing output_file")
        return jsonify({'error': 'output_file is required', 'code': 'MISSING_OUTPUT_FILE'}), 400

    # Validate parameter types
    if not isinstance(input_file, str):
        logger.error(f"Convert request input_file has invalid type: {type(input_file)}")
        return jsonify({'error': 'input_file must be a string', 'code': 'INVALID_INPUT_FILE_TYPE'}), 400

    if not isinstance(output_format, str):
        logger.error(f"Convert request output_format has invalid type: {type(output_format)}")
        return jsonify({'error': 'output_format must be a string', 'code': 'INVALID_OUTPUT_FORMAT_TYPE'}), 400

    if not isinstance(output_file, str):
        logger.error(f"Convert request output_file has invalid type: {type(output_file)}")
        return jsonify({'error': 'output_file must be a string', 'code': 'INVALID_OUTPUT_FILE_TYPE'}), 400

    # Security validation
    if '..' in input_file or '..' in output_file:
        logger.warning(f"Convert request with path traversal attempt: {input_file} -> {output_file}")
        return jsonify({'error': 'Invalid file path (path traversal not allowed)', 'code': 'PATH_TRAVERSAL'}), 400

    logger.info(f"Processing convert request: {input_file} -> {output_file} ({output_format})")

    # Import required modules
    try:
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
    except ImportError as e:
        logger.error(f"Failed to import required modules: {str(e)}")
        return jsonify({'error': 'Required modules not available', 'code': 'IMPORT_ERROR'}), 500

    converter = FormatConverter()

    # Determine input file path - check both root data directory and downloaded subdirectory
    data_dir = os.path.join(os.getcwd(), 'data')

    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return jsonify({'error': 'Data directory not configured', 'code': 'DATA_DIR_NOT_FOUND'}), 500

    input_path = None

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
        logger.warning(f"Input file not found: {input_file}")
        return jsonify({'error': 'Input file not found', 'input_file': input_file, 'code': 'FILE_NOT_FOUND'}), 404

    # Validate file is readable
    if not os.access(input_path, os.R_OK):
        logger.error(f"Input file not readable: {input_path}")
        return jsonify({'error': 'Input file is not readable', 'code': 'FILE_NOT_READABLE'}), 403

    # Detect format from file extension
    ext = os.path.splitext(input_path)[1].lower()
    if not ext:
        logger.warning(f"No file extension for input file: {input_file}")
        ext = '.csv'  # Default to CSV

    format_type = EXT_TO_FORMAT.get(ext, 'csv')
    logger.debug(f"Detected input format: {format_type}")

    # Load data - Note: File I/O requires try-except for external file operation errors
    try:
        data_obj = converter.load_file_by_type(input_path, format_type)
    except FileNotFoundError as e:
        logger.error(f"File not found loading {input_file}: {str(e)}")
        return jsonify({'error': 'Input file not found', 'code': 'FILE_NOT_FOUND'}), 404
    except PermissionError as e:
        logger.error(f"Permission denied loading {input_file}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except IOError as e:
        logger.error(f"I/O error loading {input_file}: {str(e)}")
        return jsonify({'error': 'I/O error reading input file', 'code': 'IO_ERROR'}), 500
    except pd.errors.EmptyDataError as e:
        logger.warning(f"Empty input file {input_file}: {str(e)}")
        return jsonify({'error': 'Input file is empty', 'code': 'EMPTY_FILE'}), 400
    except pd.errors.ParserError as e:
        logger.error(f"Parse error loading {input_file}: {str(e)}")
        return jsonify({'error': 'Failed to parse input file', 'code': 'PARSE_ERROR'}), 400
    except ValueError as e:
        logger.error(f"Value error loading {input_file}: {str(e)}")
        return jsonify({'error': f'Invalid input format: {str(e)}', 'code': 'INVALID_FORMAT'}), 400
    except KeyError as e:
        logger.error(f"Missing key loading {input_file}: {str(e)}")
        return jsonify({'error': f'Invalid data structure: {str(e)}', 'code': 'KEY_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error loading {input_file}: {type(e).__name__}: {str(e)}")
        return jsonify({'error': f'Failed to load input file: {str(e)}', 'code': 'LOAD_ERROR'}), 500

    # Validate data was loaded
    if data_obj is None:
        logger.error(f"Converter returned None for {input_file}")
        return jsonify({'error': 'Failed to load input file', 'code': 'NO_DATA'}), 500

    # Aggressive cleaning during conversion: clean column names, remove unnamed columns, etc.
    if isinstance(data_obj, pd.DataFrame):
        try:
            from redline.web.utils.data_helpers import clean_dataframe_columns
        except ImportError as e:
            logger.warning(f"Failed to import data_helpers for cleaning: {str(e)}")
        else:
            try:
                data_obj = clean_dataframe_columns(data_obj)
                logger.info(f"Cleaned columns during API conversion for {input_file}")
            except Exception as clean_error:
                logger.warning(f"Error during column cleaning (non-fatal) for {input_file}: {str(clean_error)}")
                # Continue with conversion anyway

    # Convert and save - Note: File I/O requires try-except
    try:
        converter.save_file_by_type(data_obj, output_file, output_format)
    except PermissionError as e:
        logger.error(f"Permission denied saving {output_file}: {str(e)}")
        return jsonify({'error': 'Permission denied saving output file', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error saving {output_file}: {str(e)}")
        return jsonify({'error': f'Failed to save output file: {str(e)}', 'code': 'OS_ERROR'}), 500
    except IOError as e:
        logger.error(f"I/O error saving {output_file}: {str(e)}")
        return jsonify({'error': 'I/O error writing output file', 'code': 'IO_ERROR'}), 500
    except ValueError as e:
        logger.error(f"Value error saving {output_file}: {str(e)}")
        return jsonify({'error': f'Invalid output format: {str(e)}', 'code': 'INVALID_OUTPUT_FORMAT'}), 400
    except KeyError as e:
        logger.error(f"Missing key saving {output_file}: {str(e)}")
        return jsonify({'error': f'Invalid data structure: {str(e)}', 'code': 'KEY_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error saving {output_file}: {type(e).__name__}: {str(e)}")
        return jsonify({'error': f'Failed to save output file: {str(e)}', 'code': 'SAVE_ERROR'}), 500

    logger.info(f"Successfully converted {input_file} to {output_file} ({output_format})")
    return jsonify({
        'success': True,
        'message': 'File converted successfully',
        'input_file': input_file,
        'output_file': output_file,
        'output_format': output_format
    })

