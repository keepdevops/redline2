# Fix for /data/multi Template Not Found Error

## Root Cause Analysis

The error occurs because Flask is looking for `data_tab_multi_file.html` but it doesn't exist in the templates directory.

## Decision Tree: Which Fix to Use?

### Choose Fix Option 1 (Add Error Handling) IF:
- The template should exist but is missing due to deployment issue
- You want to prevent the app from crashing while you fix it
- You need temporary protection while developing

### Choose Fix Option 2 (Create Template) IF:
- This is a new feature being developed
- The template was never created in the first place
- You need the actual functionality to work

### Recommended: **Do BOTH** (Defense in Depth)
1. Create the template (so the route works)
2. Add error handling (so future template issues are caught gracefully)

## Complete Solution

### Step 1: Improve the Route with Better Error Handling

```python
# /app/redline/web/routes/data_tab.py

from flask import render_template, jsonify, abort, current_app
from jinja2 import TemplateNotFound
import logging

logger = logging.getLogger(__name__)

@app.route('/data/multi')
def data_tab_multi():
    """Render multi-file data tab page"""
    try:
        return render_template('data_tab_multi_file.html')
    
    except TemplateNotFound as e:
        # Log detailed information about the missing template
        logger.error(
            "Template not found error in /data/multi route",
            extra={
                'template_name': 'data_tab_multi_file.html',
                'template_folders': current_app.jinja_env.loader.searchpath,
                'available_templates': current_app.jinja_env.list_templates(),
                'route': '/data/multi',
                'error': str(e)
            },
            exc_info=True
        )
        
        # Try to use a fallback template
        try:
            return render_template(
                'error.html',
                error_title="Page Not Available",
                error_message="The multi-file data view is currently unavailable.",
                error_detail="Template configuration error. Please contact support."
            ), 500
        except TemplateNotFound:
            # Even error.html doesn't exist, return plain response
            logger.critical("error.html template also missing!")
            return jsonify({
                'error': 'Template configuration error',
                'message': 'Page temporarily unavailable',
                'status': 500
            }), 500
    
    except Exception as e:
        # Catch any other unexpected errors
        logger.critical(
            f"Unexpected error in /data/multi route: {e}",
            extra={'route': '/data/multi'},
            exc_info=True
        )
        abort(500)
```

### Step 2: Create the Missing Template

Create the file: `/app/redline/web/templates/data_tab_multi_file.html`

```html
{% extends "base.html" %}

{% block title %}Multi-File Data View{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <h1>Multi-File Data View</h1>
            <p class="text-muted">Upload and analyze multiple data files</p>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>File Upload</h5>
                </div>
                <div class="card-body">
                    <form id="multi-file-form" method="POST" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="file-input" class="form-label">Select Files</label>
                            <input class="form-control" type="file" id="file-input" 
                                   name="files[]" multiple accept=".csv,.xlsx,.json">
                            <div class="form-text">
                                Select multiple files for batch processing
                            </div>
                        </div>
                        <button type="submit" class="btn btn-primary">Upload and Process</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4" id="results-section" style="display: none;">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>Processing Results</h5>
                </div>
                <div class="card-body">
                    <div id="results-container">
                        <!-- Results will be populated here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('multi-file-form');
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        fetch('/data/multi/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            resultsSection.style.display = 'block';
            resultsContainer.innerHTML = '<pre>' + 
                JSON.stringify(data, null, 2) + '</pre>';
        })
        .catch(error => {
            alert('Error processing files: ' + error);
            console.error('Error:', error);
        });
    });
});
</script>
{% endblock %}
```

### Step 3: Create Error Template (Fallback)

Create the file: `/app/redline/web/templates/error.html`

```html
{% extends "base.html" %}

{% block title %}{{ error_title | default('Error') }}{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center mt-5">
        <div class="col-md-8">
            <div class="card border-danger">
                <div class="card-header bg-danger text-white">
                    <h4 class="mb-0">
                        <i class="bi bi-exclamation-triangle-fill"></i>
                        {{ error_title | default('An Error Occurred') }}
                    </h4>
                </div>
                <div class="card-body">
                    <h5 class="card-title">{{ error_message | default('Something went wrong') }}</h5>
                    
                    {% if error_detail %}
                    <p class="card-text text-muted">{{ error_detail }}</p>
                    {% endif %}
                    
                    <div class="mt-4">
                        <a href="{{ url_for('index') }}" class="btn btn-primary">
                            <i class="bi bi-house-fill"></i> Return Home
                        </a>
                        <button onclick="window.history.back()" class="btn btn-secondary">
                            <i class="bi bi-arrow-left"></i> Go Back
                        </button>
                    </div>
                    
                    {% if config.DEBUG %}
                    <div class="mt-4 p-3 bg-light border rounded">
                        <h6>Debug Information:</h6>
                        <small class="text-muted">
                            {% if error %}
                            <pre>{{ error }}</pre>
                            {% endif %}
                        </small>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Step 4: Add Logging Configuration

If you don't have logging configured, add this to your app initialization:

```python
# /app/redline/web/app.py or wherever you initialize Flask

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up file handler
    file_handler = RotatingFileHandler(
        'logs/redline.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s (%(pathname)s:%(lineno)d): %(message)s'
    ))
    file_handler.setLevel(logging.ERROR)
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    ))
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Log startup
    app.logger.info('Redline application startup')

