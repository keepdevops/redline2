#!/usr/bin/env python3
"""
Payment balance and history routes for REDLINE Web GUI
Handles balance retrieval and payment/usage history
"""

from flask import Blueprint, request, jsonify
import logging
import os
import requests

from redline.payment.config import PaymentConfig
from redline.web.utils.api_helpers import rate_limit

payments_balance_bp = Blueprint('payments_balance', __name__)
logger = logging.getLogger(__name__)

# Rate limit: 1000 per hour (balance is polled frequently)
@payments_balance_bp.route('/balance', methods=['GET'])
@rate_limit("1000 per hour")
def get_balance():
    """Get remaining hours balance for a license"""
    try:
        license_key = request.args.get('license_key') or request.headers.get('X-License-Key')
        
        if not license_key:
            return jsonify({'error': 'License key is required'}), 400
        
        # Validate license before getting balance
        license_server_url = PaymentConfig.LICENSE_SERVER_URL
        require_license_server = os.environ.get('REQUIRE_LICENSE_SERVER', 'false').lower() == 'true'
        
        try:
            validate_response = requests.post(
                f'{license_server_url}/api/licenses/{license_key}/validate',
                json={},
                timeout=5
            )
            
            # License server returns 200 or 400 for validation responses
            if validate_response.status_code in (200, 400):
                try:
                    validation_result = validate_response.json()
                    if not validation_result.get('valid'):
                        error_msg = validation_result.get('error', 'Invalid license')
                        if 'inactive' in error_msg.lower():
                            return jsonify({
                                'error': 'License is inactive',
                                'success': False,
                                'hours_remaining': 0.0,
                                'used_hours': 0.0,
                                'purchased_hours': 0.0
                            }), 403
                except:
                    # If response is not JSON, check status code
                    if validate_response.status_code == 400:
                        return jsonify({
                            'error': 'License validation failed',
                            'success': False,
                            'hours_remaining': 0.0,
                            'used_hours': 0.0,
                            'purchased_hours': 0.0
                        }), 403
        except requests.exceptions.ConnectionError:
            # License server unavailable - skip validation if not required
            if not require_license_server:
                logger.debug(f"License server unavailable, skipping validation for {license_key}")
                # Continue to get balance anyway
            else:
                return jsonify({
                    'error': 'License server unavailable',
                    'success': False,
                    'hours_remaining': 0.0,
                    'used_hours': 0.0,
                    'purchased_hours': 0.0
                }), 503
        except Exception as e:
            logger.warning(f"Could not validate license: {str(e)}")
            # Continue to get balance anyway
        
        # Get hours from license server
        try:
            response = requests.get(
                f'{license_server_url}/api/licenses/{license_key}/hours',
                timeout=10
            )
        except requests.exceptions.ConnectionError:
            # License server unavailable - return local/default value
            if not require_license_server:
                logger.debug(f"License server unavailable, returning default balance for {license_key}")
                # For dev licenses, return 0 hours with success flag
                if license_key.startswith('RL-DEV-'):
                    # Try to get usage stats from local storage
                    result = {
                        'success': True,
                        'hours_remaining': 0.0,
                        'used_hours': 0.0,
                        'purchased_hours': 0.0,
                        'message': 'License server unavailable - using local tracking'
                    }
                    try:
                        from redline.database.usage_storage import usage_storage
                        if usage_storage:
                            stats = usage_storage.get_access_stats(license_key, days=30)
                            result['usage_stats'] = stats
                            # Get total used hours from history
                            history = usage_storage.get_usage_history(license_key, limit=1000)
                            total_used = sum(h.get('hours_deducted', 0) for h in history)
                            if total_used > 0:
                                result['used_hours'] = total_used
                    except Exception as e:
                        logger.debug(f"Failed to get usage stats: {str(e)}")
                    
                    return jsonify(result), 200
                return jsonify({
                    'success': False, 
                    'error': 'License server unavailable',
                    'hours_remaining': 0.0,
                    'used_hours': 0.0,
                    'purchased_hours': 0.0
                }), 503
            else:
                return jsonify({
                    'success': False, 
                    'error': 'License server unavailable',
                    'hours_remaining': 0.0,
                    'used_hours': 0.0,
                    'purchased_hours': 0.0
                }), 503
        
        # Handle non-200 responses - for dev licenses, return default
        if response.status_code != 200:
            if license_key.startswith('RL-DEV-') and not require_license_server:
                logger.debug(f"License server returned {response.status_code} for dev license, using local tracking")
                result = {
                    'success': True,
                    'hours_remaining': 0.0,
                    'used_hours': 0.0,
                    'purchased_hours': 0.0,
                    'message': 'License not found on server - using local tracking'
                }
                try:
                    from redline.database.usage_storage import UsageStorage
                    usage_storage = UsageStorage()
                    if usage_storage:
                        stats = usage_storage.get_access_stats(license_key, days=30)
                        result['usage_stats'] = stats
                        history = usage_storage.get_usage_history(license_key, limit=1000)
                        total_used = sum(h.get('hours_deducted', 0) for h in history)
                        if total_used > 0:
                            result['used_hours'] = total_used
                except Exception as e:
                    logger.debug(f"Failed to get usage stats: {str(e)}")
                
                return jsonify(result), 200
        
        if response.status_code == 200:
            result = response.json()
            
            # Ensure success flag is set
            if 'success' not in result:
                result['success'] = True
            
            # Ensure all required hours fields are included in response
            # The license server should return: hours_remaining, purchased_hours, used_hours
            if 'purchased_hours' not in result:
                result['purchased_hours'] = 0.0
            if 'hours_remaining' not in result:
                result['hours_remaining'] = 0.0
            if 'used_hours' not in result:
                result['used_hours'] = 0.0
            
            # Add usage statistics if storage is available
            try:
                from redline.database.usage_storage import UsageStorage
                usage_storage = UsageStorage()
                if usage_storage:
                    stats = usage_storage.get_access_stats(license_key, days=30)
                    result['usage_stats'] = stats
                    # Also get total used hours from history if not already set
                    if 'used_hours' not in result or result.get('used_hours', 0) == 0:
                        history = usage_storage.get_usage_history(license_key, limit=1000)
                        total_used = sum(h.get('hours_deducted', 0) for h in history)
                        if total_used > 0:
                            result['used_hours'] = total_used
            except Exception as e:
                logger.debug(f"Failed to get usage stats: {str(e)}")
            
            return jsonify(result), 200
        elif response.status_code == 404:
            # License not found - return default for dev licenses
            if license_key.startswith('RL-DEV-'):
                return jsonify({
                    'success': True,
                    'hours_remaining': 0.0,
                    'used_hours': 0.0,
                    'purchased_hours': 0.0,
                    'message': 'License not found on server - using local tracking'
                }), 200
            return jsonify({
                'success': False, 
                'error': 'License not found',
                'hours_remaining': 0.0,
                'used_hours': 0.0,
                'purchased_hours': 0.0
            }), 404
        else:
            # Try to return a helpful error message
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'Failed to retrieve balance')
                return jsonify({
                    'success': False, 
                    'error': error_msg,
                    'hours_remaining': 0.0,
                    'used_hours': 0.0,
                    'purchased_hours': 0.0
                }), response.status_code
            except:
                return jsonify({
                    'success': False, 
                    'error': f'Failed to retrieve balance (status: {response.status_code})',
                    'hours_remaining': 0.0,
                    'used_hours': 0.0,
                    'purchased_hours': 0.0
                }), 500
        
    except Exception as e:
        logger.error(f"Error getting balance: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False,
            'hours_remaining': 0.0,
            'used_hours': 0.0,
            'purchased_hours': 0.0
        }), 500

@payments_balance_bp.route('/history', methods=['GET'])
def get_history():
    """Get usage and payment history for a license"""
    try:
        license_key = request.args.get('license_key') or request.headers.get('X-License-Key')
        history_type = request.args.get('type', 'all')  # 'all', 'usage', 'payment'
        
        if not license_key:
            return jsonify({'error': 'License key is required'}), 400
        
        result = {
            'usage_history': [],
            'payment_history': [],
            'session_history': []
        }
        
        # Get usage history from storage
        try:
            from redline.database.usage_storage import UsageStorage
            usage_storage = UsageStorage()
            if usage_storage:
                if history_type in ('all', 'usage'):
                    result['usage_history'] = usage_storage.get_usage_history(license_key, limit=100)
                    result['session_history'] = usage_storage.get_session_history(license_key, limit=50)
                
                if history_type in ('all', 'payment'):
                    result['payment_history'] = usage_storage.get_payment_history(license_key, limit=50)
                
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

