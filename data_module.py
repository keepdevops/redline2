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
        else:
            raise ValueError(f"Unsupported save file type: {filetype}")

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
        self.root.title("REDLINE Stock Analyzer")
        self.loader = loader
        self.connector = connector
        self.adapter = DataAdapter()
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        self.setup_tabs()

    def setup_tabs(self):
        # Data Loader Tab
        loader_frame = ttk.Frame(self.notebook)
        self.notebook.add(loader_frame, text='Data Loader')
        ttk.Label(loader_frame, text="Select Input Files:").pack()
        self.input_listbox = tk.Listbox(loader_frame, selectmode='multiple', width=50)
        self.input_listbox.pack()
        ttk.Button(loader_frame, text="Preview File", command=self.preview_selected_loader_file).pack()
        ttk.Button(loader_frame, text="Preprocess File", command=self.preprocess_selected_loader_file).pack()
        ttk.Label(loader_frame, text="Input Format").pack()
        self.input_format = ttk.Combobox(loader_frame, values=['csv', 'txt', 'json', 'duckdb', 'pyarrow', 'polars', 'keras', 'feather'])
        self.input_format.pack()
        ttk.Label(loader_frame, text="Output Format").pack()
        self.output_format = ttk.Combobox(loader_frame, values=['csv', 'txt', 'json', 'duckdb', 'pyarrow', 'polars', 'keras', 'feather'])
        self.output_format.pack()
        ttk.Button(loader_frame, text="Browse Files", command=self.browse_files).pack()
        ttk.Button(loader_frame, text="Merge/Consolidate Files", command=self.load_and_convert).pack()
        # Progress bar for batch conversion
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(loader_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        self.progress_bar.pack_forget()  # Hide initially

        # Data View Tab
        view_frame = ttk.Frame(self.notebook)
        self.notebook.add(view_frame, text='Data View')
        # Add file listbox and view button
        ttk.Label(view_frame, text="Available Data Files:").pack()
        self.file_listbox = tk.Listbox(view_frame, width=60, selectmode='extended')
        self.file_listbox.pack()
        ttk.Button(view_frame, text="View File", command=self.view_selected_file).pack()
        ttk.Button(view_frame, text="Remove File", command=self.remove_selected_file).pack()
        self.refresh_file_list()
        # Add a horizontal scrollbar for the data_tree
        tree_frame = ttk.Frame(view_frame)
        tree_frame.pack(fill='both', expand=True)
        xscroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        self.data_tree = ttk.Treeview(tree_frame, columns=['Ticker', 'Date', 'Close', 'Format'], show='headings', xscrollcommand=xscroll.set)
        xscroll.config(command=self.data_tree.xview)
        xscroll.pack(side='bottom', fill='x')
        self.data_tree.pack(fill='both', expand=True)
        ttk.Button(view_frame, text="Refresh Data", command=self.refresh_data).pack()

    def browse_files(self):
        # Use centralized mapping for filetypes
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

    def load_and_convert(self):
        def worker():
            try:
                entries = self.input_listbox.get(0, tk.END)
                input_format = self.input_format.get()
                output_format = self.output_format.get()
                if not entries or not input_format or not output_format:
                    print("Error: Select files and formats")
                    self.run_in_main_thread(messagebox.showerror, "Error", "Select files and formats")
                    return
                # Load all selected files and concatenate them
                dfs = []
                total = len(entries)
                self.run_in_main_thread(self.progress_var.set, 0)
                self.run_in_main_thread(self.progress_bar.pack, {'fill':'x', 'padx':10, 'pady':5})
                self.run_in_main_thread(self.progress_bar.update)
                for idx, entry in enumerate(entries):
                    path = entry.split(' [')[0]
                    try:
                        df = DataLoader.load_file_by_type(path, input_format)
                        if df is not None and hasattr(df, 'columns') and len(df.columns) > 0:
                            dfs.append(df)
                        else:
                            print(f"Skipped file (empty or no columns): {path}")
                    except Exception as e:
                        print(f"Skipped file (load error): {path} ({e})")
                    # Update progress
                    progress = ((idx + 1) / total) * 100
                    self.run_in_main_thread(self.progress_var.set, progress)
                    self.run_in_main_thread(self.progress_bar.update)
                if not dfs:
                    print("Error: No valid data loaded from file(s). Check file format and contents.")
                    self.run_in_main_thread(messagebox.showerror, "Error", "No valid data loaded from file(s). Check file format and contents.")
                    self.run_in_main_thread(self.progress_bar.pack_forget)
                    return
                import pandas as pd
                if len(dfs) > 1:
                    data = pd.concat(dfs, ignore_index=True)
                else:
                    data = dfs[0]

                # Data cleaning: deduplicate
                before_dedup = len(data)
                data = data.drop_duplicates()
                after_dedup = len(data)
                dropped_dupes = before_dedup - after_dedup

                # Now schedule the rest (dialogs and saving) in the main thread
                self.run_in_main_thread(self.data_cleaning_and_save, data, input_format, output_format, dropped_dupes)
            except Exception as e:
                logging.error(f"Merge/Consolidate failed: {str(e)}")
                print(f"Merge/Consolidate failed: {str(e)}")
                self.run_in_main_thread(messagebox.showerror, "Error", f"Merge/Consolidate failed: {str(e)}")
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
                            text = tk.Text(popup, wrap='word')
                            text.insert('1.0', summary_str)
                            text.pack(fill='both', expand=True)
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
        popup.title("File Contents")
        tree = ttk.Treeview(popup, columns=list(df.columns), show='headings')
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        for _, row in df.iterrows():
            tree.insert('', 'end', values=list(row))
        tree.pack(fill='both', expand=True)

    def refresh_data(self):
        try:
            # If a file is selected in the file_listbox, show its data
            selection = self.file_listbox.curselection()
            if selection:
                file_path = self.file_listbox.get(selection[0])
                file_path = file_path.split(' [')[0]
                ext = os.path.splitext(file_path)[1].lower()
                fmt = DataLoader.EXT_TO_FORMAT.get(ext, None)
                try:
                    if fmt == 'keras':
                        # Show model summary in popup, skip table
                        model = DataLoader.load_file_by_type(file_path, fmt)
                        import io
                        stream = io.StringIO()
                        model.summary(print_fn=lambda x: stream.write(x + '\n'))
                        summary_str = stream.getvalue()
                        popup = tk.Toplevel(self.root)
                        popup.title("Keras Model Summary")
                        text = tk.Text(popup, wrap='word')
                        text.insert('1.0', summary_str)
                        text.pack(fill='both', expand=True)
                        return
                    df = DataLoader.load_file_by_type(file_path, fmt)
                    self.data_tree.delete(*self.data_tree.get_children())
                    cols = list(df.columns)
                    self.data_tree['columns'] = cols
                    self.data_tree['show'] = 'headings'
                    for col in cols:
                        self.data_tree.heading(col, text=col)
                        self.data_tree.column(col, width=100, stretch=True, anchor='center')
                    for _, row in df.iterrows():
                        self.data_tree.insert('', 'end', values=tuple(row))
                    for col in cols:
                        self.data_tree.column(col, width=tkFont.Font().measure(col) + 20)
                    if not hasattr(self, 'yscroll'):
                        self.yscroll = ttk.Scrollbar(self.data_tree.master, orient='vertical', command=self.data_tree.yview)
                        self.data_tree.configure(yscrollcommand=self.yscroll.set)
                        self.yscroll.pack(side='right', fill='y')
                    print("\n=== Data Table Screenshot ===")
                    print(df.head(10).to_string(index=False))
                    print("============================\n")
                    return
                except Exception as e:
                    logging.exception(f"Refresh data failed for selected file: {str(e)}")
                    print(f"Refresh data failed for selected file: {str(e)}")
                    messagebox.showerror("Error", f"Refresh data failed for selected file: {str(e)}")
                    return
            # Otherwise, fall back to showing tickers_data from DuckDB
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            data = self.connector.read_shared_data('tickers_data', 'pandas')
            screenshot_cols = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint', 'format']
            screenshot_cols = [col for col in screenshot_cols if col in data.columns]
            self.data_tree['columns'] = screenshot_cols
            self.data_tree['show'] = 'headings'
            for col in screenshot_cols:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100, stretch=True, anchor='center')
            for _, row in data.iterrows():
                self.data_tree.insert('', 'end', values=tuple(row[col] for col in screenshot_cols))
            for col in screenshot_cols:
                self.data_tree.column(col, width=tkFont.Font().measure(col) + 20)
            if not hasattr(self, 'yscroll'):
                self.yscroll = ttk.Scrollbar(self.data_tree.master, orient='vertical', command=self.data_tree.yview)
                self.data_tree.configure(yscrollcommand=self.yscroll.set)
                self.yscroll.pack(side='right', fill='y')
            print("\n=== Data Table Screenshot ===")
            print(data[screenshot_cols].head(10).to_string(index=False))
            print("============================\n")
        except Exception as e:
            logging.exception(f"Refresh data failed: {str(e)}")
            print(f"Refresh data failed: {str(e)}")
            messagebox.showerror("Error", f"Refresh data failed: {str(e)}")

    def preview_selected_loader_file(self):
        selection = self.input_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No file selected")
            return
        file_path = self.input_listbox.get(selection[0])
        print("Previewing file:", file_path)
        # Remove [type] if present
        file_path = file_path.split(' [')[0]
        ext = os.path.splitext(file_path)[1].lower()
        fmt = DataLoader.EXT_TO_FORMAT.get(ext, None)
        try:
            if fmt == 'keras':
                # For Keras, show model summary as text
                try:
                    model = DataLoader.load_file_by_type(file_path, fmt)
                    import io
                    stream = io.StringIO()
                    model.summary(print_fn=lambda x: stream.write(x + '\n'))
                    summary_str = stream.getvalue()
                    popup = tk.Toplevel(self.root)
                    popup.title("Keras Model Summary")
                    text = tk.Text(popup, wrap='word')
                    text.insert('1.0', summary_str)
                    text.pack(fill='both', expand=True)
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load Keras model: {str(e)}")
                    return
            df = DataLoader.load_file_by_type(file_path, fmt)
            print("DF columns:", df.columns)
            print(df.head())
            self.show_dataframe_popup(df)
        except Exception as e:
            print("Failed to read file:", file_path)
            logging.exception(f"Failed to preview file: {file_path}")
            messagebox.showerror("Error", f"Failed to read file: {str(e)}")

    def preprocess_selected_loader_file(self):
        selection = self.input_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No file selected")
            return
        file_path = self.input_listbox.get(selection[0])
        file_path = file_path.split(' [')[0]
        ext = os.path.splitext(file_path)[1].lower()
        input_format = self.input_format.get()
        fmt = DataLoader.EXT_TO_FORMAT.get(ext, input_format)
        print(f"Preprocessing file: {file_path} as format: {fmt}")
        try:
            if fmt == 'keras':
                try:
                    model = DataLoader.load_file_by_type(file_path, fmt)
                    summary = f"Model inputs: {model.inputs}\nModel outputs: {model.outputs}"
                    messagebox.showinfo("Preprocess Result", summary)
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load Keras model: {str(e)}")
                    return
            df = DataLoader.load_file_by_type(file_path, fmt)

            # ML Preprocessing: Normalize numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                scaler = MinMaxScaler()
                df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

            # Prompt user for save format
            save_format = askstring("Save Format", "Enter save format (json, keras, tensorflow):", initialvalue="json")
            if not save_format:
                messagebox.showinfo("Cancelled", "Save cancelled.")
                return
            save_format = save_format.lower().strip()
            # Prompt for filename
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            save_path = None
            # Use centralized mapping for extension and filetype
            dialog_info = DataLoader.FORMAT_DIALOG_INFO.get(save_format, ('.dat', 'All Files', '*.*'))
            out_ext, desc, pattern = dialog_info
            save_path = filedialog.asksaveasfilename(
                defaultextension=out_ext,
                initialfile=base_name+'_preprocessed'+out_ext,
                filetypes=[(desc, pattern)],
                initialdir='data'
            )
            if not save_path:
                return
            DataLoader.save_file_by_type(df, save_path, save_format)

            # Refresh file list
            self.refresh_file_list()
            messagebox.showinfo("Preprocess & Save", f"Preprocessed data saved as {save_path}")
        except Exception as e:
            logging.exception(f"Failed to preprocess file: {file_path}")
            messagebox.showerror("Error", f"Failed to preprocess file: {str(e)}")

    def remove_selected_file(self):
        def worker():
            selection = self.file_listbox.curselection()
            if not selection:
                self.run_in_main_thread(messagebox.showerror, "Error", "No file(s) selected to remove")
                return
            import os
            removed = 0
            failed = 0
            for idx in reversed(selection):
                file_entry = self.file_listbox.get(idx)
                file_path = file_entry.split(' [')[0]
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        removed += 1
                    else:
                        failed += 1
                except Exception as e:
                    logging.exception(f"Failed to remove file: {file_path}")
                    failed += 1
            def update_gui():
                self.refresh_file_list()
                self.data_tree.delete(*self.data_tree.get_children())
                message = f"Removed {removed} file(s)."
                if failed:
                    message += f" Failed to remove {failed} file(s)."
                messagebox.showinfo("File Removal", message)
            self.run_in_main_thread(update_gui)
        threading.Thread(target=worker, daemon=True).start()

    def run_in_main_thread(self, func, *args, **kwargs):
        self.root.after(0, lambda: func(*args, **kwargs))

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