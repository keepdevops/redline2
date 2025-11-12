#!/bin/bash
# Update dependencies to fix security vulnerabilities
# Based on GitHub Dependabot alerts and latest available versions

set -e

echo "🔒 Security Dependency Update Script"
echo "====================================="
echo ""
echo "This script updates packages to latest secure versions:"
echo "  - werkzeug: 3.1.3"
echo "  - jinja2: 3.1.6"
echo "  - markupsafe: 3.0.3 (major version - test compatibility)"
echo "  - requests: 2.32.5"
echo "  - urllib3: 2.5.0"
echo "  - boto3: 1.40.72"
echo ""

read -p "Continue with updates? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Update cancelled."
    exit 1
fi

echo ""
echo "1. Updating pip..."
pip3 install --upgrade pip>=25.3

echo ""
echo "2. Updating Werkzeug (security fixes)..."
pip3 install --upgrade "werkzeug>=3.1.3"

echo ""
echo "3. Updating Jinja2 (security fixes)..."
pip3 install --upgrade "jinja2>=3.1.6"

echo ""
echo "4. Updating MarkupSafe (major version - may have breaking changes)..."
pip3 install --upgrade "markupsafe>=3.0.3"

echo ""
echo "5. Updating Requests (security fixes)..."
pip3 install --upgrade "requests>=2.32.5"

echo ""
echo "6. Updating urllib3 (security fixes)..."
pip3 install --upgrade "urllib3>=2.5.0"

echo ""
echo "7. Updating Boto3 (security fixes)..."
pip3 install --upgrade "boto3>=1.40.72"

echo ""
echo "8. Updating other Flask dependencies..."
pip3 install --upgrade "click>=8.1.8" "blinker>=1.9.0" "itsdangerous>=2.2.0"

echo ""
echo "9. Updating all other dependencies from requirements.txt..."
pip3 install --upgrade -r requirements.txt

echo ""
echo "✅ Security updates complete!"
echo ""
echo "📊 Updated packages:"
pip3 list | grep -E "Flask|werkzeug|jinja2|markupsafe|requests|boto3|click|blinker|itsdangerous|urllib3" || echo "   (Some packages may not be installed)"

echo ""
echo "⚠️  IMPORTANT: MarkupSafe updated to 3.0.3 (major version)"
echo "   Please test your application for compatibility issues"
echo ""
echo "🧪 Next steps:"
echo "   1. Test the application: python3 web_app.py"
echo "   2. Run tests: python3 test_payment_integration.py"
echo "   3. Check for any breaking changes"
echo "   4. Review and commit changes"
