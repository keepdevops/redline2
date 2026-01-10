#!/usr/bin/env python3
"""
Migration Verification Script
Checks that all license_key references have been properly migrated to user_id
"""

import os
import re
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_file_for_issues(file_path: Path, patterns: dict) -> list:
    """Check a file for migration issues"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        for pattern_name, pattern_info in patterns.items():
            pattern = pattern_info['pattern']
            allowed_files = pattern_info.get('allowed_files', [])
            error_msg = pattern_info.get('error', f'Found {pattern_name}')
            
            # Skip if file is in allowed list
            if any(allowed in str(file_path) for allowed in allowed_files):
                continue
            
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ''
                issues.append({
                    'file': str(file_path),
                    'line': line_num,
                    'pattern': pattern_name,
                    'message': error_msg,
                    'line_content': line_content.strip()
                })
    except Exception as e:
        issues.append({
            'file': str(file_path),
            'line': 0,
            'pattern': 'ERROR',
            'message': f'Error reading file: {str(e)}',
            'line_content': ''
        })
    
    return issues

def main():
    """Main verification function"""
    print(f"{YELLOW}🔍 Verifying Migration from license_key to user_id...{RESET}\n")
    
    # Define patterns to check
    patterns = {
        'license_key_in_routes': {
            'pattern': r'license_key\s*=\s*(extract_license_key|request\.(get|args|form|json).*license|g\.license)',
            'error': 'Route using license_key extraction (should use user_id from g.user_id)',
            'allowed_files': []  # No deprecated functions remaining
        },
        'license_key_header': {
            'pattern': r'X-License-Key|X_LICENSE_KEY',
            'error': 'Using X-License-Key header (should use Authorization: Bearer token)',
            'allowed_files': []
        },
        'localStorage_license_key': {
            'pattern': r'localStorage\.(getItem|setItem)\([\'"]variosync_license_key',
            'error': 'Using localStorage for license_key (should use variosync_auth_token)',
            'allowed_files': []
        },
        'window_license_key': {
            'pattern': r'window\.(VarioSync_LICENSE_KEY|getLicenseKey)',
            'error': 'Using window.license_key (should use JWT token)',
            'allowed_files': []
        },
        'url_license_key': {
            'pattern': r'license_key=.*url_for|license_key=.*href|license_key=.*redirect',
            'error': 'license_key in URL parameters (should use JWT token)',
            'allowed_files': []
        }
    }
    
    # Directories to check
    check_dirs = [
        'web/routes',
        'web/templates',
        'web/static/js',
        'storage',
        'database'
    ]
    
    all_issues = []
    files_checked = 0
    
    # Check each directory
    for dir_name in check_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            print(f"{YELLOW}⚠️  Directory not found: {dir_name}{RESET}")
            continue
        
        # Get all Python and JavaScript files
        for ext in ['*.py', '*.js', '*.html']:
            for file_path in dir_path.rglob(ext):
                if file_path.is_file():
                    files_checked += 1
                    issues = check_file_for_issues(file_path, patterns)
                    all_issues.extend(issues)
    
    # Print results
    print(f"📊 Files checked: {files_checked}\n")
    
    if not all_issues:
        print(f"{GREEN}✅ No migration issues found!{RESET}\n")
        print(f"{GREEN}All license_key references have been properly migrated to user_id.{RESET}")
        return 0
    else:
        print(f"{RED}❌ Found {len(all_issues)} potential migration issues:{RESET}\n")
        
        # Group issues by pattern
        by_pattern = {}
        for issue in all_issues:
            pattern = issue['pattern']
            if pattern not in by_pattern:
                by_pattern[pattern] = []
            by_pattern[pattern].append(issue)
        
        # Print grouped issues
        for pattern, issues in by_pattern.items():
            print(f"{YELLOW}⚠️  {pattern}:{RESET}")
            for issue in issues[:5]:  # Show first 5 of each type
                print(f"  {RED}✗{RESET} {issue['file']}:{issue['line']}")
                print(f"    {issue['message']}")
                if issue['line_content']:
                    print(f"    Line: {issue['line_content'][:80]}...")
            if len(issues) > 5:
                print(f"    ... and {len(issues) - 5} more")
            print()
        
        return 1

def verify_positive_changes():
    """Verify that positive changes (JWT usage) are present"""
    print(f"\n{YELLOW}🔍 Verifying JWT authentication implementation...{RESET}\n")
    
    positive_patterns = {
        'jwt_auth_decorator': {
            'pattern': r'@auth_manager\.require_auth',
            'description': 'Routes using @require_auth decorator'
        },
        'user_id_from_g': {
            'pattern': r'g\.user_id|getattr\(g,\s*[\'"]user_id',
            'description': 'Code using g.user_id'
        },
        'authorization_header': {
            'pattern': r'Authorization.*Bearer|Bearer.*token',
            'description': 'Code using Authorization: Bearer header'
        },
        'auth_token_storage': {
            'pattern': r'variosync_auth_token|authToken',
            'description': 'Code using authToken/variosync_auth_token'
        }
    }
    
    check_dirs = ['web/routes', 'web/templates', 'web/static/js']
    found_patterns = {name: 0 for name in positive_patterns.keys()}
    
    for dir_name in check_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            continue
        
        for ext in ['*.py', '*.js', '*.html']:
            for file_path in dir_path.rglob(ext):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            for pattern_name, pattern_info in positive_patterns.items():
                                if re.search(pattern_info['pattern'], content, re.IGNORECASE):
                                    found_patterns[pattern_name] += 1
                    except Exception:
                        pass
    
    print(f"{GREEN}✅ JWT Implementation Status:{RESET}\n")
    for pattern_name, count in found_patterns.items():
        status = f"{GREEN}✓{RESET}" if count > 0 else f"{RED}✗{RESET}"
        desc = positive_patterns[pattern_name]['description']
        print(f"  {status} {desc}: {count} occurrences")
    
    print()

if __name__ == '__main__':
    exit_code = main()
    verify_positive_changes()
    
    if exit_code == 0:
        print(f"\n{GREEN}🎉 Migration verification complete!{RESET}")
    else:
        print(f"\n{RED}⚠️  Please review the issues above.{RESET}")
    
    exit(exit_code)
