#!/usr/bin/env python3
"""
API Keys management routes for REDLINE Web GUI
Helps users get free API keys for data sources
"""

from flask import Blueprint, render_template, request, jsonify, session
import logging
import os
from datetime import datetime

api_keys_bp = Blueprint('api_keys', __name__)
logger = logging.getLogger(__name__)

@api_keys_bp.route('/')
def api_keys_page():
    """API Keys management page."""
    return render_template('api_keys_page.html')

@api_keys_bp.route('/sources')
def get_api_sources():
    """Get information about API sources and how to get keys."""
    try:
        sources = {
            'alpha_vantage': {
                'name': 'Alpha Vantage',
                'website': 'https://www.alphavantage.co',
                'signup_url': 'https://www.alphavantage.co/support/#api-key',
                'free_tier': '5 calls per minute',
                'features': [
                    'Real-time stock data',
                    'Historical data',
                    'Technical indicators',
                    'Fundamental data',
                    'News sentiment',
                    'Forex data'
                ],
                'coverage': 'US and international stocks',
                'data_types': ['OHLCV', 'fundamentals', 'news', 'forex'],
                'rate_limit': '5 calls per minute',
                'daily_limit': '500 calls per day',
                'signup_steps': [
                    'Visit Alpha Vantage website',
                    'Click "Get Free API Key"',
                    'Fill out simple registration form',
                    'Verify email address',
                    'Copy your API key',
                    'Paste it in REDLINE settings'
                ],
                'pros': [
                    'High quality data',
                    'Comprehensive coverage',
                    'Good documentation',
                    'Reliable service'
                ],
                'cons': [
                    'Rate limited (5 calls/min)',
                    'Requires registration'
                ]
            },
            'finnhub': {
                'name': 'Finnhub',
                'website': 'https://finnhub.io',
                'signup_url': 'https://finnhub.io/register',
                'free_tier': '60 calls per minute',
                'features': [
                    'Real-time stock data',
                    'Historical data',
                    'Company fundamentals',
                    'News and sentiment',
                    'Cryptocurrency data',
                    'Forex data',
                    'Economic indicators'
                ],
                'coverage': 'Global stocks, forex, crypto',
                'data_types': ['OHLCV', 'fundamentals', 'news', 'crypto', 'forex'],
                'rate_limit': '60 calls per minute',
                'daily_limit': '1000 calls per day',
                'signup_steps': [
                    'Visit Finnhub website',
                    'Click "Get Free API Key"',
                    'Create account with email',
                    'Verify email address',
                    'Copy your API key',
                    'Paste it in REDLINE settings'
                ],
                'pros': [
                    'Higher rate limits',
                    'Global coverage',
                    'Crypto and forex data',
                    'Real-time data',
                    'Good API documentation'
                ],
                'cons': [
                    'Requires registration',
                    'Some advanced features are paid'
                ]
            },
            'yahoo_finance': {
                'name': 'Yahoo Finance',
                'website': 'https://finance.yahoo.com',
                'signup_url': None,
                'free_tier': 'No API key required',
                'features': [
                    'Historical stock data',
                    'Real-time quotes (delayed)',
                    'Company information',
                    'News and analysis'
                ],
                'coverage': 'US and international stocks',
                'data_types': ['OHLCV', 'fundamentals', 'news'],
                'rate_limit': 'Heavy rate limiting',
                'daily_limit': 'Unlimited but unreliable',
                'signup_steps': [
                    'No registration required',
                    'Built into REDLINE',
                    'May experience rate limiting',
                    'Consider upgrading to paid APIs'
                ],
                'pros': [
                    'No API key needed',
                    'Free to use',
                    'Good historical data'
                ],
                'cons': [
                    'Heavy rate limiting',
                    'Unreliable for batch downloads',
                    'No real-time data guarantee'
                ]
            },
            'stooq': {
                'name': 'Stooq',
                'website': 'https://stooq.com',
                'signup_url': 'https://stooq.com',
                'free_tier': 'Free historical data',
                'features': [
                    'Historical stock data',
                    'Global market coverage',
                    'End-of-day data',
                    'Multiple data formats'
                ],
                'coverage': 'Global stocks and indices',
                'data_types': ['OHLCV'],
                'rate_limit': 'May require 2FA',
                'daily_limit': 'Unlimited',
                'signup_steps': [
                    'Visit Stooq website',
                    'No registration required for basic data',
                    'May need to complete 2FA for downloads',
                    'Use manual download if automated fails'
                ],
                'pros': [
                    'Free historical data',
                    'Global coverage',
                    'No API key required'
                ],
                'cons': [
                    'May require 2FA',
                    'Manual download often needed',
                    'End-of-day data only'
                ]
            }
        }
        
        return jsonify({'sources': sources})
        
    except Exception as e:
        logger.error(f"Error getting API sources: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_keys_bp.route('/save', methods=['POST'])
def save_api_keys():
    """Save API keys to user session or config file."""
    try:
        data = request.get_json()
        api_keys = data.get('api_keys', {})
        
        # Validate API keys
        valid_keys = {}
        for source, key in api_keys.items():
            if key and key.strip():
                valid_keys[source] = key.strip()
        
        # Save to session (temporary)
        session['api_keys'] = valid_keys
        
        # Also save to a config file for persistence
        config_file = 'data/api_keys.json'
        os.makedirs('data', exist_ok=True)
        
        import json
        with open(config_file, 'w') as f:
            json.dump(valid_keys, f, indent=2)
        
        logger.info(f"Saved API keys for sources: {list(valid_keys.keys())}")
        
        return jsonify({
            'message': f'Successfully saved API keys for {len(valid_keys)} sources',
            'saved_sources': list(valid_keys.keys())
        })
        
    except Exception as e:
        logger.error(f"Error saving API keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_keys_bp.route('/load')
def load_api_keys():
    """Load saved API keys."""
    try:
        # Try to load from session first
        api_keys = session.get('api_keys', {})
        
        # Try to load from config file
        config_file = 'data/api_keys.json'
        if os.path.exists(config_file):
            import json
            with open(config_file, 'r') as f:
                file_keys = json.load(f)
                api_keys.update(file_keys)
        
        return jsonify({'api_keys': api_keys})
        
    except Exception as e:
        logger.error(f"Error loading API keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_keys_bp.route('/test', methods=['POST'])
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




