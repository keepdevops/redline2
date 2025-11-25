#!/usr/bin/env python3
"""
REDLINE ML Format Converters
Functions for converting data to ML/RL formats (NumPy, TensorFlow).
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


def convert_to_numpy_format(data_array: np.ndarray) -> Dict[str, Any]:
    """
    Convert numpy array to JSON-serializable format.
    
    Args:
        data_array: NumPy array to convert
        
    Returns:
        Dictionary with format information and preview data
    """
    if data_array is None or (hasattr(data_array, '__len__') and len(data_array) == 0):
        raise ValueError('Prepared data is empty')
    
    # Get shape and dtype
    shape = list(data_array.shape) if hasattr(data_array, 'shape') else None
    if shape:
        shape = [int(s) for s in shape]  # Convert numpy int64 to Python int
    
    dtype = str(data_array.dtype) if hasattr(data_array, 'dtype') else None
    sample_size = int(len(data_array)) if hasattr(data_array, '__len__') else 0
    
    # Convert preview data to native Python types
    data_preview = []
    if hasattr(data_array, '__len__') and len(data_array) > 0:
        preview = data_array[:10]
        if hasattr(preview, 'tolist'):
            data_preview = preview.tolist()
        else:
            data_preview = [float(x) if isinstance(x, (np.integer, np.floating)) else x for x in preview]
    
    return {
        'format': 'numpy',
        'shape': shape,
        'dtype': dtype,
        'sample_size': sample_size,
        'data_preview': data_preview
    }


def convert_to_tensorflow_dataset(data_array: np.ndarray) -> Dict[str, Any]:
    """
    Convert numpy array to TensorFlow Dataset format.
    
    Args:
        data_array: NumPy array to convert
        
    Returns:
        Dictionary with TensorFlow Dataset information
        
    Raises:
        ImportError: If TensorFlow is not installed
        ValueError: If conversion fails
    """
    try:
        import tensorflow as tf
    except ImportError:
        raise ImportError('TensorFlow is not installed. Install with: pip install tensorflow')
    
    if tf is None:
        raise ImportError('TensorFlow is not available')
    
    if np is None:
        raise ImportError('NumPy is not available')
    
    # Ensure float32 dtype for TensorFlow
    if data_array.dtype != np.float32:
        data_array = data_array.astype(np.float32)
    
    # Create TensorFlow Dataset
    tf_dataset = tf.data.Dataset.from_tensor_slices(data_array)
    
    # Get dataset info
    dataset_size = 0
    try:
        cardinality = tf_dataset.cardinality().numpy()
        if cardinality == -1:  # Unknown cardinality
            dataset_size = int(len(data_array))
        else:
            dataset_size = int(cardinality)
    except:
        dataset_size = int(len(data_array))
    
    # Convert element_spec to string safely
    element_spec_str = None
    try:
        if hasattr(tf_dataset, 'element_spec'):
            element_spec_str = str(tf_dataset.element_spec)
    except:
        pass
    
    return {
        'format': 'tensorflow',
        'type': 'Dataset',
        'sample_size': dataset_size,
        'element_spec': element_spec_str,
        'message': 'TensorFlow Dataset created successfully'
    }


def convert_to_tensorflow_tensor(data_array: np.ndarray) -> Dict[str, Any]:
    """
    Convert numpy array to TensorFlow Tensor format.
    
    Args:
        data_array: NumPy array to convert
        
    Returns:
        Dictionary with TensorFlow Tensor information
        
    Raises:
        ImportError: If TensorFlow is not installed
    """
    try:
        import tensorflow as tf
    except ImportError:
        raise ImportError('TensorFlow is not installed. Install with: pip install tensorflow')
    
    if tf is None:
        raise ImportError('TensorFlow is not available')
    
    # Convert to TensorFlow tensor
    rl_state = tf.convert_to_tensor(data_array, dtype=tf.float32)
    
    return {
        'format': 'tensorflow',
        'type': 'Tensor',
        'message': 'TensorFlow Tensor created successfully'
    }

