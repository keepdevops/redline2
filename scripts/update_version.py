#!/usr/bin/env python3
"""
REDLINE Version Management Script
Handles version updates across all configuration files
"""

import os
import re
import sys
from pathlib import Path

def get_current_version():
    """Get current version from setup.py"""
    try:
        with open('setup.py', 'r') as f:
            content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except FileNotFoundError:
        pass
    
    # Fallback to __version__.py
    try:
        with open('redline/__version__.py', 'r') as f:
            content = f.read()
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except FileNotFoundError:
        pass
    
    return "1.0.0"

def update_version_file(version):
    """Update redline/__version__.py"""
    version_file = Path('redline/__version__.py')
    version_file.parent.mkdir(exist_ok=True)
    
    content = f'''"""
REDLINE Version Information
"""

__version__ = "{version}"
__version_info__ = tuple(map(int, __version__.split('.')))
'''
    
    with open(version_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {version_file}")

def update_setup_py(version):
    """Update setup.py version"""
    setup_file = Path('setup.py')
    if not setup_file.exists():
        print("⚠️  setup.py not found")
        return
    
    with open(setup_file, 'r') as f:
        content = f.read()
    
    # Update version in setup.py
    pattern = r'version\s*=\s*["\'][^"\']+["\']'
    replacement = f'version="{version}"'
    new_content = re.sub(pattern, replacement, content)
    
    with open(setup_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated {setup_file}")

def update_dockerfile(version):
    """Update Dockerfile labels"""
    dockerfile = Path('Dockerfile.working-insights')
    if not dockerfile.exists():
        print("⚠️  Dockerfile.working-insights not found")
        return
    
    with open(dockerfile, 'r') as f:
        content = f.read()
    
    # Update LABEL version
    pattern = r'LABEL version="[^"]*"'
    replacement = f'LABEL version="{version}"'
    new_content = re.sub(pattern, replacement, content)
    
    with open(dockerfile, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated {dockerfile}")

def update_docker_compose(version):
    """Update docker-compose version"""
    compose_file = Path('docker-compose-working.yml')
    if not compose_file.exists():
        print("⚠️  docker-compose-working.yml not found")
        return
    
    with open(compose_file, 'r') as f:
        content = f.read()
    
    # Update image version
    pattern = r'image:\s*redline:[^\s]+'
    replacement = f'image: redline:{version}'
    new_content = re.sub(pattern, replacement, content)
    
    with open(compose_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated {compose_file}")

def update_readme(version):
    """Update README.md version references"""
    readme_file = Path('README.md')
    if not readme_file.exists():
        print("⚠️  README.md not found")
        return
    
    with open(readme_file, 'r') as f:
        content = f.read()
    
    # Update version references in README
    pattern = r'redline-financial==[0-9]+\.[0-9]+\.[0-9]+'
    replacement = f'redline-financial=={version}'
    new_content = re.sub(pattern, replacement, content)
    
    with open(readme_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated {readme_file}")

def validate_version(version):
    """Validate version format"""
    pattern = r'^[0-9]+\.[0-9]+\.[0-9]+$'
    if not re.match(pattern, version):
        raise ValueError(f"Invalid version format: {version}. Expected format: X.Y.Z")
    
    parts = version.split('.')
    for part in parts:
        if not part.isdigit():
            raise ValueError(f"Version parts must be numeric: {version}")
    
    return True

def main():
    """Main version update function"""
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <new_version>")
        print("Example: python update_version.py 1.2.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    try:
        validate_version(new_version)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    current_version = get_current_version()
    print(f"🔄 Updating version from {current_version} to {new_version}")
    
    # Update all version files
    update_version_file(new_version)
    update_setup_py(new_version)
    update_dockerfile(new_version)
    update_docker_compose(new_version)
    update_readme(new_version)
    
    print(f"🎉 Successfully updated version to {new_version}")
    print("\n📋 Next steps:")
    print("1. Commit changes: git add . && git commit -m 'Bump version to {new_version}'")
    print("2. Create tag: git tag v{new_version}")
    print("3. Push: git push origin main --tags")
    print("4. GitHub Actions will automatically create a release")

if __name__ == '__main__':
    main()
