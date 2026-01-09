"""
API routes for database operations.
Handles database index management.
"""

from flask import Blueprint, request, jsonify
import logging

api_database_bp = Blueprint('api_database', __name__)
logger = logging.getLogger(__name__)


@api_database_bp.route('/database/indexes', methods=['GET', 'POST', 'DELETE'])
def manage_indexes():
    """Manage database indexes for performance optimization."""
    # Pre-validation with if-else
    table_name = request.args.get('table', 'tickers_data')

    if not table_name:
        logger.error("Table name is empty")
        return jsonify({'error': 'Table name is required', 'code': 'TABLE_NAME_EMPTY'}), 400

    if not isinstance(table_name, str):
        logger.error(f"Table name must be a string, got {type(table_name)}")
        return jsonify({'error': 'Invalid table name type', 'code': 'INVALID_TABLE_TYPE'}), 400

    try:
        from redline.database.optimized_connector import OptimizedDatabaseConnector

        optimized_db = OptimizedDatabaseConnector()

        if request.method == 'GET':
            # Get index information
            indexes = optimized_db.get_index_info(table_name)
            return jsonify({
                'table': table_name,
                'indexes': indexes,
                'count': len(indexes)
            })

        elif request.method == 'POST':
            # Pre-validation for POST request
            if not request.json:
                logger.error("No JSON data provided in POST request")
                return jsonify({'error': 'JSON data required', 'code': 'NO_JSON_DATA'}), 400

            # Create indexes
            action = request.json.get('action', 'create')

            if not action:
                logger.error("Action is empty")
                return jsonify({'error': 'Action is required', 'code': 'ACTION_EMPTY'}), 400

            if action == 'create':
                optimized_db.create_indexes(table_name)
                # Get updated index info
                indexes = optimized_db.get_index_info(table_name)
                return jsonify({
                    'status': 'success',
                    'message': f'Indexes created for {table_name}',
                    'indexes': indexes
                })
            elif action == 'analyze':
                optimized_db.analyze_table(table_name)
                return jsonify({
                    'status': 'success',
                    'message': f'Table {table_name} analyzed successfully'
                })
            else:
                logger.warning(f"Invalid action requested: {action}")
                return jsonify({'error': 'Invalid action', 'code': 'INVALID_ACTION'}), 400

        elif request.method == 'DELETE':
            # Drop indexes
            optimized_db.drop_indexes(table_name)
            return jsonify({
                'status': 'success',
                'message': f'Indexes dropped for {table_name}'
            })

    except ImportError as e:
        logger.error(f"Failed to import OptimizedDatabaseConnector: {str(e)}")
        return jsonify({'error': 'Database connector not available', 'code': 'IMPORT_ERROR'}), 500
    except AttributeError as e:
        logger.error(f"Database method not found for table {table_name}: {str(e)}")
        return jsonify({'error': 'Database operation failed', 'code': 'ATTRIBUTE_ERROR'}), 500
    except KeyError as e:
        logger.error(f"Missing key in database operation for table {table_name}: {str(e)}")
        return jsonify({'error': f'Missing data: {str(e)}', 'code': 'KEY_ERROR'}), 400
    except Exception as e:
        logger.error(f"Unexpected error managing indexes for table {table_name}: {str(e)}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

