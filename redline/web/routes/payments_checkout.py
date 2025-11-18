#!/usr/bin/env python3
"""
Payment checkout routes for REDLINE Web GUI
Handles Stripe checkout session creation
"""

from flask import Blueprint, request, jsonify
import logging
import requests

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

from redline.payment.config import PaymentConfig

payments_checkout_bp = Blueprint('payments_checkout', __name__)
logger = logging.getLogger(__name__)

# Initialize Stripe if available
if STRIPE_AVAILABLE and PaymentConfig.STRIPE_SECRET_KEY:
    stripe.api_key = PaymentConfig.STRIPE_SECRET_KEY

@payments_checkout_bp.route('/create-checkout', methods=['POST'])
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

