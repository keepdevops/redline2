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

def _process_data_conversion_impl(input_file: str, output_format: str, output_file: str, 
                                  options: Dict[str, Any] = None, progress_callback=None) -> Dict[str, Any]:
    """Internal implementation of data conversion."""
    try:
        logger.info(f"Starting data conversion: {input_file} -> {output_format}")
        
        # Update progress if callback provided
        if progress_callback:
            progress_callback({'step': 'loading_data', 'progress': 10})
        
        # Load data
        converter = FormatConverter()
        format_type = converter.detect_format_from_extension(input_file)
        data = converter.load_file_by_type(input_file, format_type)
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Invalid data format")
        
        if progress_callback:
            progress_callback({'step': 'converting_data', 'progress': 50})
        
        # Convert and save
        converter.save_file_by_type(data, output_file, output_format)
        
        if progress_callback:
            progress_callback({'step': 'finalizing', 'progress': 90})
        
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

# Create the appropriate function based on Celery availability
if CELERY_AVAILABLE:
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_data_conversion')
    def process_data_conversion(self, input_file: str, output_format: str, output_file: str, 
                               options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data format conversion in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return _process_data_conversion_impl(input_file, output_format, output_file, options, progress_callback)
else:
    def process_data_conversion(input_file: str, output_format: str, output_file: str, 
                               options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data format conversion in background."""
        return _process_data_conversion_impl(input_file, output_format, output_file, options)

# Data download implementation
def _process_data_download_impl(ticker: str, start_date: str, end_date: str, 
                               source: str = 'yahoo', options: Dict[str, Any] = None, 
                               progress_callback=None) -> Dict[str, Any]:
    """Internal implementation of data download."""
    try:
        logger.info(f"Starting data download: {ticker} from {source}")
        
        if progress_callback:
            progress_callback({'step': 'initializing', 'progress': 5})
        
        # Import downloaders
        downloader = None
        if source == 'yahoo':
            from redline.downloaders.yahoo_downloader import YahooDownloader
            downloader = YahooDownloader()
        elif source == 'stooq':
            from redline.downloaders.stooq_downloader import StooqDownloader
            downloader = StooqDownloader()
        elif source == 'alpha_vantage':
            from redline.downloaders.alpha_vantage_downloader import AlphaVantageDownloader
            downloader = AlphaVantageDownloader()
        elif source == 'massive':
            from redline.downloaders.massive_downloader import MassiveDownloader
            import os
            api_key = options.get('api_key') if options else None
            api_key = api_key or os.environ.get('MASSIVE_API_KEY')
            if not api_key:
                raise ValueError("Massive.com API key is required")
            downloader = MassiveDownloader(api_key=api_key)
        else:
            raise ValueError(f"Unsupported source: {source}")
        
        if progress_callback:
            progress_callback({'step': 'downloading', 'progress': 30})
        
        # Download data
        df = downloader.download_single_ticker(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
        
        if progress_callback:
            progress_callback({'step': 'saving', 'progress': 80})
        
        # Save to file
        filename = f"{ticker}_{source}_{start_date}_to_{end_date}.csv"
        downloaded_dir = "data/downloaded"
        os.makedirs(downloaded_dir, exist_ok=True)
        filepath = os.path.join(downloaded_dir, filename)
        
        df.to_csv(filepath, index=True)
        
        if progress_callback:
            progress_callback({'step': 'completed', 'progress': 100})
        
        result = {
            'status': 'success',
            'ticker': ticker,
            'source': source,
            'filename': filename,
            'filepath': filepath,
            'records': len(df),
            'columns': list(df.columns),
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Data download completed: {len(df)} records for {ticker}")
        return result
        
    except Exception as e:
        logger.error(f"Data download failed: {str(e)}")
        raise

# Data analysis implementation
def _process_data_analysis_impl(data_file: str, analysis_type: str, 
                              options: Dict[str, Any] = None, progress_callback=None) -> Dict[str, Any]:
    """Internal implementation of data analysis."""
    try:
        logger.info(f"Starting data analysis: {data_file} - {analysis_type}")
        
        if progress_callback:
            progress_callback({'step': 'loading_data', 'progress': 10})
        
        # Load data
        loader = DataLoader()
        data_path = os.path.join('data', data_file)
        
        if not os.path.exists(data_path):
            data_path = os.path.join('data', 'downloaded', data_file)
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        df = loader.load_file_by_extension(data_path)
        
        if progress_callback:
            progress_callback({'step': 'analyzing', 'progress': 50})
        
        # Perform analysis based on type
        analysis_result = {}
        
        if analysis_type == 'basic' or analysis_type == 'statistical':
            analysis_result = df.describe().to_dict()
        elif analysis_type == 'financial':
            # Financial-specific analysis
            if 'close' in df.columns:
                analysis_result['close_stats'] = {
                    'mean': float(df['close'].mean()),
                    'std': float(df['close'].std()),
                    'min': float(df['close'].min()),
                    'max': float(df['close'].max())
                }
            if 'volume' in df.columns:
                analysis_result['volume_stats'] = {
                    'mean': float(df['volume'].mean()),
                    'total': float(df['volume'].sum())
                }
        elif analysis_type == 'correlation':
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 1:
                analysis_result = df[numeric_cols].corr().to_dict()
        else:
            analysis_result = {'error': f'Unknown analysis type: {analysis_type}'}
        
        if progress_callback:
            progress_callback({'step': 'completed', 'progress': 100})
        
        result = {
            'status': 'success',
            'data_file': data_file,
            'analysis_type': analysis_type,
            'result': analysis_result,
            'data_shape': {'rows': len(df), 'columns': len(df.columns)},
            'columns': list(df.columns),
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Data analysis completed: {analysis_type}")
        return result
        
    except Exception as e:
        logger.error(f"Data analysis failed: {str(e)}")
        raise

# File upload implementation
def _process_file_upload_impl(file_path: str, target_format: str = None, 
                             options: Dict[str, Any] = None, progress_callback=None) -> Dict[str, Any]:
    """Internal implementation of file upload processing."""
    try:
        logger.info(f"Processing file upload: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if progress_callback:
            progress_callback({'step': 'loading', 'progress': 10})
        
        # Load the file
        loader = DataLoader()
        df = loader.load_file_by_extension(file_path)
        
        if progress_callback:
            progress_callback({'step': 'processing', 'progress': 50})
        
        # Convert to target format if specified
        if target_format:
            converter = FormatConverter()
            
            output_path = file_path.rsplit('.', 1)[0] + f'.{target_format}'
            converter.save_file_by_type(df, output_path, target_format)
            
            if progress_callback:
                progress_callback({'step': 'converted', 'progress': 90})
            
            result = {
                'status': 'success',
                'original_file': file_path,
                'converted_file': output_path,
                'target_format': target_format,
                'rows': len(df),
                'columns': list(df.columns),
                'completed_at': datetime.utcnow().isoformat()
            }
        else:
            result = {
                'status': 'success',
                'file_path': file_path,
                'rows': len(df),
                'columns': list(df.columns),
                'completed_at': datetime.utcnow().isoformat()
            }
        
        if progress_callback:
            progress_callback({'step': 'completed', 'progress': 100})
        
        logger.info(f"File upload processing completed: {file_path}")
        return result
        
    except Exception as e:
        logger.error(f"File upload processing failed: {str(e)}")
        raise

# Bulk operations implementation
def _process_bulk_operations_impl(operations: List[Dict[str, Any]], 
                                  options: Dict[str, Any] = None, progress_callback=None) -> Dict[str, Any]:
    """Internal implementation of bulk operations."""
    try:
        logger.info(f"Processing bulk operations: {len(operations)} operations")
        
        results = []
        total = len(operations)
        
        for i, operation in enumerate(operations):
            op_type = operation.get('type')
            op_data = operation.get('data', {})
            
            if progress_callback:
                progress = int((i / total) * 100)
                progress_callback({'step': f'operation_{i+1}', 'progress': progress, 'current': i+1, 'total': total})
            
            try:
                if op_type == 'convert':
                    # Use data conversion
                    result = _process_data_conversion_impl(
                        input_file=op_data.get('input_file'),
                        output_format=op_data.get('output_format'),
                        output_file=op_data.get('output_file'),
                        options=options
                    )
                    results.append({'operation': i+1, 'type': op_type, 'status': 'success', 'result': result})
                elif op_type == 'download':
                    # Use data download
                    result = _process_data_download_impl(
                        ticker=op_data.get('ticker'),
                        start_date=op_data.get('start_date'),
                        end_date=op_data.get('end_date'),
                        source=op_data.get('source', 'yahoo'),
                        options=options
                    )
                    results.append({'operation': i+1, 'type': op_type, 'status': 'success', 'result': result})
                elif op_type == 'analyze':
                    # Use data analysis
                    result = _process_data_analysis_impl(
                        data_file=op_data.get('data_file'),
                        analysis_type=op_data.get('analysis_type', 'basic'),
                        options=options
                    )
                    results.append({'operation': i+1, 'type': op_type, 'status': 'success', 'result': result})
                else:
                    results.append({'operation': i+1, 'type': op_type, 'status': 'error', 'error': f'Unknown operation type: {op_type}'})
            except Exception as e:
                results.append({'operation': i+1, 'type': op_type, 'status': 'error', 'error': str(e)})
        
        if progress_callback:
            progress_callback({'step': 'completed', 'progress': 100, 'current': total, 'total': total})
        
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = total - successful
        
        result = {
            'status': 'success',
            'total_operations': total,
            'successful': successful,
            'failed': failed,
            'results': results,
            'completed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Bulk operations completed: {successful}/{total} successful")
        return result
        
    except Exception as e:
        logger.error(f"Bulk operations failed: {str(e)}")
        raise

# Create Celery tasks or regular functions based on availability
if CELERY_AVAILABLE:
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_data_download')
    def process_data_download(self, ticker: str, start_date: str, end_date: str, 
                             source: str = 'yahoo', options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data download in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return _process_data_download_impl(ticker, start_date, end_date, source, options, progress_callback)
    
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_data_analysis')
    def process_data_analysis(self, data_file: str, analysis_type: str, 
                             options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data analysis in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return _process_data_analysis_impl(data_file, analysis_type, options, progress_callback)
    
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_file_upload')
    def process_file_upload(self, file_path: str, target_format: str = None, 
                           options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process file upload in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return _process_file_upload_impl(file_path, target_format, options, progress_callback)
    
    @celery_app.task(bind=True, base=BaseTask, name='redline.background.tasks.process_bulk_operations')
    def process_bulk_operations(self, operations: List[Dict[str, Any]], 
                              options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process bulk operations in background."""
        def progress_callback(meta):
            self.update_state(state='PROGRESS', meta=meta)
        return _process_bulk_operations_impl(operations, options, progress_callback)
else:
    def process_data_download(ticker: str, start_date: str, end_date: str, 
                             source: str = 'yahoo', options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data download in background."""
        return _process_data_download_impl(ticker, start_date, end_date, source, options)
    
    def process_data_analysis(data_file: str, analysis_type: str, 
                             options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process data analysis in background."""
        return _process_data_analysis_impl(data_file, analysis_type, options)
    
    def process_file_upload(file_path: str, target_format: str = None, 
                           options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process file upload in background."""
        return _process_file_upload_impl(file_path, target_format, options)
    
    def process_bulk_operations(operations: List[Dict[str, Any]], 
                              options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process bulk operations in background."""
        return _process_bulk_operations_impl(operations, options)
