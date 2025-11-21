"""
Chart data routes for REDLINE Web GUI
Provides sample data for Chart.js visualizations
"""

from flask import Blueprint, request, jsonify
import logging
import pandas as pd
import numpy as np
import os
from ..utils.analysis_helpers import detect_price_column, detect_volume_column, clean_dataframe_columns

analysis_charts_bp = Blueprint('analysis_charts', __name__)
logger = logging.getLogger(__name__)


@analysis_charts_bp.route('/chart-data', methods=['POST'])
def get_chart_data():
    """Get sample data for charting."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        chart_type = data.get('chart_type', 'price')
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
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
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        if format_type == 'csv':
            df = pd.read_csv(data_path)
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
        else:
            df = converter.load_file_by_type(data_path, format_type)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        df = clean_dataframe_columns(df)
        
        # Prepare chart data based on type
        if chart_type == 'price':
            price_col = detect_price_column(df)
            if price_col:
                # Sample up to 1000 points for performance
                sample_size = min(1000, len(df))
                sample_df = df.sample(n=sample_size).sort_index() if len(df) > sample_size else df
                
                prices = pd.to_numeric(sample_df[price_col], errors='coerce').dropna().tolist()
                
                # Get labels (try timestamp, date, or index)
                timestamp_col = None
                for col in df.columns:
                    if any(term in str(col).lower() for term in ['date', 'time', 'timestamp']):
                        timestamp_col = col
                        break
                
                if timestamp_col:
                    labels = sample_df[timestamp_col].astype(str).tolist()[:len(prices)]
                else:
                    labels = [f"Point {i+1}" for i in range(len(prices))]
                
                return jsonify({
                    'data': prices,
                    'labels': labels,
                    'chart_type': 'price'
                })
            else:
                return jsonify({'error': 'No price column found'}), 400
        
        return jsonify({'error': f'Unknown chart type: {chart_type}'}), 400
        
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}")
        return jsonify({'error': str(e)}), 500

