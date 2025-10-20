"""
Download tab routes for REDLINE Web GUI
Handles data downloading from various sources
"""

from flask import Blueprint, render_template, request, jsonify
import logging
from datetime import datetime, timedelta

download_bp = Blueprint('download', __name__)
logger = logging.getLogger(__name__)

@download_bp.route('/')
def download_tab():
    """Download tab main page."""
    return render_template('download_tab.html')

@download_bp.route('/sources')
def get_sources():
    """Get available data sources."""
    try:
        sources = {
            'yahoo': {
                'name': 'Yahoo Finance',
                'description': 'Free financial data from Yahoo Finance',
                'supported_tickers': 'US and international stocks, ETFs, indices',
                'data_types': ['OHLCV', 'dividends', 'splits'],
                'delay': '15-20 minutes for real-time data'
            },
            'stooq': {
                'name': 'Stooq',
                'description': 'Free historical financial data',
                'supported_tickers': 'Global stocks and indices',
                'data_types': ['OHLCV'],
                'delay': 'End of day'
            }
        }
        
        return jsonify({'sources': sources})
        
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        return jsonify({'error': str(e)}), 500

@download_bp.route('/download', methods=['POST'])
def download_data():
    """Download data from specified source."""
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        source = data.get('source', 'yahoo')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        interval = data.get('interval', '1d')
        
        if not ticker:
            return jsonify({'error': 'Ticker symbol is required'}), 400
        
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        result = None
        downloader = None
        
        if source == 'yahoo':
            from redline.downloaders.yahoo_downloader import YahooDownloader
            downloader = YahooDownloader()
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        elif source == 'stooq':
            from redline.downloaders.stooq_downloader import StooqDownloader
            downloader = StooqDownloader()
            result = downloader.download_single_ticker(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
        else:
            return jsonify({'error': f'Unsupported source: {source}'}), 400
        
        if result is not None and not result.empty:
            # Save the downloaded data
            filename = f"{ticker}_{source}_{start_date}_to_{end_date}.csv"
            filepath = f"data/downloaded/{filename}"
            
            result.to_csv(filepath, index=True)
            
            return jsonify({
                'message': f'Successfully downloaded {len(result)} records for {ticker}',
                'ticker': ticker,
                'source': source,
                'records': len(result),
                'filename': filename,
                'filepath': filepath,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'columns': list(result.columns)
            })
        else:
            return jsonify({'error': f'No data found for {ticker}'}), 404
            
    except Exception as e:
        logger.error(f"Error downloading data for {ticker}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@download_bp.route('/batch-download', methods=['POST'])
def batch_download():
    """Download data for multiple tickers."""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        source = data.get('source', 'yahoo')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not tickers:
            return jsonify({'error': 'No tickers provided'}), 400
        
        results = []
        errors = []
        
        for ticker in tickers:
            try:
                # Use the single download logic
                download_data = {
                    'ticker': ticker,
                    'source': source,
                    'start_date': start_date,
                    'end_date': end_date
                }
                
                # Simulate the download call
                if source == 'yahoo':
                    from redline.downloaders.yahoo_downloader import YahooDownloader
                    downloader = YahooDownloader()
                    result = downloader.download_single_ticker(
                        ticker=ticker,
                        start_date=start_date,
                        end_date=end_date
                    )
                else:
                    result = None
                
                if result is not None and not result.empty:
                    filename = f"{ticker}_{source}_{start_date}_to_{end_date}.csv"
                    filepath = f"data/downloaded/{filename}"
                    result.to_csv(filepath, index=True)
                    
                    results.append({
                        'ticker': ticker,
                        'success': True,
                        'records': len(result),
                        'filename': filename
                    })
                else:
                    errors.append({
                        'ticker': ticker,
                        'error': 'No data found'
                    })
                    
            except Exception as e:
                errors.append({
                    'ticker': ticker,
                    'error': str(e)
                })
        
        return jsonify({
            'message': f'Batch download completed. {len(results)} successful, {len(errors)} failed.',
            'results': results,
            'errors': errors,
            'total_requested': len(tickers),
            'successful': len(results),
            'failed': len(errors)
        })
        
    except Exception as e:
        logger.error(f"Error in batch download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@download_bp.route('/history')
def get_download_history():
    """Get download history."""
    try:
        import os
        import glob
        
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

@download_bp.route('/validate-ticker', methods=['POST'])
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
                'source': siurce,
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
