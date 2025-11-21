"""
ML Data Preparation routes for REDLINE Web GUI
Exposes DataAdapter functionality for ML/RL training data preparation
"""

from flask import Blueprint, request, jsonify
import logging
import pandas as pd
import os
from ..utils.analysis_helpers import clean_dataframe_columns

analysis_ml_bp = Blueprint('analysis_ml', __name__)
logger = logging.getLogger(__name__)


@analysis_ml_bp.route('/prepare-ml-data', methods=['POST'])
def prepare_ml_data():
    """Prepare data for ML/RL training in specified format."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        format_type = data.get('format', 'numpy')  # numpy, tensorflow
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        from redline.core.data_adapter_shared import DataAdapter
        
        converter = FormatConverter()
        adapter = DataAdapter()
        
        # Find file (same logic as analysis endpoint)
        data_dir = os.path.join(os.getcwd(), 'data')
        data_path = None
        
        if file_path_hint and os.path.exists(file_path_hint):
            data_path = file_path_hint
        else:
            search_paths = [
                os.path.join(data_dir, filename),
                os.path.join(data_dir, 'stooq', filename),
                os.path.join(data_dir, 'downloaded', filename),
                os.path.join(data_dir, 'uploads', filename)
            ]
            
            converted_dir = os.path.join(data_dir, 'converted')
            if os.path.exists(converted_dir):
                for root, dirs, files in os.walk(converted_dir):
                    if filename in files:
                        search_paths.append(os.path.join(root, filename))
            
            for path in search_paths:
                if os.path.exists(path):
                    data_path = path
                    break
        
        if not data_path or not os.path.exists(data_path):
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        # Load data
        ext = os.path.splitext(data_path)[1].lower()
        format_type_file = EXT_TO_FORMAT.get(ext, 'csv')
        
        if format_type_file == 'csv':
            df = pd.read_csv(data_path)
        elif format_type_file == 'parquet':
            df = pd.read_parquet(data_path)
        elif format_type_file == 'feather':
            df = pd.read_feather(data_path)
        elif format_type_file == 'json':
            df = pd.read_json(data_path)
        elif format_type_file == 'duckdb':
            import duckdb
            conn = duckdb.connect(data_path)
            df = conn.execute("SELECT * FROM tickers_data").fetchdf()
            conn.close()
        else:
            df = converter.load_file_by_type(data_path, format_type_file)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        df = clean_dataframe_columns(df)
        
        # Prepare training data using DataAdapter
        prepared_data = adapter.prepare_training_data([df], format_type)
        
        # Convert to JSON-serializable format
        if format_type == 'numpy':
            import numpy as np
            result = {
                'format': 'numpy',
                'shape': prepared_data[0].shape if len(prepared_data) > 0 else None,
                'dtype': str(prepared_data[0].dtype) if len(prepared_data) > 0 else None,
                'sample_size': len(prepared_data),
                'data_preview': prepared_data[0][:10].tolist() if len(prepared_data) > 0 and len(prepared_data[0]) > 0 else []
            }
        elif format_type == 'tensorflow':
            result = {
                'format': 'tensorflow',
                'type': 'Dataset',
                'sample_size': 1,
                'message': 'TensorFlow Dataset created successfully'
            }
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        
        return jsonify({
            'filename': filename,
            'format': format_type,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error preparing ML data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_ml_bp.route('/prepare-rl-state', methods=['POST'])
def prepare_rl_state():
    """Prepare reinforcement learning state from data."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        portfolio = data.get('portfolio', {})
        format_type = data.get('format', 'numpy')  # numpy, tensorflow
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        from redline.core.data_adapter_shared import DataAdapter
        
        converter = FormatConverter()
        adapter = DataAdapter()
        
        # Find and load file (same logic as above)
        data_dir = os.path.join(os.getcwd(), 'data')
        data_path = None
        
        if file_path_hint and os.path.exists(file_path_hint):
            data_path = file_path_hint
        else:
            search_paths = [
                os.path.join(data_dir, filename),
                os.path.join(data_dir, 'stooq', filename),
                os.path.join(data_dir, 'downloaded', filename),
                os.path.join(data_dir, 'uploads', filename)
            ]
            
            converted_dir = os.path.join(data_dir, 'converted')
            if os.path.exists(converted_dir):
                for root, dirs, files in os.walk(converted_dir):
                    if filename in files:
                        search_paths.append(os.path.join(root, filename))
            
            for path in search_paths:
                if os.path.exists(path):
                    data_path = path
                    break
        
        if not data_path or not os.path.exists(data_path):
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        # Load data
        ext = os.path.splitext(data_path)[1].lower()
        format_type_file = EXT_TO_FORMAT.get(ext, 'csv')
        
        if format_type_file == 'csv':
            df = pd.read_csv(data_path)
        elif format_type_file == 'parquet':
            df = pd.read_parquet(data_path)
        elif format_type_file == 'feather':
            df = pd.read_feather(data_path)
        elif format_type_file == 'json':
            df = pd.read_json(data_path)
        elif format_type_file == 'duckdb':
            import duckdb
            conn = duckdb.connect(data_path)
            df = conn.execute("SELECT * FROM tickers_data").fetchdf()
            conn.close()
        else:
            df = converter.load_file_by_type(data_path, format_type_file)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        df = clean_dataframe_columns(df)
        
        # Prepare RL state using DataAdapter
        rl_state = adapter.prepare_rl_state(df, portfolio, format_type)
        
        # Convert to JSON-serializable format
        if format_type == 'numpy':
            import numpy as np
            result = {
                'format': 'numpy',
                'shape': rl_state.shape if hasattr(rl_state, 'shape') else None,
                'dtype': str(rl_state.dtype) if hasattr(rl_state, 'dtype') else None,
                'data_preview': rl_state[:10].tolist() if len(rl_state) > 0 else []
            }
        elif format_type == 'tensorflow':
            result = {
                'format': 'tensorflow',
                'type': 'Tensor',
                'message': 'TensorFlow Tensor created successfully'
            }
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        
        return jsonify({
            'filename': filename,
            'format': format_type,
            'portfolio': portfolio,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error preparing RL state: {str(e)}")
        return jsonify({'error': str(e)}), 500

