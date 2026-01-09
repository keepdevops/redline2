"""
File merge routes for VarioSync Web GUI.
Handles merging multiple files into one during batch conversion.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
from ..utils.converter_helpers import (
    find_input_file_path, 
    adjust_output_filename,
    merge_dataframes
)

converter_merge_bp = Blueprint('converter_merge', __name__)
logger = logging.getLogger(__name__)

@converter_merge_bp.route('/batch-merge', methods=['POST'])
def batch_merge():
    """Merge multiple files into one during batch conversion."""
    # Pre-validation with if-else
    data = request.get_json()

    if not data:
        logger.warning("Batch merge request with empty body")
        return jsonify({'error': 'Request body is required', 'code': 'NO_BODY'}), 400

    if not isinstance(data, dict):
        logger.error(f"Batch merge request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object', 'code': 'INVALID_BODY_TYPE'}), 400

    files = data.get('files', [])
    output_format = data.get('output_format')
    output_filename = data.get('output_filename', 'merged_data')
    column_mappings = data.get('column_mappings', {})
    column_order = data.get('column_order')
    overwrite = data.get('overwrite', False)

    if not files:
        logger.warning("Batch merge request with no files")
        return jsonify({'error': 'No files provided for merge', 'code': 'NO_FILES'}), 400

    if not isinstance(files, list):
        logger.error(f"Batch merge files must be a list, got {type(files)}")
        return jsonify({'error': 'files must be an array', 'code': 'INVALID_FILES_TYPE'}), 400

    if not output_format:
        logger.warning("Batch merge request missing output_format")
        return jsonify({'error': 'Output format is required', 'code': 'NO_OUTPUT_FORMAT'}), 400

    if not isinstance(output_format, str):
        logger.error(f"Output format must be a string, got {type(output_format)}")
        return jsonify({'error': 'Output format must be a string', 'code': 'INVALID_OUTPUT_FORMAT_TYPE'}), 400

    logger.info(f"Processing batch merge request: {len(files)} file(s), format={output_format}, overwrite={overwrite}")

    try:
        
        # Normalize format names (npz -> tensorflow for consistency)
        format_mapping = {
            'npz': 'tensorflow',
            'h5': 'keras',
            'arrow': 'pyarrow'
        }
        normalized_format = format_mapping.get(output_format.lower(), output_format.lower())
        
        data_dir = os.path.join(os.getcwd(), 'data')
        output_filename = adjust_output_filename(output_filename, normalized_format)
        output_path = os.path.join(data_dir, 'converted', output_filename)
        
        if os.path.exists(output_path) and not overwrite:
            return jsonify({
                'error': 'Output file already exists',
                'output_file': output_filename
            }), 400
        
        # Load all files
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        dataframes = []
        loaded_files = []
        errors = []
        
        for file_info in files:
            try:
                input_file = file_info.get('input_file') if isinstance(file_info, dict) else file_info
                
                # Check if it's a system file
                from ..utils.converter_helpers import is_system_file
                if is_system_file(os.path.basename(input_file)):
                    errors.append({
                        'input_file': input_file,
                        'error': 'System files cannot be merged'
                    })
                    continue
                
                # Check in converted directory first (for merging converted files)
                converted_path = os.path.join(data_dir, 'converted', input_file)
                if os.path.exists(converted_path):
                    input_path = converted_path
                else:
                    input_path = find_input_file_path(input_file, data_dir)
                if not input_path or not os.path.exists(input_path):
                    errors.append({
                        'input_file': input_file,
                        'error': 'File not found'
                    })
                    continue
                
                ext = os.path.splitext(input_path)[1].lower()
                format_type = EXT_TO_FORMAT.get(ext, 'csv')
                
                # Skip system/config files that shouldn't be merged
                filename = os.path.basename(input_path)
                if filename in ['custom_apis.json', 'api_keys.json', 'data_config.ini', 'config.ini']:
                    errors.append({
                        'input_file': input_file,
                        'error': f'Skipping system/config file: {filename}'
                    })
                    continue
                
                data_obj = converter.load_file_by_type(input_path, format_type)
                if data_obj is None or (hasattr(data_obj, 'empty') and data_obj.empty):
                    errors.append({
                        'input_file': input_file,
                        'error': 'Failed to load file or file is empty'
                    })
                    continue
                
                if isinstance(data_obj, pd.DataFrame):
                    dataframes.append(data_obj)
                    loaded_files.append(input_file)
                else:
                    errors.append({
                        'input_file': input_file,
                        'error': 'Unsupported data type for merge'
                    })

            except ImportError as e:
                logger.error(f"Import error loading file {file_info}: {str(e)}")
                errors.append({
                    'input_file': file_info if isinstance(file_info, str) else file_info.get('input_file', 'unknown'),
                    'error': f'Import error: {str(e)}',
                    'error_type': 'import_error'
                })
            except PermissionError as e:
                logger.error(f"Permission denied loading file {file_info}: {str(e)}")
                errors.append({
                    'input_file': file_info if isinstance(file_info, str) else file_info.get('input_file', 'unknown'),
                    'error': f'Permission denied: {str(e)}',
                    'error_type': 'permission_denied'
                })
            except OSError as e:
                logger.error(f"OS error loading file {file_info}: {str(e)}")
                errors.append({
                    'input_file': file_info if isinstance(file_info, str) else file_info.get('input_file', 'unknown'),
                    'error': f'File system error: {str(e)}',
                    'error_type': 'os_error'
                })
            except KeyError as e:
                logger.error(f"Missing key loading file {file_info}: {str(e)}")
                errors.append({
                    'input_file': file_info if isinstance(file_info, str) else file_info.get('input_file', 'unknown'),
                    'error': f'Missing data: {str(e)}',
                    'error_type': 'key_error'
                })
            except ValueError as e:
                logger.error(f"Value error loading file {file_info}: {str(e)}")
                errors.append({
                    'input_file': file_info if isinstance(file_info, str) else file_info.get('input_file', 'unknown'),
                    'error': f'Invalid data: {str(e)}',
                    'error_type': 'value_error'
                })
            except Exception as e:
                logger.error(f"Unexpected error loading file {file_info}: {str(e)}")
                errors.append({
                    'input_file': file_info if isinstance(file_info, str) else file_info.get('input_file', 'unknown'),
                    'error': f'Unexpected error: {str(e)}',
                    'error_type': 'unexpected_error'
                })
        
        if not dataframes:
            return jsonify({
                'error': 'No valid files could be loaded for merge',
                'errors': errors
            }), 400
        
        # Merge DataFrames
        try:
            # Parse column_order if it's a string (comma-separated)
            if column_order and isinstance(column_order, str):
                column_order = [col.strip() for col in column_order.split(',') if col.strip()]
            
            merged_df = merge_dataframes(dataframes, column_mappings, column_order=column_order)
            
            if merged_df.empty:
                return jsonify({
                    'error': 'Merged DataFrame is empty'
                }), 400
            
            # Save merged file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Check if numpy is available for npz/tensorflow format
            if normalized_format in ('tensorflow', 'npz'):
                try:
                    import numpy as np
                except ImportError:
                    return jsonify({
                        'error': 'NumPy is required for .npz format but is not available',
                        'suggestion': 'Please install numpy: pip install numpy'
                    }), 500
            
            try:
                converter.save_file_by_type(merged_df, output_path, normalized_format)
            except ImportError as e:
                logger.error(f"Import error saving file to {output_path}: {str(e)}")
                return jsonify({
                    'error': f'Import error saving file: {str(e)}',
                    'code': 'IMPORT_ERROR',
                    'output_format': normalized_format,
                    'errors': errors
                }), 500
            except PermissionError as e:
                logger.error(f"Permission denied saving file to {output_path}: {str(e)}")
                return jsonify({
                    'error': 'Permission denied saving file',
                    'code': 'PERMISSION_DENIED',
                    'output_format': normalized_format,
                    'errors': errors
                }), 403
            except OSError as e:
                logger.error(f"OS error saving file to {output_path}: {str(e)}")
                return jsonify({
                    'error': f'File system error saving file: {str(e)}',
                    'code': 'OS_ERROR',
                    'output_format': normalized_format,
                    'errors': errors
                }), 500
            except Exception as save_error:
                logger.error(f"Unexpected error saving file to {output_path}: {str(save_error)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return jsonify({
                    'error': f'Failed to save merged file: {str(save_error)}',
                    'code': 'SAVE_ERROR',
                    'output_format': normalized_format,
                    'errors': errors
                }), 500
            
            if not os.path.exists(output_path):
                return jsonify({
                    'error': 'File was not created after save operation',
                    'output_path': output_path,
                    'errors': errors
                }), 500
            
            file_stat = os.stat(output_path)
            
            return jsonify({
                'success': True,
                'message': f'Successfully merged {len(loaded_files)} files',
                'output_file': output_filename,
                'output_format': normalized_format,
                'file_size': file_stat.st_size,
                'total_records': len(merged_df),
                'columns': list(merged_df.columns),
                'loaded_files': loaded_files,
                'errors': errors
            })

        except ImportError as e:
            logger.error(f"Import error merging files: {str(e)}")
            return jsonify({
                'error': f'Import error: {str(e)}',
                'code': 'IMPORT_ERROR',
                'errors': errors
            }), 500
        except PermissionError as e:
            logger.error(f"Permission denied merging files: {str(e)}")
            return jsonify({
                'error': 'Permission denied',
                'code': 'PERMISSION_DENIED',
                'errors': errors
            }), 403
        except OSError as e:
            logger.error(f"OS error merging files: {str(e)}")
            return jsonify({
                'error': f'File system error: {str(e)}',
                'code': 'OS_ERROR',
                'errors': errors
            }), 500
        except KeyError as e:
            logger.error(f"Missing key merging files: {str(e)}")
            return jsonify({
                'error': f'Missing data: {str(e)}',
                'code': 'KEY_ERROR',
                'errors': errors
            }), 500
        except ValueError as e:
            logger.error(f"Value error merging files: {str(e)}")
            return jsonify({
                'error': f'Invalid data: {str(e)}',
                'code': 'VALUE_ERROR',
                'errors': errors
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error merging files: {str(e)}")
            return jsonify({
                'error': f'Failed to merge files: {str(e)}',
                'code': 'MERGE_ERROR',
                'errors': errors
            }), 500

    except ImportError as e:
        logger.error(f"Import error in batch merge: {str(e)}")
        return jsonify({'error': 'Import error', 'code': 'IMPORT_ERROR'}), 500
    except PermissionError as e:
        logger.error(f"Permission denied in batch merge: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except OSError as e:
        logger.error(f"OS error in batch merge: {str(e)}")
        return jsonify({'error': 'File system error', 'code': 'OS_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing key in batch merge: {str(e)}")
        return jsonify({'error': f'Missing data: {str(e)}', 'code': 'KEY_ERROR'}), 500
    except ValueError as e:
        logger.error(f"Value error in batch merge: {str(e)}")
        return jsonify({'error': f'Invalid data: {str(e)}', 'code': 'VALUE_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error in batch merge: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

