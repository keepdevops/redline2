#!/usr/bin/env python3
"""
REDLINE Bulk Operations Tasks
Background tasks for processing multiple operations in bulk.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .conversion_tasks import process_data_conversion_impl
from .download_tasks import process_data_download_impl
from .analysis_tasks import process_data_analysis_impl

logger = logging.getLogger(__name__)


def process_bulk_operations_impl(operations: List[Dict[str, Any]], 
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
                    result = process_data_conversion_impl(
                        input_file=op_data.get('input_file'),
                        output_format=op_data.get('output_format'),
                        output_file=op_data.get('output_file'),
                        options=options
                    )
                    results.append({'operation': i+1, 'type': op_type, 'status': 'success', 'result': result})
                elif op_type == 'download':
                    # Use data download
                    result = process_data_download_impl(
                        ticker=op_data.get('ticker'),
                        start_date=op_data.get('start_date'),
                        end_date=op_data.get('end_date'),
                        source=op_data.get('source', 'yahoo'),
                        options=options
                    )
                    results.append({'operation': i+1, 'type': op_type, 'status': 'success', 'result': result})
                elif op_type == 'analyze':
                    # Use data analysis
                    result = process_data_analysis_impl(
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

