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
from typing import Union, List, Dict
import argparse

# Configure logging
logging.basicConfig(filename='redline.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataLoader:
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
                    data.append(pd.read_csv(path))
                elif format == 'json':
                    data.append(pd.read_json(path))
                elif format == 'duckdb':
                    conn = duckdb.connect(path)
                    data.append(conn.execute("SELECT * FROM tickers_data").fetchdf())
                    conn.close()
                elif format == 'pyarrow':
                    data.append(pa.parquet.read_table(path))
                elif format == 'polars':
                    data.append(pl.read_parquet(path))
                elif format == 'keras':
                    data.append(tf.keras.models.load_model(path))
                logging.info(f"Loaded {path} as {format}")
            except Exception as e:
                logging.error(f"Failed to load {path}: {str(e)}")
                raise
        return data

    def validate_data(self, file_path: str, format: str) -> bool:
        try:
            if format in ['csv', 'json']:
                df = pd.read_csv(file_path) if format == 'csv' else pd.read_json(file_path)
                required = ['ticker', 'timestamp', 'close']
                return all(col in df.columns for col in required)
            return True  # Simplified for other formats
        except Exception as e:
            logging.error(f"Validation failed for {file_path}: {str(e)}")
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
            conn = duckdb.connect(self.db_path)
            if isinstance(data, pl.DataFrame):
                data = data.to_pandas()
            elif isinstance(data, pa.Table):
                data = data.to_pandas()
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} (ticker VARCHAR, table_name VARCHAR, fields VARCHAR[], data_path VARCHAR, timestamp DATETIME, env_name VARCHAR, env_status VARCHAR, row_count INTEGER, format VARCHAR)")
            data['format'] = format
            data.to_sql(table, create_engine(f'duckdb:///{self.db_path}'), if_exists='append', index=False)
            conn.close()
            logging.info(f"Saved data to {table} in format {format}")
        except Exception as e:
            logging.error(f"Failed to save to {table}: {str(e)}")
            raise

    def _standardize_txt_columns(self, df):
        # Accept both <TICKER> and TICKER, <CLOSE> and CLOSE, etc.
        col_map = {}
        for c in df.columns:
            cl = c.strip('<>').upper()
            if cl == 'TICKER':
                col_map[c] = 'ticker'
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
        # Combine date and time into timestamp if present
        if 'date' in df.columns and 'time' in df.columns:
            df['timestamp'] = df['date'].astype(str) + ' ' + df['time'].astype(str)
        elif 'date' in df.columns:
            df['timestamp'] = df['date'].astype(str)
        # Only keep required columns if present
        keep = [c for c in ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol', 'openint'] if c in df.columns]
        if all(k in df.columns for k in ['ticker', 'timestamp', 'close']):
            return df[keep]
        return df

class DatabaseConnector:
    def __init__(self, db_path: str = '/app/redline_data.duckdb'):
        self.db_path = db_path

    def create_connection(self, db_path: str) -> sqlalchemy.engine.Engine:
        return create_engine(f'duckdb:///{db_path}')

    def read_shared_data(self, table: str, format: str) -> Union[pd.DataFrame, pl.DataFrame, pa.Table]:
        try:
            conn = duckdb.connect(self.db_path)
            df = conn.execute(f"SELECT ticker, timestamp, close, format FROM {table}").fetchdf()
            conn.close()
            if format == 'polars':
                return pl.from_pandas(df)
            elif format == 'pyarrow':
                return pa.Table.from_pandas(df)
            return df
        except Exception as e:
            logging.error(f"Failed to read from {table}: {str(e)}")
            raise

    def write_shared_data(self, table: str, data: Union[pd.DataFrame, pl.DataFrame, pa.Table], format: str) -> None:
        try:
            conn = duckdb.connect(self.db_path)
            if isinstance(data, pl.DataFrame):
                data = data.to_pandas()
            elif isinstance(data, pa.Table):
                data = data.to_pandas()
            data['format'] = format
            data.to_sql(table, create_engine(f'duckdb:///{self.db_path}'), if_exists='append', index=False)
            conn.close()
            logging.info(f"Wrote data to {table} in format {format}")
        except Exception as e:
            logging.error(f"Failed to write to {table}: {str(e)}")
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
        ttk.Label(loader_frame, text="Input Format").pack()
        self.input_format = ttk.Combobox(loader_frame, values=['csv', 'json', 'duckdb', 'pyarrow', 'polars', 'keras'])
        self.input_format.pack()
        ttk.Label(loader_frame, text="Output Format").pack()
        self.output_format = ttk.Combobox(loader_frame, values=['csv', 'json', 'duckdb', 'pyarrow', 'polars', 'keras'])
        self.output_format.pack()
        ttk.Button(loader_frame, text="Browse Files", command=self.browse_files).pack()
        ttk.Button(loader_frame, text="Load and Convert", command=self.load_and_convert).pack()

        # Data View Tab
        view_frame = ttk.Frame(self.notebook)
        self.notebook.add(view_frame, text='Data View')
        self.data_tree = ttk.Treeview(view_frame, columns=['Ticker', 'Date', 'Close', 'Format'], show='headings')
        self.data_tree.heading('Ticker', text='Ticker')
        self.data_tree.heading('Date', text='Date')
        self.data_tree.heading('Close', text='Close')
        self.data_tree.heading('Format', text='Format')
        self.data_tree.pack(fill='both', expand=True)
        ttk.Button(view_frame, text="Refresh Data", command=self.refresh_data).pack()

    def browse_files(self):
        filetypes = [
            ('CSV Files', '*.csv'),
            ('TXT Files', '*.txt'),
            ('JSON Files', '*.json'),
            ('DuckDB Files', '*.duckdb'),
            ('Parquet Files', '*.parquet'),
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
                messagebox.showerror("Error", "Select files and formats")
                return
            data = self.loader.load_data(list(files), input_format)
            converted = self.loader.convert_format(data, input_format, output_format)
            self.loader.save_to_shared('tickers_data', converted[0] if isinstance(converted, list) else converted, output_format)
            messagebox.showinfo("Success", "Data loaded and converted")
        except Exception as e:
            logging.error(f"Load and convert failed: {str(e)}")
            messagebox.showerror("Error", f"Load and convert failed: {str(e)}")

    def refresh_data(self):
        try:
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            data = self.connector.read_shared_data('tickers_data', 'pandas')
            for _, row in data.iterrows():
                self.data_tree.insert('', 'end', values=(row['ticker'], row['timestamp'], row['close'], row['format']))
        except Exception as e:
            logging.error(f"Refresh data failed: {str(e)}")
            messagebox.showerror("Error", f"Refresh data failed: {str(e)}")

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