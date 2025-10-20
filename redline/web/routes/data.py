"""
Data tab routes for REDLINE Web GUI
Handles data viewing, filtering, and management
Uses the same data loading logic as the tkinter GUI
"""

from flask import Blueprint, render_template, request, jsonify
import logging
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any
from ...database.optimized_connector import OptimizedDatabaseConnector
from ...core.data_loader import DataLoader
from ...core.schema import EXT_TO_FORMAT, FORMAT_DIALOG_INFO
from ...gui.widgets.data_source import DataSource

# Initialize optimized database connector
optimized_db = OptimizedDatabaseConnector(max_connections=8, cache_size=64, cache_ttl=300)

data_bp = Blueprint('data', __name__)
logger = logging.getLogger(__name__)

def _detect_format_from_path(file_path: str) -> str:
    """Detect format from file path - same as tkinter GUI."""
    ext = os.path.splitext(file_path)[1].lower()
    return EXT_TO_FORMAT.get(ext, 'csv')

def _load_single_file_parallel(file_path: str) -> Optional[pd.DataFrame]:
    """Load a single file - optimized for speed with parallel processing (same as tkinter GUI)."""
    try:
        # Detect format from extension
        format_type = _detect_format_from_path(file_path)
        
        # Use direct pandas loading for speed (skip validation/cleaning for display)
        if format_type == 'csv':
            data = pd.read_csv(file_path)
        elif format_type == 'parquet':
            data = pd.read_parquet(file_path)
        elif format_type == 'feather':
            data = pd.read_feather(file_path)
        elif format_type == 'json':
            data = pd.read_json(file_path)
        elif format_type == 'duckdb':
            import duckdb
            conn = duckdb.connect(file_path)
            data = conn.execute("SELECT * FROM tickers_data").fetchdf()
            conn.close()
        else:
            # Fallback to loader for unsupported formats
            loader = DataLoader()
            data = loader.load_file_by_type(file_path, format_type)
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return None

def _load_files_parallel(file_paths: List[str]) -> Dict[str, Any]:
    """Load multiple files in parallel - same logic as tkinter GUI."""
    try:
        loaded_data = []
        skipped_files = []
        large_files = []
        
        # Check file sizes first
        for file_path in file_paths:
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 100 * 1024 * 1024:  # 100MB
                    large_files.append((file_path, file_size))
            except:
                pass
        
        # Use parallel processing for file loading (I/O bound, so more workers)
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Submit all file loading tasks
            future_to_file = {
                executor.submit(_load_single_file_parallel, file_path): file_path
                for file_path in file_paths
            }
            
            # Process completed loads
            completed = 0
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                completed += 1
                
                try:
                    data = future.result()
                    if data is not None and not data.empty:
                        loaded_data.append(data)
                        logger.info(f"Successfully loaded {file_path}: {len(data)} rows")
                    else:
                        skipped_files.append(file_path)
                        logger.warning(f"Skipped empty file: {file_path}")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {str(e)}")
                    skipped_files.append(file_path)
        
        # Combine loaded data with memory optimization
        if loaded_data:
            try:
                # Store count before clearing
                files_loaded_count = len(loaded_data)
                
                # Combine data with memory management
                if len(loaded_data) == 1:
                    combined_data = loaded_data[0]
                else:
                    combined_data = pd.concat(loaded_data, ignore_index=True)
                
                # Clear the list to free memory
                loaded_data.clear()
                
                return {
                    'success': True,
                    'data': combined_data,
                    'files_loaded': files_loaded_count,
                    'skipped_files': skipped_files,
                    'large_files': large_files,
                    'total_rows': len(combined_data),
                    'columns': list(combined_data.columns)
                }
                
            except MemoryError as mem_error:
                logger.error(f"Memory error combining data: {str(mem_error)}")
                return {
                    'success': False,
                    'error': 'Memory Error: File too large to load. Try loading smaller files.',
                    'skipped_files': skipped_files,
                    'large_files': large_files
                }
            except Exception as e:
                logger.error(f"Error combining data: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'skipped_files': skipped_files,
                    'large_files': large_files
                }
        else:
            return {
                'success': False,
                'error': 'No data loaded',
                'skipped_files': skipped_files,
                'large_files': large_files
            }
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in load files: {error_msg}")
        return {
            'success': False,
            'error': f"Failed to load files: {error_msg}"
        }

