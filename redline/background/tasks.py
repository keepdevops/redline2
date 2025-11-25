#!/usr/bin/env python3
"""
REDLINE Background Tasks
Defines Celery tasks for asynchronous processing.
This module serves as a registry that imports and wraps task implementations.
"""

import logging
from typing import Dict, Any, List

try:
    from celery import Celery, Task
    CELERY_AVAILABLE = True
except ImportError:
    Celery = None
    Task = None
    CELERY_AVAILABLE = False

# Import task implementations
from .tasks.conversion_tasks import process_data_conversion_impl, process_file_upload_impl
from .tasks.download_tasks import process_data_download_impl
from .tasks.analysis_tasks import process_data_analysis_impl
from .tasks.bulk_tasks import process_bulk_operations_impl

logger = logging.getLogger(__name__)

# Initialize Celery app if available
if CELERY_AVAILABLE:
    celery_app = Celery('redline')
    BaseTask = Task
else:
    celery_app = None
    # Create a dummy BaseTask class when Celery is not available
    class BaseTask:
        def __init__(self, *args, **kwargs):
            pass
        
        def on_success(self, retval, task_id, args, kwargs):
            logger.info(f"Task {task_id} completed successfully")
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f"Task {task_id} failed: {str(exc)}")
        
        def on_retry(self, exc, task_id, args, kwargs, einfo):
            logger.warning(f"Task {task_id} retrying: {str(exc)}")

# Create Celery tasks or regular functions based on availability
if CELERY_AVAILABLE:
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_data_conversion')
    def process_data_conversion(self, input_file: str, output_format: str, output_file: str, 
                               options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data format conversion in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return process_data_conversion_impl(input_file, output_format, output_file, options, progress_callback)
    
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_data_download')
    def process_data_download(self, ticker: str, start_date: str, end_date: str, 
                             source: str = 'yahoo', options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data download in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return process_data_download_impl(ticker, start_date, end_date, source, options, progress_callback)
    
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_data_analysis')
    def process_data_analysis(self, data_file: str, analysis_type: str, 
                             options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data analysis in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return process_data_analysis_impl(data_file, analysis_type, options, progress_callback)
    
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_file_upload')
    def process_file_upload(self, file_path: str, target_format: str = None, 
                           options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process file upload in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return process_file_upload_impl(file_path, target_format, options, progress_callback)
    
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_bulk_operations')
    def process_bulk_operations(self, operations: List[Dict[str, Any]], 
                              options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process bulk operations in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return process_bulk_operations_impl(operations, options, progress_callback)
else:
    def process_data_conversion(input_file: str, output_format: str, output_file: str, 
                               options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data format conversion in background."""
        return process_data_conversion_impl(input_file, output_format, output_file, options)
    
    def process_data_download(ticker: str, start_date: str, end_date: str, 
                             source: str = 'yahoo', options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data download in background."""
        return process_data_download_impl(ticker, start_date, end_date, source, options)
    
    def process_data_analysis(data_file: str, analysis_type: str, 
                             options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data analysis in background."""
        return process_data_analysis_impl(data_file, analysis_type, options)
    
    def process_file_upload(file_path: str, target_format: str = None, 
                           options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process file upload in background."""
        return process_file_upload_impl(file_path, target_format, options)
    
    def process_bulk_operations(operations: List[Dict[str, Any]], 
                              options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process bulk operations in background."""
        return process_bulk_operations_impl(operations, options)
