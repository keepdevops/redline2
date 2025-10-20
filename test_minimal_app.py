#!/usr/bin/env python3
"""
Minimal Flask app to test basic functionality
"""

import os
import sys
from flask import Flask, render_template, jsonify

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            template_folder='redline/web/templates',
            static_folder='redline/web/static')

# Configuration
app.config['SECRET_KEY'] = 'test-secret-key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'test-app'})

@app.route('/api/files')
def api_files():
    """Simple API endpoint to test file listing."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                file_path = os.path.join(data_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path
                    })
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/data/')
def data_tab():
    """Simple data tab."""
    return render_template('data_tab_basic.html')

@app.route('/test')
def test_page():
    """Test page with debug info."""
    return render_template('test_data_view.html')

@app.route('/standalone')
def standalone_test():
    """Standalone test page."""
    with open('standalone_test.html', 'r') as f:
        return f.read()

@app.route('/data/load', methods=['POST'])
def load_data():
    """Simple data loading endpoint."""
    try:
        from flask import request
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        # Simple test response
        return jsonify({
            'filename': filename,
            'total_rows': 100,
            'columns': ['col1', 'col2', 'col3'],
            'data': [
                {'col1': 'A', 'col2': 'B', 'col3': 'C'},
                {'col1': '1', 'col2': '2', 'col3': '3'},
                {'col1': 'X', 'col2': 'Y', 'col3': 'Z'}
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting minimal Flask app...")
    app.run(host='0.0.0.0', port=5000, debug=True)
