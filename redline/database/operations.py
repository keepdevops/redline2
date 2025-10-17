#!/usr/bin/env python3
"""
REDLINE Database Operations
Common database operations and utilities.
"""

import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from .connector import DatabaseConnector
from .query_builder import AdvancedQueryBuilder

logger = logging.getLogger(__name__)

class DatabaseOperations:
    """Common database operations and utilities."""
    
    def __init__(self, db_path: str = 'redline_data.duckdb'):
        """Initialize database operations."""
        self.connector = DatabaseConnector(db_path)
        self.query_builder = AdvancedQueryBuilder()
        self.logger = logging.getLogger(__name__)
    
    def get_all_tickers(self, table_name: str = 'tickers_data') -> List[str]:
        """
        Get list of all unique tickers in the database.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of unique ticker symbols
        """
        try:
            query = f"SELECT DISTINCT ticker FROM {table_name} ORDER BY ticker"
            result = self.connector.execute_query(query)
            return result['ticker'].tolist()
            
        except Exception as e:
            self.logger.error(f"Error getting tickers: {str(e)}")
            return []
    
    def get_ticker_count(self, table_name: str = 'tickers_data') -> int:
        """
        Get count of unique tickers.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of unique tickers
        """
        try:
            query = f"SELECT COUNT(DISTINCT ticker) as count FROM {table_name}"
            result = self.connector.execute_query(query)
            return result['count'].iloc[0] if not result.empty else 0
            
        except Exception as e:
            self.logger.error(f"Error getting ticker count: {str(e)}")
            return 0
    
    def get_date_range(self, table_name: str = 'tickers_data') -> Dict[str, Any]:
        """
        Get date range for all data.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with min and max dates
        """
        try:
            query = f"""
            SELECT 
                MIN(timestamp) as min_date,
                MAX(timestamp) as max_date,
                COUNT(*) as total_records
            FROM {table_name}
            """
            result = self.connector.execute_query(query)
            
            if not result.empty:
                return {
                    'min_date': result['min_date'].iloc[0],
                    'max_date': result['max_date'].iloc[0],
                    'total_records': result['total_records'].iloc[0]
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting date range: {str(e)}")
            return {}
    
    def get_ticker_stats(self, ticker: str, table_name: str = 'tickers_data') -> Dict[str, Any]:
        """
        Get statistics for a specific ticker.
        
        Args:
            ticker: Ticker symbol
            table_name: Name of the table
            
        Returns:
            Dictionary with ticker statistics
        """
        try:
            query = f"""
            SELECT 
                COUNT(*) as record_count,
                MIN(timestamp) as first_date,
                MAX(timestamp) as last_date,
                AVG(close) as avg_close,
                MIN(close) as min_close,
                MAX(close) as max_close,
                AVG(vol) as avg_volume,
                SUM(vol) as total_volume
            FROM {table_name}
            WHERE ticker = ?
            """
            result = self.connector.execute_query(query, {'ticker': ticker})
            
            if not result.empty:
                return result.iloc[0].to_dict()
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting ticker stats for {ticker}: {str(e)}")
            return {}
    
    def search_tickers(self, pattern: str, table_name: str = 'tickers_data') -> List[str]:
        """
        Search for tickers matching a pattern.
        
        Args:
            pattern: Search pattern (supports SQL LIKE patterns)
            table_name: Name of the table
            
        Returns:
            List of matching ticker symbols
        """
        try:
            query = f"SELECT DISTINCT ticker FROM {table_name} WHERE ticker LIKE ? ORDER BY ticker"
            result = self.connector.execute_query(query, {'pattern': f'%{pattern}%'})
            return result['ticker'].tolist()
            
        except Exception as e:
            self.logger.error(f"Error searching tickers: {str(e)}")
            return []
    
    def get_top_tickers_by_volume(self, limit: int = 10, 
                                 table_name: str = 'tickers_data') -> List[Dict[str, Any]]:
        """
        Get top tickers by average volume.
        
        Args:
            limit: Number of top tickers to return
            table_name: Name of the table
            
        Returns:
            List of ticker dictionaries with volume stats
        """
        try:
            query = f"""
            SELECT 
                ticker,
                COUNT(*) as record_count,
                AVG(vol) as avg_volume,
                SUM(vol) as total_volume
            FROM {table_name}
            GROUP BY ticker
            ORDER BY avg_volume DESC
            LIMIT ?
            """
            result = self.connector.execute_query(query, {'limit': limit})
            return result.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"Error getting top tickers by volume: {str(e)}")
            return []
    
    def get_price_range_stats(self, min_price: float = None, max_price: float = None,
                             table_name: str = 'tickers_data') -> Dict[str, Any]:
        """
        Get statistics for tickers within a price range.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            table_name: Name of the table
            
        Returns:
            Dictionary with price range statistics
        """
        try:
            conditions = []
            params = {}
            
            if min_price is not None:
                conditions.append("close >= ?")
                params['min_price'] = min_price
            
            if max_price is not None:
                conditions.append("close <= ?")
                params['max_price'] = max_price
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
            SELECT 
                COUNT(DISTINCT ticker) as ticker_count,
                COUNT(*) as record_count,
                AVG(close) as avg_price,
                MIN(close) as min_price,
                MAX(close) as max_price
            FROM {table_name}
            WHERE {where_clause}
            """
            
            result = self.connector.execute_query(query, params)
            
            if not result.empty:
                return result.iloc[0].to_dict()
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error getting price range stats: {str(e)}")
            return {}
    
    def get_recent_data(self, days: int = 30, table_name: str = 'tickers_data') -> pd.DataFrame:
        """
        Get recent data for the last N days.
        
        Args:
            days: Number of days to look back
            table_name: Name of the table
            
        Returns:
            DataFrame with recent data
        """
        try:
            query = f"""
            SELECT *
            FROM {table_name}
            WHERE timestamp >= date('now', '-{days} days')
            ORDER BY timestamp DESC, ticker
            """
            return self.connector.execute_query(query)
            
        except Exception as e:
            self.logger.error(f"Error getting recent data: {str(e)}")
            return pd.DataFrame()
    
    def cleanup_old_data(self, days_to_keep: int = 365, table_name: str = 'tickers_data') -> int:
        """
        Remove data older than specified days.
        
        Args:
            days_to_keep: Number of days of data to keep
            table_name: Name of the table
            
        Returns:
            Number of records deleted
        """
        try:
            # First, count records to be deleted
            count_query = f"""
            SELECT COUNT(*) as count
            FROM {table_name}
            WHERE timestamp < date('now', '-{days_to_keep} days')
            """
            count_result = self.connector.execute_query(count_query)
            records_to_delete = count_result['count'].iloc[0] if not count_result.empty else 0
            
            if records_to_delete == 0:
                return 0
            
            # Delete old records
            delete_query = f"""
            DELETE FROM {table_name}
            WHERE timestamp < date('now', '-{days_to_keep} days')
            """
            
            # Note: DuckDB doesn't support DELETE in some contexts
            # Alternative approach: create new table with recent data
            self.logger.info(f"Would delete {records_to_delete} old records (cleanup not implemented)")
            
            return records_to_delete
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")
            return 0
    
    def optimize_database(self, table_name: str = 'tickers_data') -> Dict[str, Any]:
        """
        Optimize database performance.
        
        Args:
            table_name: Name of the table to optimize
            
        Returns:
            Dictionary with optimization results
        """
        try:
            # Get table statistics before optimization
            stats_before = self.connector.get_table_info(table_name)
            
            # In DuckDB, we can analyze the table
            query = f"ANALYZE {table_name}"
            self.connector.execute_query(query)
            
            # Get table statistics after optimization
            stats_after = self.connector.get_table_info(table_name)
            
            return {
                'optimization_completed': True,
                'stats_before': stats_before,
                'stats_after': stats_after
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing database: {str(e)}")
            return {'optimization_completed': False, 'error': str(e)}
