"""
Settings database routes for REDLINE Web GUI
Handles database connection status and testing
"""

from flask import Blueprint, request, jsonify
import logging

settings_database_bp = Blueprint('settings_database', __name__)
logger = logging.getLogger(__name__)

@settings_database_bp.route('/database-status')
def get_database_status():
    """Get database connection status."""
    try:
        from redline.database.connector import DatabaseConnector
        
        connector = DatabaseConnector()
        
        status = {
            'available': connector.is_available(),
            'connection_string': f"duckdb://{connector.db_path}" if hasattr(connector, 'db_path') else 'N/A',
            'database_path': str(connector.db_path) if hasattr(connector, 'db_path') else 'N/A'
        }
        
        if status['available']:
            try:
                # Try to get some basic database info
                tables = connector.get_tables()
                status['tables'] = tables
                status['table_count'] = len(tables)
            except Exception as e:
                status['error'] = str(e)
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting database status: {str(e)}")
        return jsonify({
            'available': False,
            'error': str(e)
        })

@settings_database_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """Test database connection."""
    try:
        data = request.get_json()
        connection_type = data.get('type', 'database')
        
        if connection_type == 'database':
            from redline.database.connector import DatabaseConnector
            
            connector = DatabaseConnector()
            
            if connector.is_available():
                # Try a simple query
                result = connector.execute_query("SELECT 1 as test")
                
                # Convert DataFrame to JSON-serializable format
                test_data = None
                if result is not None:
                    if hasattr(result, 'to_dict'):
                        test_data = result.to_dict('records')
                    else:
                        test_data = str(result)
                
                return jsonify({
                    'success': True,
                    'message': 'Database connection successful',
                    'test_result': test_data
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Database not available'
                })
        
        elif connection_type == 'yahoo':
            from redline.downloaders.yahoo_downloader import YahooDownloader
            
            downloader = YahooDownloader()
            # Try to download a small amount of data
            result = downloader.download_single_ticker('AAPL', start_date='2024-01-01', end_date='2024-01-02')
            
            if result is not None and not result.empty:
                return jsonify({
                    'success': True,
                    'message': 'Yahoo Finance connection successful',
                    'test_data_rows': len(result)
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to download test data from Yahoo Finance'
                })
        
        elif connection_type == 'stooq':
            from redline.downloaders.stooq_downloader import StooqDownloader
            
            downloader = StooqDownloader()
            # Try to download a small amount of data
            result = downloader.download_single_ticker('AAPL.US', start_date='2024-01-01', end_date='2024-01-02')
            
            if result is not None and not result.empty:
                return jsonify({
                    'success': True,
                    'message': 'Stooq connection successful',
                    'test_data_rows': len(result)
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to download test data from Stooq'
                })
        
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown connection type: {connection_type}'
            })
        
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

