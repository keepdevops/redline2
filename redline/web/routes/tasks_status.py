"""
Background Task status routes for REDLINE Web GUI
Handles task status, results, and management
"""

from flask import Blueprint, request, jsonify
import logging

try:
    from ...background.task_manager import task_manager
    TASK_MANAGER_AVAILABLE = True
except ImportError:
    task_manager = None
    TASK_MANAGER_AVAILABLE = False

tasks_status_bp = Blueprint('tasks_status', __name__)
logger = logging.getLogger(__name__)

@tasks_status_bp.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get task status and result."""
    try:
        status = task_manager.get_task_status(task_id)
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_status_bp.route('/result/<task_id>', methods=['GET'])
def get_task_result(task_id):
    """Get task result."""
    try:
        result = task_manager.get_task_result(task_id)
        return jsonify({'result': result})
        
    except Exception as e:
        logger.error(f"Error getting task result: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_status_bp.route('/cancel/<task_id>', methods=['POST'])
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

@tasks_status_bp.route('/list', methods=['GET'])
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

@tasks_status_bp.route('/queue/stats', methods=['GET'])
def get_queue_stats():
    """Get queue statistics."""
    try:
        stats = task_manager.get_queue_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting queue stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_status_bp.route('/health', methods=['GET'])
def health_check():
    """Check background task system health."""
    try:
        health = task_manager.health_check()
        return jsonify(health)
        
    except Exception as e:
        logger.error(f"Error checking health: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_status_bp.route('/cleanup', methods=['POST'])
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

