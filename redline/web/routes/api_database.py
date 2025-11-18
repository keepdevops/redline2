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
    try:
        from redline.database.optimized_connector import OptimizedDatabaseConnector
        
        optimized_db = OptimizedDatabaseConnector()
        table_name = request.args.get('table', 'tickers_data')
        
        if request.method == 'GET':
            # Get index information
            indexes = optimized_db.get_index_info(table_name)
            return jsonify({
                'table': table_name,
                'indexes': indexes,
                'count': len(indexes)
            })
            
        elif request.method == 'POST':
            # Create indexes
            action = request.json.get('action', 'create')
            
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
                return jsonify({'error': 'Invalid action'}), 400
                
        elif request.method == 'DELETE':
            # Drop indexes
            optimized_db.drop_indexes(table_name)
            return jsonify({
                'status': 'success',
                'message': f'Indexes dropped for {table_name}'
            })
            
    except Exception as e:
        logger.error(f"Error managing indexes: {str(e)}")
        return jsonify({'error': str(e)}), 500

