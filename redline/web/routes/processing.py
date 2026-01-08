#!/usr/bin/env python3
"""
Processing Routes for REDLINE
Triggers Modal serverless processing jobs
"""

from flask import Blueprint, request, jsonify, g
from redline.database.supabase_client import supabase_client
from redline.storage.s3_manager import s3_manager
import os
import uuid
import logging
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

# Create Blueprint
processing_bp = Blueprint('processing', __name__, url_prefix='/processing')


@processing_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload file to S3 and trigger Modal processing

    Requires authentication (JWT token)

    Form Data:
        - file: File to upload
        - job_type: Type of processing job (default: 'csv_to_parquet')
            Options: csv_to_parquet, parquet_to_csv, aggregate_timeseries, clean_data, merge_files

    Returns:
        JSON with job_id and status
    """
    # Get authenticated user info from g (set by middleware)
    user_id = getattr(g, 'user_id', None)
    stripe_customer_id = getattr(g, 'stripe_customer_id', None)

    # Validate authentication
    if not user_id:
        logger.error("Upload request without authenticated user")
        return jsonify({
            'error': 'Authentication required',
            'code': 'AUTH_REQUIRED'
        }), 401

    if not isinstance(user_id, str):
        logger.error(f"Upload request with invalid user_id type: {type(user_id)}")
        return jsonify({
            'error': 'Invalid authentication data',
            'code': 'INVALID_AUTH'
        }), 401

    logger.info(f"Processing upload request for user: {user_id}")

    # Check if file was uploaded
    if 'file' not in request.files:
        logger.warning(f"Upload request from {user_id} missing file in form data")
        return jsonify({
            'error': 'No file provided',
            'code': 'NO_FILE'
        }), 400

    file = request.files['file']

    # Validate file
    if not file:
        logger.error(f"Upload request from {user_id} has None file object")
        return jsonify({
            'error': 'Invalid file',
            'code': 'INVALID_FILE'
        }), 400

    if not hasattr(file, 'filename') or file.filename == '':
        logger.warning(f"Upload request from {user_id} has empty filename")
        return jsonify({
            'error': 'Empty filename',
            'code': 'EMPTY_FILENAME'
        }), 400

    original_filename = file.filename
    logger.debug(f"Upload request from {user_id} for file: {original_filename}")

    # Get and validate job type
    job_type = request.form.get('job_type', 'csv_to_parquet')

    if not isinstance(job_type, str):
        logger.error(f"Upload request from {user_id} has invalid job_type type: {type(job_type)}")
        return jsonify({
            'error': 'Invalid job type format',
            'code': 'INVALID_JOB_TYPE_FORMAT'
        }), 400

    # Validate job type
    valid_job_types = [
        'csv_to_parquet',
        'parquet_to_csv',
        'aggregate_timeseries',
        'clean_data',
        'merge_files'
    ]

    if job_type not in valid_job_types:
        logger.warning(f"Upload request from {user_id} has invalid job_type: {job_type}")
        return jsonify({
            'error': f'Invalid job type. Must be one of: {", ".join(valid_job_types)}',
            'code': 'INVALID_JOB_TYPE'
        }), 400

    logger.debug(f"Job type validated: {job_type}")

    # Check S3 manager availability
    if not s3_manager.is_available():
        logger.error(f"Upload request from {user_id} but S3 manager not available")
        return jsonify({
            'error': 'Storage service not configured',
            'code': 'STORAGE_UNAVAILABLE'
        }), 503

    # Generate unique file ID and secure filename
    file_id = str(uuid.uuid4())
    filename = secure_filename(original_filename)

    if not filename:
        logger.error(f"Upload from {user_id}: secure_filename returned empty for {original_filename}")
        filename = f"file_{file_id}"

    logger.debug(f"Generated file_id: {file_id}, secure filename: {filename}")

    # Generate S3 paths
    input_s3_key = s3_manager.get_file_path(user_id, f"{file_id}_{filename}", 'raw')

    # Determine output extension based on job type
    if job_type == 'csv_to_parquet':
        output_ext = 'parquet'
    elif job_type == 'parquet_to_csv':
        output_ext = 'csv'
    else:
        output_ext = 'parquet'  # Default to parquet for other operations

    output_s3_key = s3_manager.get_file_path(user_id, f"{file_id}_output.{output_ext}", 'processed')

    logger.debug(f"S3 paths - input: {input_s3_key}, output: {output_s3_key}")

    # Save file temporarily
    temp_path = f"/tmp/{file_id}_{filename}"

    logger.debug(f"Saving file temporarily to: {temp_path}")
    file.save(temp_path)

    # Validate temp file was created
    if not os.path.exists(temp_path):
        logger.error(f"Failed to save temp file for {user_id}: {temp_path}")
        return jsonify({
            'error': 'Failed to save uploaded file',
            'code': 'FILE_SAVE_ERROR'
        }), 500

    # Get file size
    file_size = os.path.getsize(temp_path)

    if file_size == 0:
        logger.warning(f"Upload from {user_id} has zero-size file: {filename}")
        os.remove(temp_path)
        return jsonify({
            'error': 'Uploaded file is empty',
            'code': 'EMPTY_FILE'
        }), 400

    if file_size > 100 * 1024 * 1024:  # 100MB limit
        logger.warning(f"Upload from {user_id} exceeds size limit: {file_size} bytes")
        os.remove(temp_path)
        return jsonify({
            'error': 'File too large (max 100MB)',
            'code': 'FILE_TOO_LARGE'
        }), 413

    logger.info(f"Uploading file {filename} ({file_size} bytes) to S3 for user {user_id}")

    # Upload file to S3
    input_s3_uri = s3_manager.upload_file(temp_path, input_s3_key)

    # Clean up temp file immediately after upload attempt
    if os.path.exists(temp_path):
        os.remove(temp_path)
        logger.debug(f"Cleaned up temp file: {temp_path}")

    # Validate S3 upload
    if not input_s3_uri:
        logger.error(f"S3 upload failed for {user_id}, file: {filename}")
        return jsonify({
            'error': 'Failed to upload file to storage',
            'code': 'S3_UPLOAD_ERROR'
        }), 500

    logger.info(f"Successfully uploaded file to S3: {input_s3_uri}")

    output_s3_uri = s3_manager.get_s3_uri(output_s3_key)

    # Check Supabase availability
    if not supabase_client.is_available():
        logger.error(f"Upload from {user_id} but Supabase client not available")
        return jsonify({
            'error': 'Database service not configured',
            'code': 'DATABASE_UNAVAILABLE'
        }), 503

    # Create job record in Supabase
    logger.debug(f"Creating job record for user {user_id}")
    job = supabase_client.create_job(
        user_id=user_id,
        job_type=job_type,
        input_s3_path=input_s3_uri,
        output_s3_path=output_s3_uri,
        file_size_bytes=file_size
    )

    if not job:
        logger.error(f"Failed to create job record for {user_id}")
        return jsonify({
            'error': 'Failed to create job record',
            'code': 'JOB_CREATION_ERROR'
        }), 500

    if not isinstance(job, dict) or 'id' not in job:
        logger.error(f"Job creation returned invalid data for {user_id}: {type(job)}")
        return jsonify({
            'error': 'Invalid job record created',
            'code': 'INVALID_JOB_DATA'
        }), 500

    job_id = job['id']
    logger.info(f"Created job {job_id} for user {user_id}")

    # Trigger Modal function asynchronously
    logger.debug(f"Triggering Modal function for job {job_id}")

    # Note: Modal operations can raise exceptions - legitimate exception handling
    try:
        import modal
    except ImportError:
        logger.error(f"Modal library not available for job {job_id}")
        supabase_client.update_job_status(
            job_id=job_id,
            status='failed',
            error_message="Modal processing library not available"
        )
        return jsonify({
            'error': 'Processing service not available',
            'code': 'MODAL_UNAVAILABLE',
            'job_id': job_id
        }), 503

    try:
        # Lookup the deployed Modal function
        process_data = modal.Function.lookup("redline-processing", "process_data")

        if not process_data:
            raise ValueError("Modal function lookup returned None")

        # Spawn the function asynchronously
        modal_call = process_data.spawn(
            job_id=job_id,
            user_id=user_id,
            stripe_customer_id=stripe_customer_id,
            input_s3_path=input_s3_uri,
            output_s3_path=output_s3_uri,
            job_type=job_type
        )

        if not modal_call or not hasattr(modal_call, 'object_id'):
            raise ValueError("Modal spawn returned invalid call object")

        # Update job with Modal call ID
        supabase_client.update_job_status(
            job_id=job_id,
            status='processing',
            modal_call_id=modal_call.object_id
        )

        logger.info(f"Triggered Modal function for job {job_id}: {modal_call.object_id}")

    except ImportError as e:
        logger.error(f"Failed to import Modal for job {job_id}: {str(e)}")
        supabase_client.update_job_status(
            job_id=job_id,
            status='failed',
            error_message=f"Modal import failed: {str(e)}"
        )
        return jsonify({
            'error': 'Processing service import failed',
            'code': 'MODAL_IMPORT_ERROR',
            'details': str(e),
            'job_id': job_id
        }), 500

    except Exception as e:
        logger.error(f"Failed to trigger Modal function for job {job_id}: {str(e)}")
        supabase_client.update_job_status(
            job_id=job_id,
            status='failed',
            error_message=f"Failed to trigger processing: {str(e)}"
        )
        return jsonify({
            'error': 'Failed to trigger processing',
            'code': 'MODAL_TRIGGER_ERROR',
            'details': str(e),
            'job_id': job_id
        }), 500

    logger.info(f"Successfully started processing job {job_id} for user {user_id}")

    return jsonify({
        'success': True,
        'job_id': job_id,
        'status': 'processing',
        'message': 'Processing job started',
        'job_type': job_type,
        'input_file': original_filename,
        'file_size_bytes': file_size
    }), 202


@processing_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    Get job status from Supabase

    Requires authentication (JWT token)

    Returns:
        JSON with job details and download URL if completed
    """
    user_id = g.user_id

    try:
        job = supabase_client.get_job(job_id)

        if not job:
            return jsonify({
                'error': 'Job not found',
                'code': 'JOB_NOT_FOUND'
            }), 404

        # Verify job belongs to user
        if job['user_id'] != user_id:
            return jsonify({
                'error': 'Access denied',
                'code': 'ACCESS_DENIED'
            }), 403

        # If completed, generate presigned download URL
        if job['status'] == 'completed' and job.get('output_s3_path'):
            # Extract S3 key from S3 URI
            s3_uri = job['output_s3_path']
            s3_key = s3_uri.replace(f"s3://{s3_manager.bucket}/", "")

            # Generate presigned URL (valid for 1 hour)
            download_url = s3_manager.generate_presigned_url(s3_key, expiration=3600)
            job['download_url'] = download_url
            job['download_expires_in'] = 3600  # seconds

        return jsonify(job)

    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        return jsonify({
            'error': 'Failed to get job status',
            'code': 'GET_JOB_ERROR',
            'details': str(e)
        }), 500


