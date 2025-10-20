#!/usr/bin/env python3
"""
REDLINE Background Tasks
Defines Celery tasks for asynchronous processing.
"""

import os
import logging
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
import json

try:
    from celery import Celery, Task
    CELERY_AVAILABLE = True
except ImportError:
    Celery = None
    Task = None
    CELERY_AVAILABLE = False

# Import REDLINE modules
from ..core.format_converter import FormatConverter
from ..core.data_loader import DataLoader
from ..database.optimized_connector import OptimizedDatabaseConnector

logger = logging.getLogger(__name__)

# Initialize Celery app if available
if CELERY_AVAILABLE:
    celery_app = Celery('redline')
else:
    celery_app = None

class BaseTask(Task):
    """Base task class with common functionality."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called on successful task execution."""
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure."""
        logger.error(f"Task {task_id} failed: {str(exc)}")
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called on task retry."""
        logger.warning(f"Task {task_id} retrying: {str(exc)}")

@celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_data_conversion')
def process_data_conversion(self, input_file: str, output_format: str, output_file: str, 
                           options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process data format conversion in background."""
    try:
        logger.info(f"Starting data conversion: {input_file} -> {output_format}")
        
        # Update progress
        self.update_state(state='PROGRESS', meta={'step': 'loading_data', 'progress': 10})
        
        # Load data
        converter = FormatConverter()
        format_type = converter.detect_format_from_extension(input_file)
        data = converter.load_file_by_type(input_file, format_type)
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Invalid data format")
        
        self.update_state(state='PROGRESS', meta={'step': 'converting_data', 'progress': 50})
        
        # Convert and save
        converter.save_file_by_type(data, output_file, output_format)
        
        self.update_state(state='PROGRESS', meta={'step': 'finalizing', 'progress': 90})
        
        result = {
            'status': 'success',
            'input_file': input_file,
            'output_file': output_file,
            'output_format': output_format,
            'rows_converted': len(data),
            'columns': list(data.columns),
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Data conversion completed: {len(data)} rows")
        return result
        
    except Exception as e:
        logger.error(f"Data conversion failed: {str(e)}")
        raise

@celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_data_download')
def process_data_download(self, ticker: str, start_date: str, end_date: str, 
                         source: str = 'yahoo', options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process data download in background."""
    try:
        logger.info(f"Starting data download: {ticker} from {source}")
        
        self.update_state(state='PROGRESS', meta={'step': 'connecting', 'progress': 10})
        
        # Import downloader based on source
        if source == 'yahoo':
            from ..downloaders.yahoo_downloader import YahooDownloader
            downloader = YahooDownloader()
        else:
            raise ValueError(f"Unsupported source: {source}")
        
        self.update_state(state='PROGRESS', meta={'step': 'downloading', 'progress': 50})
        
        # Download data
        data = downloader.download_data(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
        
        if data is None or len(data) == 0:
            raise ValueError("No data downloaded")
        
        self.update_state(state='PROGRESS', meta={'step': 'saving', 'progress': 80})
        
        # Save data
        output_file = f"data/downloaded/{ticker}_{source}_data_{start_date}_{end_date}.csv"
        data.to_csv(output_file, index=False)
        
        result = {
            'status': 'success',
            'ticker': ticker,
            'source': source,
            'start_date': start_date,
            'end_date': end_date,
            'output_file': output_file,
            'rows_downloaded': len(data),
            'columns': list(data.columns),
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Data download completed: {len(data)} rows for {ticker}")
        return result
        
    except Exception as e:
        logger.error(f"Data download failed: {str(e)}")
        raise

@celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_data_analysis')
def process_data_analysis(self, data_file: str, analysis_type: str, 
                         parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process data analysis in background."""
    try:
        logger.info(f"Starting data analysis: {analysis_type} on {data_file}")
        
        self.update_state(state='PROGRESS', meta={'step': 'loading_data', 'progress': 10})
        
        # Load data
        converter = FormatConverter()
        format_type = converter.detect_format_from_extension(data_file)
        data = converter.load_file_by_type(data_file, format_type)
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Invalid data format")
        
        self.update_state(state='PROGRESS', meta={'step': 'analyzing', 'progress': 50})
        
        # Perform analysis based on type
        analysis_result = {}
        
        if analysis_type == 'basic_stats':
            analysis_result = {
                'row_count': len(data),
                'column_count': len(data.columns),
                'columns': list(data.columns),
                'data_types': data.dtypes.astype(str).to_dict(),
                'null_counts': data.isnull().sum().to_dict(),
                'memory_usage': data.memory_usage(deep=True).sum()
            }
        
        elif analysis_type == 'financial_metrics':
            # Calculate financial metrics
            numeric_columns = data.select_dtypes(include=['number']).columns
            
            analysis_result = {
                'numeric_columns': list(numeric_columns),
                'summary_stats': data[numeric_columns].describe().to_dict(),
                'correlations': data[numeric_columns].corr().to_dict() if len(numeric_columns) > 1 else {}
            }
        
        elif analysis_type == 'time_series':
            # Time series analysis
            date_columns = data.select_dtypes(include=['datetime']).columns
            
            analysis_result = {
                'date_columns': list(date_columns),
                'time_range': {
                    'start': str(data[date_columns[0]].min()) if len(date_columns) > 0 else None,
                    'end': str(data[date_columns[0]].max()) if len(date_columns) > 0 else None
                } if len(date_columns) > 0 else None
            }
        
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        self.update_state(state='PROGRESS', meta={'step': 'finalizing', 'progress': 90})
        
        result = {
            'status': 'success',
            'data_file': data_file,
            'analysis_type': analysis_type,
            'parameters': parameters or {},
            'analysis_result': analysis_result,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Data analysis completed: {analysis_type}")
        return result
        
    except Exception as e:
        logger.error(f"Data analysis failed: {str(e)}")
        raise

@celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_file_upload')
def process_file_upload(self, file_path: str, target_format: str = None, 
                       options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process file upload and validation in background."""
    try:
        logger.info(f"Starting file upload processing: {file_path}")
        
        self.update_state(state='PROGRESS', meta={'step': 'validating', 'progress': 10})
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        self.update_state(state='PROGRESS', meta={'step': 'analyzing', 'progress': 30})
        
        # Analyze file format
        converter = FormatConverter()
        detected_format = converter.detect_format_from_extension(file_path)
        
        # Load and validate data
        try:
            data = converter.load_file_by_type(file_path, detected_format)
            
            if isinstance(data, pd.DataFrame):
                data_info = {
                    'rows': len(data),
                    'columns': len(data.columns),
                    'column_names': list(data.columns),
                    'data_types': data.dtypes.astype(str).to_dict(),
                    'memory_usage': data.memory_usage(deep=True).sum()
                }
            else:
                data_info = {
                    'rows': 0,
                    'columns': 0,
                    'column_names': [],
                    'data_types': {},
                    'memory_usage': 0
                }
        except Exception as e:
            logger.warning(f"Could not load data for analysis: {str(e)}")
            data_info = {
                'rows': 0,
                'columns': 0,
                'column_names': [],
                'data_types': {},
                'memory_usage': 0,
                'load_error': str(e)
            }
        
        self.update_state(state='PROGRESS', meta={'step': 'storing', 'progress': 70})
        
        # Store in database if requested
        if options and options.get('store_in_db', False):
            try:
                db = OptimizedDatabaseConnector()
                table_name = f"uploaded_{file_name.replace('.', '_')}"
                db.write_shared_data(table_name, data, detected_format)
                stored_in_db = True
                db_table = table_name
            except Exception as e:
                logger.error(f"Failed to store in database: {str(e)}")
                stored_in_db = False
                db_table = None
        else:
            stored_in_db = False
            db_table = None
        
        self.update_state(state='PROGRESS', meta={'step': 'finalizing', 'progress': 90})
        
        result = {
            'status': 'success',
            'file_path': file_path,
            'file_name': file_name,
            'file_size': file_size,
            'detected_format': detected_format,
            'target_format': target_format,
            'data_info': data_info,
            'stored_in_db': stored_in_db,
            'db_table': db_table,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"File upload processing completed: {file_name}")
        return result
        
    except Exception as e:
        logger.error(f"File upload processing failed: {str(e)}")
        raise

@celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_bulk_operations')
def process_bulk_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process multiple operations in batch."""
    try:
        logger.info(f"Starting bulk operations: {len(operations)} operations")
        
        results = []
        successful = 0
        failed = 0
        
        for i, operation in enumerate(operations):
            try:
                self.update_state(state='PROGRESS', meta={
                    'step': f'processing_operation_{i+1}',
                    'progress': int((i / len(operations)) * 80),
                    'current_operation': operation.get('type', 'unknown')
                })
                
                operation_type = operation.get('type')
                operation_data = operation.get('data', {})
                
                # Execute operation based on type
                if operation_type == 'conversion':
                    result = process_data_conversion(
                        operation_data.get('input_file'),
                        operation_data.get('output_format'),
                        operation_data.get('output_file'),
                        operation_data.get('options')
                    )
                elif operation_type == 'download':
                    result = process_data_download(
                        operation_data.get('ticker'),
                        operation_data.get('start_date'),
                        operation_data.get('end_date'),
                        operation_data.get('source', 'yahoo'),
                        operation_data.get('options')
                    )
                elif operation_type == 'analysis':
                    result = process_data_analysis(
                        operation_data.get('data_file'),
                        operation_data.get('analysis_type'),
                        operation_data.get('parameters')
                    )
                else:
                    raise ValueError(f"Unknown operation type: {operation_type}")
                
                results.append({
                    'operation_id': i,
                    'operation_type': operation_type,
                    'status': 'success',
                    'result': result
                })
                successful += 1
                
            except Exception as e:
                results.append({
                    'operation_id': i,
                    'operation_type': operation.get('type', 'unknown'),
                    'status': 'failed',
                    'error': str(e)
                })
                failed += 1
        
        self.update_state(state='PROGRESS', meta={'step': 'finalizing', 'progress': 90})
        
        result = {
            'status': 'completed',
            'total_operations': len(operations),
            'successful_operations': successful,
            'failed_operations': failed,
            'success_rate': successful / len(operations) * 100 if operations else 0,
            'results': results,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Bulk operations completed: {successful}/{len(operations)} successful")
        return result
        
    except Exception as e:
        logger.error(f"Bulk operations failed: {str(e)}")
        raise

# Fallback functions for when Celery is not available
def process_data_conversion_sync(input_file: str, output_format: str, output_file: str, 
                                options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Synchronous version of process_data_conversion."""
    return process_data_conversion(input_file, output_format, output_file, options)

def process_data_download_sync(ticker: str, start_date: str, end_date: str, 
                              source: str = 'yahoo', options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Synchronous version of process_data_download."""
    return process_data_download(ticker, start_date, end_date, source, options)

def process_data_analysis_sync(data_file: str, analysis_type: str, 
                              parameters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Synchronous version of process_data_analysis."""
    return process_data_analysis(data_file, analysis_type, parameters)

def process_file_upload_sync(file_path: str, target_format: str = None, 
                            options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Synchronous version of process_file_upload."""
    return process_file_upload(file_path, target_format, options)

def process_bulk_operations_sync(operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Synchronous version of process_bulk_operations."""
    return process_bulk_operations(operations)
