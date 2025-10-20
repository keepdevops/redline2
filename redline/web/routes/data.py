"""
Data tab routes for REDLINE Web GUI
Handles data viewing, filtering, and management
"""

from flask import Blueprint, render_template, request, jsonify
import logging
import os
import pandas as pd
from ...database.optimized_connector import OptimizedDatabaseConnector

# Initialize optimized database connector
optimized_db = OptimizedDatabaseConnector(max_connections=8, cache_size=64, cache_ttl=300)

data_bp = Blueprint('data', __name__)
logger = logging.getLogger(__name__)

def _load_large_file_chunked(file_path: str, format_type: str, chunk_size: int = 10000) -> pd.DataFrame:
    """Load large files in chunks to prevent memory issues (same as Tkinter)."""
    try:
        logger.info(f"Loading large file {file_path} in chunks of {chunk_size} rows")
        
        if format_type == 'csv':
            # Load CSV in chunks
            chunks = []
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                chunks.append(chunk)
                if len(chunks) >= 10:  # Limit memory usage
                    combined = pd.concat(chunks, ignore_index=True)
                    chunks = [combined]
            
            if chunks:
                return pd.concat(chunks, ignore_index=True)
            else:
                return pd.DataFrame()
        
        elif format_type == 'txt':
            # For text files, try to detect if it's Stooq format
            try:
                # Read first few lines to detect format
                with open(file_path, 'r') as f:
                    first_line = f.readline().strip()
                    
                if '<TICKER>' in first_line:
                    # Stooq format - load in chunks
                    chunks = []
                    for chunk in pd.read_csv(file_path, chunksize=chunk_size, sep=','):
                        chunks.append(chunk)
                        if len(chunks) >= 10:
                            combined = pd.concat(chunks, ignore_index=True)
                            chunks = [combined]
                    
                    if chunks:
                        return pd.concat(chunks, ignore_index=True)
                
            except Exception as e:
                logger.warning(f"Error in chunked text loading: {str(e)}")
            
            # Fallback to regular loading
            from redline.core.format_converter import FormatConverter
            converter = FormatConverter()
            return converter.load_file_by_type(file_path, format_type)
        
        else:
            # For other formats, use regular loading
            from redline.core.format_converter import FormatConverter
            converter = FormatConverter()
            return converter.load_file_by_type(file_path, format_type)
            
    except Exception as e:
        logger.error(f"Error in chunked loading: {str(e)}")
        return pd.DataFrame()

@data_bp.route('/')
def data_tab():
    """Data tab main page."""
    return render_template('data_tab.html')

