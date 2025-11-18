"""
File loading utilities for REDLINE Web GUI
Extracted from redline/web/routes/data.py for better organization
"""

import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any
from flask import current_app
from ...core.data_loader import DataLoader
from ...core.schema import EXT_TO_FORMAT, detect_format_from_path

logger = logging.getLogger(__name__)

# Rate limiting decorator (if limiter is available)
def rate_limit(limit_string):
    """Decorator for rate limiting - gracefully handles missing limiter."""
    def decorator(func):
        try:
            limiter = current_app.config.get('limiter') if current_app else None
            if limiter:
                from flask_limiter import Limiter
                return limiter.limit(limit_string)(func)
            return func
        except:
            return func
    return decorator

# Format detection is now centralized in redline.core.schema.detect_format_from_path
# Imported above for use in this module

def load_single_file_parallel(file_path: str) -> Optional[pd.DataFrame]:
    """Load a single file - optimized for speed with parallel processing (same as tkinter GUI)."""
    try:
        # Detect format from extension
        format_type = detect_format_from_path(file_path)
        
        # Use direct pandas loading for speed (skip validation/cleaning for display)
        if format_type == 'csv':
            data = pd.read_csv(file_path)
        elif format_type == 'txt':
            # Try to read as CSV first, then try different separators
            try:
                data = pd.read_csv(file_path)
            except:
                # Try different separators for TXT files
                for sep in ['\t', ';', ' ', '|']:
                    try:
                        data = pd.read_csv(file_path, sep=sep)
                        break
                    except:
                        continue
                else:
                    # If all separators fail, try reading as fixed-width
                    data = pd.read_fwf(file_path)
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

def load_files_parallel(file_paths: List[str]) -> Dict[str, Any]:
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
                executor.submit(load_single_file_parallel, file_path): file_path
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

def load_file_by_format(file_path: str, format_type: str) -> pd.DataFrame:
    """Load file based on format type."""
    try:
        if format_type == 'csv':
            return pd.read_csv(file_path)
        elif format_type == 'txt':
            # Try to read as CSV first, then try different separators
            try:
                return pd.read_csv(file_path)
            except:
                # Try different separators for TXT files
                for sep in ['\t', ';', ' ', '|']:
                    try:
                        return pd.read_csv(file_path, sep=sep)
                    except:
                        continue
                else:
                    # If all separators fail, try reading as fixed-width
                    return pd.read_fwf(file_path)
        elif format_type == 'json':
            return pd.read_json(file_path)
        elif format_type == 'parquet':
            return pd.read_parquet(file_path)
        elif format_type == 'feather':
            return pd.read_feather(file_path)
        elif format_type == 'duckdb':
            import duckdb
            conn = None
            try:
                conn = duckdb.connect(file_path, read_only=True)
                # Try to find the table name - check common names first
                tables = conn.execute("SHOW TABLES").fetchall()
                if not tables:
                    raise ValueError("No tables found in DuckDB file")
                
                # Try to find a table with data (skip empty tables)
                df = pd.DataFrame()
                table_name = None
                for table_tuple in tables:
                    candidate_table = table_tuple[0]
                    # Check if table has data
                    count = conn.execute(f"SELECT COUNT(*) FROM {candidate_table}").fetchone()[0]
                    if count > 0:
                        table_name = candidate_table
                        logger.info(f"Loading data from DuckDB table: {table_name} ({count} rows)")
                        df = conn.execute(f"SELECT * FROM {table_name}").fetchdf()
                        break
                
                if df.empty:
                    # If no table with data found, try the first table anyway
                    table_name = tables[0][0]
                    logger.warning(f"No tables with data found, trying first table: {table_name}")
                    df = conn.execute(f"SELECT * FROM {table_name}").fetchdf()
                    if df.empty:
                        logger.warning(f"DuckDB table {table_name} is empty")
                        return pd.DataFrame()
                
                logger.info(f"Successfully loaded {len(df)} rows from DuckDB table {table_name}")
                return df
            except Exception as e:
                logger.error(f"Error loading DuckDB file {file_path}: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
            finally:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
        else:
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {str(e)}")
        return pd.DataFrame()

def save_file_by_format(df: pd.DataFrame, file_path: str, format_type: str) -> bool:
    """Save DataFrame to file based on format type."""
    try:
        if format_type == 'csv':
            df.to_csv(file_path, index=False)
        elif format_type == 'json':
            # Replace NaN/NaT values with None before saving to JSON
            # This ensures valid JSON output (NaN is not valid JSON)
            from ...utils.json_utils import clean_dataframe_for_json
            import json
            # Convert to dict and clean NaN values using centralized utility
            cleaned_data = clean_dataframe_for_json(df)
            # Write JSON directly
            with open(file_path, 'w') as f:
                json.dump(cleaned_data, f, indent=2, default=str)
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

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
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

def load_large_file_chunked(file_path: str, format_type: str, chunk_size: int = 10000) -> pd.DataFrame:
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

