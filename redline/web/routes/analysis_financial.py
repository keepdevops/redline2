"""
Financial analysis routes for REDLINE Web GUI
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
    try:
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
        
        if price_col:
            
            # Convert to numeric, handling errors
            prices = pd.to_numeric(df[price_col], errors='coerce')
            
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
                
                # Calculate returns
                returns = prices.pct_change().dropna()
                if not returns.empty and len(returns) > 0:
                    analysis['returns_analysis'] = {
                        'mean_return': convert_numpy_types(returns.mean()),
                        'std_return': convert_numpy_types(returns.std()),
                        'total_return': convert_numpy_types((prices.iloc[-1] / prices.iloc[0] - 1) * 100) if prices.iloc[0] != 0 else 0,
                        'sharpe_ratio': convert_numpy_types(returns.mean() / returns.std()) if returns.std() != 0 else 0
                    }
                    
                    analysis['volatility_analysis'] = {
                        'daily_volatility': convert_numpy_types(returns.std()),
                        'annualized_volatility': convert_numpy_types(returns.std() * np.sqrt(252)),
                        'max_drawdown': convert_numpy_types((returns.cumsum().expanding().max() - returns.cumsum()).max())
                    }
        else:
            logger.warning("No price column detected in DataFrame")
            analysis['price_analysis'] = {'error': 'No suitable price column found. Please ensure your data contains numeric price/close data.'}
        
        if volume_col:
            
            # Convert to numeric, handling errors
            volumes = pd.to_numeric(df[volume_col], errors='coerce')
            
            # Drop NaN values and validate we have numeric data
            volumes = volumes.dropna()
            
            if volumes.empty:
                logger.warning(f"Volume column '{volume_col}' contains no valid numeric data after conversion")
                analysis['volume_analysis'] = {'error': f'No valid numeric data in column {volume_col}'}
            else:
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
        else:
            logger.warning("No volume columns detected in DataFrame")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in financial analysis: {str(e)}")
        return {'error': str(e)}

