#!/usr/bin/env python3
"""REDLINE module for stock market data management in a Docker/Podman container."""

import logging
import sys
import configparser
import pandas as pd
import polars as pl
import pyarrow as pa
import duckdb
import sqlalchemy
from sqlalchemy import create_engine
import tensorflow as tf
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.simpledialog import askstring
from typing import Union, List, Dict
import argparse
import os
import traceback
import tkinter.font as tkFont
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import numpy as np
import threading
from data_user_manual import show_user_manual_popup

# Configure logging
logging.basicConfig(filename='redline.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataLoader:
    SCHEMA = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint', 'format']
    EXT_TO_FORMAT = {
        '.csv': 'csv',
        '.txt': 'txt',
        '.json': 'json',
        '.duckdb': 'duckdb',
        '.parquet': 'parquet',
        '.feather': 'feather',
        '.h5': 'keras'
    }
    # Centralized mapping for file dialog info: format -> (extension, description, pattern)
    FORMAT_DIALOG_INFO = {
        'csv':     ('.csv',     'CSV Files', '*.csv'),
        'txt':     ('.txt',     'TXT Files', '*.txt'),
        'json':    ('.json',    'JSON Files', '*.json'),
        'duckdb':  ('.duckdb',  'DuckDB Files', '*.duckdb'),
        'parquet': ('.parquet', 'Parquet Files', '*.parquet'),
        'feather': ('.feather', 'Feather Files', '*.feather'),
        'keras':   ('.h5',      'Keras Model', '*.h5'),
        'tensorflow': ('.npz',  'NumPy Zip', '*.npz')
    }

    @staticmethod
    def clean_and_select_columns(data: pd.DataFrame) -> pd.DataFrame:
        # Ensure all schema columns are present
        for col in DataLoader.SCHEMA:
            if col not in data.columns:
                data[col] = None
        data = data[DataLoader.SCHEMA]
        # Clean numeric columns to ensure no arrays/lists and cast to float
        for col in ['open', 'high', 'low', 'close', 'vol', 'openint']:
            if col in data.columns:
                data[col] = data[col].apply(lambda x: float(x) if pd.notnull(x) and not isinstance(x, (list, tuple, dict)) else None)
        return data

    def __init__(self, config_path: str = 'data_config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.db_path = self.config['Data'].get('db_path', '/app/redline_data.duckdb')
        self.csv_dir = self.config['Data'].get('csv_dir', '/app/data')
        self.json_dir = self.config['Data'].get('json_dir', '/app/data/json')
        self.parquet_dir = self.config['Data'].get('parquet_dir', '/app/data/parquet')

    def load_data(self, file_paths: List[str], format: str) -> List[Union[pd.DataFrame, pl.DataFrame, pa.Table]]:
        data = []
        for path in file_paths:
            if not self.validate_data(path, format):
                raise ValueError(f"Invalid data in {path} for format {format}")
            try:
                if format == 'csv':
                    df = pd.read_csv(path)
                elif format == 'txt':
                    df = pd.read_csv(path, delimiter='\t')
                    if df.shape[1] == 1:
                        df = pd.read_csv(path, delimiter=',')
                    df = self._standardize_txt_columns(df)
                    print(f'Loaded DataFrame shape: {df.shape}')
                elif format == 'json':
                    df = pd.read_json(path)
                elif format == 'duckdb':
                    conn = duckdb.connect(path)
                    df = conn.execute("SELECT * FROM tickers_data").fetchdf()
                    conn.close()
                elif format == 'pyarrow':
                    df = pa.parquet.read_table(path)
                elif format == 'polars':
                    df = pl.read_parquet(path)
                elif format == 'keras':
                    df = tf.keras.models.load_model(path)
                else:
                    df = None
                if format in ['csv', 'txt', 'json', 'duckdb']:
                    data.append(df)
                else:
                    data.append(df)
                logging.info(f"Loaded {path} as {format}")
            except Exception as e:
                logging.error(f"Failed to load {path}: {str(e)}")
                print(f"Failed to load {path}: {str(e)}")
                raise
        return data

    def validate_data(self, file_path: str, format: str) -> bool:
        try:
            if format in ['csv', 'json', 'txt']:
                if format == 'csv':
                    df = pd.read_csv(file_path)
                elif format == 'txt':
                    df = pd.read_csv(file_path, delimiter='\t')
                    if df.shape[1] == 1:
                        df = pd.read_csv(file_path, delimiter=',')
                    df = self._standardize_txt_columns(df)
                else:
                    df = pd.read_json(file_path)
                required = ['ticker', 'timestamp', 'close']
                return all(col in df.columns for col in required)
            return True  # Simplified for other formats
        except Exception as e:
            logging.error(f"Validation failed for {file_path}: {str(e)}")
            print(f"Validation failed for {file_path}: {str(e)}")
            return False

    def convert_format(self, data: Union[pd.DataFrame, pl.DataFrame, pa.Table], from_format: str, to_format: str) -> Union[pd.DataFrame, pl.DataFrame, pa.Table, dict]:
        if from_format == to_format:
            return data
        if isinstance(data, list):
            return [self.convert_format(d, from_format, to_format) for d in data]
        try:
            if from_format == 'pandas':
                if to_format == 'polars':
                    return pl.from_pandas(data)
                elif to_format == 'pyarrow':
                    return pa.Table.from_pandas(data)
            elif from_format == 'polars':
                if to_format == 'pandas':
                    return data.to_pandas()
                elif to_format == 'pyarrow':
                    return data.to_arrow()
            elif from_format == 'pyarrow':
                if to_format == 'pandas':
                    return data.to_pandas()
                elif to_format == 'polars':
                    return pl.from_arrow(data)
            logging.info(f"Converted from {from_format} to {to_format}")
            return data
        except Exception as e:
            logging.error(f"Conversion failed from {from_format} to {to_format}: {str(e)}")
            raise

    def save_to_shared(self, table: str, data: Union[pd.DataFrame, pl.DataFrame, pa.Table], format: str) -> None:
        try:
            # Convert to pandas DataFrame if needed
            if isinstance(data, pl.DataFrame):
                data = data.to_pandas()
            elif isinstance(data, pa.Table):
                data = data.to_pandas()
            data['format'] = format
            data = DataLoader.clean_and_select_columns(data)
            # Diagnostic: print dtypes and sample values
            print("Column dtypes before saving:")
            print(data.dtypes)
            for col in ['open', 'high', 'low', 'close', 'vol', 'openint']:
                if col in data.columns:
                    print(f"Sample values for {col}:")
                    print(data[col].head(10).to_list())
            # Create table if not exists and insert data using DuckDB native
            conn = duckdb.connect(self.db_path)
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table} (
                ticker VARCHAR,
                timestamp VARCHAR,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                vol DOUBLE,
                openint DOUBLE,
                format VARCHAR
            )
            """
            conn.execute(create_table_sql)
            # Insert data
            conn.register('temp_df', data)
            insert_sql = f"INSERT INTO {table} SELECT * FROM temp_df"
            conn.execute(insert_sql)
            conn.unregister('temp_df')
            conn.close()
            logging.info(f"Saved data to {table} in format {format}")
        except Exception as e:
            logging.exception(f"Failed to save to {table}: {str(e)}")
            print(f"Failed to save to {table}: {str(e)}")
            raise

    def _standardize_txt_columns(self, df):
        print('Original columns:', list(df.columns))
        # Remove BOM and strip whitespace from column names
        df.columns = [c.lstrip('\ufeff').strip() for c in df.columns]
        col_map = {}
        for c in df.columns:
            cl = c.strip('<>').strip().upper()
            if cl == 'TICKER':
                col_map[c] = 'ticker'
            elif cl == 'PER':
                col_map[c] = 'per'
            elif cl == 'DATE':
                col_map[c] = 'date'
            elif cl == 'TIME':
                col_map[c] = 'time'
            elif cl == 'CLOSE':
                col_map[c] = 'close'
            elif cl == 'OPEN':
                col_map[c] = 'open'
            elif cl == 'HIGH':
                col_map[c] = 'high'
            elif cl == 'LOW':
                col_map[c] = 'low'
            elif cl == 'VOL':
                col_map[c] = 'vol'
            elif cl == 'OPENINT':
                col_map[c] = 'openint'
        df = df.rename(columns=col_map)
        print('Mapped columns:', list(df.columns))
        # Combine date and time into timestamp if present
        if 'date' in df.columns and 'time' in df.columns:
            df['timestamp'] = df['date'].astype(str) + ' ' + df['time'].astype(str)
        elif 'date' in df.columns:
            df['timestamp'] = df['date'].astype(str)
        # Define the columns you want to keep
        keep = [c for c in ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint'] if c in df.columns]
        # Drop 'date', 'time', and 'per' columns after creating 'timestamp', but only if not in keep
        for col in ['date', 'time', 'per']:
            if col in df.columns and col not in keep:
                df = df.drop(columns=[col])
        # Now select only the columns you want to keep
        df = df[keep]
        if all(k in df.columns for k in ['ticker', 'timestamp', 'close']):
            return df
        return df

    @staticmethod
    def load_file_by_type(file_path, filetype=None):
        import duckdb
        import tensorflow as tf
        import pandas as pd
        import numpy as np
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
            # Use the standardize method if available
            if hasattr(DataLoader, '_standardize_txt_columns'):
                df = DataLoader._standardize_txt_columns(DataLoader, df)
            return df
        elif filetype == 'parquet':
            return pd.read_parquet(file_path)
        elif filetype == 'feather':
            return pd.read_feather(file_path)
        elif filetype == 'duckdb':
            conn = duckdb.connect(file_path)
            tables = conn.execute("SHOW TABLES").fetchall()
            if not tables:
                conn.close()
                raise ValueError("No tables found in DuckDB file")
            table_name = tables[0][0]
            df = conn.execute(f"SELECT * FROM {table_name} LIMIT 100").fetchdf()
            conn.close()
            return df
        elif filetype == 'keras':
            return tf.keras.models.load_model(file_path)
        else:
            raise ValueError(f"Unsupported file type: {filetype}")

    @staticmethod
    def save_file_by_type(df, file_path, filetype):
        import duckdb
        import numpy as np
        import tensorflow as tf
        import polars as pl
        if filetype == 'csv':
            df.to_csv(file_path, index=False)
        elif filetype == 'txt':
            df.to_csv(file_path, sep='\t', index=False)
        elif filetype == 'json':
            df.to_json(file_path, orient='records', lines=True)
        elif filetype == 'feather':
            df.reset_index(drop=True).to_feather(file_path)
        elif filetype == 'parquet':
            df.to_parquet(file_path)
        elif filetype == 'keras':
            from tensorflow.keras import Sequential, Input
            from tensorflow.keras.layers import Dense
            model = Sequential([
                Input(shape=(len(df.columns),)),
                Dense(32, activation='relu'),
                Dense(1)
            ])
            model.save(file_path)
        elif filetype == 'duckdb':
            conn = duckdb.connect(file_path)
            conn.register('temp_df', df)
            conn.execute("CREATE TABLE IF NOT EXISTS tickers_data AS SELECT * FROM temp_df")
            conn.unregister('temp_df')
            conn.close()
        elif filetype == 'tensorflow':
            np.savez(file_path, data=df.to_numpy())
        elif filetype == 'polars':
            # Save as .parquet using polars
            if not isinstance(df, pl.DataFrame):
                try:
                    df = pl.from_pandas(df)
                except Exception:
                    raise ValueError("Data must be convertible to polars DataFrame for 'polars' save type.")
            df.write_parquet(file_path)
        else:
            raise ValueError(f"Unsupported save file type: {filetype}")

    def analyze_ticker_distribution(self, data: pd.DataFrame) -> dict:
        """
        Analyze the distribution of records across tickers.
        """
        stats = {
            'total_records': len(data),
            'total_tickers': data['ticker'].nunique(),
            'records_per_ticker': data.groupby('ticker').size().to_dict(),
            'date_ranges': data.groupby('ticker').agg({
                'timestamp': ['min', 'max']
            }).to_dict()
        }
        stats['avg_records_per_ticker'] = stats['total_records'] // stats['total_tickers']
        return stats

    def filter_data_by_date_range(self, data: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Filter the dataframe by date range for all tickers.
        """
        try:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            mask = (data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)
            filtered_data = data.loc[mask]
            
            if filtered_data.empty:
                logging.warning(f"No data found between {start_date} and {end_date}")
            else:
                logging.info(f"Filtered data from {start_date} to {end_date}. Tickers: {filtered_data['ticker'].unique()}")
                
            return filtered_data
        except Exception as e:
            logging.error(f"Error filtering data by date range: {str(e)}")
            raise

    def balance_ticker_data(self, data: pd.DataFrame, target_records_per_ticker: int = None, 
                           min_records_per_ticker: int = None) -> pd.DataFrame:
        """
        Balance data across tickers by sampling or limiting records.
        """
        try:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            ticker_counts = data.groupby('ticker').size()
            
            if target_records_per_ticker is None:
                target_records_per_ticker = int(ticker_counts.median())
            
            if min_records_per_ticker is None:
                min_records_per_ticker = target_records_per_ticker // 2
                
            balanced_dfs = []
            
            for ticker in ticker_counts.index:
                ticker_data = data[data['ticker'] == ticker]
                
                if len(ticker_data) < min_records_per_ticker:
                    logging.warning(f"Skipping ticker {ticker}: insufficient records ({len(ticker_data)} < {min_records_per_ticker})")
                    continue
                    
                if len(ticker_data) > target_records_per_ticker:
                    ticker_data = ticker_data.sort_values('timestamp')
                    step = len(ticker_data) // target_records_per_ticker
                    balanced_dfs.append(ticker_data.iloc[::step].head(target_records_per_ticker))
                else:
                    balanced_dfs.append(ticker_data)
            
            if not balanced_dfs:
                raise ValueError("No tickers met the minimum record requirement")
                
            balanced_data = pd.concat(balanced_dfs, ignore_index=True)
            
            # Log statistics
            original_stats = self.analyze_ticker_distribution(data)
            balanced_stats = self.analyze_ticker_distribution(balanced_data)
            
            logging.info(f"Original data: {original_stats['total_records']} records across {original_stats['total_tickers']} tickers")
            logging.info(f"Balanced data: {balanced_stats['total_records']} records across {balanced_stats['total_tickers']} tickers")
            
            return balanced_data
            
        except Exception as e:
            logging.error(f"Error balancing ticker data: {str(e)}")
            raise

class DatabaseConnector:
    def __init__(self, db_path: str = '/app/redline_data.duckdb'):
        self.db_path = db_path

    def create_connection(self, db_path: str):
        return duckdb.connect(db_path)

    def read_shared_data(self, table: str, format: str) -> Union[pd.DataFrame, pl.DataFrame, pa.Table]:
        try:
            conn = duckdb.connect(self.db_path)
            df = conn.execute(f"SELECT * FROM {table}").fetchdf()
            conn.close()
            if format == 'polars':
                return pl.from_pandas(df)
            elif format == 'pyarrow':
                return pa.Table.from_pandas(df)
            return df
        except Exception as e:
            logging.error(f"Failed to read from {table}: {str(e)}")
            print(f"Failed to read from {table}: {str(e)}")
            raise

    def write_shared_data(self, table: str, data: Union[pd.DataFrame, pl.DataFrame, pa.Table], format: str) -> None:
        try:
            if isinstance(data, pl.DataFrame):
                data = data.to_pandas()
            elif isinstance(data, pa.Table):
                data = data.to_pandas()
            data['format'] = format
            data = DataLoader.clean_and_select_columns(data)
            # Diagnostic: print dtypes and sample values
            print("Column dtypes before saving:")
            print(data.dtypes)
            for col in ['open', 'high', 'low', 'close', 'vol', 'openint']:
                if col in data.columns:
                    print(f"Sample values for {col}:")
                    print(data[col].head(10).to_list())
            conn = duckdb.connect(self.db_path)
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table} (
                ticker VARCHAR,
                timestamp VARCHAR,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                vol DOUBLE,
                openint DOUBLE,
                format VARCHAR
            )
            """
            conn.execute(create_table_sql)
            # Insert data
            conn.register('temp_df', data)
            insert_sql = f"INSERT INTO {table} SELECT * FROM temp_df"
            conn.execute(insert_sql)
            conn.unregister('temp_df')
            conn.close()
            logging.info(f"Wrote data to {table} in format {format}")
        except Exception as e:
            logging.exception(f"Failed to write to {table}: {str(e)}")
            print(f"Failed to write to {table}: {str(e)}")
            raise

class DataAdapter:
    def prepare_training_data(self, data: Union[List[pd.DataFrame], List[pl.DataFrame], List[pa.Table]], format: str) -> Union[List['np.ndarray'], tf.data.Dataset]:
        try:
            if isinstance(data, list) and data:
                if format == 'numpy':
                    return [d.to_numpy() for d in data if isinstance(d, (pd.DataFrame, pl.DataFrame))]
                elif format == 'tensorflow':
                    return tf.data.Dataset.from_tensor_slices([d.to_numpy() for d in data if isinstance(d, (pd.DataFrame, pl.DataFrame))])
            return []
        except Exception as e:
            logging.error(f"Failed to prepare training data: {str(e)}")
            raise

    def prepare_rl_state(self, data: Union[pd.DataFrame, pl.DataFrame, pa.Table], portfolio: Dict, format: str) -> Union['np.ndarray', tf.Tensor]:
        try:
            if isinstance(data, (pl.DataFrame, pa.Table)):
                data = data.to_pandas()
            state = data[['close']].to_numpy()
            if format == 'tensorflow':
                return tf.convert_to_tensor(state, dtype=tf.float32)
            return state
        except Exception as e:
            logging.error(f"Failed to prepare RL state: {str(e)}")
            raise

    def summarize_preprocessed(self, data: Union[List['np.ndarray'], tf.data.Dataset], format: str) -> Dict:
        try:
            return {'format': format, 'size': len(data)}
        except Exception as e:
            logging.error(f"Failed to summarize preprocessed data: {str(e)}")
            raise

class StockAnalyzerGUI:
    def __init__(self, root: tk.Tk, loader: DataLoader, connector: DatabaseConnector):
        self.root = root
        self.root.title("REDLINE Data Conversion Utility")
        
        # Set minimum window size
        self.root.minsize(1200, 800)  # Increased from default size
        
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.loader = loader
        self.connector = connector
        self.adapter = DataAdapter()
        
        # Setup notebook with grid
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.setup_tabs()
        self.setup_bindings()

    def setup_tabs(self):
        # Data Loader Tab
        loader_frame = ttk.Frame(self.notebook)
        self.notebook.add(loader_frame, text='Data Loader')

        # File group section
        file_group = ttk.LabelFrame(loader_frame, text="File Selection")
        file_group.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        file_group.grid_columnconfigure(0, weight=1)
        file_group.grid_rowconfigure(1, weight=1)  # For listbox

        # Button frame
        button_frame = ttk.Frame(file_group)
        button_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Buttons in button frame
        ttk.Button(button_frame, text="Browse Files", command=self.browse_files).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Select All", command=self.select_all_files).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Deselect All", command=self.deselect_all_files).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Analyze Selected", command=self.analyze_selected_files).grid(row=0, column=3, padx=5)

        # Listbox with scrollbars
        listbox_frame = ttk.Frame(file_group)
        listbox_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)

        self.input_listbox = tk.Listbox(listbox_frame, selectmode='multiple')
        listbox_scroll_y = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.input_listbox.yview)
        listbox_scroll_x = ttk.Scrollbar(listbox_frame, orient='horizontal', command=self.input_listbox.xview)

        self.input_listbox.grid(row=0, column=0, sticky='nsew')
        listbox_scroll_y.grid(row=0, column=1, sticky='ns')
        listbox_scroll_x.grid(row=1, column=0, sticky='ew')

        self.input_listbox.configure(yscrollcommand=listbox_scroll_y.set, xscrollcommand=listbox_scroll_x.set)

        # Selection info
        self.selection_info = ttk.Label(file_group, text="")
        self.selection_info.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

        # Right side: Controls frame
        right_side_frame = ttk.Frame(loader_frame)
        right_side_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10, sticky='nsew')

        # Format controls group
        format_group = ttk.LabelFrame(right_side_frame, text="Format Settings")
        format_group.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        format_group.grid_columnconfigure(0, weight=1)

        # Input format frame
        input_format_frame = ttk.Frame(format_group)
        input_format_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        input_format_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(input_format_frame, text="Input Format:").grid(row=0, column=0, sticky='w')
        self.input_format = ttk.Combobox(input_format_frame, values=['csv', 'json', 'duckdb', 'parquet', 'feather', 'keras'])
        self.input_format.grid(row=0, column=1, sticky='ew', padx=5)

        # Output format frame
        output_format_frame = ttk.Frame(format_group)
        output_format_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        output_format_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(output_format_frame, text="Output Format:").grid(row=0, column=0, sticky='w')
        self.output_format = ttk.Combobox(output_format_frame, values=['csv', 'json', 'duckdb', 'parquet', 'feather', 'keras'])
        self.output_format.grid(row=0, column=1, sticky='ew', padx=5)

        # Date range frame
        date_frame = ttk.LabelFrame(format_group, text="Date Range")
        date_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        date_frame.grid_columnconfigure(1, weight=1)

        # Start date
        start_date_frame = ttk.Frame(date_frame)
        start_date_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        start_date_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(start_date_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w')
        self.start_date_entry = ttk.Entry(start_date_frame)
        self.start_date_entry.grid(row=0, column=1, sticky='ew', padx=5)

        # End date
        end_date_frame = ttk.Frame(date_frame)
        end_date_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        end_date_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(end_date_frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w')
        self.end_date_entry = ttk.Entry(end_date_frame)
        self.end_date_entry.grid(row=0, column=1, sticky='ew', padx=5)

        # Balance frame
        balance_frame = ttk.LabelFrame(format_group, text="Data Balance")
        balance_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
        balance_frame.grid_columnconfigure(1, weight=1)

        # Target records
        target_frame = ttk.Frame(balance_frame)
        target_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        target_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(target_frame, text="Target Records per Ticker:").grid(row=0, column=0, sticky='w')
        self.target_records_entry = ttk.Entry(target_frame)
        self.target_records_entry.grid(row=0, column=1, sticky='ew', padx=5)

        # Minimum records
        min_frame = ttk.Frame(balance_frame)
        min_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        min_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(min_frame, text="Minimum Records Required:").grid(row=0, column=0, sticky='w')
        self.min_records_entry = ttk.Entry(min_frame)
        self.min_records_entry.grid(row=0, column=1, sticky='ew', padx=5)

        # Help text
        help_text = "Leave blank to use automatic values:\n" \
                    "- Target: Median of available records\n" \
                    "- Minimum: Half of target"
        help_label = ttk.Label(balance_frame, text=help_text, wraplength=400)
        help_label.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Action buttons frame
        action_frame = ttk.Frame(loader_frame)
        action_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=10)
        action_frame.grid_columnconfigure(0, weight=1)

        # Action buttons
        ttk.Button(action_frame, text="Preview Selected", 
                   command=self.preview_selected_loader_file).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Preprocess Selected", 
                   command=self.preprocess_selected_loader_file).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="Load and Convert", 
                   command=self.load_and_convert).grid(row=0, column=2, padx=5)
        ttk.Button(action_frame, text="Show Manual", 
                   command=self.show_loader_manual).grid(row=0, column=3, padx=5)
        ttk.Button(action_frame, text="User Manual", 
                   command=lambda: show_user_manual_popup(self.root)).grid(row=0, column=4, padx=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(loader_frame, mode='indeterminate')
        self.progress_bar.grid(row=3, column=0, sticky='ew', padx=5, pady=10)

        # Configure loader frame grid weights
        loader_frame.grid_rowconfigure(1, weight=1)  # Format group gets extra space
        loader_frame.grid_columnconfigure(0, weight=1)

        # Data View Tab
        view_frame = ttk.Frame(self.notebook)
        self.notebook.add(view_frame, text='Data View')

        # Left: File list and action buttons
        left_frame = ttk.Frame(view_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ns')
        ttk.Label(left_frame, text="Available Data Files:").grid(row=0, column=0, sticky='w')
        self.file_listbox = tk.Listbox(left_frame, width=40, selectmode='extended', height=12)
        self.file_listbox.grid(row=1, column=0, sticky='nsew', pady=5)
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=2, column=0, pady=5, sticky='ew')
        ttk.Button(btn_frame, text="View File", command=self.view_selected_file).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Remove File", command=self.remove_selected_file).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="Refresh Data", command=self.refresh_data).grid(row=0, column=2, padx=2)
        view_help_btn = ttk.Button(btn_frame, text='?', width=2, command=self.show_view_manual)
        view_help_btn.grid(row=0, column=3, padx=2)
        # User Manual button now grouped with other buttons
        view_manual_btn = ttk.Button(btn_frame, text='User Manual', command=lambda: show_user_manual_popup(self.root))
        view_manual_btn.grid(row=0, column=4, padx=2)

        # Right: Data table with scrollbars
        right_frame = ttk.Frame(view_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        tree_frame = ttk.Frame(right_frame)
        tree_frame.grid(row=0, column=0, sticky='nsew')
        xscroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        yscroll = ttk.Scrollbar(tree_frame, orient='vertical')
        self.data_tree = ttk.Treeview(tree_frame, columns=['Ticker', 'Date', 'Close', 'Format'], show='headings', xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
        xscroll.config(command=self.data_tree.xview)
        yscroll.config(command=self.data_tree.yview)
        self.data_tree.grid(row=0, column=0, sticky='nsew')
        xscroll.grid(row=1, column=0, sticky='ew')
        yscroll.grid(row=0, column=1, sticky='ns')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Configure main view_frame grid
        view_frame.grid_rowconfigure(0, weight=1)
        view_frame.grid_columnconfigure(0, weight=0)
        view_frame.grid_columnconfigure(1, weight=1)

        self.refresh_file_list()

    def browse_files(self):
        filetypes = [(desc, pattern) for (_, desc, pattern) in DataLoader.FORMAT_DIALOG_INFO.values()]
        files = filedialog.askopenfilenames(filetypes=filetypes)
        self.input_listbox.delete(0, tk.END)
        detected_types = []
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            fmt = DataLoader.EXT_TO_FORMAT.get(ext, 'unknown')
            detected_types.append(fmt)
            display_name = f"{file} [{fmt}]"
            self.input_listbox.insert(tk.END, display_name)
        
        # Set input format to the most common detected type
        if detected_types:
            from collections import Counter
            most_common = Counter(detected_types).most_common(1)[0][0]
            if most_common != 'unknown':
                self.input_format.set(most_common)
        
        # Update selection info
        self.update_selection_info()

    def select_all_files(self):
        """Select all files in the listbox"""
        self.input_listbox.select_set(0, tk.END)
        self.update_selection_info()

    def deselect_all_files(self):
        """Deselect all files in the listbox"""
        self.input_listbox.selection_clear(0, tk.END)
        self.update_selection_info()

    def update_selection_info(self):
        """Update the selection info label"""
        selected_count = len(self.input_listbox.curselection())
        self.selection_info.config(text=f"Selected: {selected_count} files")

    def analyze_selected_files(self):
        """Analyze currently selected files"""
        selections = self.input_listbox.curselection()
        if not selections:
            messagebox.showerror("Error", "No files selected")
            return
        
        # Get selected file paths
        file_paths = [self.input_listbox.get(idx).split(' [')[0] for idx in selections]
        
        def worker():
            try:
                self.run_in_main_thread(lambda: self.progress_bar.grid(row=3, column=0, sticky='ew', padx=5, pady=10))
                self.run_in_main_thread(lambda: self.progress_var.set(10))
                
                # Analyze files
                analysis = self.analyze_stooq_files(file_paths)
                
                # Update GUI with analysis
                self.run_in_main_thread(lambda: self.show_stooq_analysis_popup(analysis))
                
                # Auto-fill date range if found
                if analysis['summary']['earliest_date'] and analysis['summary']['latest_date']:
                    self.run_in_main_thread(lambda: self.start_date_entry.delete(0, tk.END))
                    self.run_in_main_thread(lambda: self.start_date_entry.insert(0, 
                        analysis['summary']['earliest_date'].strftime('%Y-%m-%d')))
                    self.run_in_main_thread(lambda: self.end_date_entry.delete(0, tk.END))
                    self.run_in_main_thread(lambda: self.end_date_entry.insert(0, 
                        analysis['summary']['latest_date'].strftime('%Y-%m-%d')))
                
                # Calculate and set suggested record counts
                if analysis['summary']['total_records'] and analysis['summary']['total_tickers']:
                    avg_records = analysis['summary']['total_records'] // analysis['summary']['total_tickers']
                    self.run_in_main_thread(lambda: self.target_records_entry.delete(0, tk.END))
                    self.run_in_main_thread(lambda: self.target_records_entry.insert(0, str(avg_records)))
                    self.run_in_main_thread(lambda: self.min_records_entry.delete(0, tk.END))
                    self.run_in_main_thread(lambda: self.min_records_entry.insert(0, str(avg_records // 2)))
                
            except Exception as e:
                logging.error(f"Analysis failed: {str(e)}")
                self.run_in_main_thread(lambda: messagebox.showerror("Error", f"Analysis failed: {str(e)}"))
            finally:
                self.run_in_main_thread(lambda: self.progress_bar.pack_forget())
        
        threading.Thread(target=worker, daemon=True).start()

    def load_and_convert(self):
        def worker():
            try:
                input_format = self.input_format.get()
                output_format = self.output_format.get()
                
                # Get selected files
                selections = self.input_listbox.curselection()
                if not selections:
                    self.run_in_main_thread(messagebox.showerror, "Error", "No files selected")
                    return
                
                # Get file paths
                file_paths = [self.input_listbox.get(idx).split(' [')[0] for idx in selections]
                
                # Analyze timestamps before loading
                self.run_in_main_thread(lambda: self.progress_bar.grid(row=3, column=0, sticky='ew', padx=5, pady=10))
                self.run_in_main_thread(lambda: self.progress_var.set(10))
                
                # Analyze timestamps
                summary = self.analyze_selected_files_timestamps(file_paths, input_format)
                
                # Show timestamp analysis popup
                self.run_in_main_thread(lambda: self.show_timestamp_analysis_popup(summary))
                
                self.run_in_main_thread(lambda: self.progress_var.set(30))
                
                # Continue with existing loading process
                dfs = []
                for idx, file_path in enumerate(file_paths):
                    df = self.loader.load_data([file_path], input_format)[0]
                    if df is not None:
                        dfs.append(df)
                    progress = 30 + (40 * (idx + 1) / len(file_paths))
                    self.run_in_main_thread(lambda p=progress: self.progress_var.set(p))
                
                if not dfs:
                    print("Error: No valid data loaded from file(s)")
                    self.run_in_main_thread(messagebox.showerror, "Error", "No valid data loaded")
                    self.run_in_main_thread(lambda: self.progress_bar.pack_forget())
                    return
                
                # Combine all dataframes
                data = pd.concat(dfs, ignore_index=True)
                
                # Get date range from user
                start_date = self.start_date_entry.get()
                end_date = self.end_date_entry.get()
                
                if start_date and end_date:
                    try:
                        data = self.loader.filter_data_by_date_range(data, start_date, end_date)
                    except Exception as e:
                        self.run_in_main_thread(messagebox.showerror, "Error", f"Date filtering failed: {str(e)}")
                        self.run_in_main_thread(lambda: self.progress_bar.pack_forget())
                        return
                
                self.run_in_main_thread(lambda: self.progress_var.set(80))
                
                # Get balancing parameters and continue with existing process
                try:
                    target_records = int(self.target_records_entry.get()) if self.target_records_entry.get() else None
                    min_records = int(self.min_records_entry.get()) if self.min_records_entry.get() else None
                except ValueError:
                    target_records = None
                    min_records = None
                
                # Balance the data
                try:
                    data = self.loader.balance_ticker_data(data, target_records, min_records)
                except Exception as e:
                    self.run_in_main_thread(messagebox.showerror, "Error", f"Data balancing failed: {str(e)}")
                    self.run_in_main_thread(lambda: self.progress_bar.pack_forget())
                    return
                
                self.run_in_main_thread(lambda: self.progress_var.set(90))
                
                # Continue with existing save process...
                
            except Exception as e:
                logging.error(f"Data processing failed: {str(e)}")
                self.run_in_main_thread(messagebox.showerror, "Error", f"Processing failed: {str(e)}")
            finally:
                self.run_in_main_thread(lambda: self.progress_bar.pack_forget())
        
        threading.Thread(target=worker, daemon=True).start()

    def data_cleaning_and_save(self, data, input_format, output_format, dropped_dupes):
        # This runs in the main thread
        dropna = messagebox.askyesno("Data Cleaning", f"{dropped_dupes} duplicate rows removed.\nDo you want to drop rows with missing values?")
        if dropna:
            before_dropna = len(data)
            data = data.dropna()
            after_dropna = len(data)
            dropped_na = before_dropna - after_dropna
            messagebox.showinfo("Data Cleaning", f"{dropped_na} rows with missing values dropped.")
        # Save as a single output file
        from tkinter import filedialog
        base_name = "merged_data"
        dialog_info = DataLoader.FORMAT_DIALOG_INFO.get(output_format, ('.dat', 'All Files', '*.*'))
        out_ext, desc, pattern = dialog_info
        save_path = filedialog.asksaveasfilename(
            defaultextension=out_ext,
            filetypes=[(desc, pattern)],
            initialdir='data',
            initialfile=base_name + out_ext
        )
        if not save_path:
            self.progress_bar.pack_forget()
            return
        # Always overwrite the file (no append)
        converted = self.loader.convert_format(data, input_format, output_format)
        DataLoader.save_file_by_type(converted, save_path, output_format)
        self.refresh_file_list()
        self.progress_bar.pack_forget()
        print("Success: Files merged/consolidated, cleaned, and saved as one file")
        messagebox.showinfo("Success", "Files merged/consolidated, cleaned, and saved as one file")

        # Automatically select and preview the new file in Data View
        for idx in range(self.file_listbox.size()):
            entry = self.file_listbox.get(idx)
            if save_path in entry:
                self.file_listbox.selection_clear(0, tk.END)
                self.file_listbox.selection_set(idx)
                self.file_listbox.see(idx)
                self.view_selected_file()
                self.refresh_data()
                break

    def refresh_file_list(self):
        # Recursively list all supported files in the data directory and subdirectories
        self.file_listbox.delete(0, tk.END)
        data_dir = 'data'  # preferred data directory
        supported_exts = tuple(DataLoader.EXT_TO_FORMAT.keys())
        for root, _, files in os.walk(data_dir):
            for fname in files:
                if fname.endswith(supported_exts):
                    fpath = os.path.join(root, fname)
                    ext = os.path.splitext(fname)[1].lower()
                    fmt = DataLoader.EXT_TO_FORMAT.get(ext, 'unknown')
                    display_name = f"{fpath} [{fmt}]"
                    self.file_listbox.insert(tk.END, display_name)

    def view_selected_file(self):
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No file selected")
            return
        file_path = self.file_listbox.get(selection[0])
        print("Viewing file:", file_path)
        # Remove [type] if present
        file_path = file_path.split(' [')[0]
        ext = os.path.splitext(file_path)[1].lower()
        fmt = DataLoader.EXT_TO_FORMAT.get(ext, None)
        def worker():
            try:
                if fmt == 'keras':
                    try:
                        model = DataLoader.load_file_by_type(file_path, fmt)
                        import io
                        stream = io.StringIO()
                        model.summary(print_fn=lambda x: stream.write(x + '\n'))
                        summary_str = stream.getvalue()
                        def show_keras():
                            popup = tk.Toplevel(self.root)
                            popup.title("Keras Model Summary")
                            
                            # Configure popup grid
                            popup.grid_rowconfigure(0, weight=1)
                            popup.grid_columnconfigure(0, weight=1)
                            
                            # Text widget
                            text = tk.Text(popup, wrap='word')
                            text.grid(row=0, column=0, sticky='nsew')
                            text.insert('1.0', summary_str)
                            text.configure(state='disabled')
                        self.run_in_main_thread(show_keras)
                        return
                    except Exception as e:
                        self.run_in_main_thread(lambda: messagebox.showerror("Error", f"Failed to load Keras model: {str(e)}"))
                        return
                df = DataLoader.load_file_by_type(file_path, fmt)
                print("DF columns:", df.columns)
                print(df.head())
                def update_table():
                    self.data_tree.delete(*self.data_tree.get_children())
                    cols = list(df.columns)
                    self.data_tree['columns'] = cols
                    self.data_tree['show'] = 'headings'
                    for col in cols:
                        self.data_tree.heading(col, text=col)
                        self.data_tree.column(col, width=100, stretch=True, anchor='center')
                    max_rows = 1000
                    for i, (_, row) in enumerate(df.iterrows()):
                        if i >= max_rows:
                            break
                        self.data_tree.insert('', 'end', values=tuple(row))
                self.run_in_main_thread(update_table)
            except Exception as e:
                print("Failed to read file:", file_path)
                logging.exception(f"Failed to preview file: {file_path}")
                self.run_in_main_thread(lambda: messagebox.showerror("Error", f"Failed to read file: {str(e)}"))
        threading.Thread(target=worker, daemon=True).start()

    def show_dataframe_popup(self, df):
        popup = tk.Toplevel(self.root)
        popup.title("Data Preview")
        
        # Configure popup grid
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        
        # Create frame for text and scrollbar
        frame = ttk.Frame(popup)
        frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Text widget with scrollbars
        text = tk.Text(frame, wrap=tk.NONE)
        scrollbar_y = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
        scrollbar_x = ttk.Scrollbar(frame, orient='horizontal', command=text.xview)
        
        text.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Insert DataFrame content
        text.insert('1.0', df.to_string())
        text.configure(state='disabled')

    def show_loader_manual(self):
        popup = tk.Toplevel(self.root)
        popup.title("Data Loader Help")
        
        # Configure popup grid
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        
        # Create frame
        frame = ttk.Frame(popup)
        frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Text widget with scrollbar
        text = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
        
        text.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        text.configure(yscrollcommand=scrollbar.set)
        
        # Insert help content
        help_text = """
        Data Loader Tab Help
        
        1. File Selection:
           - Use 'Browse Files' to select input files
           - Select multiple files with Ctrl/Cmd+Click
           - Use 'Select All' or 'Deselect All' for batch selection
        
        2. Format Selection:
           - Choose input format matching your files
           - Select desired output format
           - Available formats: CSV, JSON, DuckDB, Parquet, etc.
        
        3. Date Range:
           - Optional: Filter data by date range
           - Format: YYYY-MM-DD
           - Leave blank to include all dates
        
        4. Data Balancing:
           - Set target number of records per ticker
           - Specify minimum required records
           - Leave blank for automatic values
        
        5. Actions:
           - Preview: View file contents
           - Preprocess: Clean and normalize data
           - Load/Convert: Process and save files
           - ?: Show this help
           - User Manual: Detailed documentation
        """
        text.insert('1.0', help_text)
        text.configure(state='disabled')

    def show_view_manual(self):
        popup = tk.Toplevel(self.root)
        popup.title("Data View Help")
        
        # Configure popup grid
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        
        # Create frame
        frame = ttk.Frame(popup)
        frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Text widget with scrollbar
        text = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
        
        text.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        text.configure(yscrollcommand=scrollbar.set)
        
        # Insert help content
        help_text = """
        Data View Tab Help
        
        1. File Browser:
           - Lists all supported files in data directory
           - Click to select a file
           - Use Refresh to update the list
        
        2. Data Display:
           - View file contents in table format
           - Sort columns by clicking headers
           - Navigate pages with controls below
        
        3. Controls:
           - View: Display selected file
           - Refresh: Update file list
           - Remove: Delete selected file
        
        4. Navigation:
           - Use << < > >> to move between pages
           - Enter page number to jump directly
           - Adjust rows per page as needed
        """
        text.insert('1.0', help_text)
        text.configure(state='disabled')

    def show_data_statistics(self, data: pd.DataFrame):
        popup = tk.Toplevel(self.root)
        popup.title("Data Statistics")
        
        # Configure popup grid
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        
        # Create frame
        frame = ttk.Frame(popup)
        frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Text widget with scrollbar
        text = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
        
        text.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        text.configure(yscrollcommand=scrollbar.set)
        
        # Calculate and display statistics
        stats = []
        stats.append(f"Total Records: {len(data)}")
        stats.append(f"\nColumns: {', '.join(data.columns)}")
        stats.append("\nData Types:")
        for col, dtype in data.dtypes.items():
            stats.append(f"  {col}: {dtype}")
        stats.append("\nMissing Values:")
        for col in data.columns:
            missing = data[col].isna().sum()
            if missing > 0:
                stats.append(f"  {col}: {missing} ({missing/len(data)*100:.2f}%)")
        stats.append("\nSummary Statistics:")
        stats.append(data.describe().to_string())
        
        text.insert('1.0', '\n'.join(stats))
        text.configure(state='disabled')

    def setup_bindings(self):
        """Set up event bindings"""
        self.input_listbox.bind('<<ListboxSelect>>', lambda e: self.update_selection_info())

def run(task: str = 'gui'):
    loader = DataLoader()
    connector = DatabaseConnector(loader.db_path)
    if task == 'gui':
        root = tk.Tk()
        app = StockAnalyzerGUI(root, loader, connector)
        root.mainloop()
    elif task in ['load', 'convert', 'preprocess']:
        # Example for load task
        if task == 'load':
            pass  # Removed loading of sample.csv
        logging.info(f"Completed task: {task}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', default='gui', choices=['gui', 'load', 'convert', 'preprocess'])
    args = parser.parse_args()
    run(args.task) 