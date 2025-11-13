#!/usr/bin/env python3
"""
Payment routes for REDLINE Web GUI
Handles Stripe payment processing, checkout, and webhooks
"""

from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, session as flask_session
import logging
import os
import requests
from datetime import datetime

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

from redline.payment.config import PaymentConfig

payments_bp = Blueprint('payments', __name__)
logger = logging.getLogger(__name__)

# Initialize Stripe if available
if STRIPE_AVAILABLE and PaymentConfig.STRIPE_SECRET_KEY:
    stripe.api_key = PaymentConfig.STRIPE_SECRET_KEY

@payments_bp.route('/create-checkout', methods=['POST'])
def create_checkout():
    """Create Stripe checkout session for purchasing hours"""
    if not STRIPE_AVAILABLE:
        return jsonify({'error': 'Stripe is not available. Please install stripe package.'}), 503
    
    if not PaymentConfig.validate():
        return jsonify({'error': 'Payment configuration is invalid. Please set STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY.'}), 500
    
    try:
        data = request.get_json()
        hours = data.get('hours')
        package_id = data.get('package_id')
        license_key = data.get('license_key')
        
        if not license_key:
            return jsonify({'error': 'License key is required'}), 400
        
        # Validate license (check status, etc.)
        try:
            import requests
            license_server_url = PaymentConfig.LICENSE_SERVER_URL
            validate_response = requests.post(
                f'{license_server_url}/api/licenses/{license_key}/validate',
                json={},
                timeout=5
            )
            
            # Check response - license server may return 200 or 400 for invalid licenses
            if validate_response.status_code in (200, 400):
                try:
                    validation_result = validate_response.json()
                    if not validation_result.get('valid'):
                        error_msg = validation_result.get('error', 'Invalid license')
                        # Allow purchase even if hours = 0 (user is buying more)
                        # But block if inactive
                        if 'inactive' in error_msg.lower():
                            return jsonify({'error': 'License is inactive. Please contact support.'}), 403
                        elif 'invalid' in error_msg.lower():
                            return jsonify({'error': 'Invalid license key'}), 403
                        # If error is just "No hours remaining", allow purchase
                except:
                    # If response is not JSON, check status code
                    if validate_response.status_code == 400:
                        # Likely an invalid/expired license
                        return jsonify({'error': 'License validation failed. Please check your license key.'}), 403
            else:
                logger.warning(f"License validation failed: {validate_response.status_code}")
                # Continue anyway - license server might be down
        except Exception as e:
            logger.warning(f"Could not validate license: {str(e)}")
            # Continue anyway - don't block payment if validation fails
        
        # Get package info or calculate from hours
        if package_id:
            package = PaymentConfig.get_package_info(package_id)
            if not package:
                return jsonify({'error': 'Invalid package ID'}), 400
            hours = package['hours']
            price_cents = int(package['price'] * 100)
        elif hours:
            price_cents = int(PaymentConfig.calculate_price_from_hours(hours) * 100)
        else:
            return jsonify({'error': 'Either hours or package_id is required'}), 400
        
        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': PaymentConfig.CURRENCY,
                        'product_data': {
                            'name': f'{hours} Hours of REDLINE Access',
                            'description': f'Purchase {hours} hours of access time for REDLINE'
                        },
                        'unit_amount': price_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.host_url.rstrip('/') + '/payments/success?session_id={CHECKOUT_SESSION_ID}&license_key=' + license_key,
                cancel_url=request.host_url.rstrip('/') + '/payments/cancel',
                metadata={
                    'license_key': license_key,
                    'hours': str(hours),
                    'package_id': package_id or ''
                }
            )
            
            return jsonify({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }), 200
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return jsonify({'error': f'Payment processing error: {str(e)}'}), 500
        
    except Exception as e:
        logger.error(f"Error creating checkout: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/success', methods=['GET'])
def payment_success():
    """Handle successful payment and redirect to dashboard"""
    try:
        session_id = request.args.get('session_id')
        license_key = request.args.get('license_key')
        
        if not session_id or not STRIPE_AVAILABLE:
            return render_template('payment_success.html', 
                                 success=False, 
                                 error='Invalid session',
                                 license_key=license_key), 400
        
        # Retrieve checkout session
        try:
            try:
                session = stripe.checkout.Session.retrieve(session_id)
            except Exception as stripe_err:
                # Handle Stripe API errors (invalid session, network issues, etc.)
                error_msg = str(stripe_err) if str(stripe_err) else 'Invalid payment session'
                logger.error(f"Stripe API error: {error_msg}")
                return render_template('payment_success.html',
                                     success=False,
                                     error=f'Payment verification error: {error_msg}',
                                     license_key=license_key or ''), 400
            
            if session.payment_status == 'paid':
                # Get hours from metadata
                hours = float(session.metadata.get('hours', 0))
                
                # Add hours to license via license server
                license_server_url = PaymentConfig.LICENSE_SERVER_URL
                response = requests.post(
                    f'{license_server_url}/api/licenses/{license_key}/hours',
                    json={'hours': hours},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    hours_remaining = result.get('hours_remaining', 0)
                    
                    # Log payment to persistent storage
                    try:
                        from redline.database.usage_storage import usage_storage, STORAGE_AVAILABLE
                        if STORAGE_AVAILABLE and usage_storage:
                            usage_storage.log_payment(
                                license_key=license_key,
                                hours_purchased=hours,
                                amount_paid=session.amount_total / 100.0,  # Convert cents to dollars
                                stripe_session_id=session_id,
                                payment_id=session.payment_intent,
                                payment_status='completed',
                                currency=session.currency
                            )
                    except Exception as e:
                        logger.warning(f"Failed to log payment to storage: {str(e)}")
                    
                    # Store license key in session for dashboard access
                    flask_session['license_key'] = license_key
                    flask_session['hours_remaining'] = hours_remaining
                    flask_session.permanent = True
                    
                    # Render success page that auto-redirects to dashboard
                    return render_template('payment_success.html',
                                         success=True,
                                         hours_added=hours,
                                         hours_remaining=hours_remaining,
                                         license_key=license_key)
                else:
                    logger.error(f"Failed to add hours to license: {response.text}")
                    return render_template('payment_success.html',
                                         success=False,
                                         error='Payment successful but failed to add hours. Please contact support.',
                                         license_key=license_key), 500
            else:
                return render_template('payment_success.html',
                                     success=False,
                                     error='Payment not completed',
                                     license_key=license_key), 400
                
        except Exception as e:
            error_msg = str(e) if str(e) else 'Unknown error occurred'
            logger.error(f"Error processing payment success: {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return render_template('payment_success.html',
                                 success=False,
                                 error=error_msg,
                                 license_key=license_key or ''), 500
        
    except Exception as e:
        error_msg = str(e) if str(e) else 'Unknown error occurred'
        logger.error(f"Error in payment_success: {error_msg}")
        import traceback
        logger.error(traceback.format_exc())
        return render_template('payment_success.html',
                             success=False,
                             error=error_msg,
                             license_key=request.args.get('license_key', '')), 500

@payments_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    if not STRIPE_AVAILABLE:
        logger.warning("Stripe webhook received but Stripe is not available")
        return jsonify({'error': 'Stripe is not available'}), 503
    
    if not PaymentConfig.STRIPE_WEBHOOK_SECRET:
        logger.warning("Stripe webhook received but STRIPE_WEBHOOK_SECRET is not set")
        return jsonify({'error': 'Webhook secret not configured'}), 500
    
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, PaymentConfig.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        license_key = session['metadata'].get('license_key')
        hours = float(session['metadata'].get('hours', 0))
        
        if license_key and hours > 0:
            # Add hours to license
            license_server_url = PaymentConfig.LICENSE_SERVER_URL
            try:
                response = requests.post(
                    f'{license_server_url}/api/licenses/{license_key}/hours',
                    json={'hours': hours},
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                    
                    # Log payment to persistent storage
                    try:
                        from redline.database.usage_storage import usage_storage, STORAGE_AVAILABLE
                        if STORAGE_AVAILABLE and usage_storage:
                            usage_storage.log_payment(
                                license_key=license_key,
                                hours_purchased=hours,
                                amount_paid=session.get('amount_total', 0) / 100.0,  # Convert cents to dollars
                                stripe_session_id=session.get('id'),
                                payment_id=session.get('payment_intent'),
                                payment_status='completed',
                                currency=session.get('currency', 'usd')
                            )
                    except Exception as e:
                        logger.warning(f"Failed to log payment to storage: {str(e)}")
                    
                    logger.info(f"Added {hours} hours to license {license_key} via webhook")
                else:
                    logger.error(f"Failed to add hours via webhook: {response.text}")
            except Exception as e:
                logger.error(f"Error adding hours via webhook: {str(e)}")
    
    return jsonify({'received': True}), 200

@payments_bp.route('/balance', methods=['GET'])
def get_balance():
    """Get remaining hours balance for a license"""
    try:
        license_key = request.args.get('license_key') or request.headers.get('X-License-Key')
        
        if not license_key:
            return jsonify({'error': 'License key is required'}), 400
        
        # Validate license before getting balance
        license_server_url = PaymentConfig.LICENSE_SERVER_URL
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
                            return jsonify({'error': 'License is inactive'}), 403
                except:
                    # If response is not JSON, check status code
                    if validate_response.status_code == 400:
                        return jsonify({'error': 'License validation failed'}), 403
        except Exception as e:
            logger.warning(f"Could not validate license: {str(e)}")
            # Continue to get balance anyway
        
        # Get hours from license server
        response = requests.get(
            f'{license_server_url}/api/licenses/{license_key}/hours',
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Ensure used_hours is included in response
            if 'used_hours' not in result and 'success' in result:
                # Get from license server if not in response
                hours_response = requests.get(
                    f'{license_server_url}/api/licenses/{license_key}/hours',
                    timeout=5
                )
                if hours_response.status_code == 200:
                    hours_data = hours_response.json()
                    if 'success' in hours_data and hours_data['success']:
                        result['used_hours'] = hours_data.get('used_hours', 0.0)
            
            # Add usage statistics if storage is available
            try:
                from redline.database.usage_storage import usage_storage, STORAGE_AVAILABLE
                if STORAGE_AVAILABLE and usage_storage:
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
            return jsonify({'error': 'License not found'}), 404
        else:
            return jsonify({'error': 'Failed to retrieve balance'}), 500
        
    except Exception as e:
        logger.error(f"Error getting balance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/history', methods=['GET'])
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
            from redline.database.usage_storage import usage_storage, STORAGE_AVAILABLE
            if STORAGE_AVAILABLE and usage_storage:
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

@payments_bp.route('/packages', methods=['GET'])
def get_packages():
    """Get available hour packages"""
    try:
        packages = []
        for package_id, package_info in PaymentConfig.HOUR_PACKAGES.items():
            packages.append({
                'id': package_id,
                'name': package_info['name'],
                'hours': package_info['hours'],
                'price': package_info['price'],
                'price_per_hour': package_info['price'] / package_info['hours']
            })
        
        return jsonify({
            'packages': packages,
            'currency': PaymentConfig.CURRENCY
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting packages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/')
def payment_tab():
    """Payment tab page"""
    from flask import render_template
    return render_template('payment_tab.html')

