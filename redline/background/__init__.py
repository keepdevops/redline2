"""
REDLINE Background Task Processing
Handles asynchronous task processing for long-running operations.
"""

from .task_manager import TaskManager
from .tasks import (
    process_data_conversion,
    process_data_download,
    process_data_analysis,
    process_file_upload,
    process_bulk_operations
)

__all__ = [
    'TaskManager',
    'process_data_conversion',
    'process_data_download', 
    'process_data_analysis',
    'process_file_upload',
    'process_bulk_operations'
]
