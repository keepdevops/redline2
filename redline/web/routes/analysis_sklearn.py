"""
Scikit-learn ML features for REDLINE Web GUI
Provides outlier detection, clustering, predictions, and feature scaling
"""

from flask import Blueprint, request, jsonify
import logging
import pandas as pd
import numpy as np
import os
from ..utils.analysis_helpers import clean_dataframe_columns, detect_price_column, detect_date_columns

analysis_sklearn_bp = Blueprint('analysis_sklearn', __name__)
logger = logging.getLogger(__name__)

# Optional dependencies
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    IsolationForest = None
    KMeans = None
    LinearRegression = None
    StandardScaler = None
    MinMaxScaler = None
    train_test_split = None
    SKLEARN_AVAILABLE = False


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
    else:
        df = converter.load_file_by_type(data_path, format_type)
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError('Invalid data format')
    
    return clean_dataframe_columns(df)


@analysis_sklearn_bp.route('/detect-outliers', methods=['POST'])
def detect_outliers():
    """Detect outliers using Isolation Forest."""
    if not SKLEARN_AVAILABLE:
        return jsonify({'error': 'scikit-learn not available'}), 500
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        contamination = float(data.get('contamination', 0.1))  # 10% default
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        df = _load_data_file(filename, file_path_hint)
        date_cols = detect_date_columns(df)
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in date_cols]
        
        if len(numeric_cols) == 0:
            return jsonify({'error': 'No numeric columns found'}), 400
        
        # Prepare data
        X = df[numeric_cols].fillna(0)
        
        # Detect outliers
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        outliers = iso_forest.fit_predict(X)
        
        # Convert to boolean (1 = normal, -1 = outlier)
        outlier_mask = outliers == -1
        outlier_count = int(outlier_mask.sum())
        total_count = len(df)
        
        # Get outlier indices and values
        outlier_indices = df[outlier_mask].index.tolist()
        outlier_data = df[outlier_mask][numeric_cols].to_dict(orient='records')
        
        return jsonify({
            'filename': filename,
            'total_rows': total_count,
            'outlier_count': outlier_count,
            'outlier_percentage': round((outlier_count / total_count) * 100, 2),
            'contamination': contamination,
            'outlier_indices': outlier_indices[:100],  # Limit to first 100
            'outlier_preview': outlier_data[:10],  # Preview first 10
            'columns_analyzed': numeric_cols
        })
        
    except Exception as e:
        logger.error(f"Error detecting outliers: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_sklearn_bp.route('/cluster-data', methods=['POST'])
def cluster_data():
    """Perform K-means clustering."""
    if not SKLEARN_AVAILABLE:
        return jsonify({'error': 'scikit-learn not available'}), 500
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        n_clusters = int(data.get('n_clusters', 3))
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        if n_clusters < 2 or n_clusters > 10:
            return jsonify({'error': 'Number of clusters must be between 2 and 10'}), 400
        
        df = _load_data_file(filename, file_path_hint)
        date_cols = detect_date_columns(df)
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in date_cols]
        
        if len(numeric_cols) < 2:
            return jsonify({'error': 'Need at least 2 numeric columns for clustering'}), 400
        
        # Prepare data
        X = df[numeric_cols].fillna(0)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)
        
        # Get cluster statistics
        df['cluster'] = clusters
        cluster_stats = {}
        for i in range(n_clusters):
            cluster_data = df[df['cluster'] == i][numeric_cols]
            cluster_stats[i] = {
                'count': int(len(cluster_data)),
                'percentage': round((len(cluster_data) / len(df)) * 100, 2),
                'means': cluster_data.mean().to_dict()
            }
        
        return jsonify({
            'filename': filename,
            'n_clusters': n_clusters,
            'total_rows': len(df),
            'cluster_assignments': clusters.tolist()[:100],  # Limit to first 100
            'cluster_centers': kmeans.cluster_centers_.tolist(),
            'cluster_stats': cluster_stats,
            'columns_analyzed': numeric_cols
        })
        
    except Exception as e:
        logger.error(f"Error clustering data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_sklearn_bp.route('/predict', methods=['POST'])
def predict_values():
    """Simple linear regression prediction."""
    if not SKLEARN_AVAILABLE:
        return jsonify({'error': 'scikit-learn not available'}), 500
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        target_column = data.get('target_column')
        feature_columns = data.get('feature_columns', [])
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        df = _load_data_file(filename, file_path_hint)
        date_cols = detect_date_columns(df)
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in date_cols]
        
        # Auto-detect target if not provided
        if not target_column:
            target_column = detect_price_column(df) or numeric_cols[0] if numeric_cols else None
        
        if not target_column or target_column not in df.columns:
            return jsonify({'error': f'Target column not found: {target_column}'}), 400
        
        # Auto-select features if not provided
        if not feature_columns:
            feature_columns = [col for col in numeric_cols if col != target_column][:5]  # Max 5 features
        
        if len(feature_columns) == 0:
            return jsonify({'error': 'No feature columns available'}), 400
        
        # Prepare data
        X = df[feature_columns].fillna(0)
        y = pd.to_numeric(df[target_column], errors='coerce').fillna(0)
        
        if len(X) < 10:
            return jsonify({'error': 'Not enough data for prediction (need at least 10 rows)'}), 400
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        from sklearn.metrics import mean_squared_error, r2_score
        mse = float(mean_squared_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))
        
        # Get feature importance (coefficients)
        feature_importance = dict(zip(feature_columns, model.coef_.tolist()))
        
        return jsonify({
            'filename': filename,
            'target_column': target_column,
            'feature_columns': feature_columns,
            'model_type': 'LinearRegression',
            'metrics': {
                'mean_squared_error': round(mse, 4),
                'r2_score': round(r2, 4),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            },
            'feature_importance': feature_importance,
            'predictions_preview': {
                'actual': y_test.head(10).tolist(),
                'predicted': y_pred[:10].tolist()
            }
        })
        
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_sklearn_bp.route('/scale-features', methods=['POST'])
def scale_features():
    """Scale features using StandardScaler or MinMaxScaler."""
    if not SKLEARN_AVAILABLE:
        return jsonify({'error': 'scikit-learn not available'}), 500
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        method = data.get('method', 'standard')  # 'standard' or 'minmax'
        columns = data.get('columns', [])
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        if method not in ['standard', 'minmax']:
            return jsonify({'error': "Method must be 'standard' or 'minmax'"}), 400
        
        df = _load_data_file(filename, file_path_hint)
        date_cols = detect_date_columns(df)
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in date_cols]
        
        # Use provided columns or all numeric columns
        if not columns:
            columns = numeric_cols
        
        # Filter to only numeric columns that exist
        columns = [col for col in columns if col in numeric_cols]
        
        if len(columns) == 0:
            return jsonify({'error': 'No valid numeric columns found'}), 400
        
        # Prepare data
        X = df[columns].fillna(0)
        
        # Scale features
        if method == 'standard':
            scaler = StandardScaler()
        else:
            scaler = MinMaxScaler()
        
        X_scaled = scaler.fit_transform(X)
        
        # Convert back to DataFrame for preview
        df_scaled = pd.DataFrame(X_scaled, columns=columns, index=df.index)
        
        # Get statistics - convert to JSON-serializable format
        try:
            original_desc = X.describe()
            scaled_desc = df_scaled.describe()
            
            # Build stats dictionaries manually to avoid issues with column names
            original_stats = {}
            scaled_stats = {}
            
            for stat_name in ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']:
                if stat_name in original_desc.index:
                    original_stats[stat_name] = {}
                    for col in columns:
                        if col in original_desc.columns:
                            try:
                                val = original_desc.loc[stat_name, col]
                                original_stats[stat_name][col] = float(val) if not pd.isna(val) else 0.0
                            except (KeyError, TypeError):
                                original_stats[stat_name][col] = 0.0
                
                if stat_name in scaled_desc.index:
                    scaled_stats[stat_name] = {}
                    for col in columns:
                        if col in scaled_desc.columns:
                            try:
                                val = scaled_desc.loc[stat_name, col]
                                scaled_stats[stat_name][col] = float(val) if not pd.isna(val) else 0.0
                            except (KeyError, TypeError):
                                scaled_stats[stat_name][col] = 0.0
            
            # Convert preview to JSON-serializable format
            preview = df_scaled.head(10).to_dict(orient='records')
            for record in preview:
                for key, value in record.items():
                    if hasattr(value, 'item'):  # numpy scalar
                        record[key] = value.item()
                    elif isinstance(value, (np.integer, np.floating)):
                        record[key] = float(value) if isinstance(value, np.floating) else int(value)
                    elif pd.isna(value):
                        record[key] = None
            
            return jsonify({
                'filename': filename,
                'method': method,
                'columns_scaled': columns,
                'original_stats': original_stats,
                'scaled_stats': scaled_stats,
                'scaled_preview': preview
            })
        except Exception as stats_error:
            logger.error(f"Error converting statistics to JSON: {str(stats_error)}", exc_info=True)
            # Return basic response without detailed stats
            preview = df_scaled.head(10).to_dict(orient='records')
            for record in preview:
                for key, value in record.items():
                    if hasattr(value, 'item'):
                        record[key] = value.item()
                    elif isinstance(value, (np.integer, np.floating)):
                        record[key] = float(value) if isinstance(value, np.floating) else int(value)
            
            return jsonify({
                'filename': filename,
                'method': method,
                'columns_scaled': columns,
                'message': 'Features scaled successfully (stats conversion had issues)',
                'scaled_preview': preview
            })
        
    except Exception as e:
        logger.error(f"Error scaling features: {str(e)}")
        return jsonify({'error': str(e)}), 500



