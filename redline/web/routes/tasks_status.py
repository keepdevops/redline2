"""
Background Task status routes for VarioSync Web GUI
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
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Get task status attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Validate task_id parameter
    if not task_id:
        logger.warning("Get task status request with empty task_id")
        return jsonify({'error': 'task_id is required'}), 400

    if not isinstance(task_id, str):
        logger.error(f"Get task status request with invalid task_id type: {type(task_id)}")
        return jsonify({'error': 'task_id must be a string'}), 400

    if len(task_id) == 0:
        logger.warning("Get task status request with zero-length task_id")
        return jsonify({'error': 'task_id cannot be empty'}), 400

    logger.debug(f"Getting status for task: {task_id}")

    # Get task status (legitimate exception handling for task manager operations)
    try:
        status = task_manager.get_task_status(task_id)
    except Exception as e:
        logger.error(f"Task manager failed to get status for task {task_id}: {str(e)}")
        return jsonify({'error': f'Failed to get task status: {str(e)}'}), 500

    # Validate status was returned
    if status is None:
        logger.warning(f"Task manager returned None status for task: {task_id}")
        return jsonify({'error': 'Task not found', 'task_id': task_id}), 404

    logger.debug(f"Retrieved status for task {task_id}")
    return jsonify(status)

@tasks_status_bp.route('/result/<task_id>', methods=['GET'])
def get_task_result(task_id):
    """Get task result."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Get task result attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Validate task_id parameter
    if not task_id:
        logger.warning("Get task result request with empty task_id")
        return jsonify({'error': 'task_id is required'}), 400

    if not isinstance(task_id, str):
        logger.error(f"Get task result request with invalid task_id type: {type(task_id)}")
        return jsonify({'error': 'task_id must be a string'}), 400

    if len(task_id) == 0:
        logger.warning("Get task result request with zero-length task_id")
        return jsonify({'error': 'task_id cannot be empty'}), 400

    logger.debug(f"Getting result for task: {task_id}")

    # Get task result (legitimate exception handling for task manager operations)
    try:
        result = task_manager.get_task_result(task_id)
    except Exception as e:
        logger.error(f"Task manager failed to get result for task {task_id}: {str(e)}")
        return jsonify({'error': f'Failed to get task result: {str(e)}'}), 500

    logger.debug(f"Retrieved result for task {task_id}")
    return jsonify({'result': result})

@tasks_status_bp.route('/cancel/<task_id>', methods=['POST'])
def cancel_task(task_id):
    """Cancel a running task."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Cancel task attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Validate task_id parameter
    if not task_id:
        logger.warning("Cancel task request with empty task_id")
        return jsonify({'error': 'task_id is required'}), 400

    if not isinstance(task_id, str):
        logger.error(f"Cancel task request with invalid task_id type: {type(task_id)}")
        return jsonify({'error': 'task_id must be a string'}), 400

    if len(task_id) == 0:
        logger.warning("Cancel task request with zero-length task_id")
        return jsonify({'error': 'task_id cannot be empty'}), 400

    logger.info(f"Cancelling task: {task_id}")

    # Cancel task (legitimate exception handling for task manager operations)
    try:
        success = task_manager.cancel_task(task_id)
    except Exception as e:
        logger.error(f"Task manager failed to cancel task {task_id}: {str(e)}")
        return jsonify({'error': f'Failed to cancel task: {str(e)}'}), 500

    # Validate cancellation success
    if not success:
        logger.warning(f"Task manager reported failure cancelling task: {task_id}")
        return jsonify({'error': 'Failed to cancel task', 'task_id': task_id}), 400

    logger.info(f"Task cancelled successfully: {task_id}")
    return jsonify({'message': f'Task {task_id} cancelled successfully'})

@tasks_status_bp.route('/list', methods=['GET'])
def list_tasks():
    """List tasks with optional filtering."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("List tasks attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Validate status_filter (optional)
    status_filter = request.args.get('status')
    if status_filter:
        if not isinstance(status_filter, str):
            logger.warning(f"List tasks status_filter has invalid type: {type(status_filter)}, ignoring")
            status_filter = None
        else:
            valid_statuses = ['pending', 'running', 'completed', 'failed', 'cancelled']
            if status_filter not in valid_statuses:
                logger.warning(f"List tasks with invalid status_filter: {status_filter}")
                return jsonify({
                    'error': f'Invalid status filter: {status_filter}',
                    'valid_statuses': valid_statuses
                }), 400

    # Validate limit parameter
    limit_str = request.args.get('limit', '100')
    try:
        limit = int(limit_str)
    except ValueError:
        logger.warning(f"List tasks with invalid limit: {limit_str}, defaulting to 100")
        limit = 100

    if limit < 1:
        logger.warning(f"List tasks with limit < 1: {limit}, setting to 1")
        limit = 1

    if limit > 1000:
        logger.warning(f"List tasks with limit > 1000: {limit}, clamping to 1000")
        limit = 1000

    logger.debug(f"Listing tasks: status_filter={status_filter}, limit={limit}")

    # List tasks (legitimate exception handling for task manager operations)
    try:
        tasks = task_manager.list_tasks(status_filter=status_filter, limit=limit)
    except Exception as e:
        logger.error(f"Task manager failed to list tasks: {str(e)}")
        return jsonify({'error': f'Failed to list tasks: {str(e)}'}), 500

    # Validate tasks was returned
    if tasks is None:
        logger.warning("Task manager returned None for tasks list")
        tasks = []

    if not isinstance(tasks, list):
        logger.error(f"Task manager returned invalid tasks type: {type(tasks)}")
        return jsonify({'error': 'Invalid tasks data from task manager'}), 500

    logger.info(f"Listed {len(tasks)} tasks (filter={status_filter}, limit={limit})")

    return jsonify({
        'tasks': tasks,
        'total': len(tasks),
        'filter': status_filter,
        'limit': limit
    })

