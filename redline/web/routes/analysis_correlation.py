"""
Correlation analysis routes for REDLINE Web GUI
Handles correlation analysis operations
"""

from flask import Blueprint
import logging
import pandas as pd
import numpy as np
from ..utils.analysis_helpers import detect_date_columns

analysis_correlation_bp = Blueprint('analysis_correlation', __name__)
logger = logging.getLogger(__name__)


def perform_correlation_analysis(df):
    """Perform correlation analysis - simplified version matching Tkinter GUI."""
    try:
        # Exclude date/datetime columns from correlation analysis
        date_cols = detect_date_columns(df)
        
        # Select numeric columns for correlation (excluding date columns)
        numeric_cols = [col for col in df.select_dtypes(include=['number']).columns 
                       if col not in date_cols]
        
        if len(numeric_cols) < 2:
            return {'error': 'Not enough numeric columns for correlation analysis'}
        
        # Calculate correlation matrix (simple approach like Tkinter)
        correlation_matrix = df[numeric_cols].corr()
        
        # Simple analysis like Tkinter GUI
        analysis = {
            'correlation_matrix': correlation_matrix.to_dict(),
            'summary': {
                'total_numeric_columns': len(numeric_cols),
                'columns_analyzed': list(numeric_cols)
            }
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in correlation analysis: {str(e)}")
        return {'error': str(e)}

