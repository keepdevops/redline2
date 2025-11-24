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
    try:
        # Check multiple locations for the file
        data_dir = os.path.join(os.getcwd(), 'data')
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
            return jsonify({'error': 'File not found', 'filename': filename}), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', DEFAULT_PAGE_SIZE, type=int)
        
        # Load data
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
        # Detect format from file extension
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        data = converter.load_file_by_type(data_path, format_type)
        
        if isinstance(data, pd.DataFrame):
            # Convert to records for pagination
            all_records = data.to_dict('records')
            
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
        
        # Return normal JSON; Flask-Compress handles compression
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error getting data preview for {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500


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
    except Exception as e:
        logger.error(f"Quick stats failed for {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500


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
    except Exception as e:
        logger.error(f"Quick stats failed for {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_data_bp.route('/download/<ticker>', methods=['POST'])
@rate_limit("30 per hour")
def download_data(ticker):
    """Download financial data for a ticker."""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        source = data.get('source', 'yahoo')
        
        from redline.downloaders.yahoo_downloader import YahooDownloader
        
        downloader = YahooDownloader()
        result = downloader.download_single_ticker(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'message': f'Data downloaded for {ticker}',
            'ticker': ticker,
            'records': len(result) if result is not None else 0
        })
        
    except Exception as e:
        logger.error(f"Error downloading data for {ticker}: {str(e)}")
        return jsonify({'error': str(e)}), 500