@tasks_status_bp.route('/queue/stats', methods=['GET'])
def get_queue_stats():
    """Get queue statistics."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Get queue stats attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    logger.debug("Getting queue statistics")

    # Get queue stats (legitimate exception handling for task manager operations)
    try:
        stats = task_manager.get_queue_stats()
    except Exception as e:
        logger.error(f"Task manager failed to get queue stats: {str(e)}")
        return jsonify({'error': f'Failed to get queue stats: {str(e)}'}), 500

    # Validate stats was returned
    if stats is None:
        logger.warning("Task manager returned None for queue stats")
        return jsonify({'error': 'No queue stats available'}), 500

    logger.debug("Retrieved queue statistics")
    return jsonify(stats)

@tasks_status_bp.route('/health', methods=['GET'])
def health_check():
    """Check background task system health."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Health check attempted but task manager not available")
        return jsonify({
            'status': 'unavailable',
            'error': 'Background task processing not available'
        }), 503

    logger.debug("Checking task system health")

    # Get health status (legitimate exception handling for task manager operations)
    try:
        health = task_manager.health_check()
    except Exception as e:
        logger.error(f"Task manager health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f'Health check failed: {str(e)}'
        }), 500

    # Validate health was returned
    if health is None:
        logger.warning("Task manager returned None for health check")
        return jsonify({
            'status': 'unknown',
            'error': 'No health data available'
        }), 500

    logger.debug("Health check completed")
    return jsonify(health)

@tasks_status_bp.route('/cleanup', methods=['POST'])
def cleanup_old_tasks():
    """Clean up old completed tasks."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Cleanup tasks attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Get request data (optional body)
    data = request.get_json() or {}

    # Validate data type
    if not isinstance(data, dict):
        logger.warning(f"Cleanup tasks request with invalid data type: {type(data)}, using defaults")
        data = {}

    # Validate days parameter
    days = data.get('days', 7)
    if not isinstance(days, int):
        logger.warning(f"Cleanup tasks days has invalid type: {type(days)}, defaulting to 7")
        days = 7

    if days < 1:
        logger.warning(f"Cleanup tasks with days < 1: {days}, setting to 1")
        days = 1

    if days > 365:
        logger.warning(f"Cleanup tasks with days > 365: {days}, clamping to 365")
        days = 365

    logger.info(f"Cleaning up tasks older than {days} days")

    # Cleanup old tasks (legitimate exception handling for task manager operations)
    try:
        task_manager.cleanup_old_tasks(days=days)
    except Exception as e:
        logger.error(f"Task manager failed to cleanup old tasks: {str(e)}")
        return jsonify({'error': f'Failed to cleanup tasks: {str(e)}'}), 500

    logger.info(f"Successfully cleaned up tasks older than {days} days")

    return jsonify({
        'message': f'Cleaned up tasks older than {days} days',
        'days': days
    })