# In your app initialization
app = Flask(__name__)
setup_logging(app)
```

### Step 5: Verification Script

Create this script to verify the fix:

```python
#!/usr/bin/env python3
# verify_template_fix.py

import os
from pathlib import Path

def verify_template_exists(template_path):
    """Verify template file exists"""
    if os.path.exists(template_path):
        print(f"✓ Template exists: {template_path}")
        return True
    else:
        print(f"✗ Template missing: {template_path}")
        return False

def verify_route_file(route_file):
    """Verify route has proper error handling"""
    if not os.path.exists(route_file):
        print(f"✗ Route file not found: {route_file}")
        return False
    
    with open(route_file, 'r') as f:
        content = f.read()
    
    checks = {
        'has_try_except': 'try:' in content and 'except' in content,
        'has_template_not_found': 'TemplateNotFound' in content,
        'has_logging': 'logger' in content,
        'has_exc_info': 'exc_info=True' in content
    }
    
    print(f"\nRoute file checks for {route_file}:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
    
    return all(checks.values())

if __name__ == '__main__':
    print("=" * 60)
    print("Verifying /data/multi template fix")
    print("=" * 60)
    
    # Check templates
    templates_ok = True
    templates_ok &= verify_template_exists('/app/redline/web/templates/data_tab_multi_file.html')
    templates_ok &= verify_template_exists('/app/redline/web/templates/error.html')
    
    # Check route
    route_ok = verify_route_file('/app/redline/web/routes/data_tab.py')
    
    # Check logs directory
    logs_dir = '/app/logs'
    if os.path.exists(logs_dir):
        print(f"\n✓ Logs directory exists: {logs_dir}")
        logs_ok = True
    else:
        print(f"\n✗ Logs directory missing: {logs_dir}")
        print(f"  Run: mkdir -p {logs_dir}")
        logs_ok = False
    
    # Summary
    print("\n" + "=" * 60)
    if templates_ok and route_ok and logs_ok:
        print("✓ All checks passed! The fix is complete.")
    else:
        print("✗ Some checks failed. Please review the output above.")
    print("=" * 60)
```

## Testing the Fix

### Test 1: Verify Template Rendering
```bash
# Run the verification script
python verify_template_fix.py

# Or manually check
ls -la /app/redline/web/templates/data_tab_multi_file.html
ls -la /app/redline/web/templates/error.html
```

### Test 2: Test the Route
```bash
# Start the Flask app
cd /app/redline
python -m web.app  # or however you start the app

# In another terminal, test the endpoint
curl http://localhost:5000/data/multi
```

### Test 3: Check Logs
```bash
# Monitor logs in real-time
tail -f /app/logs/redline.log

# Check for any TemplateNotFound errors
grep "TemplateNotFound" /app/logs/redline.log
```

## Next Steps After Fix

1. **Implement the backend upload handler**
   - Create `/data/multi/upload` POST endpoint
   - Handle file processing
   - Return results as JSON

2. **Add proper form validation**
   - File type checking
   - Size limits
   - Error handling for malformed files

3. **Add monitoring**
   - Track how often this route is accessed
   - Monitor error rates
   - Alert on template errors

4. **Create unit tests**
   ```python
   def test_data_multi_route_renders():
       response = client.get('/data/multi')
       assert response.status_code == 200
       assert b'Multi-File Data View' in response.data
   
   def test_missing_template_handled_gracefully():
       with patch('flask.render_template', side_effect=TemplateNotFound('test')):
           response = client.get('/data/multi')
           assert response.status_code == 500
           # Should use error.html fallback
   ```

## Summary

**Quick Fix (5 minutes):**
1. Create `data_tab_multi_file.html` template
2. Restart Flask app
3. Test the route

**Proper Fix (15 minutes):**
1. Update route with error handling
2. Create both templates
3. Set up logging
4. Run verification script
5. Test thoroughly

**Why Both Matter:**
- Template creation: Makes the feature work
- Error handling: Prevents future similar issues from crashing the app
- Logging: Helps you diagnose problems quickly

Choose based on your urgency, but I recommend doing the proper fix to prevent similar issues in the future.
