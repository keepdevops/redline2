"""
Backend visualization routes for REDLINE Web GUI
Generates charts using matplotlib/seaborn and returns as base64 images
"""

from flask import Blueprint, request, jsonify
import logging
import os
import base64
import io
import pandas as pd
import numpy as np
from ..utils.analysis_helpers import detect_price_column, detect_volume_column, detect_date_columns, _load_data_file
from ..utils.data_helpers import clean_dataframe_columns

analysis_visualization_bp = Blueprint('analysis_visualization', __name__)
logger = logging.getLogger(__name__)


def _generate_text_chart(values, title, xlabel, ylabel, width=80, height=20):
    """Generate ASCII art text chart from numeric values."""
    if len(values) == 0:
        return f"{title}\nNo data available"
    
    # Normalize values to fit in height
    min_val = float(min(values))
    max_val = float(max(values))
    val_range = max_val - min_val if max_val != min_val else 1
    
    # Create chart grid
    chart_lines = []
    chart_lines.append(f"\n{title}")
    chart_lines.append(f"{'=' * width}")
    chart_lines.append(f"{xlabel} → | {ylabel}")
    chart_lines.append(f"{'-' * width}")
    
    # Calculate step for x-axis
    step = max(1, len(values) // width)
    
    # Build chart row by row (from top to bottom)
    for row in range(height, -1, -1):
        line = ""
        threshold = min_val + (val_range * row / height)
        
        for i in range(0, len(values), step):
            val = values[i] if i < len(values) else values[-1]
            if val >= threshold:
                line += "*"
            else:
                line += " "
        
        # Add y-axis label
        y_val = min_val + (val_range * row / height)
        line = f"{y_val:8.2f} | {line}"
        chart_lines.append(line)
    
    chart_lines.append(f"{'-' * width}")
    chart_lines.append(f"Min: {min_val:.2f}, Max: {max_val:.2f}, Points: {len(values)}")
    
    return "\n".join(chart_lines)

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


@analysis_visualization_bp.route('/price-chart', methods=['POST'])
def generate_price_chart():
    """Generate price trend chart."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        file_path_hint = data.get('file_path')
        output_format = data.get('format', 'png').lower()  # Support 'png' or 'txt'
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        df = _load_data_file(filename, file_path_hint)
        
        if df.empty:
            return jsonify({'error': 'Loaded data is empty'}), 400
        
        price_col = detect_price_column(df)
        
        if not price_col:
            available_cols = ', '.join(df.columns.tolist()[:10])  # Show first 10 columns
            return jsonify({
                'error': 'No price column found',
                'available_columns': df.columns.tolist(),
                'hint': f'Available columns: {available_cols}{"..." if len(df.columns) > 10 else ""}'
            }), 400
        
        # Sample data for performance (max 1000 points)
        sample_size = min(1000, len(df))
        sample_df = df.sample(n=sample_size).sort_index() if len(df) > sample_size else df
        
        prices = pd.to_numeric(sample_df[price_col], errors='coerce').dropna()
        
        # Generate text chart if requested
        if output_format == 'txt':
            chart_text = _generate_text_chart(prices.values, 'Price Trend', 'Index', 'Price')
            return jsonify({
                'text': chart_text,
                'format': 'txt',
                'filename': filename
            })
        
        # Generate PNG chart (default)
        if not MATPLOTLIB_AVAILABLE:
            return jsonify({'error': 'matplotlib not available'}), 500
        
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
        
        if df.empty:
            return jsonify({'error': 'Loaded data is empty'}), 400
        
        date_cols = detect_date_columns(df)
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in date_cols]
        
        if len(numeric_cols) < 2:
            available_cols = ', '.join(df.columns.tolist()[:10])
            return jsonify({
                'error': 'Not enough numeric columns for correlation',
                'available_columns': df.columns.tolist(),
                'numeric_columns_found': len(numeric_cols),
                'hint': f'Available columns: {available_cols}{"..." if len(df.columns) > 10 else ""}'
            }), 400
        
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
        
        if df.empty:
            return jsonify({'error': 'Loaded data is empty'}), 400
        
        # Auto-detect column if not provided
        if not column:
            price_col = detect_price_column(df)
            column = price_col if price_col else df.select_dtypes(include=[np.number]).columns[0] if len(df.select_dtypes(include=[np.number]).columns) > 0 else None
        
        if not column or column not in df.columns:
            available_cols = ', '.join(df.columns.tolist()[:10])
            return jsonify({
                'error': f'Column not found: {column}',
                'available_columns': df.columns.tolist(),
                'hint': f'Available columns: {available_cols}{"..." if len(df.columns) > 10 else ""}'
            }), 400
        
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
        
        if df.empty:
            return jsonify({'error': 'Loaded data is empty'}), 400
        
        volume_col = detect_volume_column(df)
        
        if not volume_col:
            available_cols = ', '.join(df.columns.tolist()[:10])  # Show first 10 columns
            return jsonify({
                'error': 'No volume column found',
                'available_columns': df.columns.tolist(),
                'hint': f'Available columns: {available_cols}{"..." if len(df.columns) > 10 else ""}'
            }), 400
        
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



