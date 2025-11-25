#!/usr/bin/env python3
"""
REDLINE ML Data Preparation
Functions for preparing data for machine learning and reinforcement learning.
"""

import logging
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


def prepare_ml_features(df: pd.DataFrame, selected_features: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Prepare features for ML training from a DataFrame.
    
    Args:
        df: Input DataFrame
        selected_features: Optional list of feature column names to use
        
    Returns:
        DataFrame with selected features or all numeric columns
        
    Raises:
        ValueError: If no numeric columns found or selected features don't exist
    """
    if selected_features:
        # Validate that all selected features exist
        missing_features = [f for f in selected_features if f not in df.columns]
        if missing_features:
            raise ValueError(f'Features not found in data: {missing_features}')
        # Filter DataFrame to only selected features
        result_df = df[selected_features]
        logger.info(f"Using selected features: {selected_features}")
    else:
        # Default: use all numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            result_df = df[numeric_cols]
            logger.info(f"Using all numeric columns: {numeric_cols}")
        else:
            raise ValueError('No numeric columns found for ML training')
    
    return result_df


def prepare_ml_data_array(df: pd.DataFrame) -> np.ndarray:
    """
    Convert DataFrame to numpy array for ML training.
    
    Args:
        df: DataFrame with numeric columns
        
    Returns:
        NumPy array ready for ML training
        
    Raises:
        ValueError: If no numeric data available
    """
    if np is None:
        raise ImportError('NumPy is not available')
    
    # Convert DataFrame to numpy array
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        raise ValueError('No numeric data available for ML training')
    
    data_array = numeric_df.to_numpy()
    
    if data_array is None or len(data_array) == 0:
        raise ValueError('No numeric data available for ML training')
    
    return data_array


def prepare_rl_state(df: pd.DataFrame, close_column: str = 'close') -> np.ndarray:
    """
    Prepare reinforcement learning state from DataFrame.
    
    Args:
        df: Input DataFrame
        close_column: Name of the close price column
        
    Returns:
        NumPy array with close prices for RL state
        
    Raises:
        ValueError: If close column not found
    """
    if close_column not in df.columns:
        raise ValueError(f'Close column "{close_column}" not found in data')
    
    state = df[[close_column]].to_numpy()
    return state

