#!/usr/bin/env python3
"""
REDLINE Advanced Query Builder
Handles complex SQL query building for data filtering and analysis.
"""

import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class AdvancedQueryBuilder:
    """Advanced query builder for complex data filtering."""
    
    def __init__(self):
        """Initialize query builder with operators and date operators."""
        self.operators = {
            'equals': '=',
            'not_equals': '!=',
            'contains': 'LIKE',
            'not_contains': 'NOT LIKE',
            'greater_than': '>',
            'less_than': '<',
            'greater_equal': '>=',
            'less_equal': '<=',
            'between': 'BETWEEN',
            'in': 'IN',
            'not_in': 'NOT IN',
            'is_null': 'IS NULL',
            'is_not_null': 'IS NOT NULL'
        }
        
        self.date_operators = {
            'equals': '=',
            'not_equals': '!=',
            'greater_than': '>',
            'less_than': '<',
            'greater_equal': '>=',
            'less_equal': '<=',
            'between': 'BETWEEN',
            'in_range': 'BETWEEN'
        }
        
        self.logger = logging.getLogger(__name__)
    
    def build_query(self, conditions: List[Dict[str, Any]], table_name: str = 'tickers_data') -> Tuple[str, List]:
        """
        Build SQL query from conditions.
        
        Args:
            conditions: List of condition dictionaries
            table_name: Name of the table to query
            
        Returns:
            Tuple of (SQL query, parameters)
        """
        if not conditions:
            return f"SELECT * FROM {table_name}", []
        
        where_clauses = []
        params = []
        
        for condition in conditions:
            column = condition['column']
            operator = condition['operator']
            value = condition['value']
            
            if operator in ['is_null', 'is_not_null']:
                where_clauses.append(f"{column} {self.operators[operator]}")
            elif operator == 'between':
                where_clauses.append(f"{column} BETWEEN ? AND ?")
                params.extend([value[0], value[1]])
            elif operator == 'in':
                placeholders = ','.join(['?' for _ in value])
                where_clauses.append(f"{column} IN ({placeholders})")
                params.extend(value)
            elif operator in ['contains', 'not_contains']:
                where_clauses.append(f"{column} {self.operators[operator]} ?")
                params.append(f"%{value}%")
            else:
                where_clauses.append(f"{column} {self.operators[operator]} ?")
                params.append(value)
        
        query = f"SELECT * FROM {table_name} WHERE {' AND '.join(where_clauses)}"
        return query, params
    
    def build_aggregation_query(self, table_name: str = 'tickers_data', 
                               group_by: List[str] = None,
                               aggregations: Dict[str, str] = None,
                               conditions: List[Dict[str, Any]] = None) -> Tuple[str, List]:
        """
        Build aggregation query.
        
        Args:
            table_name: Name of the table
            group_by: Columns to group by
            aggregations: Dictionary of column -> aggregation function
            conditions: Filter conditions
            
        Returns:
            Tuple of (SQL query, parameters)
        """
        # Build SELECT clause
        if aggregations:
            select_parts = []
            for col, func in aggregations.items():
                select_parts.append(f"{func}({col}) AS {col}_{func.lower()}")
            select_clause = ', '.join(select_parts)
        else:
            select_clause = "*"
        
        # Build GROUP BY clause
        if group_by:
            group_by_clause = f"GROUP BY {', '.join(group_by)}"
        else:
            group_by_clause = ""
        
        # Build WHERE clause
        where_clause = ""
        params = []
        if conditions:
            query, params = self.build_query(conditions, table_name)
            # Extract WHERE clause from the query
            where_clause = query.split('WHERE ')[1] if 'WHERE ' in query else ""
        
        # Construct final query
        query_parts = [f"SELECT {select_clause} FROM {table_name}"]
        
        if where_clause:
            query_parts.append(f"WHERE {where_clause}")
        
        if group_by_clause:
            query_parts.append(group_by_clause)
        
        query = " ".join(query_parts)
        return query, params
    
    def build_date_range_query(self, table_name: str = 'tickers_data',
                              start_date: str = None,
                              end_date: str = None,
                              tickers: List[str] = None) -> Tuple[str, List]:
        """
        Build query for date range filtering.
        
        Args:
            table_name: Name of the table
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            tickers: List of ticker symbols
            
        Returns:
            Tuple of (SQL query, parameters)
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append({
                'column': 'timestamp',
                'operator': 'greater_equal',
                'value': start_date
            })
        
        if end_date:
            conditions.append({
                'column': 'timestamp',
                'operator': 'less_equal',
                'value': end_date
            })
        
        if tickers:
            conditions.append({
                'column': 'ticker',
                'operator': 'in',
                'value': tickers
            })
        
        return self.build_query(conditions, table_name)
    
    def build_ticker_analysis_query(self, table_name: str = 'tickers_data',
                                   ticker: str = None,
                                   analysis_type: str = 'daily') -> Tuple[str, List]:
        """
        Build query for ticker analysis.
        
        Args:
            table_name: Name of the table
            ticker: Ticker symbol
            analysis_type: Type of analysis ('daily', 'weekly', 'monthly')
            
        Returns:
            Tuple of (SQL query, parameters)
        """
        conditions = []
        params = []
        
        if ticker:
            conditions.append({
                'column': 'ticker',
                'operator': 'equals',
                'value': ticker
            })
        
        # Add date grouping based on analysis type
        if analysis_type == 'weekly':
            date_func = "DATE_TRUNC('week', timestamp)"
        elif analysis_type == 'monthly':
            date_func = "DATE_TRUNC('month', timestamp)"
        else:
            date_func = "DATE(timestamp)"
        
        # Build aggregation query
        aggregations = {
            'open': 'FIRST',
            'high': 'MAX',
            'low': 'MIN',
            'close': 'LAST',
            'vol': 'SUM'
        }
        
        group_by = [date_func, 'ticker']
        
        return self.build_aggregation_query(table_name, group_by, aggregations, conditions)
    
    def build_price_filter_query(self, table_name: str = 'tickers_data',
                                price_column: str = 'close',
                                min_price: float = None,
                                max_price: float = None) -> Tuple[str, List]:
        """
        Build query for price filtering.
        
        Args:
            table_name: Name of the table
            price_column: Column to filter on
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            Tuple of (SQL query, parameters)
        """
        conditions = []
        
        if min_price is not None:
            conditions.append({
                'column': price_column,
                'operator': 'greater_equal',
                'value': min_price
            })
        
        if max_price is not None:
            conditions.append({
                'column': price_column,
                'operator': 'less_equal',
                'value': max_price
            })
        
        return self.build_query(conditions, table_name)
    
    def build_volume_filter_query(self, table_name: str = 'tickers_data',
                                 min_volume: float = None,
                                 max_volume: float = None) -> Tuple[str, List]:
        """
        Build query for volume filtering.
        
        Args:
            table_name: Name of the table
            min_volume: Minimum volume
            max_volume: Maximum volume
            
        Returns:
            Tuple of (SQL query, parameters)
        """
        return self.build_price_filter_query(table_name, 'vol', min_volume, max_volume)
    
    def get_supported_operators(self) -> List[str]:
        """Get list of supported operators."""
        return list(self.operators.keys())
    
    def get_date_operators(self) -> List[str]:
        """Get list of supported date operators."""
        return list(self.date_operators.keys())
    
    def validate_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Validate a condition dictionary.
        
        Args:
            condition: Condition dictionary to validate
            
        Returns:
            True if condition is valid, False otherwise
        """
        required_keys = ['column', 'operator', 'value']
        
        if not all(key in condition for key in required_keys):
            return False
        
        if condition['operator'] not in self.operators:
            return False
        
        # Special validation for certain operators
        if condition['operator'] in ['is_null', 'is_not_null']:
            return True  # Value is ignored for these operators
        
        if condition['operator'] == 'between':
            return isinstance(condition['value'], (list, tuple)) and len(condition['value']) == 2
        
        if condition['operator'] in ['in', 'not_in']:
            return isinstance(condition['value'], (list, tuple))
        
        return True
