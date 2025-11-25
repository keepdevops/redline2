#!/usr/bin/env python3
"""
REDLINE Parallel File Loading
Functions for loading multiple files in parallel.
"""

import logging
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from ...core.schema import detect_format_from_path
from ...core.format_loaders import FormatLoaders

logger = logging.getLogger(__name__)


def load_single_file_parallel(file_path: str) -> Optional[pd.DataFrame]:
    """Load a single file - optimized for speed with parallel processing."""
    try:
        # Use FormatLoaders for consistent loading
        format_type = detect_format_from_path(file_path)
        loader = FormatLoaders()
        data = loader.load_file_by_type(file_path, format_type)
        
        if data is not None and isinstance(data, pd.DataFrame):
            return data
        return None
        
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return None


def load_files_parallel(file_paths: List[str]) -> Dict[str, Any]:
    """Load multiple files in parallel - same logic as tkinter GUI."""
    try:
        loaded_data = []
        skipped_files = []
        large_files = []
        
        # Check file sizes first
        for file_path in file_paths:
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 100 * 1024 * 1024:  # 100MB
                    large_files.append((file_path, file_size))
            except:
                pass
        
        # Use parallel processing for file loading (I/O bound, so more workers)
        with ThreadPoolExecutor(max_workers=8) as executor:
            # Submit all file loading tasks
            future_to_file = {
                executor.submit(load_single_file_parallel, file_path): file_path
                for file_path in file_paths
            }
            
            # Process completed loads
            completed = 0
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                completed += 1
                
                try:
                    data = future.result()
                    if data is not None and not data.empty:
                        loaded_data.append(data)
                        logger.info(f"Successfully loaded {file_path}: {len(data)} rows")
                    else:
                        skipped_files.append(file_path)
                        logger.warning(f"Skipped empty file: {file_path}")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {str(e)}")
                    skipped_files.append(file_path)
        
        # Combine loaded data with memory optimization
        if loaded_data:
            try:
                # Store count before clearing
                files_loaded_count = len(loaded_data)
                
                # Combine data with memory management
                if len(loaded_data) == 1:
                    combined_data = loaded_data[0]
                else:
                    combined_data = pd.concat(loaded_data, ignore_index=True)
                
                # Clear the list to free memory
                loaded_data.clear()
                
                return {
                    'success': True,
                    'data': combined_data,
                    'files_loaded': files_loaded_count,
                    'skipped_files': skipped_files,
                    'large_files': large_files,
                    'total_rows': len(combined_data),
                    'columns': list(combined_data.columns)
                }
                
            except MemoryError as mem_error:
                logger.error(f"Memory error combining data: {str(mem_error)}")
                return {
                    'success': False,
                    'error': 'Memory Error: File too large to load. Try loading smaller files.',
                    'skipped_files': skipped_files,
                    'large_files': large_files
                }
            except Exception as e:
                logger.error(f"Error combining data: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'skipped_files': skipped_files,
                    'large_files': large_files
                }
        else:
            return {
                'success': False,
                'error': 'No data loaded',
                'skipped_files': skipped_files,
                'large_files': large_files
            }
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in load files: {error_msg}")
        return {
            'success': False,
            'error': f"Failed to load files: {error_msg}"
        }