def _load_file_by_format(file_path: str, format_type: str) -> pd.DataFrame:
    """Load file based on format type."""
    try:
        if format_type == 'csv':
            return pd.read_csv(file_path)
        elif format_type == 'json':
            return pd.read_json(file_path)
        elif format_type == 'parquet':
            return pd.read_parquet(file_path)
        elif format_type == 'feather':
            return pd.read_feather(file_path)
        elif format_type == 'duckdb':
            # For DuckDB, we'll need to use a different approach
            # For now, return empty DataFrame
            return pd.DataFrame()
        elif format_type == 'txt':
            # Try to read as CSV first
            try:
                return pd.read_csv(file_path)
            except:
                # If that fails, read as text and try to parse
                return pd.read_csv(file_path, sep='\t')
        else:
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {str(e)}")
        return pd.DataFrame()

def _save_file_by_format(df: pd.DataFrame, file_path: str, format_type: str) -> bool:
    """Save DataFrame to file based on format type."""
    try:
        if format_type == 'csv':
            df.to_csv(file_path, index=False)
        elif format_type == 'json':
            df.to_json(file_path, orient='records', indent=2)
        elif format_type == 'parquet':
            df.to_parquet(file_path, index=False)
        elif format_type == 'feather':
            df.to_feather(file_path)
        else:
            # Default to CSV
            df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {str(e)}")
        return False

