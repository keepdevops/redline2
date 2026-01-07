"""
Main authentication routes for VarioSync Web GUI
Handles user registration with Supabase and Stripe
"""

from flask import Blueprint, request, jsonify, g
import logging
import os

main_auth_bp = Blueprint('main_auth', __name__)
logger = logging.getLogger(__name__)

# Note: register route is defined in main.py as an alias
# to maintain backward compatibility with templates using url_for('main.register')

@main_auth_bp.route('/api/register', methods=['POST'])
def create_license_proxy():
    """
    DEPRECATED: Old license key registration endpoint.
    Use /auth/signup for new Supabase-based registration.
    """
    return jsonify({
        'error': 'This endpoint is deprecated',
        'message': 'Please use /auth/signup for registration with Supabase Auth',
        'redirect': '/auth/signup'
    }), 410  # 410 Gone

@main_auth_bp.route('/api/signup', methods=['POST'])
def signup():
    """Register new user with Supabase Auth and create Stripe customer"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        company = data.get('company', '')

        # Import Supabase client
        try:
            from redline.database.supabase_client import supabase_client
        except ImportError:
            logger.error("Supabase client not available")
            return jsonify({'error': 'Authentication system not available'}), 503

        # Create user in Supabase
        try:
            user = supabase_client.create_user(email, password, {
                'name': name,
                'company': company
            })
            logger.info(f"Created Supabase user: {email}")
        except Exception as e:
            logger.error(f"Failed to create Supabase user: {str(e)}")
            return jsonify({'error': f'Registration failed: {str(e)}'}), 400

        # Create Stripe customer
        try:
            import stripe
            stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

            stripe_customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    'supabase_user_id': user['id'],
                    'company': company
                }
            )
            logger.info(f"Created Stripe customer: {stripe_customer.id}")

            # Update Supabase user with Stripe customer ID
            supabase_client.update_user(user['id'], {
                'stripe_customer_id': stripe_customer.id
            })

        except ImportError:
            logger.error("Stripe library not installed")
            # Continue without Stripe - user can still sign up
            stripe_customer = None
        except Exception as e:
            logger.error(f"Failed to create Stripe customer: {str(e)}")
            # Continue without Stripe - user can still sign up
            stripe_customer = None

        # Send welcome email
        try:
            send_welcome_email(email, name)
        except Exception as e:
            logger.warning(f"Failed to send welcome email: {str(e)}")
            # Don't fail registration if email fails

        return jsonify({
            'success': True,
            'user_id': user['id'],
            'email': email,
            'stripe_customer_id': stripe_customer.id if stripe_customer else None,
            'message': 'Registration successful! Please log in to subscribe.'
        }), 201

    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


def send_welcome_email(email, name):
    """Send welcome email to new user"""
    try:
        # Check if email is enabled
        smtp_enabled = os.environ.get('SMTP_ENABLED', 'false').lower() == 'true'
        if not smtp_enabled:
            logger.info(f"Email not enabled. Welcome email for {email}")
            return

        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # SMTP configuration
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_user = os.environ.get('SMTP_USER', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '')
        from_email = os.environ.get('FROM_EMAIL', smtp_user)

        if not smtp_user or not smtp_password:
            logger.warning("SMTP credentials not configured. Skipping email.")
            return

        # Create email
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = email
        msg['Subject'] = 'Welcome to VarioSync!'

        # Email body
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to VarioSync!</h2>
            <p>Dear {name},</p>
            <p>Thank you for signing up with VarioSync.</p>
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Log in to your account</li>
                <li>Subscribe to VarioSync to start using the platform</li>
                <li>Upload your data and start analyzing!</li>
            </ol>
            <p>VarioSync uses subscription-based pricing with metered billing, so you only pay for what you use.</p>
            <p>If you have any questions, please contact support.</p>
            <p>Best regards,<br>The VarioSync Team</p>
        </body>
        </html>
        """

        text_body = f"""
Welcome to VarioSync!

Dear {name},

Thank you for signing up with VarioSync.

Next Steps:
1. Log in to your account
2. Subscribe to VarioSync to start using the platform
3. Upload your data and start analyzing!

VarioSync uses subscription-based pricing with metered billing, so you only pay for what you use.

If you have any questions, please contact support.

Best regards,
The VarioSync Team
        """

        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Welcome email sent to {email}")

    except ImportError:
        logger.warning("Email libraries not available")
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")
        # Don't raise - email failure shouldn't block registration
