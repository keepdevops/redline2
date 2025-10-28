"""
Settings tab routes for REDLINE Web GUI
Handles application configuration and settings
"""

from flask import Blueprint, render_template, request, jsonify
import logging
import os
import configparser

settings_bp = Blueprint('settings', __name__)
logger = logging.getLogger(__name__)

@settings_bp.route('/')
def settings_tab():
    """Settings tab main page."""
    return render_template('settings_tab.html')

@settings_bp.route('/config')
def get_config():
    """Get current application configuration."""
    try:
        config_file = os.path.join(os.getcwd(), 'data_config.ini')
        
        config = configparser.ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file)
        
        # Convert to dictionary format
        config_dict = {}
        for section in config.sections():
            config_dict[section] = dict(config[section])
        
        # Add default configurations if not present
        default_config = {
            'data_sources': {
                'yahoo_enabled': 'true',
                'stooq_enabled': 'true',
                'default_source': 'yahoo'
            },
            'display': {
                'max_rows': '1000',
                'auto_refresh': 'false',
                'theme': 'light'
            },
            'performance': {
                'chunk_size': '10000',
                'max_memory': '1GB',
                'parallel_processing': 'true'
            },
            'export': {
                'default_format': 'csv',
                'include_metadata': 'true',
                'compression': 'none'
            }
        }
        
        # Merge with existing config
        for section, options in default_config.items():
            if section not in config_dict:
                config_dict[section] = options
            else:
                for key, value in options.items():
                    if key not in config_dict[section]:
                        config_dict[section][key] = value
        
        return jsonify({
            'config': config_dict,
            'config_file': config_file,
            'config_exists': os.path.exists(config_file)
        })
        
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/config', methods=['POST'])
def update_config():
    """Update application configuration."""
    try:
        data = request.get_json()
        new_config = data.get('config')
        
        if not new_config:
            return jsonify({'error': 'No configuration provided'}), 400
        
        config_file = os.path.join(os.getcwd(), 'data_config.ini')
        
        config = configparser.ConfigParser()
        
        # Create backup of existing config
        if os.path.exists(config_file):
            backup_file = f"{config_file}.backup"
            os.rename(config_file, backup_file)
        
        # Write new configuration
        for section, options in new_config.items():
            config.add_section(section)
            for key, value in options.items():
                config.set(section, key, str(value))
        
        with open(config_file, 'w') as f:
            config.write(f)
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'config_file': config_file
        })
        
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/reset-config')
def reset_config():
    """Reset configuration to defaults."""
    try:
        config_file = os.path.join(os.getcwd(), 'data_config.ini')
        
        # Create backup
        if os.path.exists(config_file):
            backup_file = f"{config_file}.backup.{int(time.time())}"
            os.rename(config_file, backup_file)
        
        # Create default configuration
        default_config = {
            'data_sources': {
                'yahoo_enabled': 'true',
                'stooq_enabled': 'true',
                'default_source': 'yahoo'
            },
            'display': {
                'max_rows': '1000',
                'auto_refresh': 'false',
                'theme': 'light'
            },
            'performance': {
                'chunk_size': '10000',
                'max_memory': '1GB',
                'parallel_processing': 'true'
            },
            'export': {
                'default_format': 'csv',
                'include_metadata': 'true',
                'compression': 'none'
            }
        }
        
        config = configparser.ConfigParser()
        for section, options in default_config.items():
            config.add_section(section)
            for key, value in options.items():
                config.set(section, key, str(value))
        
        with open(config_file, 'w') as f:
            config.write(f)
        
        return jsonify({
            'message': 'Configuration reset to defaults',
            'config_file': config_file
        })
        
    except Exception as e:
        logger.error(f"Error resetting configuration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/system-info')
def get_system_info():
    """Get system information."""
    try:
        import psutil
        import platform
        
        system_info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            },
            'python': {
                'version': platform.python_version(),
                'implementation': platform.python_implementation(),
                'compiler': platform.python_compiler()
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'cpu': {
                'count': psutil.cpu_count(),
                'percent': psutil.cpu_percent(interval=1)
            }
        }
        
        return jsonify(system_info)
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/logs')
def get_logs():
    """Get application logs."""
    try:
        log_file = os.path.join(os.getcwd(), 'redline.log')
        
        if not os.path.exists(log_file):
            return jsonify({'logs': [], 'message': 'No log file found'})
        
        # Read last 100 lines of log file
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-100:] if len(lines) > 100 else lines
        
        logs = []
        for line in recent_lines:
            logs.append({
                'line': line.strip(),
                'timestamp': line.split(' - ')[0] if ' - ' in line else '',
                'level': line.split(' - ')[1].split(' ')[0] if ' - ' in line else 'INFO'
            })
        
        return jsonify({
            'logs': logs,
            'total_lines': len(lines),
            'recent_lines': len(recent_lines)
        })
        
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/clear-logs', methods=['POST'])
def clear_logs():
    """Clear application logs."""
    try:
        log_file = os.path.join(os.getcwd(), 'redline.log')
        
        if os.path.exists(log_file):
            # Create backup before clearing
            backup_file = f"{log_file}.backup.{int(time.time())}"
            os.rename(log_file, backup_file)
        
        return jsonify({
            'message': 'Logs cleared successfully',
            'backup_created': os.path.exists(f"{log_file}.backup.{int(time.time())}")
        })
        
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/database-status')
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

@settings_bp.route('/test-connection', methods=['POST'])
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
