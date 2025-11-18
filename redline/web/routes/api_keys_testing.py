#!/usr/bin/env python3
"""
API Keys testing routes for REDLINE Web GUI
Handles testing API keys by making sample requests
"""

from flask import Blueprint, request, jsonify
import logging

api_keys_testing_bp = Blueprint('api_keys_testing', __name__)
logger = logging.getLogger(__name__)

@api_keys_testing_bp.route('/test', methods=['POST'])
def test_api_keys():
    """Test API keys by making a sample request."""
    try:
        data = request.get_json()
        source = data.get('source')
        api_key = data.get('api_key')
        
        if not source or not api_key:
            return jsonify({'error': 'Source and API key are required'}), 400
        
        # Test the API key
        test_result = None
        
        if source == 'alpha_vantage':
            test_result = _test_alpha_vantage_key(api_key)
        elif source == 'finnhub':
            test_result = _test_finnhub_key(api_key)
        else:
            return jsonify({'error': f'Testing not supported for {source}'}), 400
        
        return jsonify({
            'source': source,
            'valid': test_result['valid'],
            'message': test_result['message'],
            'rate_limit': test_result.get('rate_limit'),
            'daily_limit': test_result.get('daily_limit')
        })
        
    except Exception as e:
        logger.error(f"Error testing API key: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _test_alpha_vantage_key(api_key):
    """Test Alpha Vantage API key."""
    try:
        import requests
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': 'AAPL',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'Error Message' in data:
                return {
                    'valid': False,
                    'message': f"API Error: {data['Error Message']}"
                }
            elif 'Note' in data:
                return {
                    'valid': False,
                    'message': f"Rate Limited: {data['Note']}"
                }
            elif 'Time Series (Daily)' in data:
                return {
                    'valid': True,
                    'message': 'API key is valid and working!',
                    'rate_limit': '5 calls per minute',
                    'daily_limit': '500 calls per day'
                }
            else:
                return {
                    'valid': False,
                    'message': 'Unexpected response format'
                }
        else:
            return {
                'valid': False,
                'message': f'HTTP Error: {response.status_code}'
            }
            
    except Exception as e:
        return {
            'valid': False,
            'message': f'Connection error: {str(e)}'
        }

def _test_finnhub_key(api_key):
    """Test Finnhub API key."""
    try:
        import requests
        
        url = "https://finnhub.io/api/v1/quote"
        params = {
            'symbol': 'AAPL',
            'token': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data:
                return {
                    'valid': False,
                    'message': f"API Error: {data['error']}"
                }
            elif 'c' in data:  # 'c' is current price
                return {
                    'valid': True,
                    'message': 'API key is valid and working!',
                    'rate_limit': '60 calls per minute',
                    'daily_limit': '1000 calls per day'
                }
            else:
                return {
                    'valid': False,
                    'message': 'Unexpected response format'
                }
        else:
            return {
                'valid': False,
                'message': f'HTTP Error: {response.status_code}'
            }
            
    except Exception as e:
        return {
            'valid': False,
            'message': f'Connection error: {str(e)}'
        }

