"""
Batch file conversion routes for VarioSync Web GUI.
Handles multiple file format conversion operations.
"""

from flask import Blueprint, request, jsonify, g
import logging
import os
import pandas as pd
import traceback
from ..utils.converter_helpers import find_input_file_path, adjust_output_filename, validate_file_before_conversion
from redline.auth.supabase_auth import auth_manager

converter_batch_bp = Blueprint('converter_batch', __name__)
logger = logging.getLogger(__name__)

@converter_batch_bp.route('/batch-convert', methods=['POST'])
@auth_manager.require_auth
def batch_convert():
    """Convert multiple files in batch. Requires JWT authentication."""
    # Get authenticated user from g (set by @require_auth decorator)
    user_id = getattr(g, 'user_id', None)
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Batch convert request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Batch convert request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate files list
    files = data.get('files', [])

    if not files:
        logger.warning("Batch convert request with no files")
        return jsonify({'error': 'No files provided for conversion'}), 400

    if not isinstance(files, list):
        logger.error(f"Batch convert request files field has invalid type: {type(files)}")
        return jsonify({'error': 'files must be an array'}), 400

    if len(files) == 0:
        logger.warning("Batch convert request with empty files array")
        return jsonify({'error': 'files array cannot be empty'}), 400

    if len(files) > 100:
        logger.warning(f"Batch convert request with too many files: {len(files)}")
        return jsonify({'error': 'Too many files. Maximum 100 files per batch'}), 400

    # Validate overwrite flag
    overwrite = data.get('overwrite', False)
    if not isinstance(overwrite, bool):
        logger.warning(f"Batch convert request has invalid overwrite type: {type(overwrite)}, defaulting to False")
        overwrite = False

    logger.info(f"Processing batch conversion request: {len(files)} file(s), overwrite={overwrite}")

    # Validate data directory
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return jsonify({'error': 'Data directory not configured', 'code': 'DATA_DIR_NOT_FOUND'}), 500

    results = []
    errors = []

    for idx, file_config in enumerate(files, 1):
        # Validate file_config is a dict
        if not isinstance(file_config, dict):
            logger.error(f"File {idx}/{len(files)} has invalid type: {type(file_config)}")
            errors.append({
                'index': idx,
                'error': 'File configuration must be an object',
                'error_type': 'invalid_config_type'
            })
            continue

        # Extract and validate fields
        input_file = file_config.get('input_file')
        output_format = file_config.get('output_format')
        output_filename = file_config.get('output_filename')

        # Validate required fields presence
        if not input_file:
            logger.warning(f"File {idx}/{len(files)} missing input_file field")
            errors.append({
                'index': idx,
                'error': 'input_file is required',
                'error_type': 'missing_input_file'
            })
            continue

        if not output_format:
            logger.warning(f"File {idx}/{len(files)} ({input_file}) missing output_format field")
            errors.append({
                'index': idx,
                'input_file': input_file,
                'error': 'output_format is required',
                'error_type': 'missing_output_format'
            })
            continue

        if not output_filename:
            logger.warning(f"File {idx}/{len(files)} ({input_file}) missing output_filename field")
            errors.append({
                'index': idx,
                'input_file': input_file,
                'error': 'output_filename is required',
                'error_type': 'missing_output_filename'
            })
            continue

        # Validate field types
        if not isinstance(input_file, str):
            logger.error(f"File {idx}/{len(files)} input_file has invalid type: {type(input_file)}")
            errors.append({
                'index': idx,
                'input_file': str(input_file),
                'error': 'input_file must be a string',
                'error_type': 'invalid_input_file_type'
            })
            continue

        if not isinstance(output_format, str):
            logger.error(f"File {idx}/{len(files)} ({input_file}) output_format has invalid type: {type(output_format)}")
            errors.append({
                'index': idx,
                'input_file': input_file,
                'error': 'output_format must be a string',
                'error_type': 'invalid_output_format_type'
            })
            continue

        if not isinstance(output_filename, str):
            logger.error(f"File {idx}/{len(files)} ({input_file}) output_filename has invalid type: {type(output_filename)}")
            errors.append({
                'index': idx,
                'input_file': input_file,
                'error': 'output_filename must be a string',
                'error_type': 'invalid_output_filename_type'
            })
            continue

        # Validate output format
        valid_formats = ['csv', 'json', 'parquet', 'feather', 'excel', 'txt', 'duckdb']
        if output_format not in valid_formats:
            logger.warning(f"File {idx}/{len(files)} ({input_file}) has invalid output_format: {output_format}")
            errors.append({
                'index': idx,
                'input_file': input_file,
                'error': f'Invalid output_format. Must be one of: {", ".join(valid_formats)}',
                'error_type': 'invalid_output_format'
            })
            continue

        # Security check: prevent path traversal
        for filename, field_name in [(input_file, 'input_file'), (output_filename, 'output_filename')]:
            if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
                logger.warning(f"File {idx}/{len(files)} has suspicious {field_name}: {filename}")
                errors.append({
                    'index': idx,
                    'input_file': input_file,
                    'error': f'Invalid {field_name} format (path traversal detected)',
                    'error_type': 'path_traversal'
                })
                continue

        logger.info(f"Processing file {idx}/{len(files)}: {input_file} -> {output_format}")

        try:
            # Adjust output filename extension
            output_filename = adjust_output_filename(output_filename, output_format)
                
            # Check if output file exists
            output_path = os.path.join(data_dir, 'converted', output_filename)
                
            if os.path.exists(output_path) and not overwrite:
                errors.append({
                    'input_file': input_file,
                    'output_file': output_filename,
                    'error': 'Output file already exists'
                })
                continue
                
            # Find input file path
            input_path = find_input_file_path(input_file, data_dir)
                
            # Log debugging info
            logger.debug(f"Input file search: {input_file}")
                
            if not input_path or not os.path.exists(input_path):
                # Check if it's a system file
                from ..utils.converter_helpers import is_system_file
                if is_system_file(os.path.basename(input_file)):
                    error_msg = f'System files cannot be converted: {input_file}'
                    logger.warning(error_msg)
                    errors.append({
                        'input_file': input_file,
                        'error': error_msg,
                        'error_type': 'system_file'
                    })
                else:
                    error_msg = f'Input file not found: {input_file}'
                    logger.warning(f"{error_msg} (searched in: {data_dir})")
                    errors.append({
                        'input_file': input_file,
                        'error': error_msg,
                        'error_type': 'file_not_found',
                        'searched_paths': [
                            os.path.join(data_dir, input_file),
                            os.path.join(data_dir, 'downloaded', input_file),
                            os.path.join(data_dir, 'stooq', input_file)
                        ]
                    })
                continue
                
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
                errors.append({
                    'input_file': input_file,
                    'error': error_msg,
                    'error_type': 'validation_failed',
                    'validation_details': validation_details
                })
                continue
                
            # Log validation success with details
            if validation_details.get('file_size'):
                logger.info(f"File validation passed: {input_file} "
                          f"(size: {validation_details['file_size']} bytes, "
                          f"format: {format_type}, "
                          f"encoding: {validation_details.get('encoding', 'N/A')})")
                
            from redline.core.format_converter import FormatConverter
            converter = FormatConverter()
                
            # Load and convert
            logger.info(f"Loading file {input_file} as {format_type} format...")
            try:
                data_obj = converter.load_file_by_type(input_path, format_type)
            except Exception as load_error:
                error_msg = f"Error loading file: {str(load_error)}"
                logger.error(f"Failed to load {input_file}: {error_msg}")
                logger.debug(f"Load error traceback:\n{traceback.format_exc()}")
                errors.append({
                    'input_file': input_file,
                    'error': error_msg,
                    'error_type': 'load_error',
                    'format_attempted': format_type,
                    'file_path': input_path,
                    'file_size': validation_details.get('file_size', 'unknown')
                })
                continue
                
            if data_obj is None:
                error_msg = f"File loaded but returned None: {input_file}"
                logger.error(error_msg)
                errors.append({
                    'input_file': input_file,
                    'error': error_msg,
                    'error_type': 'empty_result',
                    'format_attempted': format_type,
                    'file_path': input_path,
                    'file_size': validation_details.get('file_size', 'unknown')
                })
                continue
                
            if hasattr(data_obj, 'empty') and data_obj.empty:
                error_msg = f"File loaded but contains no data: {input_file}"
                logger.warning(error_msg)
                logger.debug(f"Data object type: {type(data_obj)}, shape: {getattr(data_obj, 'shape', 'N/A')}")
                errors.append({
                    'input_file': input_file,
                    'error': error_msg,
                    'error_type': 'empty_data',
                    'format_attempted': format_type,
                    'file_path': input_path,
                    'file_size': validation_details.get('file_size', 'unknown')
                })
                continue
                
            logger.info(f"Successfully loaded {input_file}: {len(data_obj)} rows")
                
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            logger.info(f"Saving converted file to {output_path}...")
            converter.save_file_by_type(data_obj, output_path, output_format)
                
            file_stat = os.stat(output_path)
            logger.info(f"Successfully converted {input_file} to {output_filename} ({file_stat.st_size} bytes)")
                
            results.append({
                'input_file': input_file,
                'output_file': output_filename,
                'output_format': output_format,
                'file_size': file_stat.st_size,
                'records': len(data_obj) if isinstance(data_obj, pd.DataFrame) else 0,
                'success': True
            })

        except ImportError as e:
            logger.error(f"Import error processing {input_file}: {str(e)}")
            errors.append({
                'input_file': input_file,
                'error': f'Import error: {str(e)}',
                'error_type': 'import_error',
                'exception_type': type(e).__name__
            })
        except PermissionError as e:
            logger.error(f"Permission denied processing {input_file}: {str(e)}")
            errors.append({
                'input_file': input_file,
                'error': f'Permission denied: {str(e)}',
                'error_type': 'permission_denied',
                'exception_type': type(e).__name__
            })
        except OSError as e:
            logger.error(f"OS error processing {input_file}: {str(e)}")
            errors.append({
                'input_file': input_file,
                'error': f'File system error: {str(e)}',
                'error_type': 'os_error',
                'exception_type': type(e).__name__
            })
        except KeyError as e:
            logger.error(f"Missing key processing {input_file}: {str(e)}")
            errors.append({
                'input_file': input_file,
                'error': f'Missing data: {str(e)}',
                'error_type': 'key_error',
                'exception_type': type(e).__name__
            })
        except ValueError as e:
            logger.error(f"Value error processing {input_file}: {str(e)}")
            errors.append({
                'input_file': input_file,
                'error': f'Invalid data: {str(e)}',
                'error_type': 'value_error',
                'exception_type': type(e).__name__
            })
        except Exception as e:
            logger.error(f"Unexpected error processing {input_file}: {str(e)}")
            logger.debug(f"Exception traceback:\n{traceback.format_exc()}")
            errors.append({
                'input_file': input_file,
                'error': f'Unexpected error: {str(e)}',
                'error_type': 'unexpected_error',
                'exception_type': type(e).__name__
            })

    logger.info(f"Batch conversion completed: {len(results)} successful, {len(errors)} failed")

    return jsonify({
        'message': f'Batch conversion completed. {len(results)} successful, {len(errors)} failed.',
        'results': results,
        'errors': errors,
        'total_files': len(files),
        'successful': len(results),
        'failed': len(errors)
    })

