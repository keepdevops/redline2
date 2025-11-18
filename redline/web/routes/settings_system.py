"""
Settings system routes for REDLINE Web GUI
Handles system information and log management
"""

from flask import Blueprint, jsonify
import logging
import os
import time

settings_system_bp = Blueprint('settings_system', __name__)
logger = logging.getLogger(__name__)

@settings_system_bp.route('/system-info')
def get_system_info():
    """Get system information."""
    try:
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
            }
        }
        
        # Try to get psutil metrics if available
        try:
            import psutil
            system_info['memory'] = {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used,
                'free': psutil.virtual_memory().free
            }
            system_info['disk'] = {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            }
            system_info['cpu'] = {
                'count': psutil.cpu_count(),
                'percent': psutil.cpu_percent(interval=1)
            }
        except ImportError:
            # psutil not available, skip those metrics
            system_info['memory'] = {'message': 'psutil not available'}
            system_info['disk'] = {'message': 'psutil not available'}
            system_info['cpu'] = {'message': 'psutil not available'}
        
        return jsonify(system_info)
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_system_bp.route('/logs')
def get_logs():
    """Get application logs."""
    try:
        # Check multiple possible log file locations
        # Note: web_app.py uses 'redline_web.log' as the log file name
        possible_log_files = [
            os.path.join(os.getcwd(), 'redline_web.log'),  # Primary log file (from web_app.py)
            os.path.join(os.getcwd(), 'redline.log'),  # Fallback
            os.path.join(os.getcwd(), 'logs', 'redline_web.log'),
            os.path.join(os.getcwd(), 'logs', 'redline.log'),
            os.path.join(os.getcwd(), 'data', 'logs', 'redline_web.log'),
            os.path.join(os.getcwd(), 'data', 'logs', 'redline.log'),
            '/var/log/redline_web.log',
            '/var/log/redline.log',
            '/app/redline_web.log',
            '/app/redline.log',
            '/app/logs/redline_web.log',
            '/app/logs/redline.log'
        ]
        
        log_file = None
        for possible_file in possible_log_files:
            if os.path.exists(possible_file):
                log_file = possible_file
                break
        
        if not log_file:
            # Return info about missing log file
            return jsonify({
                'logs': [],
                'message': 'No log file found. Logs may be going to stdout/stderr in Docker.',
                'hint': 'Use "docker logs redline-webgui" to view logs in Docker environment.',
                'possible_locations': possible_log_files
            })
        
        # Read last 100 lines of log file
        try:
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
                'recent_lines': len(recent_lines),
                'log_file': log_file
            })
        except Exception as read_error:
            logger.error(f"Error reading log file: {str(read_error)}")
            return jsonify({
                'logs': [],
                'error': f'Error reading log file: {str(read_error)}',
                'log_file': log_file
            })
        
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_system_bp.route('/clear-logs', methods=['POST'])
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

