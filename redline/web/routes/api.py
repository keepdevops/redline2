"""
API routes for REDLINE Web GUI
Provides REST API endpoints for data operations
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import os
import pandas as pd
from werkzeug.utils import secure_filename
import json

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Rate limiting decorator (if limiter is available)
def rate_limit(limit_string):
    """Decorator for rate limiting - gracefully handles missing limiter."""
    def decorator(func):
        limiter = current_app.config.get('limiter') if current_app else None
        if limiter:
            from flask_limiter import Limiter
            return limiter.limit(limit_string)(func)
        return func
    return decorator

@api_bp.route('/status')
def get_status():
    """Get application status."""
    try:
        status = {
            'status': 'running',
            'version': '1.0.0',
            'database': 'available',
            'supported_formats': ['csv', 'json', 'parquet', 'feather', 'duckdb'],
            'timestamp': pd.Timestamp.now().isoformat()
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/database/indexes', methods=['GET', 'POST', 'DELETE'])
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

@api_bp.route('/files')
def api_list_files():
    """List available data files via API."""
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        files = []
        
        # Get files from main data directory
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
        
        # Get files from downloaded directory
        downloaded_dir = os.path.join(data_dir, 'downloaded')
        if os.path.exists(downloaded_dir):
            for filename in os.listdir(downloaded_dir):
                file_path = os.path.join(downloaded_dir, filename)
                if os.path.isfile(file_path) and not filename.startswith('.'):
                    file_stat = os.stat(file_path)
                    files.append({
                        'name': filename,
                        'size': file_stat.st_size,
                        'modified': file_stat.st_mtime,
                        'path': file_path,
                        'location': 'downloaded'
                    })

        # Get files from converted/export directory (recursively including subdirectories)
        converted_dir = os.path.join(data_dir, 'converted')
        if os.path.exists(converted_dir):
            # Recursively search subdirectories in converted/ (duckdb/, parquet/, etc.)
            for root, dirs, filenames in os.walk(converted_dir):
                for filename in filenames:
                    if not filename.startswith('.'):
                        file_path = os.path.join(root, filename)
                        if os.path.isfile(file_path):
                            file_stat = os.stat(file_path)
                            # Get relative path for location
                            rel_path = os.path.relpath(file_path, data_dir)
                            files.append({
                                'name': filename,
                                'size': file_stat.st_size,
                                'modified': file_stat.st_mtime,
                                'path': file_path,
                                'location': rel_path
                            })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'files': files})
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'txt', 'json', 'parquet', 'feather', 'duckdb'}

# API Configuration
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000
COMPRESSION_THRESHOLD = 1024  # Legacy threshold (no longer used)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Manual gzip compression removed; rely on Flask-Compress

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
@rate_limit("10 per minute")
def upload_file():
    """Upload a file for processing. Handles ZIP extraction for Stooq files."""
    try:
        import zipfile
        from werkzeug.utils import secure_filename
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # Check if it's a ZIP file and extract to data/stooq
            extracted_files = []
            final_path = upload_path
            
            if zipfile.is_zipfile(upload_path):
                logger.info(f"Detected ZIP file: {filename}, extracting to data/stooq...")
                try:
                    from redline.utils.stooq_file_handler import extract_zip_file
                    extracted = extract_zip_file(upload_path)
                    extracted_files = extracted if isinstance(extracted, list) else [extracted]
                    os.remove(upload_path)  # Remove ZIP after extraction
                    
                    if extracted_files:
                        final_path = extracted_files[0] if len(extracted_files) == 1 else extracted_files
                except Exception as e:
                    logger.error(f"Error extracting ZIP: {str(e)}")
            else:
                # Check if it's a Stooq file and move to data/stooq
                try:
                    from redline.utils.stooq_file_handler import is_stooq_file, move_file_to_stooq_dir
                    if is_stooq_file(filename):
                        final_path = move_file_to_stooq_dir(upload_path, filename)
                        logger.info(f"Moved Stooq file {filename} to data/stooq directory")
                except Exception as e:
                    logger.warning(f"Could not check/move to stooq directory: {str(e)}")
            
            response = {
                'message': 'File uploaded successfully',
                'filename': os.path.basename(final_path) if isinstance(final_path, str) else filename,
                'path': final_path
            }
            
            if extracted_files:
                response['extracted_files'] = [os.path.basename(f) for f in extracted_files]
                response['extracted_count'] = len(extracted_files)
                response['message'] = f'ZIP file extracted. {len(extracted_files)} file(s) in data/stooq.'
            
            return jsonify(response)
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
@rate_limit("20 per hour")
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
        from redline.core.schema import EXT_TO_FORMAT
        converter = FormatConverter()
        
        # Determine input file path - check both root data directory and downloaded subdirectory
        data_dir = os.path.join(os.getcwd(), 'data')
        input_path = None
        
        # Check in root data directory first
        root_path = os.path.join(data_dir, input_file)
        if os.path.exists(root_path):
            input_path = root_path
        else:
            # Check in downloaded directory
            downloaded_path = os.path.join(data_dir, 'downloaded', input_file)
            if os.path.exists(downloaded_path):
                input_path = downloaded_path
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({'error': 'Input file not found'}), 404
        
        # Detect format from file extension
        ext = os.path.splitext(input_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        # Load data
        data_obj = converter.load_file_by_type(input_path, format_type)
        
        # Aggressive cleaning during conversion: clean column names, remove unnamed columns, etc.
        if isinstance(data_obj, pd.DataFrame):
            from redline.web.routes.data_routes import clean_dataframe_columns
            try:
                data_obj = clean_dataframe_columns(data_obj)
                logger.info(f"Cleaned columns during API conversion")
            except Exception as clean_error:
                logger.warning(f"Error during column cleaning (non-fatal): {str(clean_error)}")
                # Continue with conversion anyway
        
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
@rate_limit("30 per hour")
def download_data(ticker):
    """Download financial data for a ticker."""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        source = data.get('source', 'yahoo')
        
        from redline.downloaders.yahoo_downloader import YahooDownloader
        
        downloader = YahooDownloader()
        result = downloader.download_single_ticker(
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

@api_bp.route('/data/quick/<path:filename>', methods=['GET'])
def get_file_quick_stats(filename: str):
    """
    Return quick stats (columns, row count, preview) for a file located under
    data/, data/downloaded/, or data/converted/.
    Supports CSV, TXT, JSON, Parquet, Feather, and DuckDB.
    """
    try:
        from redline.core.schema import EXT_TO_FORMAT
        base_dir = os.path.join(os.getcwd(), 'data')

        candidates = [
            os.path.join(base_dir, filename),
            os.path.join(base_dir, 'downloaded', filename),
            os.path.join(base_dir, 'converted', filename),
        ]
        file_path = next((p for p in candidates if os.path.exists(p)), None)
        if not file_path:
            return jsonify({'error': 'File not found', 'filename': filename, 'searched': candidates}), 404

        ext = os.path.splitext(file_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')

        # Load data with robust fallbacks
        df = None
        if format_type == 'csv':
            df = pd.read_csv(file_path)
        elif format_type == 'txt':
            for sep in [',', '\t', ';', ' ', '|']:
                try:
                    tmp = pd.read_csv(file_path, sep=sep)
                    if len(tmp.columns) > 1:
                        df = tmp
                        break
                except Exception:
                    continue
            if df is None:
                df = pd.read_fwf(file_path)
        elif format_type == 'parquet':
            df = pd.read_parquet(file_path)
        elif format_type == 'feather':
            df = pd.read_feather(file_path)
        elif format_type == 'json':
            try:
                df = pd.read_json(file_path, lines=True)
            except Exception:
                df = pd.read_json(file_path)
        elif format_type == 'duckdb':
            import duckdb
            conn = duckdb.connect(file_path)
            try:
                tables = conn.execute('SHOW TABLES').fetchall()
                if not tables:
                    return jsonify({'error': 'No tables found in DuckDB file'}), 404
                table_name = tables[0][0]
                df = conn.execute(f'SELECT * FROM {table_name} LIMIT 1000').fetchdf()
            finally:
                conn.close()
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400

        if df is None or not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data'}), 400

        # Minimal cleanup: drop Unnamed columns only
        unnamed = [c for c in df.columns if str(c).startswith('Unnamed:')]
        if unnamed:
            df = df.drop(columns=unnamed)

        return jsonify({
            'filename': filename,
            'file_path': file_path,
            'format': format_type,
            'columns': list(df.columns),
            'total_rows': int(len(df)),
            'preview': df.head(5).to_dict(orient='records')
        })
    except Exception as e:
        logger.error(f"Quick stats failed for {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/data/<filename>', methods=['GET'])
def get_data_preview(filename):
    """Get paginated preview of data file with compression."""
    try:
        # Check multiple locations for the file
        data_dir = os.path.join(os.getcwd(), 'data')
        data_path = None
        
        # Check in root data directory first
        root_path = os.path.join(data_dir, filename)
        if os.path.exists(root_path):
            data_path = root_path
        else:
            # Check in downloaded directory
            downloaded_path = os.path.join(data_dir, 'downloaded', filename)
            if os.path.exists(downloaded_path):
                data_path = downloaded_path
            else:
                # Check in converted directory (and subdirectories)
                converted_dir = os.path.join(data_dir, 'converted')
                # Try common direct path first
                converted_path = os.path.join(converted_dir, filename)
                if os.path.exists(converted_path):
                    data_path = converted_path
                else:
                    # Walk converted/ recursively to find the file
                    if os.path.exists(converted_dir):
                        for root, dirs, files in os.walk(converted_dir):
                            if filename in files:
                                data_path = os.path.join(root, filename)
                                break
        
        if not data_path or not os.path.exists(data_path):
            return jsonify({'error': 'File not found', 'filename': filename}), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', DEFAULT_PAGE_SIZE, type=int)
        
        # Load data
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
        # Detect format from file extension
        ext = os.path.splitext(data_path)[1].lower()
        format_type = EXT_TO_FORMAT.get(ext, 'csv')
        
        data = converter.load_file_by_type(data_path, format_type)
        
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
        
        # Return normal JSON; Flask-Compress handles compression
        return jsonify(response_data)
        
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

@api_bp.route('/font-colors', methods=['GET'])
def get_font_colors():
    """Get current font color configuration."""
    try:
        # This would typically come from a database or user preferences
        # For now, return default font color variables
        font_colors = {
            'text-primary': '#1e293b',
            'text-secondary': '#64748b',
            'text-muted': '#94a3b8',
            'text-light': '#cbd5e1',
            'text-dark': '#0f172a',
            'text-white': '#ffffff',
            'text-success': '#059669',
            'text-warning': '#d97706',
            'text-danger': '#dc2626',
            'text-info': '#0891b2',
            'text-link': '#2563eb',
            'text-link-hover': '#1d4ed8'
        }
        
        return jsonify({'font_colors': font_colors})
        
    except Exception as e:
        logger.error(f"Error getting font colors: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/font-colors', methods=['POST'])
def set_font_colors():
    """Set custom font color configuration."""
    try:
        data = request.get_json()
        font_colors = data.get('font_colors', {})
        
        # Validate font colors
        valid_color_keys = [
            'text-primary', 'text-secondary', 'text-muted', 'text-light', 
            'text-dark', 'text-white', 'text-success', 'text-warning', 
            'text-danger', 'text-info', 'text-link', 'text-link-hover'
        ]
        
        # Validate color format (basic hex color validation)
        import re
        hex_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
        
        for key, value in font_colors.items():
            if key not in valid_color_keys:
                return jsonify({'error': f'Invalid color key: {key}'}), 400
            
            if not hex_pattern.match(value):
                return jsonify({'error': f'Invalid color format for {key}: {value}'}), 400
        
        # Store font colors in session (you could also store in database)
        session['font_colors'] = font_colors
        
        return jsonify({
            'message': 'Font colors updated successfully',
            'font_colors': font_colors
        })
        
    except Exception as e:
        logger.error(f"Error setting font colors: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/font-color-presets', methods=['GET'])
def get_font_color_presets():
    """Get available font color presets."""
    try:
        presets = {
            'default': {
                'text-primary': '#1e293b',
                'text-secondary': '#64748b',
                'text-muted': '#94a3b8',
                'text-light': '#cbd5e1',
                'text-dark': '#0f172a',
                'text-white': '#ffffff',
                'text-success': '#059669',
                'text-warning': '#d97706',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#2563eb',
                'text-link-hover': '#1d4ed8'
            },
            'high-contrast': {
                'text-primary': '#000000',
                'text-secondary': '#404040',
                'text-muted': '#808080',
                'text-light': '#c0c0c0',
                'text-dark': '#000000',
                'text-white': '#ffffff',
                'text-success': '#008000',
                'text-warning': '#ff8000',
                'text-danger': '#ff0000',
                'text-info': '#0080ff',
                'text-link': '#0000ff',
                'text-link-hover': '#0000cc'
            },
            'ocean': {
                'text-primary': '#0f172a',
                'text-secondary': '#475569',
                'text-muted': '#64748b',
                'text-light': '#94a3b8',
                'text-dark': '#020617',
                'text-white': '#ffffff',
                'text-success': '#0d9488',
                'text-warning': '#f59e0b',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#0369a1',
                'text-link-hover': '#075985'
            },
            'forest': {
                'text-primary': '#14532d',
                'text-secondary': '#365314',
                'text-muted': '#4b5563',
                'text-light': '#9ca3af',
                'text-dark': '#052e16',
                'text-white': '#ffffff',
                'text-success': '#16a34a',
                'text-warning': '#ca8a04',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#166534',
                'text-link-hover': '#15803d'
            },
            'sunset': {
                'text-primary': '#431407',
                'text-secondary': '#9a3412',
                'text-muted': '#a16207',
                'text-light': '#d97706',
                'text-dark': '#292524',
                'text-white': '#ffffff',
                'text-success': '#16a34a',
                'text-warning': '#f59e0b',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#ea580c',
                'text-link-hover': '#c2410c'
            },
            'monochrome': {
                'text-primary': '#111827',
                'text-secondary': '#374151',
                'text-muted': '#6b7280',
                'text-light': '#9ca3af',
                'text-dark': '#000000',
                'text-white': '#ffffff',
                'text-success': '#059669',
                'text-warning': '#d97706',
                'text-danger': '#dc2626',
                'text-info': '#0891b2',
                'text-link': '#374151',
                'text-link-hover': '#1f2937'
            },
                    'dark': {
                        'text-primary': '#f9fafb',
                        'text-secondary': '#d1d5db',
                        'text-muted': '#9ca3af',
                        'text-light': '#6b7280',
                        'text-dark': '#ffffff',
                        'text-white': '#ffffff',
                        'text-success': '#10b981',
                        'text-warning': '#f59e0b',
                        'text-danger': '#ef4444',
                        'text-info': '#06b6d4',
                        'text-link': '#3b82f6',
                        'text-link-hover': '#2563eb'
                    },
                    'grayscale': {
                        'text-primary': '#2d3748',
                        'text-secondary': '#4a5568',
                        'text-muted': '#718096',
                        'text-light': '#a0aec0',
                        'text-dark': '#1a202c',
                        'text-white': '#ffffff',
                        'text-success': '#38a169',
                        'text-warning': '#d69e2e',
                        'text-danger': '#e53e3e',
                        'text-info': '#3182ce',
                        'text-link': '#4a5568',
                        'text-link-hover': '#2d3748'
                    }
        }
        
        return jsonify({'presets': presets})
        
    except Exception as e:
        logger.error(f"Error getting font color presets: {str(e)}")
        return jsonify({'error': str(e)}), 500
