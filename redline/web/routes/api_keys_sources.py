#!/usr/bin/env python3
"""
API Keys sources routes for REDLINE Web GUI
Provides information about API sources and how to get keys
"""

from flask import Blueprint, jsonify
import logging

api_keys_sources_bp = Blueprint('api_keys_sources', __name__)
logger = logging.getLogger(__name__)

@api_keys_sources_bp.route('/sources')
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
            },
            'massive': {
                'name': 'Massive.com',
                'website': 'https://massive.com',
                'signup_url': 'https://massive.com',
                'free_tier': '5 calls per minute',
                'features': [
                    'Real-time stock data',
                    'Historical data',
                    'Trade-level data',
                    'Quote-level data',
                    'Fundamental data',
                    'SQL query interface',
                    'WebSocket streaming',
                    'All U.S. exchanges',
                    'Dark pool data',
                    'OTC market data',
                    'Options, indices, currencies, futures'
                ],
                'coverage': 'All U.S. exchanges, dark pools, OTC markets',
                'data_types': ['OHLCV', 'trades', 'quotes', 'fundamentals', 'options', 'indices'],
                'rate_limit': 'Free: 5 calls/min, Paid: <100 calls/sec',
                'daily_limit': 'Varies by plan',
                'signup_steps': [
                    'Visit Massive.com website',
                    'Sign up for an account',
                    'Navigate to API Keys section',
                    'Generate a new API key',
                    'Copy your API key',
                    'Paste it in REDLINE settings'
                ],
                'pros': [
                    'Comprehensive market data',
                    'Real-time and historical',
                    'Multiple access methods (REST, WebSocket, SQL)',
                    'High quality, standardized data',
                    'All U.S. exchanges coverage',
                    'Dark pool and OTC data',
                    'SQL interface for custom queries'
                ],
                'cons': [
                    'API key required',
                    'Free tier has low rate limits (5/min)',
                    'Paid plans required for production use'
                ]
            }
        }
        
        return jsonify({'sources': sources})
        
    except Exception as e:
        logger.error(f"Error getting API sources: {str(e)}")
        return jsonify({'error': str(e)}), 500

