"""
API routes for data operations (Modal-powered).
Handles data preview, quick stats, and data downloads using Modal serverless functions.
"""

from flask import Blueprint, request, jsonify, g
import logging
import os
from ..utils.api_helpers import rate_limit, paginate_data, DEFAULT_PAGE_SIZE
from redline.clients.modal_client import modal_client

api_data_bp = Blueprint('api_data', __name__)
logger = logging.getLogger(__name__)


@api_data_bp.route('/data/<filename>', methods=['GET'])
def get_data_preview(filename):
    """Get paginated preview of data file using Modal processing."""
    try:
        # Check multiple locations for the file
        data_dir = os.path.join(os.getcwd(), 'data')
        data_path = None

        candidates = [
            os.path.join(data_dir, filename),
            os.path.join(data_dir, 'downloaded', filename),
            os.path.join(data_dir, 'converted', filename),
        ]

        # Also search in converted subdirectories
        converted_dir = os.path.join(data_dir, 'converted')
        if os.path.exists(converted_dir):
            for root, dirs, files in os.walk(converted_dir):
                if filename in files:
                    candidates.append(os.path.join(root, filename))

        data_path = next((p for p in candidates if os.path.exists(p)), None)

        if not data_path:
            return jsonify({'error': 'File not found', 'filename': filename}), 404

        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', DEFAULT_PAGE_SIZE, type=int)

        # Read file and send to Modal for processing
        with open(data_path, 'rb') as f:
            file_data = f.read()

        # Use Modal to process the file
        result = modal_client.process_csv(
            file_data=file_data,
            filename=filename,
            operation='preview',
            limit=per_page * page  # Get enough data for pagination
        )

        if 'error' in result:
            return jsonify({'error': result['error']}), 500

        # Paginate the results
        all_records = result.get('data', [])
        paginated_result = paginate_data(all_records, page, per_page)

        response_data = {
            'columns': result.get('columns', []),
            'total_rows': result.get('total_rows', 0),
            'filename': filename,
            'preview': paginated_result['data'],
            'pagination': paginated_result['pagination']
        }

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error getting data preview for {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_data_bp.route('/data/quick/<path:filename>', methods=['GET'])
def get_file_quick_stats(filename: str):
    """
    Return quick stats (columns, row count, preview) using Modal processing.
    """
    try:
        base_dir = os.path.join(os.getcwd(), 'data')

        candidates = [
            os.path.join(base_dir, filename),
            os.path.join(base_dir, 'downloaded', filename),
            os.path.join(base_dir, 'converted', filename),
        ]

        file_path = next((p for p in candidates if os.path.exists(p)), None)

        if not file_path:
            return jsonify({'error': 'File not found', 'filename': filename}), 404

        # Read file and send to Modal
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Get metadata from Modal
        result = modal_client.get_metadata(file_data=file_data, filename=filename)

        if 'error' in result:
            return jsonify({'error': result['error']}), 500

        return jsonify({
            'filename': filename,
            'file_path': file_path,
            'format': result.get('format'),
            'columns': result.get('columns', []),
            'total_rows': result.get('total_rows', 0),
            'preview': result.get('sample_data', [])
        })

    except Exception as e:
        logger.error(f"Quick stats failed for {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_data_bp.route('/data/quick-stats', methods=['POST'])
def get_file_quick_stats_post():
    """
    POST endpoint for quick stats using Modal processing.
    """
    try:
        data = request.get_json()
        filename = data.get('filename')
        file_path_hint = data.get('file_path')

        if not filename:
            return jsonify({'error': 'No filename provided'}), 400

        base_dir = os.path.join(os.getcwd(), 'data')

        # Use file_path_hint if provided and exists, otherwise search
        file_path = None
        if file_path_hint and os.path.exists(file_path_hint):
            file_path = file_path_hint
        else:
            candidates = [
                os.path.join(base_dir, filename),
                os.path.join(base_dir, 'downloaded', filename),
                os.path.join(base_dir, 'stooq', filename),
                os.path.join(base_dir, 'uploads', filename),
                os.path.join(base_dir, 'converted', filename),
            ]

            # Also search in converted subdirectories
            converted_dir = os.path.join(base_dir, 'converted')
            if os.path.exists(converted_dir):
                for root, dirs, files in os.walk(converted_dir):
                    if filename in files:
                        candidates.append(os.path.join(root, filename))

            file_path = next((p for p in candidates if os.path.exists(p)), None)

        if not file_path:
            return jsonify({'error': 'File not found', 'filename': filename}), 404

        # Read file and send to Modal
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Get metadata from Modal
        result = modal_client.get_metadata(file_data=file_data, filename=filename)

        if 'error' in result:
            return jsonify({'error': result['error']}), 500

        return jsonify({
            'filename': filename,
            'file_path': file_path,
            'format': result.get('format'),
            'rows': result.get('total_rows', 0),
            'columns': len(result.get('columns', [])),
            'columns_list': result.get('columns', []),
            'preview': result.get('sample_data', [])
        })

    except Exception as e:
        logger.error(f"Quick stats failed: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_data_bp.route('/download/<ticker>', methods=['POST'])
@rate_limit("30 per hour")
def download_data(ticker):
    """Download financial data for a ticker."""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')

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
