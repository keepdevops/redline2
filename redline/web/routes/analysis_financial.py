"""
Financial analysis routes for REDLINE Web GUI
Handles financial data analysis operations
"""

from flask import Blueprint
import logging
import pandas as pd
import numpy as np
from ..utils.analysis_helpers import convert_numpy_types

analysis_financial_bp = Blueprint('analysis_financial', __name__)
logger = logging.getLogger(__name__)


def perform_financial_analysis(df):
    """Perform financial data analysis."""
    try:
        analysis = {
            'price_analysis': {},
            'volume_analysis': {},
            'returns_analysis': {},
            'volatility_analysis': {}
        }
        
        # Common financial column names - enhanced detection
        price_cols = [col for col in df.columns if any(price in col.lower() for price in ['close', 'price', 'adj close', 'px_last', '<close>', 'c'])]
        volume_cols = [col for col in df.columns if any(vol in col.lower() for vol in ['volume', 'vol', '<vol>', 'px_volume', 'v'])]
        high_cols = [col for col in df.columns if any(high in col.lower() for high in ['high', '<high>', 'px_high', 'h'])]
        low_cols = [col for col in df.columns if any(low in col.lower() for low in ['low', '<low>', 'px_low', 'l'])]
        open_cols = [col for col in df.columns if any(open in col.lower() for open in ['open', '<open>', 'px_open', 'o'])]
        
        if price_cols:
            price_col = price_cols[0]  # Use first price column
            prices = pd.to_numeric(df[price_col], errors='coerce')
            
            analysis['price_analysis'] = {
                    'current_price': convert_numpy_types(prices.iloc[-1]) if not prices.empty else None,
                    'price_range': {
                        'min': convert_numpy_types(prices.min()),
                        'max': convert_numpy_types(prices.max()),
                        'avg': convert_numpy_types(prices.mean())
                    },
                    'price_change': {
                        'absolute': convert_numpy_types(prices.iloc[-1] - prices.iloc[0]) if len(prices) > 1 else 0,
                        'percentage': convert_numpy_types(((prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]) * 100) if len(prices) > 1 and prices.iloc[0] != 0 else 0
                    }
                }
            
            # Calculate returns
            returns = prices.pct_change().dropna()
            if not returns.empty:
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
        
        if volume_cols:
            volume_col = volume_cols[0]
            volumes = pd.to_numeric(df[volume_col], errors='coerce')
            
            analysis['volume_analysis'] = {
                'avg_volume': convert_numpy_types(volumes.mean()),
                'max_volume': convert_numpy_types(volumes.max()),
                'min_volume': convert_numpy_types(volumes.min()),
                'volume_trend': 'increasing' if volumes.iloc[-5:].mean() > volumes.iloc[:5].mean() else 'decreasing'
            }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in financial analysis: {str(e)}")
        return {'error': str(e)}

