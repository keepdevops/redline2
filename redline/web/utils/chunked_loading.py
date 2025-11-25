#!/usr/bin/env python3
"""
REDLINE Chunked File Loading
Functions for loading large files in chunks to prevent memory issues.
"""

import logging
import pandas as pd
from typing import Optional
from ...core.format_converter import FormatConverter

logger = logging.getLogger(__name__)


def load_large_file_chunked(file_path: str, format_type: str, chunk_size: int = 10000) -> pd.DataFrame:
    """Load large files in chunks to prevent memory issues (same as Tkinter)."""
    try:
        logger.info(f"Loading large file {file_path} in chunks of {chunk_size} rows")
        
        if format_type == 'csv':
            # Load CSV in chunks
            chunks = []
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                chunks.append(chunk)
                if len(chunks) >= 10:  # Limit memory usage
                    combined = pd.concat(chunks, ignore_index=True)
                    chunks = [combined]
            
            if chunks:
                return pd.concat(chunks, ignore_index=True)
            else:
                return pd.DataFrame()
        
        elif format_type == 'txt':
            # For text files, try to detect if it's Stooq format
            try:
                # Read first few lines to detect format
                with open(file_path, 'r') as f:
                    first_line = f.readline().strip()
                    
                if '<TICKER>' in first_line:
                    # Stooq format - load in chunks
                    chunks = []
                    for chunk in pd.read_csv(file_path, chunksize=chunk_size, sep=','):
                        chunks.append(chunk)
                        if len(chunks) >= 10:
                            combined = pd.concat(chunks, ignore_index=True)
                            chunks = [combined]
                    
                    if chunks:
                        return pd.concat(chunks, ignore_index=True)
                
            except Exception as e:
                logger.warning(f"Error in chunked text loading: {str(e)}")
            
            # Fallback to regular loading
            converter = FormatConverter()
            return converter.load_file_by_type(file_path, format_type)
        
        else:
            # For other formats, use regular loading
            converter = FormatConverter()
            return converter.load_file_by_type(file_path, format_type)
            
    except Exception as e:
        logger.error(f"Error in chunked loading: {str(e)}")
        return pd.DataFrame()

