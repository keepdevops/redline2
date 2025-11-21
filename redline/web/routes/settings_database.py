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
            'database_path': str(connector.db_path) if hasattr(connector, 'db_path') else 'N/A',
            'total_records': 0,
            'total_tickers': 0
        }
        
        if status['available']:
            try:
                # Try to get some basic database info
                tables = connector.get_tables()
                status['tables'] = tables
                status['table_count'] = len(tables)
                
                # Calculate total record count and ticker count from all tables
                total_records = 0
                total_tickers = 0
                conn = None
                try:
                    # Try to create connection, use read-only if locked
                    try:
                        conn = connector.create_connection()
                    except Exception as conn_error:
                        # If connection fails due to lock, try read-only mode
                        if 'lock' in str(conn_error).lower() or 'conflicting' in str(conn_error).lower():
                            logger.warning(f"Database locked, trying read-only mode: {str(conn_error)}")
                            try:
                                import duckdb
                                conn = duckdb.connect(connector.db_path, read_only=True)
                            except Exception as read_error:
                                logger.warning(f"Could not connect in read-only mode: {str(read_error)}")
                                raise conn_error
                        else:
                            raise
                    
                    if conn:
                        for table in tables:
                            try:
                                # Get record count for each table
                                result = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                                if result:
                                    total_records += result[0]
                                
                                # Try to get ticker count if table has a 'ticker' column
                                try:
                                    ticker_result = conn.execute(f"SELECT COUNT(DISTINCT ticker) as count FROM {table}").fetchone()
                                    if ticker_result and ticker_result[0]:
                                        # Use the maximum ticker count across all tables (in case data is split)
                                        total_tickers = max(total_tickers, ticker_result[0])
                                except:
                                    # Table might not have a ticker column, that's okay
                                    pass
                            except Exception as e:
                                logger.warning(f"Could not count records in table {table}: {str(e)}")
                        conn.close()
                except Exception as e:
                    logger.warning(f"Could not calculate total records: {str(e)}")
                    if conn:
                        try:
                            conn.close()
                        except:
                            pass
                
                status['total_records'] = total_records
                status['total_tickers'] = total_tickers
            except Exception as e:
                logger.warning(f"Error getting database info: {str(e)}")
                status['error'] = str(e)
                # Keep total_records and total_tickers as 0 (already set in initial status)
        
        # Also check converted databases in /app/data/converted/ if main DB is empty or unavailable
        if status.get('total_records', 0) == 0 or not status.get('available', False):
            try:
                import os
                import duckdb
                converted_dir = os.path.join(os.getcwd(), 'data', 'converted')
                if not os.path.exists(converted_dir):
                    # Try Docker path
                    converted_dir = '/app/data/converted'
                
                if os.path.exists(converted_dir):
                    converted_total = 0
                    converted_tickers = set()
                    for db_file in os.listdir(converted_dir):
                        if db_file.endswith('.duckdb'):
                            db_path = os.path.join(converted_dir, db_file)
                            try:
                                conn = duckdb.connect(db_path, read_only=True)
                                tables = conn.execute('SHOW TABLES').fetchall()
                                for table_row in tables:
                                    table = table_row[0]
                                    try:
                                        count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                                        converted_total += count
                                        
                                        # Try to get tickers
                                        try:
                                            ticker_result = conn.execute(f'SELECT DISTINCT ticker FROM {table}').fetchall()
                                            for ticker_row in ticker_result:
                                                if ticker_row and ticker_row[0]:
                                                    converted_tickers.add(ticker_row[0])
                                        except:
                                            pass
                                    except Exception as e:
                                        logger.debug(f"Could not count records in {db_file}/{table}: {str(e)}")
                                conn.close()
                            except Exception as e:
                                logger.debug(f"Could not read converted database {db_file}: {str(e)}")
                    
                    if converted_total > 0:
                        status['total_records'] = converted_total
                        status['total_tickers'] = len(converted_tickers) if converted_tickers else status.get('total_tickers', 0)
                        status['converted_db_count'] = len([f for f in os.listdir(converted_dir) if f.endswith('.duckdb')])
            except Exception as e:
                logger.debug(f"Could not check converted databases: {str(e)}")
        
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

