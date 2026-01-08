"""
Background Task submission routes for VarioSync Web GUI
Handles submitting asynchronous tasks
"""

from flask import Blueprint, request, jsonify
import logging

try:
    from ...background.task_manager import task_manager
    TASK_MANAGER_AVAILABLE = True
except ImportError:
    task_manager = None
    TASK_MANAGER_AVAILABLE = False

tasks_submit_bp = Blueprint('tasks_submit', __name__)
logger = logging.getLogger(__name__)

@tasks_submit_bp.route('/submit', methods=['POST'])
def submit_task():
    """Submit a background task."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Task submission attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Submit task request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Submit task request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate task_name
    task_name = data.get('task_name')

    if not task_name:
        logger.warning("Submit task request missing task_name field")
        return jsonify({'error': 'task_name is required'}), 400

    if not isinstance(task_name, str):
        logger.error(f"Submit task request task_name has invalid type: {type(task_name)}")
        return jsonify({'error': 'task_name must be a string'}), 400

    # Validate task name against allowed list
    valid_tasks = [
        'process_data_conversion',
        'process_data_download',
        'process_data_analysis',
        'process_file_upload',
        'process_bulk_operations'
    ]

    if task_name not in valid_tasks:
        logger.warning(f"Submit task request with invalid task_name: {task_name}")
        return jsonify({
            'error': f'Invalid task name: {task_name}',
            'valid_tasks': valid_tasks
        }), 400

    # Validate args
    args = data.get('args', [])
    if not isinstance(args, list):
        logger.warning(f"Submit task request args has invalid type: {type(args)}, defaulting to []")
        args = []

    # Validate kwargs
    kwargs = data.get('kwargs', {})
    if not isinstance(kwargs, dict):
        logger.warning(f"Submit task request kwargs has invalid type: {type(kwargs)}, defaulting to {{}}")
        kwargs = {}

    # Validate queue (optional)
    queue = data.get('queue')
    if queue and not isinstance(queue, str):
        logger.warning(f"Submit task request queue has invalid type: {type(queue)}, ignoring")
        queue = None

    # Validate priority
    priority = data.get('priority', 5)
    if not isinstance(priority, int):
        logger.warning(f"Submit task request priority has invalid type: {type(priority)}, defaulting to 5")
        priority = 5

    if priority < 1 or priority > 10:
        logger.warning(f"Submit task request priority out of range: {priority}, clamping to 1-10")
        priority = max(1, min(10, priority))

    logger.info(f"Processing task submission: task_name={task_name}, priority={priority}, queue={queue}")

    # Submit task (legitimate exception handling for task manager operations)
    try:
        task_id = task_manager.submit_task(
            task_name=task_name,
            args=tuple(args),
            kwargs=kwargs,
            queue=queue,
            priority=priority
        )
    except Exception as e:
        logger.error(f"Task manager failed to submit task {task_name}: {str(e)}")
        return jsonify({'error': f'Failed to submit task: {str(e)}'}), 500

    # Validate task_id was returned
    if not task_id:
        logger.error(f"Task manager returned invalid task_id for {task_name}")
        return jsonify({'error': 'Failed to get task ID from task manager'}), 500

    logger.info(f"Task submitted successfully: task_id={task_id}, task_name={task_name}")

    return jsonify({
        'task_id': task_id,
        'status': 'submitted',
        'message': f'Task {task_name} submitted successfully'
    })

@tasks_submit_bp.route('/convert', methods=['POST'])
def submit_conversion_task():
    """Submit a data conversion task."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Conversion task submission attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Submit conversion task request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Submit conversion task request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate required fields
    required_fields = ['input_file', 'output_format', 'output_file']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Submit conversion task request missing {field} field")
            return jsonify({'error': f'{field} is required'}), 400

        if not isinstance(data[field], str):
            logger.error(f"Submit conversion task {field} has invalid type: {type(data[field])}")
            return jsonify({'error': f'{field} must be a string'}), 400

        if len(data[field]) == 0:
            logger.warning(f"Submit conversion task request with empty {field}")
            return jsonify({'error': f'{field} cannot be empty'}), 400

    # Security check: prevent path traversal
    for field in ['input_file', 'output_file']:
        if '..' in data[field]:
            logger.warning(f"Submit conversion task with path traversal in {field}: {data[field]}")
            return jsonify({'error': f'Invalid {field} format (path traversal not allowed)'}), 400

    # Validate output_format
    valid_formats = ['csv', 'json', 'parquet', 'feather', 'excel', 'txt', 'duckdb']
    if data['output_format'] not in valid_formats:
        logger.warning(f"Submit conversion task with invalid output_format: {data['output_format']}")
        return jsonify({
            'error': f'Invalid output_format: {data["output_format"]}',
            'valid_formats': valid_formats
        }), 400

    # Validate options (optional)
    options = data.get('options', {})
    if not isinstance(options, dict):
        logger.warning(f"Submit conversion task options has invalid type: {type(options)}, defaulting to {{}}")
        options = {}

    # Validate priority
    priority = data.get('priority', 5)
    if not isinstance(priority, int):
        logger.warning(f"Submit conversion task priority has invalid type: {type(priority)}, defaulting to 5")
        priority = 5

    priority = max(1, min(10, priority))

    logger.info(f"Processing conversion task submission: {data['input_file']} -> {data['output_file']} ({data['output_format']})")

    # Submit task (legitimate exception handling for task manager operations)
    try:
        task_id = task_manager.submit_task(
            task_name='process_data_conversion',
            args=(),
            kwargs={
                'input_file': data['input_file'],
                'output_format': data['output_format'],
                'output_file': data['output_file'],
                'options': options
            },
            priority=priority
        )
    except Exception as e:
        logger.error(f"Task manager failed to submit conversion task: {str(e)}")
        return jsonify({'error': f'Failed to submit conversion task: {str(e)}'}), 500

    # Validate task_id was returned
    if not task_id:
        logger.error("Task manager returned invalid task_id for conversion task")
        return jsonify({'error': 'Failed to get task ID from task manager'}), 500

    logger.info(f"Conversion task submitted successfully: task_id={task_id}")

    return jsonify({
        'task_id': task_id,
        'status': 'submitted',
        'message': 'Data conversion task submitted successfully'
    })

