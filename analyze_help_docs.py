#!/usr/bin/env python3
"""
Analyze help/documentation .md files to determine if they are:
1. Still valid for subscription service (not local machine setup)
2. Based on Redline features and capabilities
3. Need updating for cloud/subscription context
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Keywords that indicate local machine setup (should be updated)
LOCAL_SETUP_KEYWORDS = [
    r'\blocalhost\b',
    r'\blocal\s+installation\b',
    r'\binstall\s+locally\b',
    r'\brun\s+locally\b',
    r'\bsetup\s+on\s+your\s+machine\b',
    r'\bpython\s+web_app\.py\b',
    r'\bpython3\s+web_app\.py\b',
    r'\b\.\/web_app\.py\b',
    r'\bport\s+8080\b',
    r'\bhttp://localhost\b',
    r'\bhttp://127\.0\.0\.1\b',
    r'\bsudo\s+apt\s+install\b',
    r'\bpip\s+install\b',
    r'\bvenv\b',
    r'\bvirtualenv\b',
    r'\bconda\s+env\b',
    r'\brequirements\.txt\b',
    r'\binstall\s+dependencies\b',
    r'\bsetup\.py\b',
    r'\bDocker\s+run\s+locally\b',
    r'\bdocker-compose\s+up\b',
    r'\b\.env\s+file\b',
    r'\benvironment\s+variables\s+locally\b',
]

# Keywords that indicate subscription/cloud service (good)
SUBSCRIPTION_KEYWORDS = [
    r'\bsubscription\b',
    r'\bcloud\b',
    r'\bweb\s+service\b',
    r'\bonline\b',
    r'\baccess\s+via\s+browser\b',
    r'\bhttps://\b',
    r'\bregister\b',
    r'\blicense\s+key\b',
    r'\baccount\b',
    r'\bpayment\b',
    r'\bstripe\b',
    r'\bhours\s+remaining\b',
    r'\busage\s+tracking\b',
    r'\bweb\s+interface\b',
    r'\bdashboard\b',
    r'\bportal\b',
]

# Redline feature keywords (should be present)
REDLINE_FEATURES = [
    r'\bdata\s+download\b',
    r'\bdata\s+conversion\b',
    r'\bdata\s+analysis\b',
    r'\bdata\s+view\b',
    r'\bstooq\b',
    r'\byahoo\s+finance\b',
    r'\balpha\s+vantage\b',
    r'\bfinnhub\b',
    r'\bapi\s+keys\b',
    r'\bcustom\s+api\b',
    r'\bformat\s+conversion\b',
    r'\bstatistical\s+analysis\b',
    r'\bfinancial\s+analysis\b',
    r'\bcorrelation\s+analysis\b',
    r'\bdata\s+cleaning\b',
    r'\bduckdb\b',
    r'\bdata\s+storage\b',
    r'\bfile\s+upload\b',
    r'\bbatch\s+download\b',
    r'\bbatch\s+conversion\b',
    r'\bthemes\b',
    r'\bcolor\s+customization\b',
    r'\bdate\s+format\b',
]

# Help/documentation files to check
HELP_FILES = [
    'README.md',
    'REDLINE_USER_GUIDE.md',
    'REDLINE_INSTALLATION_GUIDE.md',
    'REDLINE_DEVELOPER_GUIDE.md',
    'QUICK_START_GUIDE.md',
    'REDLINE_WEBGUI_GUIDE.md',
    'API_DOCUMENTATION.md',
    'TROUBLESHOOTING_GUIDE.md',
    'WEB_APP_STARTUP_GUIDE.md',
    'LOCAL_SETUP_GUIDE.md',
    'UBUNTU_INSTALLATION_GUIDE.md',
    'UNIVERSAL_INSTALLATION_GUIDE.md',
    'DOCKER_QUICK_START.md',
    'RENDER_DEPLOYMENT_GUIDE.md',
    'CLOUDFLARE_DNS_SETUP.md',
    'COMPLETE_CLOUD_DEPLOYMENT.md',
]

def analyze_file(filepath):
    """Analyze a single .md file for subscription service relevance."""
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}
    
    # Count matches
    local_setup_matches = []
    subscription_matches = []
    feature_matches = []
    
    for pattern in LOCAL_SETUP_KEYWORDS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            local_setup_matches.extend(matches)
    
    for pattern in SUBSCRIPTION_KEYWORDS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            subscription_matches.extend(matches)
    
    for pattern in REDLINE_FEATURES:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            feature_matches.extend(matches)
    
    # Determine status
    local_count = len(local_setup_matches)
    sub_count = len(subscription_matches)
    feature_count = len(feature_matches)
    
    status = "✅ VALID"
    if local_count > sub_count * 2:  # More local references than subscription
        status = "⚠️  NEEDS UPDATE (too many local setup references)"
    elif local_count > 5:
        status = "⚠️  NEEDS UPDATE (local setup references found)"
    elif feature_count == 0:
        status = "❌ INVALID (no Redline features mentioned)"
    elif sub_count == 0 and local_count > 0:
        status = "⚠️  NEEDS UPDATE (no subscription context)"
    
    return {
        'file': filepath,
        'status': status,
        'local_setup_count': local_count,
        'subscription_count': sub_count,
        'feature_count': feature_count,
        'local_examples': list(set(local_setup_matches[:5])),  # First 5 unique
        'subscription_examples': list(set(subscription_matches[:5])),
        'feature_examples': list(set(feature_matches[:5])),
        'size': os.path.getsize(filepath),
    }

def main():
    """Main analysis function."""
    print("=" * 80)
    print("HELP DOCUMENTATION ANALYSIS FOR SUBSCRIPTION SERVICE")
    print("=" * 80)
    print()
    
    results = []
    for filename in HELP_FILES:
        filepath = os.path.join('.', filename)
        result = analyze_file(filepath)
        if result:
            results.append(result)
    
    # Also check redline/web/templates/help.html references
    help_html_path = 'redline/web/templates/help.html'
    if os.path.exists(help_html_path):
        print("Checking help.html template for .md file references...")
        with open(help_html_path, 'r', encoding='utf-8') as f:
            help_content = f.read()
        
        # Find referenced .md files
        md_refs = re.findall(r'([A-Z_]+\.md|README\.md)', help_content)
        for md_ref in set(md_refs):
            if md_ref not in [r['file'] for r in results]:
                filepath = os.path.join('.', md_ref)
                result = analyze_file(filepath)
                if result:
                    results.append(result)
    
    # Sort by status priority
    status_order = {
        '❌ INVALID (no Redline features mentioned)': 0,
        '⚠️  NEEDS UPDATE (too many local setup references)': 1,
        '⚠️  NEEDS UPDATE (local setup references found)': 2,
        '⚠️  NEEDS UPDATE (no subscription context)': 3,
        '✅ VALID': 4,
    }
    
    results.sort(key=lambda x: status_order.get(x['status'], 99))
    
    # Print results
    print("FILE ANALYSIS RESULTS:")
    print("-" * 80)
    print()
    
    for result in results:
        print(f"📄 {result['file']}")
        print(f"   Status: {result['status']}")
        print(f"   Size: {result['size']:,} bytes")
        print(f"   Local setup references: {result['local_setup_count']}")
        print(f"   Subscription references: {result['subscription_count']}")
        print(f"   Feature references: {result['feature_count']}")
        
        if result['local_examples']:
            print(f"   Local examples: {', '.join(result['local_examples'][:3])}")
        if result['subscription_examples']:
            print(f"   Subscription examples: {', '.join(result['subscription_examples'][:3])}")
        if result['feature_examples']:
            print(f"   Feature examples: {', '.join(result['feature_examples'][:3])}")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    status_counts = defaultdict(int)
    for result in results:
        status_counts[result['status']] += 1
    
    for status, count in sorted(status_counts.items(), key=lambda x: status_order.get(x[0], 99)):
        print(f"{status}: {count} file(s)")
    
    print()
    print(f"Total files analyzed: {len(results)}")
    print()
    
    # Recommendations
    needs_update = [r for r in results if 'NEEDS UPDATE' in r['status'] or 'INVALID' in r['status']]
    if needs_update:
        print("=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print()
        print("Files that need updating for subscription service:")
        for result in needs_update:
            print(f"  - {result['file']}")
            if result['local_setup_count'] > 0:
                print(f"    → Remove {result['local_setup_count']} local setup references")
            if result['subscription_count'] == 0:
                print(f"    → Add subscription/cloud service context")
            if result['feature_count'] == 0:
                print(f"    → Add Redline feature descriptions")
        print()

if __name__ == '__main__':
    main()

