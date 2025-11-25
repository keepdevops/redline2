"""
File loading utilities for REDLINE Web GUI
Extracted from redline/web/routes/data.py for better organization.

This module now serves as a compatibility layer that re-exports functions
from specialized modules for backward compatibility.
"""

import logging
from flask import current_app

# Import from specialized modules
from .parallel_loading import load_single_file_parallel, load_files_parallel
from .file_filters import apply_filters
from .chunked_loading import load_large_file_chunked
from ...core.format_loaders import FormatLoaders
from ...core.format_savers import FormatSavers

logger = logging.getLogger(__name__)

# Rate limiting decorator (if limiter is available)
def rate_limit(limit_string):
    """Decorator for rate limiting - gracefully handles missing limiter."""
    def decorator(func):
        try:
            limiter = current_app.config.get('limiter') if current_app else None
            if limiter:
                from flask_limiter import Limiter
                return limiter.limit(limit_string)(func)
            return func
        except:
            return func
    return decorator

# Compatibility functions that delegate to FormatLoaders/FormatSavers
def load_file_by_format(file_path: str, format_type: str):
    """Load file based on format type."""
    import pandas as pd
    loader = FormatLoaders()
    return loader.load_file_by_type(file_path, format_type)

def save_file_by_format(df, file_path: str, format_type: str) -> bool:
    """Save DataFrame to file based on format type."""
    try:
        saver = FormatSavers()
        saver.save_file_by_type(df, file_path, format_type)
        return True
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {str(e)}")
        return False

# Re-export for backward compatibility
__all__ = [
    'rate_limit',
    'load_single_file_parallel',
    'load_files_parallel',
    'load_file_by_format',
    'save_file_by_format',
    'apply_filters',
    'load_large_file_chunked'
]
