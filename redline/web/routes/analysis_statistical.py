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
        
        # Get numeric columns excluding date columns and string columns
        # Exclude known string columns (ticker, symbol, etc.)
        string_cols = ['ticker', 'symbol', 'format']
        numeric_cols = []
        
        # First, get columns that pandas thinks are numeric
        potential_numeric = [col for col in df.select_dtypes(include=[np.number]).columns 
                           if col not in date_cols]
        
        # Validate each column is actually numeric (not string data)
        for col in potential_numeric:
            if col.lower() in [s.lower() for s in string_cols]:
                continue  # Skip known string columns
            
            try:
                # Check a sample of values to ensure they're actually numeric
                sample = df[col].dropna().head(20)
                if len(sample) > 0:
                    # Check if values are strings that look like repeated patterns
                    if all(isinstance(x, str) for x in sample):
                        first_val = str(sample.iloc[0])
                        
                        # Check for repeated patterns (like "AAPLAAPL..." or "IBMIBM")
                        def is_repeated_pattern(s):
                            """Check if string is a repetition of a shorter substring."""
                            if len(s) < 2:
                                return False
                            # Check if string is repetition of first N characters
                            for i in range(1, len(s) // 2 + 1):
                                substring = s[:i]
                                if len(s) % len(substring) == 0:
                                    repetitions = len(s) // len(substring)
                                    if substring * repetitions == s:
                                        return True
                            return False
                        
                        if is_repeated_pattern(first_val):
                            logger.warning(f"Skipping column '{col}' - contains repeated string pattern: '{first_val[:20]}...'")
                            continue
                        
                        # Check for long repeated patterns (like "AAPLAAPLAAPL...")
                        if len(first_val) > 20 and len(set(first_val)) < 5:
                            logger.warning(f"Skipping column '{col}' - appears to contain repeated string pattern")
                            continue
                        
                        # Check if it's ticker-like (short uppercase strings that aren't repeated)
                        if all(len(str(x)) <= 10 and str(x).isupper() and not is_repeated_pattern(str(x)) for x in sample):
                            # This might be legitimate ticker data, but check if it's actually numeric
                            # If all values are the same ticker repeated, skip it
                            unique_values = set(str(x) for x in sample)
                            if len(unique_values) == 1 and is_repeated_pattern(list(unique_values)[0]):
                                logger.warning(f"Skipping column '{col}' - appears to be repeated ticker data")
                                continue
                    # Try numeric conversion to validate
                    numeric_sample = pd.to_numeric(sample, errors='coerce')
                    if numeric_sample.notna().sum() < len(sample) * 0.8:  # Less than 80% numeric
                        logger.warning(f"Skipping column '{col}' - less than 80% numeric values")
                        continue
                numeric_cols.append(col)
            except Exception as e:
                logger.warning(f"Error validating column '{col}': {str(e)}, skipping")
                continue
        
        # Only describe numeric columns (excluding dates and strings)
        if len(numeric_cols) > 0:
            try:
                # Ensure all columns are actually numeric before describing
                numeric_df = df[numeric_cols].copy()
                # Convert any remaining object columns to numeric
                for col in numeric_df.columns:
                    if numeric_df[col].dtype == 'object':
                        numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce')
                stats = numeric_df.describe()
            except Exception as e:
                logger.error(f"Error describing numeric columns: {str(e)}")
                stats = pd.DataFrame()
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
        
        if close_col and close_col in df.columns:
            try:
                # Convert to numeric first, handling errors gracefully
                prices = pd.to_numeric(df[close_col], errors='coerce')
                
                # Drop NaN values
                prices = prices.dropna()
                
                # Validate we have numeric data and it's not string data
                if prices.empty:
                    logger.warning(f"Price column '{close_col}' contains no valid numeric data")
                elif len(prices) < 2:
                    logger.warning(f"Price column '{close_col}' has insufficient data (found {len(prices)} values)")
                else:
                    # Check if values look like prices (not repeated strings)
                    sample_values = prices.head(10)
                    if all(isinstance(v, (int, float)) and not pd.isna(v) for v in sample_values):
                        close_stats = {
                            'Mean': float(prices.mean()),
                            'Median': float(prices.median()),
                            'Std Dev': float(prices.std()),
                            'Min': float(prices.min()),
                            'Max': float(prices.max())
                        }
                        analysis['close_price_stats'] = close_stats
                    else:
                        logger.warning(f"Price column '{close_col}' contains non-numeric data")
            except Exception as e:
                logger.error(f"Error calculating close price stats for column '{close_col}': {str(e)}")
                # Don't fail the entire analysis if price stats fail
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in statistical analysis: {str(e)}")
        return {'error': str(e)}

