#!/usr/bin/env python3
"""
Payment balance and history routes for VarioSync Web GUI
Handles balance retrieval and payment/usage history
"""

from flask import Blueprint, request, jsonify, current_app, g
import logging

from redline.auth.supabase_auth import supabase_auth

payments_balance_bp = Blueprint('payments_balance', __name__)
logger = logging.getLogger(__name__)

# Rate limit: 1000 per hour (balance is polled frequently)
@payments_balance_bp.route('/balance', methods=['GET'])
def get_balance():
    """Get remaining hours balance for authenticated user"""
    try:
        # User ID comes from JWT (set by middleware)
        user_id = g.user_id

        # Get hours from Supabase
        from redline.auth.supabase_config import supabase_admin
        hours_data = supabase_admin.table('user_hours').select('*').eq('user_id', str(user_id)).single().execute()

        result = {
            'success': True,
            'hours_remaining': hours_data.data.get('hours_remaining', 0.0),
            'total_hours_purchased': hours_data.data.get('total_hours_purchased', 0.0),
            'total_hours_used': hours_data.data.get('total_hours_used', 0.0)
        }

        # Add usage statistics from DuckDB if available
        try:
            from redline.database.usage_storage import usage_storage
            if usage_storage:
                stats = usage_storage.get_access_stats(user_id, days=30)
                result['usage_stats'] = stats
        except Exception as e:
            logger.debug(f"Failed to get usage stats: {str(e)}")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting balance: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False,
            'hours_remaining': 0.0,
            'total_hours_purchased': 0.0,
            'total_hours_used': 0.0
        }), 500

@payments_balance_bp.route('/history', methods=['GET'])
def get_history():
    """Get usage and payment history for authenticated user"""
    try:
        # User ID comes from JWT (set by middleware)
        user_id = g.user_id
        history_type = request.args.get('type', 'all')  # 'all', 'usage', 'payment'

        result = {
            'usage_history': [],
            'payment_history': [],
            'session_history': []
        }

        # Get usage history from DuckDB storage
        try:
            from redline.database.usage_storage import usage_storage
            if usage_storage:
                if history_type in ('all', 'usage'):
                    result['usage_history'] = usage_storage.get_usage_history(user_id, limit=100)
                    result['session_history'] = usage_storage.get_session_history(user_id, limit=50)

                if history_type in ('all', 'payment'):
                    result['payment_history'] = usage_storage.get_payment_history(user_id, limit=50)

                # Calculate totals
                total_used = sum(h.get('hours_deducted', 0) for h in result['usage_history'])
                total_purchased = sum(p.get('hours_purchased', 0) for p in result['payment_history'])

                result['totals'] = {
                    'total_hours_used': total_used,
                    'total_hours_purchased': total_purchased,
                    'total_payments': len(result['payment_history']),
                    'total_sessions': len(result['session_history'])
                }
        except Exception as e:
            logger.warning(f"Failed to get history from storage: {str(e)}")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'error': str(e)}), 500

