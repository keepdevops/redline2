"""
S3/R2 Direct Upload Routes
Handles direct uploads to S3/R2 storage, bypassing container storage.
Supports presigned URLs for browser-based uploads.
"""

from flask import Blueprint, request, jsonify
import logging
import os
from datetime import datetime, timedelta
from ..utils.api_helpers import rate_limit

s3_upload_bp = Blueprint('s3_upload', __name__)
logger = logging.getLogger(__name__)

# Initialize S3/R2 client if available
try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    boto3 = None
    ClientError = None

def get_s3_client():
    """Get configured S3/R2 client."""
    if not S3_AVAILABLE:
        return None
    
    endpoint_url = os.environ.get('S3_ENDPOINT_URL')
    access_key = os.environ.get('S3_ACCESS_KEY')
    secret_key = os.environ.get('S3_SECRET_KEY')
    region = os.environ.get('S3_REGION', 'us-east-1')
    
    if not all([access_key, secret_key]):
        logger.warning("S3 credentials not configured")
        return None
    
    client_config = {
        'aws_access_key_id': access_key,
        'aws_secret_access_key': secret_key,
        'region_name': region
    }
    
    if endpoint_url:
        client_config['endpoint_url'] = endpoint_url
    
    return boto3.client('s3', **client_config)

def get_s3_bucket():
    """Get S3/R2 bucket name from environment."""
    return os.environ.get('S3_BUCKET')

@s3_upload_bp.route('/presigned-url', methods=['POST'])
@rate_limit("20 per minute")
def get_presigned_url():
    """
    Generate a presigned URL for direct browser upload to S3/R2.
    This bypasses container storage and M3 Apple Silicon security restrictions.
    """
    try:
        if not S3_AVAILABLE:
            return jsonify({'error': 'S3/R2 not available. Install boto3.'}), 503
        
        data = request.get_json() or {}
        filename = data.get('filename')
        file_type = data.get('file_type', 'csv')
        license_key = data.get('license_key') or request.headers.get('X-License-Key')
        
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        
        if not license_key:
            return jsonify({'error': 'License key is required'}), 400
        
        # Generate S3 key based on license key (hashed for security)
        import hashlib
        key_hash = hashlib.sha256(license_key.encode()).hexdigest()[:16]
        s3_key = f"users/{key_hash}/files/{filename}"
        
        s3_client = get_s3_client()
        bucket = get_s3_bucket()
        
        if not s3_client or not bucket:
            return jsonify({'error': 'S3/R2 not configured. Set S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY.'}), 503
        
        # Generate presigned URL (valid for 1 hour)
        expiration = 3600  # 1 hour
        
        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': bucket,
                    'Key': s3_key,
                    'ContentType': f'application/{file_type}'
                },
                ExpiresIn=expiration
            )
            
            return jsonify({
                'success': True,
                'presigned_url': presigned_url,
                's3_key': s3_key,
                'bucket': bucket,
                'expires_in': expiration,
                'upload_url': presigned_url,
                'method': 'PUT'
            })
            
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            return jsonify({'error': f'Failed to generate upload URL: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error in get_presigned_url: {str(e)}")
        return jsonify({'error': str(e)}), 500

@s3_upload_bp.route('/direct-upload', methods=['POST'])
@rate_limit("10 per minute")
def direct_upload():
    """
    Upload file directly to S3/R2 via server.
    Alternative to presigned URLs for server-side uploads.
    """
    try:
        if not S3_AVAILABLE:
            return jsonify({'error': 'S3/R2 not available'}), 503
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        license_key = request.headers.get('X-License-Key') or request.form.get('license_key')
        if not license_key:
            return jsonify({'error': 'License key is required'}), 400
        
        # Generate S3 key
        import hashlib
        key_hash = hashlib.sha256(license_key.encode()).hexdigest()[:16]
        filename = file.filename
        s3_key = f"users/{key_hash}/files/{filename}"
        
        s3_client = get_s3_client()
        bucket = get_s3_bucket()
        
        if not s3_client or not bucket:
            return jsonify({'error': 'S3/R2 not configured'}), 503
        
        # Read file data
        file_data = file.read()
        file_type = os.path.splitext(filename)[1][1:].lower() or 'csv'
        
        # Upload to S3/R2
        try:
            s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=file_data,
                ContentType=f'application/{file_type}'
            )
            
            # Get file URL
            if os.environ.get('S3_ENDPOINT_URL'):
                # R2 or custom endpoint
                endpoint = os.environ.get('S3_ENDPOINT_URL').rstrip('/')
                file_url = f"{endpoint}/{bucket}/{s3_key}"
            else:
                # Standard S3
                region = os.environ.get('S3_REGION', 'us-east-1')
                file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
            
            return jsonify({
                'success': True,
                'message': 'File uploaded to S3/R2 successfully',
                'filename': filename,
                's3_key': s3_key,
                'file_url': file_url,
                'size': len(file_data)
            })
            
        except ClientError as e:
            logger.error(f"Error uploading to S3/R2: {str(e)}")
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error in direct_upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

@s3_upload_bp.route('/check-config', methods=['GET'])
def check_config():
    """Check if S3/R2 is configured and available."""
    try:
        use_s3 = os.environ.get('USE_S3_STORAGE', 'false').lower() == 'true'
        has_credentials = all([
            os.environ.get('S3_ACCESS_KEY'),
            os.environ.get('S3_SECRET_KEY'),
            os.environ.get('S3_BUCKET')
        ])
        
        endpoint_url = os.environ.get('S3_ENDPOINT_URL')
        is_r2 = endpoint_url and 'r2.cloudflarestorage.com' in endpoint_url if endpoint_url else False
        
        config = {
            's3_available': S3_AVAILABLE,
            'use_s3_storage': use_s3,
            'has_credentials': has_credentials,
            'bucket_configured': bool(os.environ.get('S3_BUCKET')),
            'storage_type': 'R2' if is_r2 else 'S3' if endpoint_url else 'S3',
            'endpoint_url': endpoint_url
        }
        
        # Test connection if configured
        if use_s3 and has_credentials and S3_AVAILABLE:
            try:
                s3_client = get_s3_client()
                bucket = get_s3_bucket()
                if s3_client and bucket:
                    s3_client.head_bucket(Bucket=bucket)
                    config['connection_test'] = 'success'
                else:
                    config['connection_test'] = 'failed'
            except Exception as e:
                config['connection_test'] = f'error: {str(e)}'
        else:
            config['connection_test'] = 'not_configured'
        
        return jsonify(config)
        
    except Exception as e:
        logger.error(f"Error checking S3 config: {str(e)}")
        return jsonify({'error': str(e)}), 500

