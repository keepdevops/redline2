#!/usr/bin/env python3
"""
REDLINE File Filters
Functions for applying filters to DataFrames.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply filters to DataFrame."""
    filtered_df = df.copy()
    
    for column, filter_config in filters.items():
        if column not in filtered_df.columns:
            continue
            
        filter_type = filter_config.get('type')
        filter_value = filter_config.get('value')
        
        if not filter_type or not filter_value:
            continue
        
        try:
            if filter_type == 'equals':
                filtered_df = filtered_df[filtered_df[column].astype(str) == str(filter_value)]
            elif filter_type == 'contains':
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(filter_value), case=False, na=False)]
            elif filter_type == 'greater_than':
                filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') > float(filter_value)]
            elif filter_type == 'less_than':
                filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') < float(filter_value)]
            elif filter_type == 'date_range':
                # Handle date range filtering
                if ' to ' in filter_value:
                    start_date, end_date = filter_value.split(' to ')
                    filtered_df = filtered_df[
                        (pd.to_datetime(filtered_df[column], errors='coerce') >= pd.to_datetime(start_date)) &
                        (pd.to_datetime(filtered_df[column], errors='coerce') <= pd.to_datetime(end_date))
                    ]
        except Exception as e:
            logger.error(f"Error applying filter {column}: {str(e)}")
            continue
    
    return filtered_df

