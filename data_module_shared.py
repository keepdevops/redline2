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
        ttk.Button(loader_frame, text="Load and Convert", command=self.load_and_convert).pack()
        ttk.Button(loader_frame, text="Batch Convert", command=self.batch_convert_files).pack()
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
        self.file_listbox = tk.Listbox(view_frame, width=60)
        self.file_listbox.pack()
        ttk.Button(view_frame, text="View File", command=self.view_selected_file).pack()
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
        filetypes = [
            ('CSV Files', '*.csv'),
            ('TXT Files', '*.txt'),
            ('JSON Files', '*.json'),
            ('DuckDB Files', '*.duckdb'),
            ('Parquet Files', '*.parquet'),
            ('Feather Files', '*.feather'),
            ('Keras Models', '*.h5')
        ]
        files = filedialog.askopenfilenames(filetypes=filetypes)
        self.input_listbox.delete(0, tk.END)
        for file in files:
            self.input_listbox.insert(tk.END, file)

    def load_and_convert(self):
        try:
            files = self.input_listbox.get(0, tk.END)
            input_format = self.input_format.get()
            output_format = self.output_format.get()
            if not files or not input_format or not output_format:
                print("Error: Select files and formats")
                messagebox.showerror("Error", "Select files and formats")
                return
            data = self.loader.load_data(list(files), input_format)
            if not data:
                print("Error: No data loaded from file(s). Check file format and contents.")
                messagebox.showerror("Error", "No data loaded from file(s). Check file format and contents.")
                return
            converted = self.loader.convert_format(data, input_format, output_format)
            if isinstance(converted, list) and not converted:
                print("Error: Conversion returned no data.")
                messagebox.showerror("Error", "Conversion returned no data.")
                return
            self.loader.save_to_shared('tickers_data', converted[0] if isinstance(converted, list) else converted, output_format)
            print("Success: Data loaded and converted")
            messagebox.showinfo("Success", "Data loaded and converted")
        except Exception as e:
            logging.error(f"Load and convert failed: {str(e)}")
            print(f"Load and convert failed: {str(e)}")
            messagebox.showerror("Error", f"Load and convert failed: {str(e)}")

    def refresh_file_list(self):
        # List all supported files in the data directory
        self.file_listbox.delete(0, tk.END)
        data_dir = 'data'  # preferred data directory
        supported_exts = ('.txt', '.csv', '.json', '.duckdb', '.parquet', '.feather', '.h5')
        if os.path.isdir(data_dir):
            for fname in os.listdir(data_dir):
                if fname.endswith(supported_exts):
                    self.file_listbox.insert(tk.END, os.path.join(data_dir, fname))

    def view_selected_file(self):
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No file selected")
            return
        file_path = self.file_listbox.get(selection[0])
        print("Viewing file:", file_path)
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext == '.json':
                try:
                    df = pd.read_json(file_path, lines=True)
                except ValueError:
                    df = pd.read_json(file_path)
            elif ext == '.txt':
                df = pd.read_csv(file_path, delimiter='\t')
                if df.shape[1] == 1:
                    df = pd.read_csv(file_path, delimiter=',')
                df = self.loader._standardize_txt_columns(df)
            elif ext == '.feather':
                df = pd.read_feather(file_path)
            elif ext == '.parquet':
                df = pd.read_parquet(file_path)
            elif ext == '.duckdb':
                try:
                    conn = duckdb.connect(file_path)
                    tables = conn.execute("SHOW TABLES").fetchall()
                    if not tables:
                        messagebox.showerror("Error", "No tables found in DuckDB file")
                        return
                    if len(tables) == 1:
                        table_name = tables[0][0]
                    else:
                        # Prompt user to select a table
                        table_names = [t[0] for t in tables]
                        table_name = askstring("Select Table", f"Available tables: {', '.join(table_names)}\nEnter table name to preview:", initialvalue=table_names[0])
                        if not table_name or table_name not in table_names:
                            messagebox.showerror("Error", "Invalid or no table selected.")
                            return
                    df = conn.execute(f"SELECT * FROM {table_name} LIMIT 100").fetchdf()
                    conn.close()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to preview DuckDB file: {str(e)}")
                    return
            elif ext == '.h5':
                try:
                    model = tf.keras.models.load_model(file_path)
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
            else:
                messagebox.showerror("Error", "Unsupported file type")
                return
            print("DF columns:", df.columns)
            print(df.head())
            self.show_dataframe_popup(df)
        except Exception as e:
            print("Failed to read file:", file_path)
            logging.exception(f"Failed to preview file: {file_path}")
            messagebox.showerror("Error", f"Failed to read file: {str(e)}")

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
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            data = self.connector.read_shared_data('tickers_data', 'pandas')
            # Always show 9 columns if present
            screenshot_cols = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint', 'format']
            screenshot_cols = [col for col in screenshot_cols if col in data.columns]
            self.data_tree['columns'] = screenshot_cols
            self.data_tree['show'] = 'headings'
            # Add vertical scrollbar and enable column resizing
            for col in screenshot_cols:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100, stretch=True, anchor='center')
            for _, row in data.iterrows():
                self.data_tree.insert('', 'end', values=tuple(row[col] for col in screenshot_cols))
            # Auto-size columns to fit content
            for col in screenshot_cols:
                self.data_tree.column(col, width=tkFont.Font().measure(col) + 20)
            # Add vertical scrollbar if not already present
            if not hasattr(self, 'yscroll'):
                self.yscroll = ttk.Scrollbar(self.data_tree.master, orient='vertical', command=self.data_tree.yview)
                self.data_tree.configure(yscrollcommand=self.yscroll.set)
                self.yscroll.pack(side='right', fill='y')
            # Print a screenshot-like output to the terminal
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
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext == '.json':
                df = pd.read_json(file_path)
            elif ext == '.txt':
                df = pd.read_csv(file_path, delimiter='\t')
                if df.shape[1] == 1:
                    df = pd.read_csv(file_path, delimiter=',')
                df = self.loader._standardize_txt_columns(df)
            elif ext == '.feather':
                df = pd.read_feather(file_path)
            elif ext == '.parquet':
                df = pd.read_parquet(file_path)
            elif ext == '.h5':
                # For Keras, show model summary as text
                try:
                    model = tf.keras.models.load_model(file_path)
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
            elif ext == '.duckdb':
                # List tables and preview the first one
                try:
                    conn = duckdb.connect(file_path)
                    tables = conn.execute("SHOW TABLES").fetchall()
                    if not tables:
                        messagebox.showerror("Error", "No tables found in DuckDB file")
                        return
                    table_name = tables[0][0]
                    df = conn.execute(f"SELECT * FROM {table_name} LIMIT 100").fetchdf()
                    conn.close()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to preview DuckDB file: {str(e)}")
                    return
            else:
                messagebox.showerror("Error", "Unsupported file type")
                return
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
        input_format = self.input_format.get()
        ext = os.path.splitext(file_path)[1].lower()
        print(f"Preprocessing file: {file_path} as format: {input_format}")
        try:
            # Load the file in the selected format
            if input_format == 'csv' or ext == '.csv':
                df = pd.read_csv(file_path)
            elif input_format == 'json' or ext == '.json':
                df = pd.read_json(file_path)
            elif input_format == 'txt' or ext == '.txt':
                df = pd.read_csv(file_path, delimiter='\t')
                if df.shape[1] == 1:
                    df = pd.read_csv(file_path, delimiter=',')
                df = self.loader._standardize_txt_columns(df)
            elif input_format == 'feather' or ext == '.feather':
                df = pd.read_feather(file_path)
            elif input_format == 'parquet' or ext == '.parquet':
                df = pd.read_parquet(file_path)
            elif input_format == 'h5' or ext == '.h5':
                try:
                    model = tf.keras.models.load_model(file_path)
                    summary = f"Model inputs: {model.inputs}\nModel outputs: {model.outputs}"
                    messagebox.showinfo("Preprocess Result", summary)
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load Keras model: {str(e)}")
                    return
            elif input_format == 'duckdb' or ext == '.duckdb':
                try:
                    conn = duckdb.connect(file_path)
                    tables = conn.execute("SHOW TABLES").fetchall()
                    if not tables:
                        messagebox.showerror("Error", "No tables found in DuckDB file")
                        return
                    table_name = tables[0][0]
                    df = conn.execute(f"SELECT * FROM {table_name} LIMIT 100").fetchdf()
                    conn.close()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to preprocess DuckDB file: {str(e)}")
                    return
            else:
                messagebox.showerror("Error", "Unsupported file type for preprocessing")
                return

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
            if save_format == 'json':
                save_path = filedialog.asksaveasfilename(defaultextension='.json', initialfile=base_name+'_preprocessed.json', filetypes=[('JSON Files', '*.json')], initialdir='data')
                if not save_path:
                    return
                df.to_json(save_path, orient='records', lines=True)
            elif save_format == 'keras':
                # Save as a dummy Keras model with the same shape as the data, using Input layer to avoid warning
                save_path = filedialog.asksaveasfilename(defaultextension='.h5', initialfile=base_name+'_preprocessed.h5', filetypes=[('Keras Model', '*.h5')], initialdir='data')
                if not save_path:
                    return
                from tensorflow.keras import Sequential, Input
                from tensorflow.keras.layers import Dense
                model = Sequential([
                    Input(shape=(len(df.columns),)),
                    Dense(32, activation='relu'),
                    Dense(1)
                ])
                model.save(save_path)
            elif save_format == 'tensorflow':
                # Save as a numpy npz file (simple TF dataset serialization)
                save_path = filedialog.asksaveasfilename(defaultextension='.npz', initialfile=base_name+'_preprocessed.npz', filetypes=[('NumPy Zip', '*.npz')], initialdir='data')
                if not save_path:
                    return
                np.savez(save_path, data=df.to_numpy())
            elif save_format == 'feather':
                save_path = filedialog.asksaveasfilename(defaultextension='.feather', initialfile=base_name+'_preprocessed.feather', filetypes=[('Feather Files', '*.feather')], initialdir='data')
                if not save_path:
                    return
                df.reset_index(drop=True).to_feather(save_path)
            else:
                messagebox.showerror("Error", f"Unsupported save format: {save_format}")
                return

            # Refresh file list
            self.refresh_file_list()
            messagebox.showinfo("Preprocess & Save", f"Preprocessed data saved as {save_path}")
        except Exception as e:
            logging.exception(f"Failed to preprocess file: {file_path}")
            messagebox.showerror("Error", f"Failed to preprocess file: {str(e)}")

    def batch_convert_files(self):
        files = self.input_listbox.get(0, tk.END)
        input_format = self.input_format.get()
        output_format = self.output_format.get()
        if not files or not input_format or not output_format:
            messagebox.showerror("Error", "Select files and formats for batch conversion")
            return
        # Disable button to prevent re-entry
        self.root.config(cursor="watch")
        self.progress_var.set(0)
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        self.progress_bar.update()
        def worker():
            success_count = 0
            fail_count = 0
            total = len(files)
            def update_progress(val):
                self.progress_var.set(val)
                self.progress_bar.update()
            for idx, path in enumerate(files):
                try:
                    # Load
                    data = self.loader.load_data([path], input_format)[0]
                    # Convert
                    converted = self.loader.convert_format(data, input_format, output_format)
                    # Save
                    base_name = os.path.splitext(os.path.basename(path))[0]
                    ext_map = {
                        'csv': '.csv', 'txt': '.txt', 'json': '.json', 'duckdb': '.duckdb',
                        'pyarrow': '.parquet', 'polars': '.parquet', 'keras': '.h5', 'feather': '.feather'
                    }
                    out_ext = ext_map.get(output_format, '.' + output_format)
                    out_path = os.path.join('data', base_name + '_converted' + out_ext)
                    if output_format == 'csv':
                        converted.to_csv(out_path, index=False)
                    elif output_format == 'txt':
                        converted.to_csv(out_path, sep='\t', index=False)
                    elif output_format == 'json':
                        converted.to_json(out_path, orient='records', lines=True)
                    elif output_format == 'feather':
                        converted.reset_index(drop=True).to_feather(out_path)
                    elif output_format == 'parquet' or output_format == 'pyarrow' or output_format == 'polars':
                        converted.to_parquet(out_path)
                    elif output_format == 'keras':
                        from tensorflow.keras import Sequential, Input
                        from tensorflow.keras.layers import Dense
                        model = Sequential([
                            Input(shape=(len(converted.columns),)),
                            Dense(32, activation='relu'),
                            Dense(1)
                        ])
                        model.save(out_path)
                    elif output_format == 'duckdb':
                        import duckdb
                        conn = duckdb.connect(out_path)
                        conn.execute("CREATE TABLE IF NOT EXISTS tickers_data AS SELECT * FROM temp_df")
                        conn.register('temp_df', converted)
                        conn.execute("INSERT INTO tickers_data SELECT * FROM temp_df")
                        conn.unregister('temp_df')
                        conn.close()
                    else:
                        fail_count += 1
                        continue
                    success_count += 1
                except Exception as e:
                    logging.exception(f"Batch convert failed for {path}: {str(e)}")
                    fail_count += 1
                # Update progress
                progress = ((idx + 1) / total) * 100
                self.root.after(0, update_progress, progress)
            # Refresh file list in main thread
            self.root.after(0, self.refresh_file_list)
            self.root.after(0, lambda: messagebox.showinfo("Batch Convert", f"Batch conversion complete. Success: {success_count}, Failed: {fail_count}"))
            self.root.after(0, lambda: self.root.config(cursor=""))
            self.root.after(0, self.progress_bar.pack_forget)
        threading.Thread(target=worker, daemon=True).start()

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
            data = loader.load_data([f"{loader.csv_dir}/sample.csv"], 'csv')
            loader.save_to_shared('tickers_data', data[0], 'pandas')
        logging.info(f"Completed task: {task}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', default='gui', choices=['gui', 'load', 'convert', 'preprocess'])
    args = parser.parse_args()
    run(args.task) 