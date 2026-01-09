"""
API routes for data operations.
Handles data preview, quick stats, and data downloads.
"""

from flask import Blueprint, request, jsonify
import logging
import os
import pandas as pd
from ..utils.api_helpers import rate_limit, paginate_data, DEFAULT_PAGE_SIZE

api_data_bp = Blueprint('api_data', __name__)
logger = logging.getLogger(__name__)


@api_data_bp.route('/data/<filename>', methods=['GET'])
def get_data_preview(filename):
    """Get paginated preview of data file with compression."""
    # Pre-validation with if-else
    if not filename:
        logger.warning("Data preview request with empty filename")
        return jsonify({'error': 'Filename is required', 'code': 'EMPTY_FILENAME'}), 400

    if not isinstance(filename, str):
        logger.error(f"Data preview request with invalid filename type: {type(filename)}")
        return jsonify({'error': 'Filename must be a string', 'code': 'INVALID_FILENAME_TYPE'}), 400

    if '..' in filename:
        logger.warning(f"Data preview request with path traversal attempt: {filename}")
        return jsonify({'error': 'Invalid filename (path traversal not allowed)', 'code': 'PATH_TRAVERSAL'}), 400

    # Check multiple locations for the file
    data_dir = os.path.join(os.getcwd(), 'data')

    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        return jsonify({'error': 'Data directory not configured', 'code': 'DATA_DIR_NOT_FOUND'}), 500

    data_path = None

    # Check in root data directory first
    root_path = os.path.join(data_dir, filename)
    if os.path.exists(root_path):
        data_path = root_path
    else:
        # Check in downloaded directory
        downloaded_path = os.path.join(data_dir, 'downloaded', filename)
        if os.path.exists(downloaded_path):
            data_path = downloaded_path
        else:
            # Check in converted directory (and subdirectories)
            converted_dir = os.path.join(data_dir, 'converted')
            # Try common direct path first
            converted_path = os.path.join(converted_dir, filename)
            if os.path.exists(converted_path):
                data_path = converted_path
            else:
                # Walk converted/ recursively to find the file
                if os.path.exists(converted_dir):
                    for root, dirs, files in os.walk(converted_dir):
                        if filename in files:
                            data_path = os.path.join(root, filename)
                            break

    if not data_path or not os.path.exists(data_path):
        logger.warning(f"Data file not found: {filename}")
        return jsonify({'error': 'File not found', 'filename': filename, 'code': 'FILE_NOT_FOUND'}), 404

    # Validate file is readable
    if not os.access(data_path, os.R_OK):
        logger.error(f"Data file not readable: {data_path}")
        return jsonify({'error': 'File is not readable', 'filename': filename, 'code': 'FILE_NOT_READABLE'}), 403

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', DEFAULT_PAGE_SIZE, type=int)

    # Validate pagination parameters
    if not isinstance(page, int) or page < 1:
        logger.warning(f"Invalid page parameter for {filename}: {page}")
        page = 1

    if not isinstance(per_page, int) or per_page < 1 or per_page > 10000:
        logger.warning(f"Invalid per_page parameter for {filename}: {per_page}")
        per_page = DEFAULT_PAGE_SIZE

    logger.debug(f"Loading data preview for {filename} (page={page}, per_page={per_page})")

    # Load data - Note: File I/O requires try-except for external file operation errors
    try:
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
    except ImportError as e:
        logger.error(f"Failed to import required modules for {filename}: {str(e)}")
        return jsonify({'error': 'Required modules not available', 'code': 'IMPORT_ERROR'}), 500

    converter = FormatConverter()

    # Detect format from file extension
    ext = os.path.splitext(data_path)[1].lower()
    if not ext:
        logger.warning(f"No file extension found for {filename}")
        ext = '.csv'  # Default to CSV

    format_type = EXT_TO_FORMAT.get(ext, 'csv')
    logger.debug(f"Detected format for {filename}: {format_type}")

    try:
        data = converter.load_file_by_type(data_path, format_type)
    except FileNotFoundError as e:
        logger.error(f"File not found loading {filename}: {str(e)}")
        return jsonify({'error': 'File not found', 'code': 'FILE_NOT_FOUND'}), 404
    except PermissionError as e:
        logger.error(f"Permission denied loading {filename}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except IOError as e:
        logger.error(f"I/O error loading {filename}: {str(e)}")
        return jsonify({'error': 'I/O error reading file', 'code': 'IO_ERROR'}), 500
    except pd.errors.EmptyDataError as e:
        logger.warning(f"Empty file {filename}: {str(e)}")
        return jsonify({'error': 'File is empty', 'code': 'EMPTY_FILE'}), 400
    except pd.errors.ParserError as e:
        logger.error(f"Parse error loading {filename}: {str(e)}")
        return jsonify({'error': 'Failed to parse file', 'code': 'PARSE_ERROR'}), 400
    except ValueError as e:
        logger.error(f"Value error loading {filename}: {str(e)}")
        return jsonify({'error': f'Invalid file format: {str(e)}', 'code': 'INVALID_FORMAT'}), 400
    except KeyError as e:
        logger.error(f"Missing key loading {filename}: {str(e)}")
        return jsonify({'error': f'Invalid data structure: {str(e)}', 'code': 'KEY_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error loading {filename}: {type(e).__name__}: {str(e)}")
        return jsonify({'error': f'Failed to load file: {str(e)}', 'code': 'LOAD_ERROR'}), 500

    # Validate data was loaded
    if data is None:
        logger.error(f"Converter returned None for {filename}")
        return jsonify({'error': 'Failed to load file data', 'code': 'NO_DATA'}), 500

    if isinstance(data, pd.DataFrame):
        # Validate DataFrame is not empty
        if data.empty:
            logger.warning(f"Loaded empty DataFrame for {filename}")
            return jsonify({
                'columns': list(data.columns),
                'total_rows': 0,
                'filename': filename,
                'preview': [],
                'pagination': {'page': 1, 'per_page': per_page, 'total': 0, 'pages': 0, 'has_next': False, 'has_prev': False}
            })

        # Convert to records for pagination
        try:
            all_records = data.to_dict('records')
        except AttributeError as e:
            logger.error(f"Attribute error converting DataFrame to records for {filename}: {str(e)}")
            return jsonify({'error': 'Invalid data structure', 'code': 'ATTRIBUTE_ERROR'}), 500
        except TypeError as e:
            logger.error(f"Type error converting DataFrame to records for {filename}: {str(e)}")
            return jsonify({'error': 'Invalid data type', 'code': 'TYPE_ERROR'}), 500
        except Exception as e:
            logger.error(f"Unexpected error converting DataFrame to records for {filename}: {str(e)}")
            return jsonify({'error': 'Failed to process data', 'code': 'CONVERSION_ERROR'}), 500

        # Paginate the data
        paginated_result = paginate_data(all_records, page, per_page)

        response_data = {
            'columns': list(data.columns),
            'total_rows': len(data),
            'filename': filename,
            'preview': paginated_result['data'],
            'pagination': paginated_result['pagination']
        }
    else:
        # Handle non-DataFrame data
        preview = str(data)[:1000]  # Truncate for non-DataFrame data
        response_data = {
            'columns': [],
            'total_rows': 0,
            'filename': filename,
            'preview': preview,
            'pagination': {'page': 1, 'per_page': 1, 'total': 1, 'pages': 1, 'has_next': False, 'has_prev': False}
        }

    logger.info(f"Successfully loaded data preview for {filename} ({response_data['total_rows']} rows)")
    # Return normal JSON; Flask-Compress handles compression
    return jsonify(response_data)


@api_data_bp.route('/data/quick/<path:filename>', methods=['GET'])
def get_file_quick_stats(filename: str):
    """
    Return quick stats (columns, row count, preview) for a file located under
    data/, data/downloaded/, or data/converted/.
    Supports CSV, TXT, JSON, Parquet, Feather, and DuckDB.
    """
    try:
        from redline.core.schema import EXT_TO_FORMAT
        base_dir = os.path.join(os.getcwd(), 'data')

        candidates = [
            os.path.join(base_dir, filename),
            os.path.join(base_dir, 'downloaded', filename),
            os.path.join(base_dir, 'converted', filename),
        ]
        file_path = next((p for p in candidates if os.path.exists(p)), None)
        if not file_path:
            return jsonify({'error': 'File not found', 'filename': filename, 'searched': candidates}), 404

        ext = os.path.splitext(file_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')

        # Load data with robust fallbacks
        df = None
        if format_type == 'csv':
            df = pd.read_csv(file_path)
        elif format_type == 'txt':
            for sep in [',', '\t', ';', ' ', '|']:
                try:
                    tmp = pd.read_csv(file_path, sep=sep)
                    if len(tmp.columns) > 1:
                        df = tmp
                        break
                except Exception:
                    continue
            if df is None:
                df = pd.read_fwf(file_path)
        elif format_type == 'parquet':
            df = pd.read_parquet(file_path)
        elif format_type == 'feather':
            df = pd.read_feather(file_path)
        elif format_type == 'json':
            try:
                df = pd.read_json(file_path, lines=True)
            except Exception:
                df = pd.read_json(file_path)
        elif format_type == 'duckdb':
            import duckdb
            conn = duckdb.connect(file_path)
            try:
                tables = conn.execute('SHOW TABLES').fetchall()
                if not tables:
                    return jsonify({'error': 'No tables found in DuckDB file'}), 404
                table_name = tables[0][0]
                df = conn.execute(f'SELECT * FROM {table_name} LIMIT 1000').fetchdf()
            finally:
                conn.close()
        elif format_type == 'tensorflow' or format_type == 'npz':
            import numpy as np
            loaded = np.load(file_path)
            if 'data' in loaded:
                df = pd.DataFrame(loaded['data'])
            else:
                # Get first array from the npz file
                first_key = list(loaded.keys())[0]
                df = pd.DataFrame(loaded[first_key])
        elif format_type == 'keras' or format_type == 'h5':
            try:
                import tensorflow as tf
                model = tf.keras.models.load_model(file_path)
                # For Keras models, return model info instead of DataFrame
                return jsonify({
                    'filename': filename,
                    'file_path': file_path,
                    'format': format_type,
                    'type': 'keras_model',
                    'message': 'Keras model loaded. Use Analysis tab for model operations.',
                    'model_summary': str(model.summary()) if hasattr(model, 'summary') else 'Model loaded successfully'
                })
            except ImportError:
                return jsonify({'error': 'TensorFlow is required to load .h5 files'}), 400
        elif format_type == 'pyarrow' or format_type == 'arrow':
            try:
                import pyarrow as pa
                with pa.ipc.open_file(file_path) as reader:
                    df = reader.read_all().to_pandas()
            except ImportError:
                return jsonify({'error': 'PyArrow is required to load .arrow files'}), 400
            except Exception as e:
                return jsonify({'error': f'Error loading Arrow file: {str(e)}'}), 400
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400

        if df is None or not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data'}), 400

        # Minimal cleanup: drop Unnamed columns only
        unnamed = [c for c in df.columns if str(c).startswith('Unnamed:')]
        if unnamed:
            df = df.drop(columns=unnamed)

        return jsonify({
            'filename': filename,
            'file_path': file_path,
            'format': format_type,
            'columns': list(df.columns),
            'total_rows': int(len(df)),
            'preview': df.head(5).to_dict(orient='records')
        })
    except ImportError as e:
        logger.error(f"Import error getting quick stats for {filename}: {str(e)}")
        return jsonify({'error': f'Required module not available: {str(e)}', 'code': 'IMPORT_ERROR'}), 500
    except FileNotFoundError as e:
        logger.error(f"File not found getting quick stats for {filename}: {str(e)}")
        return jsonify({'error': 'File not found', 'code': 'FILE_NOT_FOUND'}), 404
    except PermissionError as e:
        logger.error(f"Permission denied getting quick stats for {filename}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except IOError as e:
        logger.error(f"I/O error getting quick stats for {filename}: {str(e)}")
        return jsonify({'error': 'I/O error reading file', 'code': 'IO_ERROR'}), 500
    except pd.errors.EmptyDataError as e:
        logger.warning(f"Empty file getting quick stats for {filename}: {str(e)}")
        return jsonify({'error': 'File is empty', 'code': 'EMPTY_FILE'}), 400
    except pd.errors.ParserError as e:
        logger.error(f"Parse error getting quick stats for {filename}: {str(e)}")
        return jsonify({'error': 'Failed to parse file', 'code': 'PARSE_ERROR'}), 400
    except ValueError as e:
        logger.error(f"Value error getting quick stats for {filename}: {str(e)}")
        return jsonify({'error': f'Invalid data: {str(e)}', 'code': 'VALUE_ERROR'}), 400
    except KeyError as e:
        logger.error(f"Missing key getting quick stats for {filename}: {str(e)}")
        return jsonify({'error': f'Invalid data structure: {str(e)}', 'code': 'KEY_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error getting quick stats for {filename}: {str(e)}")
        return jsonify({'error': str(e), 'code': 'QUICK_STATS_ERROR'}), 500


@api_data_bp.route('/data/quick-stats', methods=['POST'])
def get_file_quick_stats_post():
    """
    POST endpoint for quick stats that accepts filename and file_path in request body.
    Returns quick stats (columns, row count, preview) for a file.
    Supports CSV, TXT, JSON, Parquet, Feather, DuckDB, NPZ, H5, and Arrow.
    """
    try:
        data = request.get_json()
        filename = data.get('filename')
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        from redline.core.schema import EXT_TO_FORMAT
        base_dir = os.path.join(os.getcwd(), 'data')
        
        # Use file_path_hint if provided and exists, otherwise search
        file_path = None
        if file_path_hint and os.path.exists(file_path_hint):
            file_path = file_path_hint
        else:
            candidates = [
                os.path.join(base_dir, filename),
                os.path.join(base_dir, 'downloaded', filename),
                os.path.join(base_dir, 'stooq', filename),
                os.path.join(base_dir, 'uploads', filename),
                os.path.join(base_dir, 'converted', filename),
            ]
            # Also search in converted subdirectories
            converted_dir = os.path.join(base_dir, 'converted')
            if os.path.exists(converted_dir):
                for root, dirs, files in os.walk(converted_dir):
                    if filename in files:
                        candidates.append(os.path.join(root, filename))
            
            file_path = next((p for p in candidates if os.path.exists(p)), None)
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found', 'filename': filename}), 404

        ext = os.path.splitext(file_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')

        # Load data with robust fallbacks
        df = None
        if format_type == 'csv':
            df = pd.read_csv(file_path)
        elif format_type == 'txt':
            for sep in [',', '\t', ';', ' ', '|']:
                try:
                    tmp = pd.read_csv(file_path, sep=sep)
                    if len(tmp.columns) > 1:
                        df = tmp
                        break
                except Exception:
                    continue
            if df is None:
                df = pd.read_fwf(file_path)
        elif format_type == 'parquet':
            df = pd.read_parquet(file_path)
        elif format_type == 'feather':
            df = pd.read_feather(file_path)
        elif format_type == 'json':
            try:
                df = pd.read_json(file_path, lines=True)
            except Exception:
                df = pd.read_json(file_path)
        elif format_type == 'duckdb':
            import duckdb
            conn = duckdb.connect(file_path)
            try:
                tables = conn.execute('SHOW TABLES').fetchall()
                if not tables:
                    return jsonify({'error': 'No tables found in DuckDB file'}), 404
                table_name = tables[0][0]
                df = conn.execute(f'SELECT * FROM {table_name} LIMIT 1000').fetchdf()
            finally:
                conn.close()
        elif format_type in ('tensorflow', 'npz'):
            import numpy as np
            loaded = np.load(file_path, allow_pickle=True)
            if 'data' in loaded:
                data_array = loaded['data']
                if 'columns' in loaded:
                    columns = loaded['columns'].tolist()
                    df = pd.DataFrame(data_array, columns=columns)
                else:
                    df = pd.DataFrame(data_array, columns=[f'col_{i}' for i in range(data_array.shape[1])])
                # Convert object columns to numeric where possible
                for col in df.columns:
                    if df[col].dtype == 'object':
                        numeric_series = pd.to_numeric(df[col], errors='coerce')
                        if numeric_series.notna().sum() > len(df) * 0.5:
                            df[col] = numeric_series
            else:
                first_key = list(loaded.keys())[0]
                df = pd.DataFrame(loaded[first_key])
                # Convert object columns to numeric where possible
                for col in df.columns:
                    if df[col].dtype == 'object':
                        numeric_series = pd.to_numeric(df[col], errors='coerce')
                        if numeric_series.notna().sum() > len(df) * 0.5:
                            df[col] = numeric_series
        elif format_type in ('keras', 'h5'):
            try:
                import tensorflow as tf
                model = tf.keras.models.load_model(file_path)
                return jsonify({
                    'filename': filename,
                    'file_path': file_path,
                    'format': format_type,
                    'type': 'keras_model',
                    'message': 'Keras model loaded. Use ML tab for model operations.',
                    'rows': 0,
                    'columns': 0,
                    'columns_list': []
                })
            except ImportError:
                return jsonify({'error': 'TensorFlow is required to load .h5 files'}), 400
        elif format_type in ('pyarrow', 'arrow'):
            try:
                import pyarrow as pa
                with pa.ipc.open_file(file_path) as reader:
                    df = reader.read_all().to_pandas()
            except ImportError:
                return jsonify({'error': 'PyArrow is required to load .arrow files'}), 400
            except Exception as e:
                return jsonify({'error': f'Error loading Arrow file: {str(e)}'}), 400
        else:
            from redline.core.format_converter import FormatConverter
            converter = FormatConverter()
            df = converter.load_file_by_type(file_path, format_type)

        if df is None or not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data'}), 400

        # Minimal cleanup: drop Unnamed columns only
        unnamed = [c for c in df.columns if str(c).startswith('Unnamed:')]
        if unnamed:
            df = df.drop(columns=unnamed)

        return jsonify({
            'filename': filename,
            'file_path': file_path,
            'format': format_type,
            'rows': int(len(df)),
            'columns': len(df.columns),
            'columns_list': list(df.columns),
            'preview': df.head(5).to_dict(orient='records')
        })
    except ImportError as e:
        logger.error(f"Import error getting quick stats POST for {filename}: {str(e)}")
        return jsonify({'error': f'Required module not available: {str(e)}', 'code': 'IMPORT_ERROR'}), 500
    except FileNotFoundError as e:
        logger.error(f"File not found getting quick stats POST for {filename}: {str(e)}")
        return jsonify({'error': 'File not found', 'code': 'FILE_NOT_FOUND'}), 404
    except PermissionError as e:
        logger.error(f"Permission denied getting quick stats POST for {filename}: {str(e)}")
        return jsonify({'error': 'Permission denied', 'code': 'PERMISSION_DENIED'}), 403
    except IOError as e:
        logger.error(f"I/O error getting quick stats POST for {filename}: {str(e)}")
        return jsonify({'error': 'I/O error reading file', 'code': 'IO_ERROR'}), 500
    except pd.errors.EmptyDataError as e:
        logger.warning(f"Empty file getting quick stats POST for {filename}: {str(e)}")
        return jsonify({'error': 'File is empty', 'code': 'EMPTY_FILE'}), 400
    except pd.errors.ParserError as e:
        logger.error(f"Parse error getting quick stats POST for {filename}: {str(e)}")
        return jsonify({'error': 'Failed to parse file', 'code': 'PARSE_ERROR'}), 400
    except ValueError as e:
        logger.error(f"Value error getting quick stats POST for {filename}: {str(e)}")
        return jsonify({'error': f'Invalid data: {str(e)}', 'code': 'VALUE_ERROR'}), 400
    except KeyError as e:
        logger.error(f"Missing key getting quick stats POST for {filename}: {str(e)}")
        return jsonify({'error': f'Invalid data structure: {str(e)}', 'code': 'KEY_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error getting quick stats POST for {filename}: {str(e)}")
        return jsonify({'error': str(e), 'code': 'QUICK_STATS_ERROR'}), 500


@api_data_bp.route('/download/<ticker>', methods=['POST'])
@rate_limit("30 per hour")
def download_data(ticker):
    """Download financial data for a ticker."""
    # Validate ticker parameter
    if not ticker:
        logger.warning("Download data request with empty ticker")
        return jsonify({'error': 'Ticker is required'}), 400

    if not isinstance(ticker, str):
        logger.error(f"Download data request with invalid ticker type: {type(ticker)}")
        return jsonify({'error': 'Ticker must be a string'}), 400

    ticker = ticker.strip().upper()

    if len(ticker) == 0:
        logger.warning("Download data request with empty ticker after strip")
        return jsonify({'error': 'Ticker cannot be empty'}), 400

    if len(ticker) > 20:
        logger.warning(f"Download data request with oversized ticker: {ticker}")
        return jsonify({'error': 'Ticker too long (max 20 characters)'}), 400

    # Get request body
    data = request.get_json() or {}

    # Validate optional parameters
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    source = data.get('source', 'yahoo')

    if source and not isinstance(source, str):
        logger.warning(f"Download data request for {ticker} has invalid source type: {type(source)}")
        source = 'yahoo'

    logger.info(f"Processing download request: ticker={ticker}, source={source}, dates={start_date} to {end_date}")

    # Import downloader
    try:
        from redline.downloaders.yahoo_downloader import YahooDownloader
    except ImportError as e:
        logger.error(f"Failed to import YahooDownloader: {str(e)}")
        return jsonify({'error': 'Downloader module not available', 'code': 'IMPORT_ERROR'}), 500

    try:
        downloader = YahooDownloader()

        # Download data
        result = downloader.download_single_ticker(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )

        # Validate result
        if result is None:
            logger.warning(f"Download returned None for ticker: {ticker}")
            return jsonify({
                'error': 'No data found',
                'ticker': ticker,
                'message': f'No data available for {ticker}',
                'code': 'NO_DATA'
            }), 404

        records = len(result) if hasattr(result, '__len__') else 0
        logger.info(f"Successfully downloaded {records} records for {ticker}")

        return jsonify({
            'message': f'Data downloaded for {ticker}',
            'ticker': ticker,
            'records': records
        })

    except AttributeError as e:
        logger.error(f"Attribute error downloading {ticker}: {str(e)}")
        return jsonify({'error': 'Downloader configuration error', 'ticker': ticker, 'code': 'ATTRIBUTE_ERROR'}), 500
    except ValueError as e:
        logger.error(f"Value error downloading {ticker}: {str(e)}")
        return jsonify({'error': f'Invalid parameter: {str(e)}', 'ticker': ticker, 'code': 'VALUE_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error downloading {ticker}: {type(e).__name__}: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}', 'ticker': ticker, 'code': 'DOWNLOAD_ERROR'}), 500

