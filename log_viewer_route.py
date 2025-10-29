from flask import jsonify, request
import os
import logging

@settings_bp.route('/logs')
def view_logs():
    """View application logs."""
    try:
        log_file = '/app/redline_web.log'
        lines = request.args.get('lines', 50, type=int)
        
        if not os.path.exists(log_file):
            return jsonify({'error': 'Log file not found'}), 404
        
        with open(log_file, 'r') as f:
            log_lines = f.readlines()
        
        # Get the last N lines
        recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
        
        return jsonify({
            'logs': [line.strip() for line in recent_lines],
            'total_lines': len(log_lines),
            'file_size': os.path.getsize(log_file),
            'log_file': log_file
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/logs/clear', methods=['POST']) 
def clear_logs():
    """Clear application logs."""
    try:
        log_file = '/app/redline_web.log'
        if os.path.exists(log_file):
            open(log_file, 'w').close()
        return jsonify({'message': 'Logs cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
