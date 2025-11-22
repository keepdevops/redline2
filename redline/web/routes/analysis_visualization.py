"""
Backend visualization routes for REDLINE Web GUI
Generates charts using matplotlib/seaborn and returns as base64 images
"""

from flask import Blueprint, request, jsonify
import logging
import pandas as pd
import numpy as np
import os
import base64
import io
from ..utils.analysis_helpers import clean_dataframe_columns, detect_price_column, detect_volume_column, detect_date_columns

analysis_visualization_bp = Blueprint('analysis_visualization', __name__)
logger = logging.getLogger(__name__)

# Optional dependencies
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    MATPLOTLIB_AVAILABLE = False

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    sns = None
    SEABORN_AVAILABLE = False


def _load_data_file(filename, file_path_hint=None):
    """Load data file (shared helper)."""
    from redline.core.format_converter import FormatConverter
    from redline.core.schema import EXT_TO_FORMAT
    
    converter = FormatConverter()
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
        raise FileNotFoundError(f'File not found: {filename}')
    
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
    elif format_type in ('tensorflow', 'npz'):
        import numpy as np
        loaded = np.load(data_path)
        if 'data' in loaded:
            df = pd.DataFrame(loaded['data'])
        else:
            first_key = list(loaded.keys())[0]
            df = pd.DataFrame(loaded[first_key])
    elif format_type in ('keras', 'h5'):
        raise ValueError('Keras model files (.h5) cannot be used for visualization. Use the Analysis tab for model operations.')
    elif format_type in ('pyarrow', 'arrow'):
        try:
            import pyarrow as pa
            with pa.ipc.open_file(data_path) as reader:
                df = reader.read_all().to_pandas()
        except ImportError:
            raise ImportError('PyArrow is required to load .arrow files')
        except Exception as e:
            raise Exception(f'Error loading Arrow file: {str(e)}')
    else:
        df = converter.load_file_by_type(data_path, format_type)
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError('Invalid data format')
    
    return clean_dataframe_columns(df)


@analysis_visualization_bp.route('/price-chart', methods=['POST'])
def generate_price_chart():
    """Generate price trend chart."""
    if not MATPLOTLIB_AVAILABLE:
        return jsonify({'error': 'matplotlib not available'}), 500
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        df = _load_data_file(filename, file_path_hint)
        price_col = detect_price_column(df)
        
        if not price_col:
            return jsonify({'error': 'No price column found'}), 400
        
        # Sample data for performance (max 1000 points)
        sample_size = min(1000, len(df))
        sample_df = df.sample(n=sample_size).sort_index() if len(df) > sample_size else df
        
        prices = pd.to_numeric(sample_df[price_col], errors='coerce').dropna()
        
        # Create chart
        plt.figure(figsize=(10, 6))
        plt.plot(prices.index, prices.values, linewidth=1.5, color='#007bff')
        plt.title('Price Trend', fontsize=14, fontweight='bold')
        plt.xlabel('Index', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return jsonify({
            'image': f'data:image/png;base64,{image_base64}',
            'format': 'png'
        })
        
    except Exception as e:
        logger.error(f"Error generating price chart: {str(e)}")
        if plt:
            plt.close('all')
        return jsonify({'error': str(e)}), 500


@analysis_visualization_bp.route('/correlation-heatmap', methods=['POST'])
def generate_correlation_heatmap():
    """Generate correlation heatmap using seaborn."""
    if not MATPLOTLIB_AVAILABLE or not SEABORN_AVAILABLE:
        return jsonify({'error': 'matplotlib/seaborn not available'}), 500
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        df = _load_data_file(filename, file_path_hint)
        date_cols = detect_date_columns(df)
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in date_cols]
        
        if len(numeric_cols) < 2:
            return jsonify({'error': 'Not enough numeric columns for correlation'}), 400
        
        # Calculate correlation
        corr_matrix = df[numeric_cols].corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
        plt.title('Correlation Heatmap', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return jsonify({
            'image': f'data:image/png;base64,{image_base64}',
            'format': 'png'
        })
        
    except Exception as e:
        logger.error(f"Error generating correlation heatmap: {str(e)}")
        if plt:
            plt.close('all')
        return jsonify({'error': str(e)}), 500


@analysis_visualization_bp.route('/distribution-chart', methods=['POST'])
def generate_distribution_chart():
    """Generate distribution/histogram chart."""
    if not MATPLOTLIB_AVAILABLE:
        return jsonify({'error': 'matplotlib not available'}), 500
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        column = data.get('column')
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        df = _load_data_file(filename, file_path_hint)
        
        # Auto-detect column if not provided
        if not column:
            price_col = detect_price_column(df)
            column = price_col if price_col else df.select_dtypes(include=[np.number]).columns[0] if len(df.select_dtypes(include=[np.number]).columns) > 0 else None
        
        if not column or column not in df.columns:
            return jsonify({'error': f'Column not found: {column}'}), 400
        
        values = pd.to_numeric(df[column], errors='coerce').dropna()
        
        if len(values) == 0:
            return jsonify({'error': 'No valid numeric data in column'}), 400
        
        # Create histogram
        plt.figure(figsize=(10, 6))
        plt.hist(values, bins=50, edgecolor='black', alpha=0.7, color='#007bff')
        plt.title(f'Distribution: {column}', fontsize=14, fontweight='bold')
        plt.xlabel(column, fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return jsonify({
            'image': f'data:image/png;base64,{image_base64}',
            'format': 'png',
            'column': column
        })
        
    except Exception as e:
        logger.error(f"Error generating distribution chart: {str(e)}")
        if plt:
            plt.close('all')
        return jsonify({'error': str(e)}), 500


@analysis_visualization_bp.route('/volume-chart', methods=['POST'])
def generate_volume_chart():
    """Generate volume bar chart."""
    if not MATPLOTLIB_AVAILABLE:
        return jsonify({'error': 'matplotlib not available'}), 500
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        df = _load_data_file(filename, file_path_hint)
        volume_col = detect_volume_column(df)
        
        if not volume_col:
            return jsonify({'error': 'No volume column found'}), 400
        
        # Sample data for performance
        sample_size = min(500, len(df))
        sample_df = df.sample(n=sample_size).sort_index() if len(df) > sample_size else df
        
        volumes = pd.to_numeric(sample_df[volume_col], errors='coerce').dropna()
        
        # Create bar chart
        plt.figure(figsize=(12, 6))
        plt.bar(volumes.index, volumes.values, alpha=0.7, color='#28a745', width=0.8)
        plt.title('Volume Chart', fontsize=14, fontweight='bold')
        plt.xlabel('Index', fontsize=12)
        plt.ylabel('Volume', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return jsonify({
            'image': f'data:image/png;base64,{image_base64}',
            'format': 'png'
        })
        
    except Exception as e:
        logger.error(f"Error generating volume chart: {str(e)}")
        if plt:
            plt.close('all')
        return jsonify({'error': str(e)}), 500



