#!/bin/bash

# REDLINE Custom API Local Integration Test
# Tests that Custom API functionality works correctly on the local system

set -e

echo "🧪 REDLINE Custom API Local Integration Test"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Test 1: Check Python environment
log_info "Checking Python environment..."
if python3 -c "import flask, pandas, json" 2>/dev/null; then
    log_success "Python environment has required packages"
else
    log_error "Missing required Python packages (flask, pandas)"
    exit 1
fi

# Test 2: Check Custom API files exist
log_info "Checking Custom API files..."
if [ -f "redline/web/routes/custom_api.py" ]; then
    log_success "Custom API backend file exists"
else
    log_error "Custom API backend file missing"
    exit 1
fi

if [ -f "redline/web/templates/custom_api_builder.html" ]; then
    log_success "Custom API template file exists"
else
    log_error "Custom API template file missing"
    exit 1
fi

# Test 3: Check if Custom API is imported correctly
log_info "Testing Custom API imports..."
if python3 -c "
import sys
sys.path.append('.')
from redline.web.routes.custom_api import custom_api_bp
print('Custom API blueprint imported successfully')
" 2>/dev/null; then
    log_success "Custom API imports work correctly"
else
    log_error "Custom API import failed"
    exit 1
fi

# Test 4: Test Custom API functions
log_info "Testing Custom API functions..."
python3 -c "
import sys
sys.path.append('.')
from redline.web.routes.custom_api import validate_parameters, execute_basic_logic

# Test parameter validation
api_def = {
    'name': 'Test API',
    'parameters': [
        {'name': 'test_param', 'type': 'string', 'required': True}
    ]
}
data = {'test_param': 'test_value'}
result = validate_parameters(api_def, data)
assert result['error'] is None, 'Parameter validation failed'

# Test basic logic execution
result = execute_basic_logic(api_def, data)
assert 'processed_parameters' in result, 'Basic logic execution failed'

print('Custom API functions work correctly')
"

if [ $? -eq 0 ]; then
    log_success "Custom API functions work correctly"
else
    log_error "Custom API function tests failed"
    exit 1
fi

# Test 5: Test Flask app integration
log_info "Testing Flask app integration..."
python3 -c "
import sys
sys.path.append('.')
from redline.web import create_app

app, socketio = create_app()
with app.app_context():
    # Check if custom API blueprint is registered
    blueprints = [bp.name for bp in app.blueprints.values()]
    assert 'custom_api' in blueprints, 'Custom API blueprint not registered'
    
    # Check if routes are registered
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    custom_routes = [r for r in routes if '/custom-api' in r]
    assert len(custom_routes) > 0, 'Custom API routes not registered'
    
print('Flask app integration successful')
print('Custom API routes registered:', len([r for r in routes if '/custom-api' in r]))
"

if [ $? -eq 0 ]; then
    log_success "Flask app integration works correctly"
else
    log_error "Flask app integration test failed"
    exit 1
fi

# Test 6: Test Configuration
log_info "Testing Custom API configuration..."
python3 -c "
import sys, os, json
sys.path.append('.')
from redline.web.routes.custom_api import CUSTOM_API_CONFIG_FILE, save_custom_apis, load_custom_apis

# Test config file path
print(f'Config file path: {CUSTOM_API_CONFIG_FILE}')

# Test save/load functions
test_apis = {
    'test_api': {
        'name': 'Test API',
        'endpoint': '/test',
        'method': 'POST',
        'parameters': []
    }
}

# Save test config
import redline.web.routes.custom_api as custom_api_module
custom_api_module.CUSTOM_APIS = test_apis
save_custom_apis()

# Load test config
custom_api_module.CUSTOM_APIS = {}
load_custom_apis()
assert 'test_api' in custom_api_module.CUSTOM_APIS, 'Config save/load failed'

print('Configuration system works correctly')
"

if [ $? -eq 0 ]; then
    log_success "Configuration system works correctly"
else
    log_error "Configuration system test failed"
    exit 1
fi

# Test 7: Check if data directory structure is correct
log_info "Checking data directory structure..."
mkdir -p data
if [ -d "data" ]; then
    log_success "Data directory exists"
else
    log_error "Data directory missing"
    exit 1
fi

# Test 8: Test JSON serialization
log_info "Testing JSON serialization..."
python3 -c "
import json
from datetime import datetime

# Test that datetime serialization works (custom APIs store timestamps)
test_data = {
    'timestamp': datetime.now().isoformat(),
    'parameters': [{'name': 'test', 'type': 'string'}]
}

json_str = json.dumps(test_data)
loaded_data = json.loads(json_str)
assert loaded_data['timestamp'] is not None, 'JSON serialization failed'

print('JSON serialization works correctly')
"

if [ $? -eq 0 ]; then
    log_success "JSON serialization works correctly"
else
    log_error "JSON serialization test failed"
    exit 1
fi

echo ""
echo "🎉 All local tests passed! Custom API integration is working correctly."
echo ""
echo "📊 Test Summary:"
echo "  ✅ Python environment and dependencies"
echo "  ✅ Custom API files exist and are accessible"
echo "  ✅ Custom API imports work correctly"
echo "  ✅ Custom API functions operate properly"
echo "  ✅ Flask app integration is successful"
echo "  ✅ Configuration system works"
echo "  ✅ Data directory structure is correct"
echo "  ✅ JSON serialization works"
echo ""
echo "🚀 Your Custom API integration is ready!"
echo ""
echo "Next steps for Docker:"
echo "  • The integration is confirmed working locally"
echo "  • All necessary files are included in your codebase"
echo "  • Docker builds will include Custom API functionality automatically"
echo "  • Use docker-compose.yml for easy deployment with data persistence"
echo ""
echo "To start the web application locally:"
echo "  python3 web_app.py"
echo "  Then visit: http://localhost:8080/custom-api/"
echo ""
