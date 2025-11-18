"""
Basic analysis routes for REDLINE Web GUI
Handles basic data analysis operations
"""

from flask import Blueprint
import logging
import pandas as pd
import numpy as np
from ..utils.analysis_helpers import convert_numpy_types, detect_date_columns

analysis_basic_bp = Blueprint('analysis_basic', __name__)
logger = logging.getLogger(__name__)


def perform_basic_analysis(df):
    """Perform basic data analysis."""
    try:
        analysis = {
            'shape': {
                'rows': int(len(df)),
                'columns': int(len(df.columns))
            },
            'data_types': df.dtypes.astype(str).to_dict(),
            'null_counts': convert_numpy_types(df.isnull().sum().to_dict()),
            'memory_usage': int(df.memory_usage(deep=True).sum()),
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # Exclude date/datetime columns from numeric analysis
        date_cols = detect_date_columns(df)
        
        # Numeric columns analysis (excluding date columns)
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in date_cols]
        
        if len(numeric_cols) > 0:
            numeric_df = df[numeric_cols]
            
            analysis['numeric_summary'] = {
                'count': convert_numpy_types(numeric_df.count().to_dict()),
                'mean': convert_numpy_types(numeric_df.mean().to_dict()),
                'std': convert_numpy_types(numeric_df.std().to_dict()),
                'min': convert_numpy_types(numeric_df.min().to_dict()),
                'max': convert_numpy_types(numeric_df.max().to_dict()),
                'percentiles': {
                    '25%': convert_numpy_types(numeric_df.quantile(0.25).to_dict()),
                    '50%': convert_numpy_types(numeric_df.quantile(0.50).to_dict()),
                    '75%': convert_numpy_types(numeric_df.quantile(0.75).to_dict())
                }
            }
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                analysis['categorical_summary'][col] = {
                    'unique_count': int(df[col].nunique()),
                    'most_common': convert_numpy_types(df[col].value_counts().head(5).to_dict()),
                    'null_count': int(df[col].isnull().sum())
                }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in basic analysis: {str(e)}")
        return {'error': str(e)}

