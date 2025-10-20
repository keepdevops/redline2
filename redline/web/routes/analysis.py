"""
Analysis tab routes for REDLINE Web GUI
Handles data analysis and statistical operations
"""

from flask import Blueprint, render_template, request, jsonify
import logging
import pandas as pd
import numpy as np
import os

analysis_bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

@analysis_bp.route('/')
def analysis_tab():
    """Analysis tab main page."""
    return render_template('analysis_tab.html')

@analysis_bp.route('/analyze', methods=['POST'])
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
        
        # Determine file path - check both root data directory and downloaded subdirectory
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
        
        if not data_path or not os.path.exists(data_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Detect format from file extension (same as Tkinter)
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        df = converter.load_file_by_type(data_path, format_type)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
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
        
        return jsonify({
            'filename': filename,
            'analysis_type': analysis_type,
            'result': analysis_result,
            'data_shape': df.shape,
            'columns': list(df.columns)
        })
        
    except Exception as e:
        logger.error(f"Error performing analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

def perform_basic_analysis(df):
    """Perform basic data analysis."""
    try:
        analysis = {
            'shape': {
                'rows': int(len(df)),
                'columns': int(len(df.columns))
            },
            'data_types': df.dtypes.astype(str).to_dict(),
            'null_counts': convert_numpy_types(df.isnull().sum().to_dict()),
            'memory_usage': int(df.memory_usage(deep=True).sum()),
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            numeric_df = df[numeric_cols]
            
            analysis['numeric_summary'] = {
                'count': convert_numpy_types(numeric_df.count().to_dict()),
                'mean': convert_numpy_types(numeric_df.mean().to_dict()),
                'std': convert_numpy_types(numeric_df.std().to_dict()),
                'min': convert_numpy_types(numeric_df.min().to_dict()),
                'max': convert_numpy_types(numeric_df.max().to_dict()),
                'percentiles': {
                    '25%': convert_numpy_types(numeric_df.quantile(0.25).to_dict()),
                    '50%': convert_numpy_types(numeric_df.quantile(0.50).to_dict()),
                    '75%': convert_numpy_types(numeric_df.quantile(0.75).to_dict())
                }
            }
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                analysis['categorical_summary'][col] = {
                    'unique_count': int(df[col].nunique()),
                    'most_common': convert_numpy_types(df[col].value_counts().head(5).to_dict()),
                    'null_count': int(df[col].isnull().sum())
                }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in basic analysis: {str(e)}")
        return {'error': str(e)}

def perform_financial_analysis(df):
    """Perform financial data analysis."""
    try:
        analysis = {
            'price_analysis': {},
            'volume_analysis': {},
            'returns_analysis': {},
            'volatility_analysis': {}
        }
        
        # Common financial column names
        price_cols = [col for col in df.columns if any(price in col.lower() for price in ['close', 'price', 'adj close'])]
        volume_cols = [col for col in df.columns if 'volume' in col.lower()]
        high_cols = [col for col in df.columns if 'high' in col.lower()]
        low_cols = [col for col in df.columns if 'low' in col.lower()]
        
        if price_cols:
            price_col = price_cols[0]  # Use first price column
            prices = pd.to_numeric(df[price_col], errors='coerce')
            
            analysis['price_analysis'] = {
                    'current_price': convert_numpy_types(prices.iloc[-1]) if not prices.empty else None,
                    'price_range': {
                        'min': convert_numpy_types(prices.min()),
                        'max': convert_numpy_types(prices.max()),
                        'avg': convert_numpy_types(prices.mean())
                    },
                    'price_change': {
                        'absolute': convert_numpy_types(prices.iloc[-1] - prices.iloc[0]) if len(prices) > 1 else 0,
                        'percentage': convert_numpy_types(((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100) if len(prices) > 1 and prices.iloc[0] != 0 else 0
                    }
                }
            
            # Calculate returns
            returns = prices.pct_change().dropna()
            if not returns.empty:
                analysis['returns_analysis'] = {
                    'mean_return': convert_numpy_types(returns.mean()),
                    'std_return': convert_numpy_types(returns.std()),
                    'total_return': convert_numpy_types((prices.iloc[-1] / prices.iloc[0] - 1) * 100) if prices.iloc[0] != 0 else 0,
                    'sharpe_ratio': convert_numpy_types(returns.mean() / returns.std()) if returns.std() != 0 else 0
                }
                
                analysis['volatility_analysis'] = {
                    'daily_volatility': convert_numpy_types(returns.std()),
                    'annualized_volatility': convert_numpy_types(returns.std() * np.sqrt(252)),
                    'max_drawdown': convert_numpy_types((returns.cumsum().expanding().max() - returns.cumsum()).max())
                }
        
        if volume_cols:
            volume_col = volume_cols[0]
            volumes = pd.to_numeric(df[volume_col], errors='coerce')
            
            analysis['volume_analysis'] = {
                'avg_volume': convert_numpy_types(volumes.mean()),
                'max_volume': convert_numpy_types(volumes.max()),
                'min_volume': convert_numpy_types(volumes.min()),
                'volume_trend': 'increasing' if volumes.iloc[-5:].mean() > volumes.iloc[:5].mean() else 'decreasing'
            }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in financial analysis: {str(e)}")
        return {'error': str(e)}

def perform_statistical_analysis(df):
    """Perform statistical analysis - simplified version matching Tkinter GUI."""
    try:
        # Simple approach like Tkinter GUI
        stats = df.describe()
        
        # Convert to simple dictionary format
        analysis = {
            'descriptive_stats': stats.to_dict(),
            'summary': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'numeric_columns': len(df.select_dtypes(include=[np.number]).columns)
            }
        }
        
        # Additional analysis - check for close price column (like Tkinter)
        close_col = None
        if 'close' in df.columns:
            close_col = 'close'
        elif '<CLOSE>' in df.columns:
            close_col = '<CLOSE>'
        
        if close_col:
            close_stats = {
                'Mean': float(df[close_col].mean()),
                'Median': float(df[close_col].median()),
                'Std Dev': float(df[close_col].std()),
                'Min': float(df[close_col].min()),
                'Max': float(df[close_col].max())
            }
            analysis['close_price_stats'] = close_stats
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in statistical analysis: {str(e)}")
        return {'error': str(e)}

def perform_correlation_analysis(df):
    """Perform correlation analysis - simplified version matching Tkinter GUI."""
    try:
        # Select numeric columns for correlation (like Tkinter)
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) < 2:
            return {'error': 'Not enough numeric columns for correlation analysis'}
        
        # Calculate correlation matrix (simple approach like Tkinter)
        correlation_matrix = df[numeric_cols].corr()
        
        # Simple analysis like Tkinter GUI
        analysis = {
            'correlation_matrix': correlation_matrix.to_dict(),
            'summary': {
                'total_numeric_columns': len(numeric_cols),
                'columns_analyzed': list(numeric_cols)
            }
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in correlation analysis: {str(e)}")
        return {'error': str(e)}

@analysis_bp.route('/export-analysis', methods=['POST'])
def export_analysis():
    """Export analysis results to file."""
    try:
        data = request.get_json()
        analysis_result = data.get('analysis_result')
        filename = data.get('filename', 'analysis_results')
        export_format = data.get('format', 'json')
        
        if not analysis_result:
            return jsonify({'error': 'No analysis result provided'}), 400
        
        import os
        import json
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'json':
            export_filename = f"{filename}_{timestamp}.json"
            export_path = os.path.join(os.getcwd(), 'data', 'analysis', export_filename)
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            with open(export_path, 'w') as f:
                json.dump(analysis_result, f, indent=2, default=str)
        
        elif export_format == 'csv':
            # Try to convert analysis to DataFrame if possible
            export_filename = f"{filename}_{timestamp}.csv"
            export_path = os.path.join(os.getcwd(), 'data', 'analysis', export_filename)
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            # Create a flattened version of the analysis for CSV export
            flattened_data = []
            flatten_dict(analysis_result, flattened_data)
            
            if flattened_data:
                df = pd.DataFrame(flattened_data)
                df.to_csv(export_path, index=False)
            else:
                return jsonify({'error': 'Cannot export analysis to CSV format'}), 400
        
        else:
            return jsonify({'error': f'Unsupported export format: {export_format}'}), 400
        
        file_stat = os.stat(export_path)
        
        return jsonify({
            'message': 'Analysis exported successfully',
            'export_filename': export_filename,
            'export_path': export_path,
            'file_size': file_stat.st_size,
            'format': export_format
        })
        
    except Exception as e:
        logger.error(f"Error exporting analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

def flatten_dict(d, parent_key='', sep='_'):
    """Flatten nested dictionary for CSV export."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
