"""
Shared utilities for API routes.
"""

from flask import current_app
import logging

logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'txt', 'json', 'parquet', 'feather', 'duckdb'}

# API Configuration
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000


def rate_limit(limit_string):
    """Decorator for rate limiting - applies Flask-Limiter limits.
    
    This decorator applies rate limits when the limiter is available.
    Flask-Limiter will handle the actual rate limiting.
    """
    def decorator(func):
        # Store the limit string for later application
        func._rate_limit = limit_string
        return func
    return decorator


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def paginate_data(data, page=1, per_page=None):
    """Paginate data for API responses."""
    if per_page is None:
        per_page = DEFAULT_PAGE_SIZE
    
    # Ensure page and per_page are valid
    page = max(1, int(page))
    per_page = min(max(1, int(per_page)), MAX_PAGE_SIZE)
    
    # Calculate pagination
    total_items = len(data)
    total_pages = (total_items + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    
    # Get paginated data
    paginated_data = data[start_idx:end_idx]
    
    return {
        'data': paginated_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total_items,
            'pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }

