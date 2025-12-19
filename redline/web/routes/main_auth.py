"""
Main authentication routes for VarioSync Web GUI
Handles user registration and login with Supabase Auth
"""

from flask import Blueprint, request, jsonify, g
import logging
from redline.auth.supabase_auth import supabase_auth

main_auth_bp = Blueprint('main_auth', __name__)
logger = logging.getLogger(__name__)


@main_auth_bp.route('/api/register', methods=['POST'])
def register():
    """Register new user with Supabase"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Register user with Supabase
        result = supabase_auth.register(
            email=data['email'],
            password=data['password'],
            name=data.get('name'),
            company=data.get('company')
        )

        logger.info(f"User registered successfully: {data['email']}")

        return jsonify({
            'success': True,
            'user_id': result['user_id'],
            'email': result['email'],
            'access_token': result['access_token'],
            'message': 'Registration successful. Please purchase hours to start using the service.'
        }), 201

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return jsonify({'error': str(e)}), 400


@main_auth_bp.route('/api/login', methods=['POST'])
def login():
    """Login with Supabase (email/password)"""
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        # Login via Supabase
        result = supabase_auth.login(data['email'], data['password'])

        # Get user's remaining hours
        hours = supabase_auth.get_user_hours(result['user_id'])

        logger.info(f"User logged in successfully: {data['email']}")

        return jsonify({
            'success': True,
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token'],
            'user_id': result['user_id'],
            'email': result['email'],
            'hours_remaining': hours
        }), 200

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify({'error': 'Invalid email or password'}), 401


@main_auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """Logout user (client should discard tokens)"""
    # Note: Supabase tokens are JWT-based and stateless
    # Client should simply discard the token
    # We can track logout in DuckDB if needed
    try:
        if hasattr(g, 'user_id'):
            logger.info(f"User logged out: {g.user_id}")

        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': str(e)}), 500
