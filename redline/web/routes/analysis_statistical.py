"""
Statistical analysis routes for VarioSync Web GUI
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
    # Validate input DataFrame
    if df is None:
        logger.error("Statistical analysis called with None DataFrame")
        return {'error': 'No data provided for analysis'}

    if not isinstance(df, pd.DataFrame):
        logger.error(f"Statistical analysis called with invalid type: {type(df)}")
        return {'error': 'Invalid data type (expected DataFrame)'}

    if df.empty:
        logger.warning("Statistical analysis called with empty DataFrame")
        return {'error': 'DataFrame contains no data'}

    if len(df.columns) == 0:
        logger.error("Statistical analysis called with DataFrame having no columns")
        return {'error': 'DataFrame has no columns'}

    logger.debug(f"Starting statistical analysis on DataFrame with shape: {df.shape}")

    # Exclude date/datetime columns from statistical analysis
    date_cols = detect_date_columns(df)
    logger.debug(f"Detected {len(date_cols)} date columns: {date_cols}")

    # Get numeric columns excluding date columns
    try:
        numeric_df = df.select_dtypes(include=[np.number])
        numeric_cols = [col for col in numeric_df.columns if col not in date_cols]
    except Exception as e:
        logger.error(f"Error selecting numeric columns: {str(e)}")
        return {'error': f'Failed to identify numeric columns: {str(e)}'}

    logger.info(f"Found {len(numeric_cols)} numeric columns for analysis (excluding {len(date_cols)} date columns)")

    # Only describe numeric columns (excluding dates)
    stats = pd.DataFrame()
    if len(numeric_cols) > 0:
        try:
            stats = df[numeric_cols].describe()
            logger.debug(f"Generated descriptive statistics for {len(numeric_cols)} columns")
        except Exception as e:
            logger.error(f"Error generating descriptive statistics: {str(e)}")
            stats = pd.DataFrame()
    else:
        logger.warning("No numeric columns found for statistical analysis")

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
        logger.debug(f"Detected price column: {close_col}, calculating price statistics")

        try:
            # Validate price column has numeric data
            price_series = df[close_col]

            if price_series.empty:
                logger.warning(f"Price column '{close_col}' is empty")
            else:
                # Calculate statistics with validation
                mean_val = price_series.mean()
                median_val = price_series.median()
                std_val = price_series.std()
                min_val = price_series.min()
                max_val = price_series.max()

                # Validate results are not NaN
                if pd.isna(mean_val) or pd.isna(median_val):
                    logger.warning(f"Price column '{close_col}' statistics resulted in NaN values")
                    analysis['close_price_stats'] = {'error': 'Invalid price data (NaN values)'}
                else:
                    close_stats = {
                        'Mean': float(mean_val),
                        'Median': float(median_val),
                        'Std Dev': float(std_val) if not pd.isna(std_val) else 0.0,
                        'Min': float(min_val),
                        'Max': float(max_val)
                    }
                    analysis['close_price_stats'] = close_stats
                    logger.debug("Price column statistics calculated successfully")

        except Exception as e:
            logger.error(f"Error calculating price column statistics: {str(e)}")
            analysis['close_price_stats'] = {'error': f'Price statistics calculation failed: {str(e)}'}
    else:
        logger.debug("No price column detected for additional analysis")

    logger.info("Statistical analysis completed")
    return analysis

