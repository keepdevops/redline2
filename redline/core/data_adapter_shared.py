#!/usr/bin/env python3
"""
DataAdapter class extracted from data_module_shared.py (shared module)
Handles data preparation for ML/RL training.
"""

import logging
from typing import Union, List, Dict, Any
import pandas as pd

# Optional dependencies
try:
    import polars as pl
except ImportError:
    pl = None

try:
    import pyarrow as pa
except ImportError:
    pa = None

try:
    import tensorflow as tf
except ImportError:
    tf = None

try:
    import numpy as np
except ImportError:
    np = None

logger = logging.getLogger(__name__)


class DataAdapter:
    """Adapter for preparing data for ML/RL training."""
    
    def prepare_training_data(self, data: Union[List[pd.DataFrame], List[Any], List[Any]], 
                             format: str) -> Union[List[Any], Any]:
        """Prepare training data in specified format."""
        try:
            if isinstance(data, list) and data:
                if format == 'numpy':
                    return [d.to_numpy() for d in data if isinstance(d, (pd.DataFrame, pl.DataFrame))]
                elif format == 'tensorflow' and tf:
                    return tf.data.Dataset.from_tensor_slices(
                        [d.to_numpy() for d in data if isinstance(d, (pd.DataFrame, pl.DataFrame))]
                    )
            return []
        except Exception as e:
            logger.error(f"Failed to prepare training data: {str(e)}")
            raise

    def prepare_rl_state(self, data: Union[pd.DataFrame, Any, Any], 
                        portfolio: Dict, format: str) -> Union[Any, Any]:
        """Prepare reinforcement learning state from data."""
        try:
            if isinstance(data, (pl.DataFrame, pa.Table)):
                data = data.to_pandas()
            state = data[['close']].to_numpy()
            if format == 'tensorflow' and tf:
                return tf.convert_to_tensor(state, dtype=tf.float32)
            return state
        except Exception as e:
            logger.error(f"Failed to prepare RL state: {str(e)}")
            raise

    def summarize_preprocessed(self, data: Union[List[Any], Any], 
                               format: str) -> Dict:
        """Summarize preprocessed data."""
        try:
            return {'format': format, 'size': len(data)}
        except Exception as e:
            logger.error(f"Failed to summarize preprocessed data: {str(e)}")
            raise

