"""
API routes for REDLINE Web GUI
Provides REST API endpoints for data operations
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import os
import pandas as pd
from werkzeug.utils import secure_filename
import gzip
import json

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'json', 'parquet', 'feather', 'duckdb'}

# API Configuration
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000
COMPRESSION_THRESHOLD = 1024  # Compress responses > 1KB

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_response(response_data):
    """Compress response data if it's large enough."""
    try:
        response_json = json.dumps(response_data)
        if len(response_json) > COMPRESSION_THRESHOLD:
            compressed = gzip.compress(response_json.encode('utf-8'))
            return compressed, True
        return response_json.encode('utf-8'), False
    except Exception as e:
        logger.error(f"Error compressing response: {str(e)}")
        return json.dumps(response_data).encode('utf-8'), False

def paginate_data(data, page=1, per_page=None):
    """Paginate data for API responses."""
    if per_page is None:
        per_page = DEFAULT_PAGE_SIZE
    
    # Ensure page and per_page are valid
    page = max(1, int(page))
    per_page = min(max(1, int(per_page)), MAX_PAGE_SIZE)
    
    # Calculate pagination
    total_items = len(data)
    total_pages = (total_items + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    
    # Get paginated data
    paginated_data = data[start_idx:end_idx]
    
    return {
        'data': paginated_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total_items,
            'pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }

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
    """Get paginated preview of data file with compression."""
    try:
        data_path = os.path.join(os.getcwd(), 'data', filename)
        
        if not os.path.exists(data_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', DEFAULT_PAGE_SIZE, type=int)
        
        # Load data
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        data = converter.load_file(data_path)
        
        if isinstance(data, pd.DataFrame):
            # Convert to records for pagination
            all_records = data.to_dict('records')
            
            # Paginate the data
            paginated_result = paginate_data(all_records, page, per_page)
            
            response_data = {
                'columns': list(data.columns),
                'total_rows': len(data),
                'filename': filename,
                'preview': paginated_result['data'],
                'pagination': paginated_result['pagination']
            }
        else:
            # Handle non-DataFrame data
            preview = str(data)[:1000]  # Truncate for non-DataFrame data
            response_data = {
                'columns': [],
                'total_rows': 0,
                'filename': filename,
                'preview': preview,
                'pagination': {'page': 1, 'per_page': 1, 'total': 1, 'pages': 1, 'has_next': False, 'has_prev': False}
            }
        
        # Compress response if large
        compressed_data, is_compressed = compress_response(response_data)
        
        response = jsonify(response_data)
        if is_compressed:
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = str(len(compressed_data))
        
        return response
        
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
