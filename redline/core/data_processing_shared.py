#!/usr/bin/env python3
"""
Data processing utilities extracted from data_module_shared.py (shared module)
Handles data analysis, filtering, and balancing operations.
"""

import logging
import pandas as pd
from typing import Dict

logger = logging.getLogger(__name__)


class DataProcessor:
    """Data processing utilities."""
    
    @staticmethod
    def analyze_ticker_distribution(data: pd.DataFrame) -> dict:
        """Analyze the distribution of records across tickers."""
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

    @staticmethod
    def filter_data_by_date_range(data: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """Filter the dataframe by date range for all tickers."""
        try:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            mask = (data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)
            filtered_data = data.loc[mask]
            if filtered_data.empty:
                logger.warning(f"No data found between {start_date} and {end_date}")
            else:
                logger.info(f"Filtered data from {start_date} to {end_date}. Tickers: {filtered_data['ticker'].unique()}")
            return filtered_data
        except Exception as e:
            logger.error(f"Error filtering data by date range: {str(e)}")
            raise

    @staticmethod
    def balance_ticker_data(data: pd.DataFrame, target_records_per_ticker: int = None, 
                           min_records_per_ticker: int = None) -> pd.DataFrame:
        """Balance data across tickers by sampling or limiting records."""
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
                    logger.warning(f"Skipping ticker {ticker}: insufficient records ({len(ticker_data)} < {min_records_per_ticker})")
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
            original_stats = DataProcessor.analyze_ticker_distribution(data)
            balanced_stats = DataProcessor.analyze_ticker_distribution(balanced_data)
            logger.info(f"Original data: {original_stats['total_records']} records across {original_stats['total_tickers']} tickers")
            logger.info(f"Balanced data: {balanced_stats['total_records']} records across {balanced_stats['total_tickers']} tickers")
            return balanced_data
        except Exception as e:
            logger.error(f"Error balancing ticker data: {str(e)}")
            raise