@tasks_submit_bp.route('/download', methods=['POST'])
def submit_download_task():
    """Submit a data download task."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Download task submission attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Submit download task request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Submit download task request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate required fields
    required_fields = ['ticker', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Submit download task request missing {field} field")
            return jsonify({'error': f'{field} is required'}), 400

        if not isinstance(data[field], str):
            logger.error(f"Submit download task {field} has invalid type: {type(data[field])}")
            return jsonify({'error': f'{field} must be a string'}), 400

        if len(data[field]) == 0:
            logger.warning(f"Submit download task request with empty {field}")
            return jsonify({'error': f'{field} cannot be empty'}), 400

    # Validate and normalize ticker
    ticker = data['ticker'].strip().upper()
    if len(ticker) > 20:
        logger.warning(f"Submit download task with oversized ticker: {ticker}")
        return jsonify({'error': 'Ticker too long (max 20 characters)'}), 400

    # Validate source
    source = data.get('source', 'yahoo')
    if not isinstance(source, str):
        logger.warning(f"Submit download task source has invalid type: {type(source)}, defaulting to 'yahoo'")
        source = 'yahoo'

    valid_sources = ['yahoo', 'stooq', 'alpha_vantage', 'finnhub', 'massive']
    if source not in valid_sources:
        logger.warning(f"Submit download task with invalid source: {source}")
        return jsonify({
            'error': f'Invalid source: {source}',
            'valid_sources': valid_sources
        }), 400

    # Validate options (optional)
    options = data.get('options', {})
    if not isinstance(options, dict):
        logger.warning(f"Submit download task options has invalid type: {type(options)}, defaulting to {{}}")
        options = {}

    # Validate priority
    priority = data.get('priority', 5)
    if not isinstance(priority, int):
        logger.warning(f"Submit download task priority has invalid type: {type(priority)}, defaulting to 5")
        priority = 5

    priority = max(1, min(10, priority))

    logger.info(f"Processing download task submission: ticker={ticker}, source={source}, dates={data['start_date']} to {data['end_date']}")

    # Submit task (legitimate exception handling for task manager operations)
    try:
        task_id = task_manager.submit_task(
            task_name='process_data_download',
            args=(),
            kwargs={
                'ticker': ticker,
                'start_date': data['start_date'],
                'end_date': data['end_date'],
                'source': source,
                'options': options
            },
            priority=priority
        )
    except Exception as e:
        logger.error(f"Task manager failed to submit download task: {str(e)}")
        return jsonify({'error': f'Failed to submit download task: {str(e)}'}), 500

    # Validate task_id was returned
    if not task_id:
        logger.error("Task manager returned invalid task_id for download task")
        return jsonify({'error': 'Failed to get task ID from task manager'}), 500

    logger.info(f"Download task submitted successfully: task_id={task_id}, ticker={ticker}")

    return jsonify({
        'task_id': task_id,
        'status': 'submitted',
        'message': 'Data download task submitted successfully'
    })

@tasks_submit_bp.route('/analyze', methods=['POST'])
def submit_analysis_task():
    """Submit a data analysis task."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Analysis task submission attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Submit analysis task request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Submit analysis task request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate required fields
    required_fields = ['data_file', 'analysis_type']
    for field in required_fields:
        if field not in data:
            logger.warning(f"Submit analysis task request missing {field} field")
            return jsonify({'error': f'{field} is required'}), 400

        if not isinstance(data[field], str):
            logger.error(f"Submit analysis task {field} has invalid type: {type(data[field])}")
            return jsonify({'error': f'{field} must be a string'}), 400

        if len(data[field]) == 0:
            logger.warning(f"Submit analysis task request with empty {field}")
            return jsonify({'error': f'{field} cannot be empty'}), 400

    # Security check: prevent path traversal in data_file
    if '..' in data['data_file']:
        logger.warning(f"Submit analysis task with path traversal in data_file: {data['data_file']}")
        return jsonify({'error': 'Invalid data_file format (path traversal not allowed)'}), 400

    # Validate analysis_type
    valid_analysis_types = ['financial', 'statistical', 'correlation', 'ml', 'visualization']
    if data['analysis_type'] not in valid_analysis_types:
        logger.warning(f"Submit analysis task with invalid analysis_type: {data['analysis_type']}")
        return jsonify({
            'error': f'Invalid analysis_type: {data["analysis_type"]}',
            'valid_types': valid_analysis_types
        }), 400

    # Validate parameters (optional)
    parameters = data.get('parameters', {})
    if not isinstance(parameters, dict):
        logger.warning(f"Submit analysis task parameters has invalid type: {type(parameters)}, defaulting to {{}}")
        parameters = {}

    # Validate priority
    priority = data.get('priority', 5)
    if not isinstance(priority, int):
        logger.warning(f"Submit analysis task priority has invalid type: {type(priority)}, defaulting to 5")
        priority = 5

    priority = max(1, min(10, priority))

    logger.info(f"Processing analysis task submission: data_file={data['data_file']}, analysis_type={data['analysis_type']}")

    # Submit task (legitimate exception handling for task manager operations)
    try:
        task_id = task_manager.submit_task(
            task_name='process_data_analysis',
            args=(),
            kwargs={
                'data_file': data['data_file'],
                'analysis_type': data['analysis_type'],
                'parameters': parameters
            },
            priority=priority
        )
    except Exception as e:
        logger.error(f"Task manager failed to submit analysis task: {str(e)}")
        return jsonify({'error': f'Failed to submit analysis task: {str(e)}'}), 500

    # Validate task_id was returned
    if not task_id:
        logger.error("Task manager returned invalid task_id for analysis task")
        return jsonify({'error': 'Failed to get task ID from task manager'}), 500

    logger.info(f"Analysis task submitted successfully: task_id={task_id}, analysis_type={data['analysis_type']}")

    return jsonify({
        'task_id': task_id,
        'status': 'submitted',
        'message': 'Data analysis task submitted successfully'
    })