@data_bp.route('/load', methods=['POST'])
def load_data():
    """Load data from file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        data_path = os.path.join(os.getcwd(), 'data', filename)
        
        if not os.path.exists(data_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Use EXACT same data loading pipeline as Tkinter GUI
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
        # Detect format from file extension (same as Tkinter _detect_format_from_path)
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Check if this is a large file (same as Tkinter)
        file_size = os.path.getsize(data_path)
        is_large_file = file_size > 50 * 1024 * 1024  # 50MB
        
        # Load data with chunked approach for large files (same as Tkinter)
        if is_large_file and format_type in ['csv', 'txt']:
            df = _load_large_file_chunked(data_path, format_type)
        else:
            df = converter.load_file_by_type(data_path, format_type)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Convert to JSON-serializable format
        data_dict = {
            'columns': list(df.columns),
            'data': df.head(1000).to_dict('records'),  # Limit to 1000 rows for web display
            'total_rows': len(df),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'filename': filename
        }
        
        return jsonify(data_dict)
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/filter', methods=['POST'])
def filter_data():
    """Apply filters to loaded data."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        filters = data.get('filters', {})
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        data_path = os.path.join(os.getcwd(), 'data', filename)
        
        # Use EXACT same data loading pipeline as Tkinter GUI
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
        # Detect format from file extension (same as Tkinter _detect_format_from_path)
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Check if this is a large file (same as Tkinter)
        file_size = os.path.getsize(data_path)
        is_large_file = file_size > 50 * 1024 * 1024  # 50MB
        
        # Load data with chunked approach for large files (same as Tkinter)
        if is_large_file and format_type in ['csv', 'txt']:
            df = _load_large_file_chunked(data_path, format_type)
        else:
            df = converter.load_file_by_type(data_path, format_type)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Apply filters - handle both list and dict formats
        filtered_df = df.copy()
        
        # Handle filters as a list (from frontend) or dict (legacy)
        if isinstance(filters, list):
            # New format: list of filter objects
            for filter_obj in filters:
                column = filter_obj.get('column')
                operator = filter_obj.get('operator')  # 'equals', 'contains', 'greater_than', etc.
                value = filter_obj.get('value')
                
                if column in filtered_df.columns:
                    if operator == 'equals':
                        filtered_df = filtered_df[filtered_df[column].astype(str) == str(value)]
                    elif operator == 'contains':
                        filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(value), na=False)]
                    elif operator == 'greater_than':
                        try:
                            numeric_value = float(value)
                            filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') > numeric_value]
                        except (ValueError, TypeError):
                            pass
                    elif operator == 'less_than':
                        try:
                            numeric_value = float(value)
                            filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') < numeric_value]
                        except (ValueError, TypeError):
                            pass
                    elif operator == 'date_range':
                        if 'start' in value and 'end' in value:
                            filtered_df = filtered_df[
                                (filtered_df[column] >= value['start']) &
                                (filtered_df[column] <= value['end'])
                            ]
        else:
            # Legacy format: dict where keys are column names
            for column, filter_config in filters.items():
                if column in filtered_df.columns:
                    filter_type = filter_config.get('type')
                    filter_value = filter_config.get('value')
                    
                    if filter_type == 'equals':
                        filtered_df = filtered_df[filtered_df[column].astype(str) == str(filter_value)]
                    elif filter_type == 'contains':
                        filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(filter_value), na=False)]
                    elif filter_type == 'greater_than':
                        try:
                            numeric_value = float(filter_value)
                            filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') > numeric_value]
                        except (ValueError, TypeError):
                            pass
                    elif filter_type == 'less_than':
                        try:
                            numeric_value = float(filter_value)
                            filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') < numeric_value]
                        except (ValueError, TypeError):
                            pass
                    elif filter_type == 'date_range':
                        if 'start' in filter_value and 'end' in filter_value:
                            filtered_df = filtered_df[
                                (filtered_df[column] >= filter_value['start']) &
                                (filtered_df[column] <= filter_value['end'])
                            ]
        
        # Convert to JSON-serializable format
        data_dict = {
            'columns': list(filtered_df.columns),
            'data': filtered_df.head(1000).to_dict('records'),
            'total_rows': len(filtered_df),
            'original_rows': len(df),
            'filters_applied': len(filters)
        }
        
        return jsonify(data_dict)
        
    except Exception as e:
        logger.error(f"Error filtering data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/columns/<filename>')
def get_columns(filename):
    """Get column information for a file."""
    try:
        data_path = os.path.join(os.getcwd(), 'data', filename)
        
        if not os.path.exists(data_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Use EXACT same data loading pipeline as Tkinter GUI
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
        # Detect format from file extension (same as Tkinter _detect_format_from_path)
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Check if this is a large file (same as Tkinter)
        file_size = os.path.getsize(data_path)
        is_large_file = file_size > 50 * 1024 * 1024  # 50MB
        
        # Load data with chunked approach for large files (same as Tkinter)
        if is_large_file and format_type in ['csv', 'txt']:
            df = _load_large_file_chunked(data_path, format_type)
        else:
            df = converter.load_file_by_type(data_path, format_type)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        columns_info = []
        for col in df.columns:
            col_info = {
                'name': col,
                'dtype': str(df[col].dtype),
                'non_null_count': int(df[col].count()),
                'null_count': int(df[col].isnull().sum()),
                'unique_count': int(df[col].nunique())
            }
            
            # Add sample values for preview
            sample_values = df[col].dropna().head(5).tolist()
            col_info['sample_values'] = sample_values
            
            columns_info.append(col_info)
        
        return jsonify({
            'columns': columns_info,
            'total_columns': len(df.columns),
            'total_rows': len(df)
        })
        
    except Exception as e:
        logger.error(f"Error getting columns for {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/export', methods=['POST'])
def export_data():
    """Export filtered data to file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        export_format = data.get('format', 'csv')
        export_filename = data.get('export_filename')
        filters = data.get('filters', {})
        
        if not all([filename, export_filename]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        data_path = os.path.join(os.getcwd(), 'data', filename)
        export_path = os.path.join(os.getcwd(), 'data', export_filename)
        
        # Use EXACT same data loading pipeline as Tkinter GUI
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
        # Detect format from file extension (same as Tkinter _detect_format_from_path)
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Check if this is a large file (same as Tkinter)
        file_size = os.path.getsize(data_path)
        is_large_file = file_size > 50 * 1024 * 1024  # 50MB
        
        # Load data with chunked approach for large files (same as Tkinter)
        if is_large_file and format_type in ['csv', 'txt']:
            df = _load_large_file_chunked(data_path, format_type)
        else:
            df = converter.load_file_by_type(data_path, format_type)
        
        # Apply filters if provided
        if filters:
            filtered_df = df.copy()
            for column, filter_config in filters.items():
                if column in filtered_df.columns:
                    filter_type = filter_config.get('type')
                    filter_value = filter_config.get('value')
                    
                    if filter_type == 'equals':
                        filtered_df = filtered_df[filtered_df[column].astype(str) == str(filter_value)]
                    elif filter_type == 'contains':
                        filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(filter_value), na=False)]
                    elif filter_type == 'greater_than':
                        try:
                            numeric_value = float(filter_value)
                            filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') > numeric_value]
                        except (ValueError, TypeError):
                            pass
                    elif filter_type == 'less_than':
                        try:
                            numeric_value = float(filter_value)
                            filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') < numeric_value]
                        except (ValueError, TypeError):
                            pass
            
            df = filtered_df
        
        # Save in requested format
        converter.save_file_by_type(df, export_path, export_format)
        
        return jsonify({
            'message': 'Data exported successfully',
            'export_filename': export_filename,
            'records_exported': len(df)
        })
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/files')
def list_files():
    """List available data files."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # Get files from main data directory
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                file_path = os.path.join(data_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path
                    })
        
        # Get files from downloaded directory
        downloaded_dir = os.path.join(data_dir, 'downloaded')
        if os.path.exists(downloaded_dir):
            for filename in os.listdir(downloaded_dir):
                file_path = os.path.join(downloaded_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path,
                        'location': 'downloaded'
                    })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/db-stats')
def get_database_stats():
    """Get database performance statistics."""
    try:
        stats = optimized_db.get_performance_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