@processing_bp.route('/jobs', methods=['GET'])
def list_jobs():
    """
    List all jobs for current user

    Requires authentication (JWT token)

    Query Parameters:
        - limit: Number of jobs to return (default: 50, max: 500)
        - status: Filter by status (optional)

    Returns:
        JSON with list of jobs
    """
    user_id = g.user_id

    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        status_filter = request.args.get('status')

        # Validate limit
        if limit < 1 or limit > 500:
            return jsonify({
                'error': 'Limit must be between 1 and 500',
                'code': 'INVALID_LIMIT'
            }), 400

        # Get jobs from Supabase
        jobs = supabase_client.get_user_jobs(user_id, limit=limit)

        # Filter by status if provided
        if status_filter:
            jobs = [job for job in jobs if job.get('status') == status_filter]

        return jsonify({
            'jobs': jobs,
            'count': len(jobs)
        })

    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        return jsonify({
            'error': 'Failed to list jobs',
            'code': 'LIST_JOBS_ERROR',
            'details': str(e)
        }), 500


@processing_bp.route('/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """
    Cancel a running job

    Requires authentication (JWT token)

    Note: This only updates the job status in Supabase.
    Modal functions will still complete, but results won't be used.

    Returns:
        JSON with success message
    """
    user_id = g.user_id

    try:
        job = supabase_client.get_job(job_id)

        if not job:
            return jsonify({
                'error': 'Job not found',
                'code': 'JOB_NOT_FOUND'
            }), 404

        # Verify job belongs to user
        if job['user_id'] != user_id:
            return jsonify({
                'error': 'Access denied',
                'code': 'ACCESS_DENIED'
            }), 403

        # Check if job can be cancelled
        if job['status'] in ['completed', 'failed', 'cancelled']:
            return jsonify({
                'error': f'Cannot cancel job with status: {job["status"]}',
                'code': 'INVALID_STATUS'
            }), 400

        # Update job status to cancelled
        supabase_client.update_job_status(
            job_id=job_id,
            status='cancelled',
            error_message='Cancelled by user'
        )

        logger.info(f"Cancelled job {job_id} for user {user_id}")

        return jsonify({
            'success': True,
            'message': 'Job cancelled successfully',
            'job_id': job_id
        })

    except Exception as e:
        logger.error(f"Error cancelling job: {str(e)}")
        return jsonify({
            'error': 'Failed to cancel job',
            'code': 'CANCEL_JOB_ERROR',
            'details': str(e)
        }), 500


@processing_bp.route('/jobs/<job_id>/download', methods=['GET'])
def download_job_result(job_id):
    """
    Generate download URL for completed job

    Requires authentication (JWT token)

    Query Parameters:
        - expiration: URL expiration time in seconds (default: 3600, max: 86400)

    Returns:
        JSON with presigned download URL
    """
    user_id = g.user_id

    try:
        job = supabase_client.get_job(job_id)

        if not job:
            return jsonify({
                'error': 'Job not found',
                'code': 'JOB_NOT_FOUND'
            }), 404

        # Verify job belongs to user
        if job['user_id'] != user_id:
            return jsonify({
                'error': 'Access denied',
                'code': 'ACCESS_DENIED'
            }), 403

        # Check if job is completed
        if job['status'] != 'completed':
            return jsonify({
                'error': f'Job is not completed (status: {job["status"]})',
                'code': 'JOB_NOT_COMPLETED'
            }), 400

        if not job.get('output_s3_path'):
            return jsonify({
                'error': 'No output file available',
                'code': 'NO_OUTPUT_FILE'
            }), 404

        # Get expiration time
        expiration = int(request.args.get('expiration', 3600))

        # Validate expiration (max 24 hours)
        if expiration < 60 or expiration > 86400:
            return jsonify({
                'error': 'Expiration must be between 60 and 86400 seconds',
                'code': 'INVALID_EXPIRATION'
            }), 400

        # Extract S3 key from S3 URI
        s3_uri = job['output_s3_path']
        s3_key = s3_uri.replace(f"s3://{s3_manager.bucket}/", "")

        # Generate presigned URL
        download_url = s3_manager.generate_presigned_url(s3_key, expiration=expiration)

        if not download_url:
            return jsonify({
                'error': 'Failed to generate download URL',
                'code': 'URL_GENERATION_ERROR'
            }), 500

        return jsonify({
            'download_url': download_url,
            'expires_in': expiration,
            'job_id': job_id,
            'filename': s3_key.split('/')[-1]  # Extract filename from key
        })

    except Exception as e:
        logger.error(f"Error generating download URL: {str(e)}")
        return jsonify({
            'error': 'Failed to generate download URL',
            'code': 'DOWNLOAD_ERROR',
            'details': str(e)
        }), 500


@processing_bp.route('/stats', methods=['GET'])
def get_processing_stats():
    """
    Get processing statistics for current user

    Requires authentication (JWT token)

    Returns:
        JSON with processing statistics
    """
    user_id = g.user_id

    try:
        # Get all jobs for user
        jobs = supabase_client.get_user_jobs(user_id, limit=1000)

        # Calculate statistics
        stats = {
            'total_jobs': len(jobs),
            'completed': sum(1 for job in jobs if job['status'] == 'completed'),
            'processing': sum(1 for job in jobs if job['status'] == 'processing'),
            'failed': sum(1 for job in jobs if job['status'] == 'failed'),
            'queued': sum(1 for job in jobs if job['status'] == 'queued'),
            'cancelled': sum(1 for job in jobs if job['status'] == 'cancelled'),
            'total_rows_processed': sum(job.get('row_count', 0) for job in jobs if job.get('row_count')),
            'total_processing_hours': sum(job.get('processing_hours', 0) for job in jobs if job.get('processing_hours')),
            'job_types': {}
        }

        # Count jobs by type
        for job in jobs:
            job_type = job.get('job_type', 'unknown')
            if job_type not in stats['job_types']:
                stats['job_types'][job_type] = 0
            stats['job_types'][job_type] += 1

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting processing stats: {str(e)}")
        return jsonify({
            'error': 'Failed to get statistics',
            'code': 'STATS_ERROR',
            'details': str(e)
        }), 500
