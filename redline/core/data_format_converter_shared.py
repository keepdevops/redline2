#!/usr/bin/env python3
"""
Format conversion utilities extracted from data_module_shared.py (shared module)
Handles format conversion and file I/O operations.
"""

import logging
import os
from typing import Union, Any
import pandas as pd

# Optional dependencies
try:
    import duckdb
except ImportError:
    duckdb = None

try:
    import tensorflow as tf
except ImportError:
    tf = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import polars as pl
except ImportError:
    pl = None

try:
    import pyarrow as pa
except ImportError:
    pa = None

logger = logging.getLogger(__name__)


class FormatConverter:
    """Format conversion utilities."""
    
    @staticmethod
    def convert_format(data: Union[pd.DataFrame, Any, Any], 
                      from_format: str, to_format: str) -> Union[pd.DataFrame, Any, Any, dict]:
        """Convert data between formats."""
        if from_format == to_format:
            return data
        if isinstance(data, list):
            return [FormatConverter.convert_format(d, from_format, to_format) for d in data]
        try:
            if from_format == 'pandas':
                if to_format == 'polars' and pl:
                    return pl.from_pandas(data)
                elif to_format == 'pyarrow' and pa:
                    return pa.Table.from_pandas(data)
            elif from_format == 'polars' and pl:
                if to_format == 'pandas':
                    return data.to_pandas()
                elif to_format == 'pyarrow' and pa:
                    return data.to_arrow()
            elif from_format == 'pyarrow' and pa:
                if to_format == 'pandas':
                    return data.to_pandas()
                elif to_format == 'polars' and pl:
                    return pl.from_arrow(data)
            logger.info(f"Converted from {from_format} to {to_format}")
            return data
        except Exception as e:
            logger.error(f"Conversion failed from {from_format} to {to_format}: {str(e)}")
            raise

    @staticmethod
    def load_file_by_type(file_path, filetype=None):
        """Load file by type."""
        from redline.core.data_loader_shared import DataLoader
        ext = os.path.splitext(file_path)[1].lower()
        if not filetype:
            filetype = DataLoader.EXT_TO_FORMAT.get(ext, None)
        if filetype == 'csv':
            return pd.read_csv(file_path)
        elif filetype == 'json':
            # Handle JSON files that might be scalar objects (like api_keys.json)
            # or empty objects (like custom_apis.json)
            try:
                import json
                with open(file_path, 'r') as f:
                    json_data = json.load(f)
                
                # If it's an empty object or scalar values, return empty DataFrame
                if not json_data or (isinstance(json_data, dict) and not any(isinstance(v, (list, dict)) for v in json_data.values())):
                    return pd.DataFrame()
                
                # Try to read as DataFrame
                try:
                    return pd.read_json(file_path, lines=True)
                except Exception:
                    return pd.read_json(file_path)
            except ValueError as e:
                # Handle "If using all scalar values, you must pass an index" error
                if "scalar values" in str(e):
                    return pd.DataFrame()
                raise
        elif filetype == 'txt':
            # Try multiple delimiters for TXT files
            try:
                # First try comma-separated (most common for Stooq format)
                df = pd.read_csv(file_path, delimiter=',')
            except Exception:
                try:
                    # Try tab-separated
                    df = pd.read_csv(file_path, delimiter='\t')
                except Exception:
                    # Try other common separators
                    for sep in [';', ' ', '|']:
                        try:
                            df = pd.read_csv(file_path, sep=sep)
                            break
                        except Exception:
                            continue
                    else:
                        # If all separators fail, try fixed-width
                        df = pd.read_fwf(file_path)
            
            # Standardize columns if method exists
            from redline.core.data_loader_shared import DataLoader
            if hasattr(DataLoader, '_standardize_txt_columns'):
                loader = DataLoader()
                df = loader._standardize_txt_columns(df)
            return df
        elif filetype == 'parquet':
            return pd.read_parquet(file_path)
        elif filetype == 'feather':
            return pd.read_feather(file_path)
        elif filetype == 'duckdb' and duckdb:
            conn = duckdb.connect(file_path)
            tables = conn.execute("SHOW TABLES").fetchall()
            if not tables:
                conn.close()
                raise ValueError("No tables found in DuckDB file")
            table_name = tables[0][0]
            df = conn.execute(f"SELECT * FROM {table_name} LIMIT 100").fetchdf()
            conn.close()
            return df
        elif filetype == 'keras' and tf:
            return tf.keras.models.load_model(file_path)
        else:
            raise ValueError(f"Unsupported file type: {filetype}")

    @staticmethod
    def save_file_by_type(df, file_path, filetype):
        """Save file by type."""
        if filetype == 'csv':
            df.to_csv(file_path, index=False)
        elif filetype == 'txt':
            df.to_csv(file_path, sep='\t', index=False)
        elif filetype == 'json':
            # Replace NaN/NaT values with None before saving to JSON
            # This ensures valid JSON output (NaN is not valid JSON)
            from ...utils.json_utils import clean_dataframe_for_json
            import json
            # Convert to dict and clean NaN values using centralized utility
            cleaned_data = clean_dataframe_for_json(df)
            # Write JSON directly (lines format for compatibility)
            with open(file_path, 'w') as f:
                for record in cleaned_data:
                    json.dump(record, f)
                    f.write('\n')
        elif filetype == 'feather':
            df.reset_index(drop=True).to_feather(file_path)
        elif filetype == 'parquet':
            df.to_parquet(file_path)
        elif filetype == 'keras' and tf:
            from tensorflow.keras import Sequential, Input
            from tensorflow.keras.layers import Dense
            model = Sequential([
                Input(shape=(len(df.columns),)),
                Dense(32, activation='relu'),
                Dense(1)
            ])
            model.save(file_path)
        elif filetype == 'duckdb' and duckdb:
            conn = duckdb.connect(file_path)
            conn.register('temp_df', df)
            conn.execute("CREATE TABLE IF NOT EXISTS tickers_data AS SELECT * FROM temp_df")
            conn.unregister('temp_df')
            conn.close()
        elif filetype in ('tensorflow', 'npz'):
            if not np:
                raise ImportError("NumPy is required for .npz format but is not available. Please install numpy: pip install numpy")
            try:
                np.savez(file_path, data=df.to_numpy())
            except Exception as e:
                logger.error(f"Error saving NPZ file: {str(e)}")
                raise Exception(f"Failed to save .npz file: {str(e)}")
        elif filetype == 'polars' and pl:
            if not isinstance(df, pl.DataFrame):
                try:
                    df = pl.from_pandas(df)
                except Exception:
                    raise ValueError("Data must be convertible to polars DataFrame for 'polars' save type.")
            df.write_parquet(file_path)
        elif filetype == 'pyarrow' and pa:
            table = pa.Table.from_pandas(df)
            import pyarrow.parquet as pq
            pq.write_table(table, file_path)
        else:
            raise ValueError(f"Unsupported save file type: {filetype}")

