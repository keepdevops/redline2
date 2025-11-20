#!/usr/bin/env python3
"""
Interactive setup script for Massive.com API key configuration in REDLINE.
Provides a user-friendly way to configure the API key.
"""

import os
import json
import sys
from pathlib import Path

def get_config_dir():
    """Get REDLINE config directory."""
    home = Path.home()
    config_dir = home / ".redline"
    config_dir.mkdir(exist_ok=True)
    return config_dir

def get_api_keys_file():
    """Get path to API keys config file."""
    return get_config_dir() / "api_keys.json"

def save_to_config_file(api_key):
    """Save API key to REDLINE config file."""
    api_keys_file = get_api_keys_file()
    
    # Load existing keys
    if api_keys_file.exists():
        try:
            with open(api_keys_file, 'r') as f:
                keys = json.load(f)
        except:
            keys = {}
    else:
        keys = {}
    
    # Update with Massive.com key
    keys['massive'] = api_key
    
    # Save back
    with open(api_keys_file, 'w') as f:
        json.dump(keys, f, indent=2)
    
    # Set secure permissions (rw-------)
    os.chmod(api_keys_file, 0o600)
    
    return api_keys_file

def save_to_env_file(api_key):
    """Save API key to shell RC file."""
    shell = os.environ.get('SHELL', '/bin/bash')
    shell_name = Path(shell).name
    
    if shell_name == 'zsh':
        rc_file = Path.home() / '.zshrc'
    elif shell_name == 'bash':
        rc_file = Path.home() / '.bashrc'
    else:
        rc_file = Path.home() / '.profile'
    
    # Read existing content
    content = ""
    if rc_file.exists():
        with open(rc_file, 'r') as f:
            content = f.read()
    
    # Remove old MASSIVE_API_KEY if exists
    lines = content.split('\n')
    new_lines = []
    skip_next = False
    for i, line in enumerate(lines):
        if 'MASSIVE_API_KEY' in line:
            continue
        new_lines.append(line)
    
    # Add new entry
    new_lines.append("")
    new_lines.append("# Massive.com API Key for REDLINE")
    new_lines.append(f'export MASSIVE_API_KEY="{api_key}"')
    
    # Write back
    with open(rc_file, 'w') as f:
        f.write('\n'.join(new_lines))
    
    return rc_file

def test_api_key(api_key):
    """Test the API key by trying to initialize the downloader."""
    try:
        from redline.downloaders.massive_downloader import MassiveDownloader
        downloader = MassiveDownloader(api_key=api_key)
        print("✅ API key is valid (downloader initialized successfully)")
        return True
    except Exception as e:
        print(f"⚠️  Could not verify API key: {e}")
        print("   (This is normal if the massive-client library is not installed)")
        return False

def main():
    print("=" * 50)
    print("Massive.com API Key Setup for REDLINE")
    print("=" * 50)
    print()
    
    # Check if already configured
    api_keys_file = get_api_keys_file()
    existing_key = None
    if api_keys_file.exists():
        try:
            with open(api_keys_file, 'r') as f:
                keys = json.load(f)
                existing_key = keys.get('massive')
        except:
            pass
    
    if existing_key:
        print(f"⚠️  Found existing API key: {existing_key[:10]}...")
        response = input("Do you want to update it? (y/n): ").strip().lower()
        if response != 'y':
            print("Keeping existing API key.")
            return 0
    
    # Get API key from user
    print()
    print("Enter your Massive.com API key:")
    print("(Get it from https://massive.com)")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API key cannot be empty")
        return 1
    
    # Choose configuration method
    print()
    print("Choose configuration method:")
    print("1. Save to REDLINE config file (for web UI)")
    print("2. Set as environment variable (for command-line)")
    print("3. Both (recommended)")
    choice = input("Enter choice (1-3): ").strip()
    
    config_saved = False
    env_saved = False
    
    if choice in ['1', '3']:
        print("\n📝 Saving to REDLINE config file...")
        config_file = save_to_config_file(api_key)
        print(f"✅ Saved to: {config_file}")
        config_saved = True
    
    if choice in ['2', '3']:
        print("\n📝 Saving to environment file...")
        rc_file = save_to_env_file(api_key)
        print(f"✅ Added to: {rc_file}")
        print(f"   Run 'source {rc_file}' or restart terminal to use in new sessions")
        env_saved = True
        
        # Set for current session
        os.environ['MASSIVE_API_KEY'] = api_key
        print("✅ Set for current session")
    
    # Test the API key
    print()
    print("🧪 Testing API key...")
    test_api_key(api_key)
    
    # Summary
    print()
    print("=" * 50)
    print("✅ Setup Complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    if config_saved:
        print("  • API key is saved and ready for REDLINE web UI")
        print("  • Go to Settings → API Keys to verify")
    if env_saved:
        print("  • Restart terminal or run 'source ~/.zshrc' (or ~/.bashrc)")
        print("  • Use in Python scripts: os.environ.get('MASSIVE_API_KEY')")
    print()
    print("To use in REDLINE:")
    print("  1. Go to Settings → API Keys")
    print("  2. Find 'Massive.com' in the list")
    print("  3. Your API key should be saved (or enter it manually)")
    print("  4. Go to Download tab")
    print("  5. Select 'Massive.com' as source")
    print("  6. Download data!")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

