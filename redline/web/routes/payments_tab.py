#!/usr/bin/env python3
"""
Payment tab routes for REDLINE Web GUI
Handles payment success page, packages, and main payment tab
"""

from flask import Blueprint, request, jsonify, render_template, session as flask_session
import logging
import os
import requests
import traceback

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

from redline.payment.config import PaymentConfig

payments_tab_bp = Blueprint('payments_tab', __name__)
logger = logging.getLogger(__name__)

# Initialize Stripe if available
if STRIPE_AVAILABLE and PaymentConfig.STRIPE_SECRET_KEY:
    stripe.api_key = PaymentConfig.STRIPE_SECRET_KEY

@payments_tab_bp.route('/success', methods=['GET'])
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
                require_license_server = os.environ.get('REQUIRE_LICENSE_SERVER', 'false').lower() == 'true'
                
                try:
                    response = requests.post(
                        f'{license_server_url}/api/licenses/{license_key}/hours',
                        json={'hours': hours},
                        timeout=10
                    )
                except requests.exceptions.ConnectionError:
                    # License server unavailable - log payment but can't add hours
                    if not require_license_server:
                        logger.warning(f"License server unavailable, payment processed but hours not added to server for {license_key}")
                        # Log payment anyway
                        try:
                            from redline.database.usage_storage import UsageStorage
                            usage_storage = UsageStorage()
                            if usage_storage:
                                usage_storage.log_payment(
                                    license_key=license_key,
                                    hours=hours,
                                    amount=session.amount_total / 100,
                                    currency=session.currency,
                                    payment_id=session.id,
                                    status='completed'
                                )
                        except Exception as e:
                            logger.warning(f"Failed to log payment: {str(e)}")
                        
                        return jsonify({
                            'success': True,
                            'message': f'Payment processed. {hours} hours will be added when license server is available.',
                            'hours': hours,
                            'license_key': license_key,
                            'warning': 'License server unavailable - hours not added yet'
                        }), 200
                    else:
                        return jsonify({'error': 'License server unavailable'}), 503
                
                if response.status_code == 200:
                    result = response.json()
                    hours_remaining = result.get('hours_remaining', 0)
                    
                    # Log payment to persistent storage
                    try:
                        from redline.database.usage_storage import UsageStorage
                        usage_storage = UsageStorage()
                        if usage_storage:
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
            logger.error(traceback.format_exc())
            return render_template('payment_success.html',
                                 success=False,
                                 error=error_msg,
                                 license_key=license_key or ''), 500
        
    except Exception as e:
        error_msg = str(e) if str(e) else 'Unknown error occurred'
        logger.error(f"Error in payment_success: {error_msg}")
        logger.error(traceback.format_exc())
        return render_template('payment_success.html',
                             success=False,
                             error=error_msg,
                             license_key=request.args.get('license_key', '')), 500

@payments_tab_bp.route('/packages', methods=['GET'])
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

# Note: payment_tab route is defined in payments.py as an alias
# to maintain backward compatibility with templates using url_for('payments.payment_tab')

