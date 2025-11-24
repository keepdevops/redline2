#!/usr/bin/env python3
"""
AdvancedQueryBuilder class extracted from data_module_shared.py (shared module)
Builds SQL queries for complex data filtering.
"""

import logging

logger = logging.getLogger(__name__)


class AdvancedQueryBuilder:
    """Advanced query builder for complex data filtering."""
    
    def __init__(self):
        """Initialize query builder with operators."""
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
        
    def build_query(self, conditions, table_name='tickers_data'):
        """Build SQL query from conditions."""
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

