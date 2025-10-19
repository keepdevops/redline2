"""
Analysis tab routes for REDLINE Web GUI
Handles data analysis and statistical operations
"""

from flask import Blueprint, render_template, request, jsonify
import logging
import pandas as pd
import numpy as np

analysis_bp = Blueprint('analysis', __name__)
logger = logging.getLogger(__name__)

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
        converter = FormatConverter()
        
        data_path = f"data/{filename}"
        df = converter.load_file(data_path)
        
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
                'rows': len(df),
                'columns': len(df.columns)
            },
            'data_types': df.dtypes.astype(str).to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            numeric_df = df[numeric_cols]
            analysis['numeric_summary'] = {
                'count': numeric_df.count().to_dict(),
                'mean': numeric_df.mean().to_dict(),
                'std': numeric_df.std().to_dict(),
                'min': numeric_df.min().to_dict(),
                'max': numeric_df.max().to_dict(),
                'percentiles': {
                    '25%': numeric_df.quantile(0.25).to_dict(),
                    '50%': numeric_df.quantile(0.50).to_dict(),
                    '75%': numeric_df.quantile(0.75).to_dict()
                }
            }
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                analysis['categorical_summary'][col] = {
                    'unique_count': df[col].nunique(),
                    'most_common': df[col].value_counts().head(5).to_dict(),
                    'null_count': df[col].isnull().sum()
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
                'current_price': float(prices.iloc[-1]) if not prices.empty else None,
                'price_range': {
                    'min': float(prices.min()),
                    'max': float(prices.max()),
                    'avg': float(prices.mean())
                },
                'price_change': {
                    'absolute': float(prices.iloc[-1] - prices.iloc[0]) if len(prices) > 1 else 0,
                    'percentage': float(((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100) if len(prices) > 1 and prices.iloc[0] != 0 else 0
                }
            }
            
            # Calculate returns
            returns = prices.pct_change().dropna()
            if not returns.empty:
                analysis['returns_analysis'] = {
                    'mean_return': float(returns.mean()),
                    'std_return': float(returns.std()),
                    'total_return': float((prices.iloc[-1] / prices.iloc[0] - 1) * 100) if prices.iloc[0] != 0 else 0,
                    'sharpe_ratio': float(returns.mean() / returns.std()) if returns.std() != 0 else 0
                }
                
                analysis['volatility_analysis'] = {
                    'daily_volatility': float(returns.std()),
                    'annualized_volatility': float(returns.std() * np.sqrt(252)),
                    'max_drawdown': float((returns.cumsum().expanding().max() - returns.cumsum()).max())
                }
        
        if volume_cols:
            volume_col = volume_cols[0]
            volumes = pd.to_numeric(df[volume_col], errors='coerce')
            
            analysis['volume_analysis'] = {
                'avg_volume': float(volumes.mean()),
                'max_volume': float(volumes.max()),
                'min_volume': float(volumes.min()),
                'volume_trend': 'increasing' if volumes.iloc[-5:].mean() > volumes.iloc[:5].mean() else 'decreasing'
            }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in financial analysis: {str(e)}")
        return {'error': str(e)}

def perform_statistical_analysis(df):
    """Perform statistical analysis."""
    try:
        analysis = {
            'descriptive_stats': {},
            'distribution_analysis': {},
            'outlier_detection': {},
            'correlation_matrix': {}
        }
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            numeric_df = df[numeric_cols]
            
            # Descriptive statistics
            analysis['descriptive_stats'] = numeric_df.describe().to_dict()
            
            # Distribution analysis
            for col in numeric_cols:
                col_data = numeric_df[col].dropna()
                if not col_data.empty:
                    analysis['distribution_analysis'][col] = {
                        'skewness': float(col_data.skew()),
                        'kurtosis': float(col_data.kurtosis()),
                        'normality_test': 'normal' if abs(col_data.skew()) < 0.5 and abs(col_data.kurtosis()) < 0.5 else 'non-normal'
                    }
            
            # Outlier detection using IQR method
            for col in numeric_cols:
                col_data = numeric_df[col].dropna()
                if not col_data.empty:
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                    
                    analysis['outlier_detection'][col] = {
                        'outlier_count': len(outliers),
                        'outlier_percentage': float(len(outliers) / len(col_data) * 100),
                        'outlier_values': outliers.tolist()[:10]  # First 10 outliers
                    }
            
            # Correlation matrix
            if len(numeric_cols) > 1:
                correlation_matrix = numeric_df.corr()
                analysis['correlation_matrix'] = correlation_matrix.to_dict()
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in statistical analysis: {str(e)}")
        return {'error': str(e)}

def perform_correlation_analysis(df):
    """Perform correlation analysis."""
    try:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for correlation analysis'}
        
        numeric_df = df[numeric_cols]
        correlation_matrix = numeric_df.corr()
        
        # Find strong correlations
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        'column1': correlation_matrix.columns[i],
                        'column2': correlation_matrix.columns[j],
                        'correlation': float(corr_value),
                        'strength': 'strong positive' if corr_value > 0.7 else 'strong negative'
                    })
        
        analysis = {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_correlations': strong_correlations,
            'avg_correlation': float(correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean())
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
