"""
API routes for REDLINE Web GUI
Provides REST API endpoints for data operations
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import os
import pandas as pd
from werkzeug.utils import secure_filename

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'json', 'parquet', 'feather', 'duckdb'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file for processing."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'path': upload_path
            })
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files', methods=['GET'])
def list_files():
    """List available data files."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        for filename in os.listdir(data_dir):
            if allowed_file(filename):
                file_path = os.path.join(data_dir, filename)
                file_stat = os.stat(file_path)
                files.append({
                    'name': filename,
                    'size': file_stat.st_size,
                    'modified': file_stat.st_mtime
                })
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/formats', methods=['GET'])
def get_supported_formats():
    """Get supported file formats."""
    try:
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        formats = converter.get_supported_formats()
        
        return jsonify({'formats': formats})
        
    except Exception as e:
        logger.error(f"Error getting formats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/convert', methods=['POST'])
def convert_file():
    """Convert file between formats."""
    try:
        data = request.get_json()
        input_file = data.get('input_file')
        output_format = data.get('output_format')
        output_file = data.get('output_file')
        
        if not all([input_file, output_format, output_file]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        # Load data
        data_obj = converter.load_file(input_file)
        
        # Convert and save
        converter.save_file_by_type(data_obj, output_file, output_format)
        
        return jsonify({
            'message': 'File converted successfully',
            'output_file': output_file
        })
        
    except Exception as e:
        logger.error(f"Error converting file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/download/<ticker>', methods=['POST'])
def download_data(ticker):
    """Download financial data for a ticker."""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        source = data.get('source', 'yahoo')
        
        from redline.downloaders.yahoo_downloader import YahooDownloader
        
        downloader = YahooDownloader()
        result = downloader.download_data(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'message': f'Data downloaded for {ticker}',
            'ticker': ticker,
            'records': len(result) if result is not None else 0
        })
        
    except Exception as e:
        logger.error(f"Error downloading data for {ticker}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/data/<filename>', methods=['GET'])
def get_data_preview(filename):
    """Get preview of data file."""
    try:
        data_path = os.path.join(os.getcwd(), 'data', filename)
        
        if not os.path.exists(data_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Load first 100 rows for preview
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        data = converter.load_file(data_path)
        
        if isinstance(data, pd.DataFrame):
            preview = data.head(100).to_dict('records')
            columns = list(data.columns)
            total_rows = len(data)
        else:
            preview = str(data)[:1000]  # Truncate for non-DataFrame data
            columns = []
            total_rows = 0
        
        return jsonify({
            'preview': preview,
            'columns': columns,
            'total_rows': total_rows,
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"Error getting data preview for {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/themes', methods=['GET'])
def get_themes():
    """Get available themes."""
    themes = {
        'theme-default': {
            'name': 'Default',
            'description': 'Default color-blind friendly theme',
            'icon': 'fas fa-circle',
            'color': 'primary'
        },
        'theme-high-contrast': {
            'name': 'High Contrast',
            'description': 'High contrast theme for better visibility',
            'icon': 'fas fa-circle',
            'color': 'danger'
        },
        'theme-ocean': {
            'name': 'Ocean',
            'description': 'Ocean-inspired blue theme',
            'icon': 'fas fa-circle',
            'color': 'info'
        },
        'theme-forest': {
            'name': 'Forest',
            'description': 'Nature-inspired green theme',
            'icon': 'fas fa-circle',
            'color': 'success'
        },
        'theme-sunset': {
            'name': 'Sunset',
            'description': 'Warm sunset colors',
            'icon': 'fas fa-circle',
            'color': 'warning'
        },
        'theme-monochrome': {
            'name': 'Monochrome',
            'description': 'Black and white theme',
            'icon': 'fas fa-circle',
            'color': 'secondary'
        },
        'theme-dark': {
            'name': 'Dark',
            'description': 'Dark mode theme',
            'icon': 'fas fa-moon',
            'color': 'dark'
        }
    }
    
    return jsonify({
        'themes': themes,
        'default': 'theme-default'
    })

@api_bp.route('/theme', methods=['POST'])
def set_theme():
    """Set user theme preference."""
    try:
        data = request.get_json()
        theme = data.get('theme', 'theme-default')
        
        # Validate theme
        valid_themes = [
            'theme-default', 'theme-high-contrast', 'theme-ocean', 
            'theme-forest', 'theme-sunset', 'theme-monochrome', 'theme-dark'
        ]
        
        if theme not in valid_themes:
            return jsonify({'error': 'Invalid theme'}), 400
        
        # TODO: Store theme preference in user session/database
        # For now, just return success
        return jsonify({
            'message': 'Theme preference updated',
            'theme': theme
        })
        
    except Exception as e:
        logger.error(f"Error setting theme: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/theme', methods=['GET'])
def get_theme():
    """Get current theme preference."""
    # TODO: Get theme from user session/database
    # For now, return default
    return jsonify({
        'theme': 'theme-default'
    })
