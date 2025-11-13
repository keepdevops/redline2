"""
Main routes for REDLINE Web GUI
Provides the main dashboard and navigation
"""

from flask import Blueprint, render_template, request, jsonify, session
import logging
import os
import requests

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard with overview of all tabs."""
    return render_template('dashboard.html')

@main_bp.route('/help')
def help_page():
    """Help and documentation page."""
    return render_template('help.html')

@main_bp.route('/register')
def register():
    """User registration page to get a license key."""
    return render_template('register.html')

@main_bp.route('/test-button-clicks')
def test_button_clicks():
    """Test page for verifying license key inclusion in API calls."""
    from flask import send_from_directory
    import os
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'redline', 'web', 'static')
    return send_from_directory(static_dir, 'test_button_clicks.html')

@main_bp.route('/api/register', methods=['POST'])
def create_license_proxy():
    """Proxy endpoint for creating licenses (avoids CORS issues)"""
    try:
        import requests
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'company']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Get license server URL
        license_server_url = os.environ.get('LICENSE_SERVER_URL', 'http://localhost:5001')
        
        # Forward request to license server
        response = requests.post(
            f'{license_server_url}/api/licenses',
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            license_data = result.get('license', {})
            license_key = license_data.get('key')
            email = data.get('email')
            
            # Send email with license key
            try:
                send_license_email(email, license_key, data.get('name'), license_data)
            except Exception as e:
                logger.warning(f"Failed to send license email: {str(e)}")
                # Don't fail registration if email fails
            
            # Return response from license server
            return jsonify(result), 201
        else:
            # Return error response
            return jsonify(response.json()), response.status_code
        
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Could not connect to license server. Please try again later.'}), 503
    except Exception as e:
        logger.error(f"Error creating license: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

def send_license_email(email, license_key, name, license_data):
    """Send license key via email"""
    try:
        # Check if email is enabled
        smtp_enabled = os.environ.get('SMTP_ENABLED', 'false').lower() == 'true'
        if not smtp_enabled:
            logger.info(f"Email not enabled. License key for {email}: {license_key}")
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
        msg['Subject'] = 'Your REDLINE License Key'
        
        # Email body
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to REDLINE!</h2>
            <p>Dear {name},</p>
            <p>Thank you for registering with REDLINE. Your license key has been generated.</p>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Your License Key:</strong></p>
                <p style="font-size: 1.5em; font-weight: bold; color: #0d6efd; font-family: monospace;">{license_key}</p>
            </div>
            <p><strong>License Details:</strong></p>
            <ul>
                <li>Type: {license_data.get('type', 'trial').title()}</li>
                <li>Expires: {license_data.get('expires', 'N/A')}</li>
                <li>Hours Remaining: {license_data.get('hours_remaining', 0)}</li>
            </ul>
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Save this license key securely</li>
                <li>Go to the Payment tab to purchase hours</li>
                <li>Start using REDLINE!</li>
            </ol>
            <p>If you have any questions, please contact support.</p>
            <p>Best regards,<br>The REDLINE Team</p>
        </body>
        </html>
        """
        
        text_body = f"""
Welcome to REDLINE!

Dear {name},

Thank you for registering with REDLINE. Your license key has been generated.

Your License Key: {license_key}

License Details:
- Type: {license_data.get('type', 'trial').title()}
- Expires: {license_data.get('expires', 'N/A')}
- Hours Remaining: {license_data.get('hours_remaining', 0)}

Next Steps:
1. Save this license key securely
2. Go to the Payment tab to purchase hours
3. Start using REDLINE!

If you have any questions, please contact support.

Best regards,
The REDLINE Team
        """
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"License key email sent to {email}")
        
    except ImportError:
        logger.warning("Email libraries not available. Install with: pip install secure-smtplib")
    except Exception as e:
        logger.error(f"Error sending license email: {str(e)}")
        # Don't raise - email failure shouldn't block registration

@main_bp.route('/status')
def status():
    """Get application status."""
    try:
        status_data = {
            'status': 'running',
            'data_loader': 'available',
            'database': 'available',
            'supported_formats': ['csv', 'txt', 'parquet', 'feather', 'json', 'duckdb'],
            'version': '1.1.0'
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@main_bp.route('/health')
def health():
    """Health check endpoint for Docker."""
    return jsonify({'status': 'healthy', 'service': 'redline-web'})

@main_bp.route('/tasks')
def tasks_page():
    """Background tasks page."""
    return render_template('tasks_tab.html')

@main_bp.route('/data-modular')
def data_modular():
    """Modular data tab page."""
    return render_template('data_tab_modular.html')