def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply filters to DataFrame."""
    filtered_df = df.copy()
    
    for column, filter_config in filters.items():
        if column not in filtered_df.columns:
            continue
            
        filter_type = filter_config.get('type')
        filter_value = filter_config.get('value')
        
        if not filter_type or not filter_value:
            continue
        
        try:
            if filter_type == 'equals':
                filtered_df = filtered_df[filtered_df[column].astype(str) == str(filter_value)]
            elif filter_type == 'contains':
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(filter_value), case=False, na=False)]
            elif filter_type == 'greater_than':
                filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') > float(filter_value)]
            elif filter_type == 'less_than':
                filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') < float(filter_value)]
            elif filter_type == 'date_range':
                # Handle date range filtering
                if ' to ' in filter_value:
                    start_date, end_date = filter_value.split(' to ')
                    filtered_df = filtered_df[
                        (pd.to_datetime(filtered_df[column], errors='coerce') >= pd.to_datetime(start_date)) &
                        (pd.to_datetime(filtered_df[column], errors='coerce') <= pd.to_datetime(end_date))
                    ]
        except Exception as e:
            logger.error(f"Error applying filter {column}: {str(e)}")
            continue
    
    return filtered_df

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
    """Data tab main page - TKINTER STYLE VERSION."""
    return render_template('data_tab_tkinter_style.html')

@data_bp.route('/multi')
def data_tab_multi():
    """Multi-file data tab."""
    return render_template('data_tab_multi_file.html')

@data_bp.route('/load-multiple', methods=['POST'])
def load_multiple_files():
    """Load multiple files at once."""
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        
        if not filenames:
            return jsonify({'error': 'No filenames provided'}), 400
        
        results = {}
        errors = {}
        
        for filename in filenames:
            try:
                # Use the same logic as single file loading
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
                    errors[filename] = 'File not found'
                    continue
                
                # Detect format and load data
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
                    from redline.core.format_converter import FormatConverter
                    converter = FormatConverter()
                    df = converter.load_file_by_type(data_path, format_type)
                
                if not isinstance(df, pd.DataFrame):
                    errors[filename] = 'Invalid data format'
                    continue
                
                # Convert to JSON-serializable format
                results[filename] = {
                    'columns': list(df.columns),
                    'data': df.head(1000).to_dict('records'),  # Limit to 1000 rows
                    'total_rows': len(df),
                    'dtypes': df.dtypes.astype(str).to_dict(),
                    'filename': filename
                }
                
            except Exception as e:
                errors[filename] = str(e)
                logger.error(f"Error loading {filename}: {str(e)}")
        
        return jsonify({
            'results': results,
            'errors': errors,
            'success_count': len(results),
            'error_count': len(errors)
        })
        
    except Exception as e:
        logger.error(f"Error in load_multiple_files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/debug')
def data_tab_debug():
    """Data tab debug page."""
    return render_template('data_tab_debug.html')

@data_bp.route('/simple')
def data_tab_simple():
    """Data tab simple version."""
    return render_template('data_tab_simple.html')

@data_bp.route('/load', methods=['POST'])
def load_data():
    """Load data from file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
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
        
        # Use EXACT same data loading pipeline as Tkinter GUI
        # Detect format from file extension (same as Tkinter _detect_format_from_path)
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Use direct pandas loading for speed (same as Tkinter _load_single_file_parallel)
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
            # Fallback to loader for unsupported formats
            from redline.core.format_converter import FormatConverter
            converter = FormatConverter()
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
def get_columns(filename):
    """Get column information for a file."""
    try:
        data_path = os.path.join(os.getcwd(), 'data', filename)
        
        if not os.path.exists(data_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Use EXACT same data loading pipeline as Tkinter GUI
        # Detect format from file extension (same as Tkinter _detect_format_from_path)
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Use direct pandas loading for speed (same as Tkinter _load_single_file_parallel)
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
            # Fallback to loader for unsupported formats
            from redline.core.format_converter import FormatConverter
            converter = FormatConverter()
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

@data_bp.route('/load', methods=['POST'])
def load_file_data():
    """Load data from a file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        
        # Determine file path - check both root data directory and downloaded subdirectory
        data_dir = os.path.join(os.getcwd(), 'data')
        file_path = None
        
        # Check in root data directory first
        root_path = os.path.join(data_dir, filename)
        if os.path.exists(root_path):
            file_path = root_path
        else:
            # Check in downloaded directory
            downloaded_path = os.path.join(data_dir, 'downloaded', filename)
            if os.path.exists(downloaded_path):
                file_path = downloaded_path
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Detect file format
        format_type = _detect_format_from_path(file_path)
        if not format_type:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Load data
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        is_large_file = file_size_mb > 50  # 50MB threshold
        
        if is_large_file and format_type in ['csv', 'txt']:
            df = _load_large_file_chunked(file_path, format_type)
        else:
            df = _load_file_by_format(file_path, format_type)
        
        if df.empty:
            return jsonify({'error': 'No data found in file'}), 404
        
        # Convert to JSON-serializable format
        data_dict = df.to_dict('records')
        
        return jsonify({
            'data': data_dict,
            'columns': list(df.columns),
            'total_rows': len(df),
            'file_size': os.path.getsize(file_path),
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/filter', methods=['POST'])
def filter_file_data():
    """Apply filters to loaded data."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        filters = data.get('filters', {})
        
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        
        # Load the file first
        data_dir = 'data'
        file_path = None
        
        root_path = os.path.join(data_dir, filename)
        if os.path.exists(root_path):
            file_path = root_path
        else:
            downloaded_path = os.path.join(data_dir, 'downloaded', filename)
            if os.path.exists(downloaded_path):
                file_path = downloaded_path
        
        if not file_path:
            return jsonify({'error': 'File not found'}), 404
        
        # Load and filter data
        format_type = _detect_format_from_path(file_path)
        df = _load_file_by_format(file_path, format_type)
        
        # Apply filters
        filtered_df = _apply_filters(df, filters)
        
        # Convert to JSON-serializable format
        data_dict = filtered_df.to_dict('records')
        
        return jsonify({
            'data': data_dict,
            'columns': list(filtered_df.columns),
            'total_rows': len(filtered_df),
            'original_rows': len(df),
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Error filtering data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/export', methods=['POST'])
def export_file_data():
    """Export filtered data to a file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        format_type = data.get('format', 'csv')
        export_filename = data.get('export_filename')
        filters = data.get('filters', {})
        
        if not filename or not export_filename:
            return jsonify({'error': 'Filename and export filename are required'}), 400
        
        # Load and filter data
        data_dir = 'data'
        file_path = None
        
        root_path = os.path.join(data_dir, filename)
        if os.path.exists(root_path):
            file_path = root_path
        else:
            downloaded_path = os.path.join(data_dir, 'downloaded', filename)
            if os.path.exists(downloaded_path):
                file_path = downloaded_path
        
        if not file_path:
            return jsonify({'error': 'File not found'}), 404
        
        # Load data
        original_format = _detect_format_from_path(file_path)
        df = _load_file_by_format(file_path, original_format)
        
        # Apply filters if any
        if filters:
            df = _apply_filters(df, filters)
        
        # Export to new format
        export_path = os.path.join(data_dir, export_filename)
        _save_file_by_format(df, export_path, format_type)
        
        return jsonify({
            'message': f'Data exported successfully to {export_filename}',
            'export_path': export_path,
            'rows_exported': len(df)
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
        
        # Get files from root data directory
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                file_path = os.path.join(data_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path,
                        'location': 'root'
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


