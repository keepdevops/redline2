"""
Financial analysis routes for VarioSync Web GUI
Handles financial data analysis operations
"""

from flask import Blueprint
import logging
import pandas as pd
import numpy as np
from ..utils.analysis_helpers import convert_numpy_types, detect_price_column, detect_volume_column

analysis_financial_bp = Blueprint('analysis_financial', __name__)
logger = logging.getLogger(__name__)



def perform_financial_analysis(df):
    """Perform financial data analysis on any DataFrame with numeric columns."""
    # Validate input DataFrame
    if df is None:
        logger.error("Financial analysis called with None DataFrame")
        return {'error': 'No data provided for analysis'}

    if not isinstance(df, pd.DataFrame):
        logger.error(f"Financial analysis called with invalid type: {type(df)}")
        return {'error': 'Invalid data type (expected DataFrame)'}

    if df.empty:
        logger.warning("Financial analysis called with empty DataFrame")
        return {'error': 'DataFrame contains no data'}

    if len(df.columns) == 0:
        logger.error("Financial analysis called with DataFrame having no columns")
        return {'error': 'DataFrame has no columns'}

    logger.debug(f"Starting financial analysis on DataFrame with shape: {df.shape}")

    # Initialize analysis structure
    analysis = {
        'price_analysis': {},
        'volume_analysis': {},
        'returns_analysis': {},
        'volatility_analysis': {}
    }

    # Log available columns for debugging
    logger.info(f"Available columns in DataFrame: {list(df.columns)}")

    # Use flexible column detection that works with any column names
    price_col = detect_price_column(df)
    volume_col = detect_volume_column(df)

    logger.info(f"Detected price column: {price_col}")
    logger.info(f"Detected volume column: {volume_col}")

    # Price analysis
    if price_col:
        logger.debug(f"Analyzing price column: {price_col}")

        # Convert to numeric, handling errors
        try:
            prices = pd.to_numeric(df[price_col], errors='coerce')
        except Exception as e:
            logger.error(f"Error converting price column to numeric: {str(e)}")
            analysis['price_analysis'] = {'error': f'Failed to convert price column: {str(e)}'}
            prices = None

        if prices is not None:
            # Drop NaN values and validate we have numeric data
            prices = prices.dropna()

            if prices.empty:
                logger.warning(f"Price column '{price_col}' contains no valid numeric data after conversion")
                analysis['price_analysis'] = {'error': f'No valid numeric data in column {price_col}'}
            elif len(prices) < 2:
                logger.warning(f"Price column '{price_col}' has less than 2 valid values (found {len(prices)})")
                analysis['price_analysis'] = {
                    'current_price': convert_numpy_types(prices.iloc[0]) if len(prices) > 0 else None,
                    'error': 'Insufficient data for analysis (need at least 2 data points)'
                }
            else:
                logger.debug(f"Price column has {len(prices)} valid data points")

                # Calculate price statistics
                try:
                    analysis['price_analysis'] = {
                        'current_price': convert_numpy_types(prices.iloc[-1]),
                        'price_range': {
                            'min': convert_numpy_types(prices.min()),
                            'max': convert_numpy_types(prices.max()),
                            'avg': convert_numpy_types(prices.mean())
                        },
                        'price_change': {
                            'absolute': convert_numpy_types(prices.iloc[-1] - prices.iloc[0]),
                            'percentage': convert_numpy_types(((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100) if prices.iloc[0] != 0 else 0
                        }
                    }
                    logger.debug("Price analysis completed successfully")
                except Exception as e:
                    logger.error(f"Error calculating price statistics: {str(e)}")
                    analysis['price_analysis'] = {'error': f'Price calculation failed: {str(e)}'}

                # Calculate returns
                try:
                    returns = prices.pct_change().dropna()

                    if not returns.empty and len(returns) > 0:
                        logger.debug(f"Calculating returns analysis on {len(returns)} data points")

                        # Validate returns calculations
                        mean_return = returns.mean()
                        std_return = returns.std()

                        if pd.isna(mean_return) or pd.isna(std_return):
                            logger.warning("Returns calculations resulted in NaN values")
                            analysis['returns_analysis'] = {'error': 'Invalid returns calculation'}
                        else:
                            analysis['returns_analysis'] = {
                                'mean_return': convert_numpy_types(mean_return),
                                'std_return': convert_numpy_types(std_return),
                                'total_return': convert_numpy_types((prices.iloc[-1] / prices.iloc[0] - 1) * 100) if prices.iloc[0] != 0 else 0,
                                'sharpe_ratio': convert_numpy_types(mean_return / std_return) if std_return != 0 else 0
                            }

                            # Calculate volatility
                            analysis['volatility_analysis'] = {
                                'daily_volatility': convert_numpy_types(std_return),
                                'annualized_volatility': convert_numpy_types(std_return * np.sqrt(252)),
                                'max_drawdown': convert_numpy_types((returns.cumsum().expanding().max() - returns.cumsum()).max())
                            }
                            logger.debug("Returns and volatility analysis completed successfully")
                    else:
                        logger.warning("Returns calculation resulted in empty series")

                except Exception as e:
                    logger.error(f"Error calculating returns/volatility: {str(e)}")
                    analysis['returns_analysis'] = {'error': f'Returns calculation failed: {str(e)}'}
                    analysis['volatility_analysis'] = {'error': f'Volatility calculation failed: {str(e)}'}
    else:
        logger.warning("No price column detected in DataFrame")
        analysis['price_analysis'] = {'error': 'No suitable price column found. Please ensure your data contains numeric price/close data.'}

    # Volume analysis
    if volume_col:
        logger.debug(f"Analyzing volume column: {volume_col}")

        # Convert to numeric, handling errors
        try:
            volumes = pd.to_numeric(df[volume_col], errors='coerce')
        except Exception as e:
            logger.error(f"Error converting volume column to numeric: {str(e)}")
            analysis['volume_analysis'] = {'error': f'Failed to convert volume column: {str(e)}'}
            volumes = None

        if volumes is not None:
            # Drop NaN values and validate we have numeric data
            volumes = volumes.dropna()

            if volumes.empty:
                logger.warning(f"Volume column '{volume_col}' contains no valid numeric data after conversion")
                analysis['volume_analysis'] = {'error': f'No valid numeric data in column {volume_col}'}
            else:
                logger.debug(f"Volume column has {len(volumes)} valid data points")

                try:
                    # Calculate volume trend safely
                    volume_trend = 'stable'
                    if len(volumes) >= 10:
                        recent_avg = volumes.iloc[-5:].mean()
                        early_avg = volumes.iloc[:5].mean()
                        volume_trend = 'increasing' if recent_avg > early_avg else 'decreasing'
                    elif len(volumes) >= 2:
                        recent_avg = volumes.iloc[-1]
                        early_avg = volumes.iloc[0]
                        volume_trend = 'increasing' if recent_avg > early_avg else 'decreasing'

                    analysis['volume_analysis'] = {
                        'avg_volume': convert_numpy_types(volumes.mean()),
                        'max_volume': convert_numpy_types(volumes.max()),
                        'min_volume': convert_numpy_types(volumes.min()),
                        'volume_trend': volume_trend
                    }
                    logger.debug("Volume analysis completed successfully")

                except Exception as e:
                    logger.error(f"Error calculating volume statistics: {str(e)}")
                    analysis['volume_analysis'] = {'error': f'Volume calculation failed: {str(e)}'}
    else:
        logger.warning("No volume column detected in DataFrame")

    logger.info("Financial analysis completed")
    return analysis