@tasks_submit_bp.route('/upload', methods=['POST'])
def submit_upload_task():
    """Submit a file upload processing task."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Upload task submission attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Submit upload task request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Submit upload task request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate required field
    if 'file_path' not in data:
        logger.warning("Submit upload task request missing file_path field")
        return jsonify({'error': 'file_path is required'}), 400

    if not isinstance(data['file_path'], str):
        logger.error(f"Submit upload task file_path has invalid type: {type(data['file_path'])}")
        return jsonify({'error': 'file_path must be a string'}), 400

    if len(data['file_path']) == 0:
        logger.warning("Submit upload task request with empty file_path")
        return jsonify({'error': 'file_path cannot be empty'}), 400

    # Security check: prevent path traversal
    if '..' in data['file_path']:
        logger.warning(f"Submit upload task with path traversal in file_path: {data['file_path']}")
        return jsonify({'error': 'Invalid file_path format (path traversal not allowed)'}), 400

    # Validate target_format (optional)
    target_format = data.get('target_format')
    if target_format:
        if not isinstance(target_format, str):
            logger.warning(f"Submit upload task target_format has invalid type: {type(target_format)}, ignoring")
            target_format = None
        else:
            valid_formats = ['csv', 'json', 'parquet', 'feather', 'excel', 'txt', 'duckdb']
            if target_format not in valid_formats:
                logger.warning(f"Submit upload task with invalid target_format: {target_format}")
                return jsonify({
                    'error': f'Invalid target_format: {target_format}',
                    'valid_formats': valid_formats
                }), 400

    # Validate options (optional)
    options = data.get('options', {})
    if not isinstance(options, dict):
        logger.warning(f"Submit upload task options has invalid type: {type(options)}, defaulting to {{}}")
        options = {}

    # Validate priority
    priority = data.get('priority', 5)
    if not isinstance(priority, int):
        logger.warning(f"Submit upload task priority has invalid type: {type(priority)}, defaulting to 5")
        priority = 5

    priority = max(1, min(10, priority))

    logger.info(f"Processing upload task submission: file_path={data['file_path']}, target_format={target_format}")

    # Submit task (legitimate exception handling for task manager operations)
    try:
        task_id = task_manager.submit_task(
            task_name='process_file_upload',
            args=(),
            kwargs={
                'file_path': data['file_path'],
                'target_format': target_format,
                'options': options
            },
            priority=priority
        )
    except Exception as e:
        logger.error(f"Task manager failed to submit upload task: {str(e)}")
        return jsonify({'error': f'Failed to submit upload task: {str(e)}'}), 500

    # Validate task_id was returned
    if not task_id:
        logger.error("Task manager returned invalid task_id for upload task")
        return jsonify({'error': 'Failed to get task ID from task manager'}), 500

    logger.info(f"Upload task submitted successfully: task_id={task_id}")

    return jsonify({
        'task_id': task_id,
        'status': 'submitted',
        'message': 'File upload task submitted successfully'
    })

@tasks_submit_bp.route('/bulk', methods=['POST'])
def submit_bulk_task():
    """Submit a bulk operations task."""
    # Validate task manager availability
    if not TASK_MANAGER_AVAILABLE:
        logger.error("Bulk task submission attempted but task manager not available")
        return jsonify({'error': 'Background task processing not available'}), 503

    # Get request data
    data = request.get_json()

    if not data:
        logger.warning("Submit bulk task request with empty body")
        return jsonify({'error': 'Request body is required'}), 400

    if not isinstance(data, dict):
        logger.error(f"Submit bulk task request with invalid data type: {type(data)}")
        return jsonify({'error': 'Request body must be JSON object'}), 400

    # Validate operations field
    if 'operations' not in data:
        logger.warning("Submit bulk task request missing operations field")
        return jsonify({'error': 'operations is required'}), 400

    operations = data['operations']

    if not isinstance(operations, list):
        logger.error(f"Submit bulk task operations has invalid type: {type(operations)}")
        return jsonify({'error': 'operations must be an array'}), 400

    if len(operations) == 0:
        logger.warning("Submit bulk task request with empty operations array")
        return jsonify({'error': 'operations array cannot be empty'}), 400

    # Validate operations count limit
    max_operations = 1000
    if len(operations) > max_operations:
        logger.warning(f"Submit bulk task with too many operations: {len(operations)}")
        return jsonify({
            'error': f'Too many operations. Maximum {max_operations} operations per bulk task',
            'operations_count': len(operations)
        }), 400

    # Validate each operation is a dict
    invalid_operations = 0
    for idx, op in enumerate(operations):
        if not isinstance(op, dict):
            logger.warning(f"Submit bulk task operation at index {idx} has invalid type: {type(op)}")
            invalid_operations += 1

    if invalid_operations > 0:
        logger.warning(f"Submit bulk task has {invalid_operations} invalid operations")
        return jsonify({
            'error': f'{invalid_operations} operation(s) have invalid type (must be objects)',
            'total_operations': len(operations),
            'invalid_operations': invalid_operations
        }), 400

    # Validate priority
    priority = data.get('priority', 5)
    if not isinstance(priority, int):
        logger.warning(f"Submit bulk task priority has invalid type: {type(priority)}, defaulting to 5")
        priority = 5

    priority = max(1, min(10, priority))

    logger.info(f"Processing bulk task submission: {len(operations)} operations, priority={priority}")

    # Submit task (legitimate exception handling for task manager operations)
    try:
        task_id = task_manager.submit_task(
            task_name='process_bulk_operations',
            args=(),
            kwargs={'operations': operations},
            priority=priority
        )
    except Exception as e:
        logger.error(f"Task manager failed to submit bulk task: {str(e)}")
        return jsonify({'error': f'Failed to submit bulk task: {str(e)}'}), 500

    # Validate task_id was returned
    if not task_id:
        logger.error("Task manager returned invalid task_id for bulk task")
        return jsonify({'error': 'Failed to get task ID from task manager'}), 500

    logger.info(f"Bulk task submitted successfully: task_id={task_id}, operations={len(operations)}")

    return jsonify({
        'task_id': task_id,
        'status': 'submitted',
        'message': f'Bulk operations task submitted successfully ({len(operations)} operations)'
    })

