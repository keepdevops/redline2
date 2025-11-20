"""
Statistical analysis routes for REDLINE Web GUI
Handles statistical analysis operations
"""

from flask import Blueprint
import logging
import pandas as pd
import numpy as np
from ..utils.analysis_helpers import detect_date_columns

analysis_statistical_bp = Blueprint('analysis_statistical', __name__)
logger = logging.getLogger(__name__)


def perform_statistical_analysis(df):
    """Perform statistical analysis - simplified version matching Tkinter GUI."""
    try:
        # Exclude date/datetime columns from statistical analysis
        date_cols = detect_date_columns(df)
        
        # Get numeric columns excluding date columns
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in date_cols]
        
        # Only describe numeric columns (excluding dates)
        if len(numeric_cols) > 0:
            stats = df[numeric_cols].describe()
        else:
            stats = pd.DataFrame()
        
        # Convert to simple dictionary format
        analysis = {
            'descriptive_stats': stats.to_dict() if not stats.empty else {},
            'summary': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'numeric_columns': len(numeric_cols),
                'excluded_date_columns': date_cols
            }
        }
        
        # Additional analysis - check for close price column (flexible detection)
        from ..utils.analysis_helpers import detect_price_column
        close_col = detect_price_column(df)
        
        if close_col:
            close_stats = {
                'Mean': float(df[close_col].mean()),
                'Median': float(df[close_col].median()),
                'Std Dev': float(df[close_col].std()),
                'Min': float(df[close_col].min()),
                'Max': float(df[close_col].max())
            }
            analysis['close_price_stats'] = close_stats
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in statistical analysis: {str(e)}")
        return {'error': str(e)}

