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
            try:
                return pd.read_json(file_path, lines=True)
            except Exception:
                return pd.read_json(file_path)
        elif filetype == 'txt':
            df = pd.read_csv(file_path, delimiter='\t')
            if df.shape[1] == 1:
                df = pd.read_csv(file_path, delimiter=',')
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
            import json
            def replace_nan_in_dict(obj):
                """Recursively replace NaN values with None."""
                if isinstance(obj, dict):
                    return {k: replace_nan_in_dict(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [replace_nan_in_dict(item) for item in obj]
                elif isinstance(obj, float) and (pd.isna(obj) or pd.isnull(obj)):
                    return None
                elif pd.isna(obj):
                    return None
                return obj
            # Convert to dict and clean NaN values
            data_dict = df.to_dict(orient='records')
            cleaned_data = [replace_nan_in_dict(record) for record in data_dict]
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
        elif filetype == 'tensorflow' and np:
            np.savez(file_path, data=df.to_numpy())
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

