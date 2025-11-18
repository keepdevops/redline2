"""
Download sources endpoint.
Handles retrieval of available data sources.
"""

import os
from flask import Blueprint, jsonify
import logging

download_sources_bp = Blueprint('download_sources', __name__)
logger = logging.getLogger(__name__)

@download_sources_bp.route('/sources')
def get_sources():
    """Get available data sources."""
    try:
        sources = {
            'yahoo': {
                'name': 'Yahoo Finance',
                'description': 'Free financial data from Yahoo Finance',
                'supported_tickers': 'US and international stocks, ETFs, indices',
                'data_types': ['OHLCV', 'dividends', 'splits'],
                'delay': '15-20 minutes for real-time data',
                'rate_limit': 'Rate limited - may fail frequently',
                'api_key_required': False
            },
            'stooq': {
                'name': 'Stooq',
                'description': 'Free historical financial data',
                'supported_tickers': 'Global stocks and indices',
                'data_types': ['OHLCV'],
                'delay': 'End of day',
                'rate_limit': 'May require 2FA',
                'api_key_required': False
            },
            'alpha_vantage': {
                'name': 'Alpha Vantage',
                'description': 'Professional financial data API',
                'supported_tickers': 'US and international stocks',
                'data_types': ['OHLCV', 'fundamentals', 'news'],
                'delay': 'Real-time',
                'rate_limit': '5 calls per minute (free tier)',
                'api_key_required': True,
                'api_key_url': 'https://www.alphavantage.co/support/#api-key'
            },
            'finnhub': {
                'name': 'Finnhub',
                'description': 'Global financial data API',
                'supported_tickers': 'Global stocks, forex, crypto',
                'data_types': ['OHLCV', 'fundamentals', 'news'],
                'delay': 'Real-time',
                'rate_limit': '60 calls per minute (free tier)',
                'api_key_required': True,
                'api_key_url': 'https://finnhub.io/register'
            },
            'csv': {
                'name': 'CSV Files',
                'description': 'Local CSV files and sample data',
                'supported_tickers': 'Any ticker (creates sample data)',
                'data_types': ['OHLCV'],
                'delay': 'Instant',
                'rate_limit': 'No limits',
                'api_key_required': False,
                'note': 'Uses existing CSV files or creates sample data'
            }
        }
        
        # Load custom API configurations
        custom_apis_file = 'data/custom_apis.json'
        if os.path.exists(custom_apis_file):
            import json
            try:
                with open(custom_apis_file, 'r') as f:
                    custom_apis = json.load(f)
                    for api_id, api_config in custom_apis.items():
                        # Only include if it has required fields
                        if api_config.get('name') and api_config.get('base_url') and api_config.get('endpoint'):
                            source_key = f'custom_{api_id}'
                            sources[source_key] = {
                                'name': api_config.get('name', 'Custom API'),
                                'description': api_config.get('description', 'Custom financial data API'),
                                'supported_tickers': api_config.get('supported_tickers', 'Varies by API'),
                                'data_types': api_config.get('data_types', ['OHLCV']),
                                'delay': api_config.get('delay', 'Varies'),
                                'rate_limit': f"{api_config.get('rate_limit_per_minute', 60)} calls per minute",
                                'api_key_required': True,
                                'custom': True,
                                'api_id': api_id
                            }
            except Exception as e:
                logger.warning(f"Error loading custom APIs: {str(e)}")
        
        return jsonify({'sources': sources})
        
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}")
        return jsonify({'error': str(e)}), 500

