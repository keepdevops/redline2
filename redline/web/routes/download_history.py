"""
Download history and validation routes.
Handles download history retrieval and ticker validation.
"""

import os
import glob
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta

download_history_bp = Blueprint('download_history', __name__)
logger = logging.getLogger(__name__)

@download_history_bp.route('/history')
def get_download_history():
    """Get download history."""
    try:
        download_dir = os.path.join(os.getcwd(), 'data', 'downloaded')
        
        if not os.path.exists(download_dir):
            return jsonify({'downloads': []})
        
        files = glob.glob(os.path.join(download_dir, '*.csv'))
        downloads = []
        
        for filepath in files:
            filename = os.path.basename(filepath)
            stat = os.stat(filepath)
            
            downloads.append({
                'filename': filename,
                'filepath': filepath,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime
            })
        
        # Sort by modification time (newest first)
        downloads.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({'downloads': downloads})
        
    except Exception as e:
        logger.error(f"Error getting download history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@download_history_bp.route('/validate-ticker', methods=['POST'])
def validate_ticker():
    """Validate if a ticker symbol exists."""
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        source = data.get('source', 'yahoo')
        
        if not ticker:
            return jsonify({'error': 'Ticker symbol is required'}), 400
        
        # Try to download a small amount of data to validate
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        if source == 'yahoo':
            from redline.downloaders.yahoo_downloader import YahooDownloader
            downloader = YahooDownloader()
            result = downloader.download_data(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        else:
            result = None
        
        if result is not None and not result.empty:
            return jsonify({
                'valid': True,
                'ticker': ticker,
                'source': source,
                'sample_data': {
                    'columns': list(result.columns),
                    'records': len(result),
                    'date_range': {
                        'start': str(result.index.min()),
                        'end': str(result.index.max())
                    }
                }
            })
        else:
            return jsonify({
                'valid': False,
                'ticker': ticker,
                'source': source,
                'error': 'No data found for this ticker'
            })
            
    except Exception as e:
        logger.error(f"Error validating ticker {ticker}: {str(e)}")
        return jsonify({
            'valid': False,
            'ticker': ticker,
            'error': str(e)
        })

