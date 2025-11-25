"""
REDLINE Background Task Processing
Handles asynchronous task processing for long-running operations.
"""

from .task_manager import TaskManager
# Import from tasks module (tasks.py), not tasks package
import os
import importlib.util

# Import tasks module explicitly to avoid package/module conflict
# Get the directory containing this __init__.py
current_dir = os.path.dirname(os.path.abspath(__file__))
tasks_py_path = os.path.join(current_dir, 'tasks.py')

if os.path.exists(tasks_py_path):
    spec = importlib.util.spec_from_file_location("redline.background.tasks_module", tasks_py_path)
    tasks_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tasks_module)
    
    # Re-export task functions
    process_data_conversion = tasks_module.process_data_conversion
    process_data_download = tasks_module.process_data_download
    process_data_analysis = tasks_module.process_data_analysis
    process_file_upload = tasks_module.process_file_upload
    process_bulk_operations = tasks_module.process_bulk_operations
else:
    # Fallback: create dummy functions if tasks.py doesn't exist
    def process_data_conversion(*args, **kwargs):
        raise NotImplementedError("tasks.py not found")
    def process_data_download(*args, **kwargs):
        raise NotImplementedError("tasks.py not found")
    def process_data_analysis(*args, **kwargs):
        raise NotImplementedError("tasks.py not found")
    def process_file_upload(*args, **kwargs):
        raise NotImplementedError("tasks.py not found")
    def process_bulk_operations(*args, **kwargs):
        raise NotImplementedError("tasks.py not found")

__all__ = [
    'TaskManager',
    'process_data_conversion',
    'process_data_download', 
    'process_data_analysis',
    'process_file_upload',
    'process_bulk_operations'
]
