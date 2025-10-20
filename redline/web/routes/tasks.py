"""
Background Task routes for REDLINE Web GUI
Handles asynchronous task processing and monitoring
"""

from flask import Blueprint, request, jsonify
import logging
from ...background.task_manager import task_manager

tasks_bp = Blueprint('tasks', __name__)
logger = logging.getLogger(__name__)

@tasks_bp.route('/submit', methods=['POST'])
def submit_task():
    """Submit a background task."""
    try:
        data = request.get_json()
        task_name = data.get('task_name')
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        queue = data.get('queue')
        priority = data.get('priority', 5)
        
        if not task_name:
            return jsonify({'error': 'task_name is required'}), 400
        
        # Validate task name
        valid_tasks = [
            'process_data_conversion',
            'process_data_download',
            'process_data_analysis',
            'process_file_upload',
            'process_bulk_operations'
        ]
        
        if task_name not in valid_tasks:
            return jsonify({'error': f'Invalid task name: {task_name}'}), 400
        
        # Submit task
        task_id = task_manager.submit_task(
            task_name=task_name,
            args=tuple(args),
            kwargs=kwargs,
            queue=queue,
            priority=priority
        )
        
        return jsonify({
            'task_id': task_id,
            'status': 'submitted',
            'message': f'Task {task_name} submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get task status and result."""
    try:
        status = task_manager.get_task_status(task_id)
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/result/<task_id>', methods=['GET'])
def get_task_result(task_id):
    """Get task result."""
    try:
        result = task_manager.get_task_result(task_id)
        return jsonify({'result': result})
        
    except Exception as e:
        logger.error(f"Error getting task result: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/cancel/<task_id>', methods=['POST'])
def cancel_task(task_id):
    """Cancel a running task."""
    try:
        success = task_manager.cancel_task(task_id)
        
        if success:
            return jsonify({'message': f'Task {task_id} cancelled successfully'})
        else:
            return jsonify({'error': 'Failed to cancel task'}), 400
            
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/list', methods=['GET'])
def list_tasks():
    """List tasks with optional filtering."""
    try:
        status_filter = request.args.get('status')
        limit = int(request.args.get('limit', 100))
        
        tasks = task_manager.list_tasks(status_filter=status_filter, limit=limit)
        
        return jsonify({
            'tasks': tasks,
            'total': len(tasks),
            'filter': status_filter
        })
        
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/queue/stats', methods=['GET'])
def get_queue_stats():
    """Get queue statistics."""
    try:
        stats = task_manager.get_queue_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting queue stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/health', methods=['GET'])
def health_check():
    """Check background task system health."""
    try:
        health = task_manager.health_check()
        return jsonify(health)
        
    except Exception as e:
        logger.error(f"Error checking health: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/cleanup', methods=['POST'])
def cleanup_old_tasks():
    """Clean up old completed tasks."""
    try:
        data = request.get_json() or {}
        days = data.get('days', 7)
        
        task_manager.cleanup_old_tasks(days=days)
        
        return jsonify({
            'message': f'Cleaned up tasks older than {days} days'
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Convenience endpoints for common tasks

@tasks_bp.route('/convert', methods=['POST'])
def submit_conversion_task():
    """Submit a data conversion task."""
    try:
        data = request.get_json()
        
        required_fields = ['input_file', 'output_format', 'output_file']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        task_id = task_manager.submit_task(
            task_name='process_data_conversion',
            args=(),
            kwargs={
                'input_file': data['input_file'],
                'output_format': data['output_format'],
                'output_file': data['output_file'],
                'options': data.get('options', {})
            },
            priority=data.get('priority', 5)
        )
        
        return jsonify({
            'task_id': task_id,
            'status': 'submitted',
            'message': 'Data conversion task submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting conversion task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/download', methods=['POST'])
def submit_download_task():
    """Submit a data download task."""
    try:
        data = request.get_json()
        
        required_fields = ['ticker', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        task_id = task_manager.submit_task(
            task_name='process_data_download',
            args=(),
            kwargs={
                'ticker': data['ticker'],
                'start_date': data['start_date'],
                'end_date': data['end_date'],
                'source': data.get('source', 'yahoo'),
                'options': data.get('options', {})
            },
            priority=data.get('priority', 5)
        )
        
        return jsonify({
            'task_id': task_id,
            'status': 'submitted',
            'message': 'Data download task submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting download task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/analyze', methods=['POST'])
def submit_analysis_task():
    """Submit a data analysis task."""
    try:
        data = request.get_json()
        
        required_fields = ['data_file', 'analysis_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        task_id = task_manager.submit_task(
            task_name='process_data_analysis',
            args=(),
            kwargs={
                'data_file': data['data_file'],
                'analysis_type': data['analysis_type'],
                'parameters': data.get('parameters', {})
            },
            priority=data.get('priority', 5)
        )
        
        return jsonify({
            'task_id': task_id,
            'status': 'submitted',
            'message': 'Data analysis task submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting analysis task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/upload', methods=['POST'])
def submit_upload_task():
    """Submit a file upload processing task."""
    try:
        data = request.get_json()
        
        required_fields = ['file_path']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        task_id = task_manager.submit_task(
            task_name='process_file_upload',
            args=(),
            kwargs={
                'file_path': data['file_path'],
                'target_format': data.get('target_format'),
                'options': data.get('options', {})
            },
            priority=data.get('priority', 5)
        )
        
        return jsonify({
            'task_id': task_id,
            'status': 'submitted',
            'message': 'File upload task submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting upload task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/bulk', methods=['POST'])
def submit_bulk_task():
    """Submit a bulk operations task."""
    try:
        data = request.get_json()
        
        if 'operations' not in data:
            return jsonify({'error': 'operations is required'}), 400
        
        operations = data['operations']
        if not isinstance(operations, list) or len(operations) == 0:
            return jsonify({'error': 'operations must be a non-empty list'}), 400
        
        task_id = task_manager.submit_task(
            task_name='process_bulk_operations',
            args=(),
            kwargs={'operations': operations},
            priority=data.get('priority', 5)
        )
        
        return jsonify({
            'task_id': task_id,
            'status': 'submitted',
            'message': f'Bulk operations task submitted successfully ({len(operations)} operations)'
        })
        
    except Exception as e:
        logger.error(f"Error submitting bulk task: {str(e)}")
        return jsonify({'error': str(e)}), 500
