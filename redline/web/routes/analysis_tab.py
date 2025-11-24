"""
Analysis tab routes for REDLINE Web GUI
Main route handlers for analysis operations
"""

from flask import Blueprint, render_template, request, jsonify
import logging
import pandas as pd
import os
from ..utils.analysis_helpers import convert_numpy_types
from ..utils.data_helpers import clean_dataframe_columns
from .analysis_basic import perform_basic_analysis
from .analysis_financial import perform_financial_analysis
from .analysis_statistical import perform_statistical_analysis
from .analysis_correlation import perform_correlation_analysis

analysis_tab_bp = Blueprint('analysis_tab', __name__)
logger = logging.getLogger(__name__)


@analysis_tab_bp.route('/')
def analysis_tab():
    """Analysis tab main page."""
    return render_template('analysis_tab.html')


@analysis_tab_bp.route('/analyze', methods=['POST'])
def analyze_data():
    """Perform analysis on loaded data."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        analysis_type = data.get('analysis_type', 'basic')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
        # Determine file path - check multiple locations including converted files
        data_dir = os.path.join(os.getcwd(), 'data')
        data_path = None
        
        # If file_path is provided (from converted files), use it directly
        file_path_hint = data.get('file_path')
        if file_path_hint and os.path.exists(file_path_hint):
            data_path = file_path_hint
        else:
            # Check locations in order of priority (same as /data/load endpoint):
            # 1. Root data directory
            # 2. data/stooq directory (for Stooq downloads)
            # 3. data/downloaded directory (for other downloads)
            # 4. data/uploads directory (for uploaded files)
            # 5. data/converted directory (recursively, for converted files)
            search_paths = [
                os.path.join(data_dir, filename),
                os.path.join(data_dir, 'stooq', filename),
                os.path.join(data_dir, 'downloaded', filename),
                os.path.join(data_dir, 'uploads', filename)
            ]
            
            # Check converted directory recursively
            converted_dir = os.path.join(data_dir, 'converted')
            if os.path.exists(converted_dir):
                for root, dirs, files in os.walk(converted_dir):
                    if filename in files:
                        search_paths.append(os.path.join(root, filename))
            
            # Try each path
            for path in search_paths:
                if os.path.exists(path):
                    data_path = path
                    break
        
        if not data_path or not os.path.exists(data_path):
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        # Detect format from file extension (same as Tkinter)
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Use direct pandas loading for speed (same as data routes)
        if format_type == 'csv':
            df = pd.read_csv(data_path)
        elif format_type == 'txt':
            # Try different separators for TXT files
            df = None
            for sep in [',', '\t', ';', ' ', '|']:
                try:
                    test_df = pd.read_csv(data_path, sep=sep)
                    # Check if we got multiple columns (good parsing)
                    if len(test_df.columns) > 1:
                        df = test_df
                        break
                except:
                    continue
            
            if df is None:
                # If all separators fail, try reading as fixed-width
                df = pd.read_fwf(data_path)
        elif format_type == 'parquet':
            df = pd.read_parquet(data_path)
        elif format_type == 'feather':
            df = pd.read_feather(data_path)
        elif format_type == 'json':
            df = pd.read_json(data_path)
        elif format_type == 'duckdb':
            import duckdb
            conn = duckdb.connect(data_path)
            df = conn.execute("SELECT * FROM tickers_data").fetchdf()
            conn.close()
        elif format_type in ('tensorflow', 'npz'):
            import numpy as np
            # Use allow_pickle=True for .npz files that may contain object arrays
            loaded = np.load(data_path, allow_pickle=True)
            if 'data' in loaded:
                data_array = loaded['data']
                # Restore column names if they were saved
                if 'columns' in loaded:
                    columns = loaded['columns'].tolist()
                    df = pd.DataFrame(data_array, columns=columns)
                else:
                    # Fallback: create generic column names
                    df = pd.DataFrame(data_array, columns=[f'col_{i}' for i in range(data_array.shape[1])])
                
                # Convert object columns to numeric where possible (important for .npz files with mixed types)
                for col in df.columns:
                    if df[col].dtype == 'object':
                        # Try to convert to numeric
                        numeric_series = pd.to_numeric(df[col], errors='coerce')
                        # If most values converted successfully, use numeric type
                        if numeric_series.notna().sum() > len(df) * 0.5:  # More than 50% numeric
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
            # Keras models can't be analyzed as DataFrames
            return jsonify({'error': 'Keras model files (.h5) cannot be analyzed as data. Use the Analysis tab for model operations.'}), 400
        elif format_type in ('pyarrow', 'arrow'):
            try:
                import pyarrow as pa
                with pa.ipc.open_file(data_path) as reader:
                    df = reader.read_all().to_pandas()
            except ImportError:
                return jsonify({'error': 'PyArrow is required to load .arrow files'}), 400
            except Exception as e:
                return jsonify({'error': f'Error loading Arrow file: {str(e)}'}), 400
        else:
            # Fallback to converter for unsupported formats
            df = converter.load_file_by_type(data_path, format_type)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Clean up malformed CSV headers - remove unnamed/empty columns
        df = clean_dataframe_columns(df)
        
        analysis_result = {}
        
        if analysis_type == 'basic':
            analysis_result = perform_basic_analysis(df)
        elif analysis_type == 'financial':
            analysis_result = perform_financial_analysis(df)
        elif analysis_type == 'statistical':
            analysis_result = perform_statistical_analysis(df)
        elif analysis_type == 'correlation':
            analysis_result = perform_correlation_analysis(df)
        else:
            return jsonify({'error': f'Unknown analysis type: {analysis_type}'}), 400
        
        # Convert all numpy types in the result
        cleaned_result = convert_numpy_types(analysis_result)
        
        response_data = {
            'filename': filename,
            'analysis_type': analysis_type,
            'result': cleaned_result,
            'data_shape': df.shape,
            'columns': list(df.columns)
        }
        
        # Include file_path hint for chart data loading
        if data_path:
            response_data['file_path'] = data_path
        
        return jsonify(response_data)
        
    except ValueError as ve:
        logger.error(f"Value error in analysis: {str(ve)}")
        return jsonify({'error': f'Value error: {str(ve)}'}), 500
    except Exception as e:
        logger.error(f"Error performing analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

