#!/usr/bin/env python3
"""
REDLINE Update Checker
Checks for software updates and handles installation
"""

import os
import sys
import json
import requests
import subprocess
import platform
from pathlib import Path
from datetime import datetime

class UpdateChecker:
    def __init__(self, current_version=None, update_server_url=None):
        self.current_version = current_version or self._get_current_version()
        self.update_server_url = update_server_url or os.environ.get(
            'UPDATE_SERVER_URL',
            'https://api.github.com/repos/keepdevops/redline2/releases/latest'
        )
        self.github_api_url = 'https://api.github.com/repos/keepdevops/redline2/releases'
    
    def _get_current_version(self):
        """Get current version from __version__.py"""
        try:
            from redline import __version__
            return __version__
        except ImportError:
            return "1.0.0"
    
    def check_for_updates(self):
        """Check for available updates"""
        try:
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            
            releases = response.json()
            if not releases:
                return {
                    'update_available': False,
                    'error': 'No releases found'
                }
            
            latest_release = releases[0]
            latest_version = latest_release['tag_name'].lstrip('v')
            
            update_available = self._compare_versions(latest_version, self.current_version) > 0
            
            return {
                'update_available': update_available,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'release_info': latest_release if update_available else None,
                'download_url': self._get_download_url(latest_release) if update_available else None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'update_available': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'update_available': False,
                'error': f'Error checking updates: {str(e)}'
            }
    
    def _compare_versions(self, version1, version2):
        """Compare two version strings"""
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        
        v1 = version_tuple(version1)
        v2 = version_tuple(version2)
        
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        else:
            return 0
    
    def _get_download_url(self, release_info):
        """Get appropriate download URL for current platform"""
        platform_name = platform.system().lower()
        architecture = platform.machine().lower()
        
        # Map platform names
        platform_map = {
            'windows': 'windows',
            'darwin': 'macos',
            'linux': 'linux'
        }
        
        platform_key = platform_map.get(platform_name, platform_name)
        
        # Look for appropriate asset
        for asset in release_info.get('assets', []):
            asset_name = asset['name'].lower()
            
            # Check for PyPI package (recommended)
            if asset_name.endswith('.whl') and 'py3-none-any' in asset_name:
                return asset['browser_download_url']
            
            # Check for platform-specific executable
            if platform_key in asset_name:
                if architecture in ['x86_64', 'amd64'] and 'x64' in asset_name:
                    return asset['browser_download_url']
                elif architecture in ['arm64', 'aarch64'] and 'arm64' in asset_name:
                    return asset['browser_download_url']
                elif 'x64' not in asset_name and 'arm64' not in asset_name:
                    return asset['browser_download_url']
        
        # Fallback to source archive
        for asset in release_info.get('assets', []):
            if asset['name'].endswith('.tar.gz') or asset['name'].endswith('.zip'):
                return asset['browser_download_url']
        
        return None
    
    def download_update(self, download_url, download_path=None):
        """Download update file"""
        if not download_path:
            download_path = Path.home() / 'Downloads' / f'redline-update-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        
        download_path = Path(download_path)
        
        try:
            print(f"📥 Downloading update from: {download_url}")
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Determine file extension
            if download_url.endswith('.whl'):
                download_path = download_path.with_suffix('.whl')
            elif download_url.endswith('.tar.gz'):
                download_path = download_path.with_suffix('.tar.gz')
            elif download_url.endswith('.zip'):
                download_path = download_path.with_suffix('.zip')
            else:
                download_path = download_path.with_suffix('.exe')
            
            # Download file
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r📊 Progress: {percent:.1f}%", end='', flush=True)
            
            print(f"\n✅ Download completed: {download_path}")
            return download_path
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Download failed: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error downloading update: {str(e)}")
            return None
    
    def install_update(self, update_file_path):
        """Install the downloaded update"""
        update_file = Path(update_file_path)
        
        if not update_file.exists():
            print(f"❌ Update file not found: {update_file}")
            return False
        
        try:
            if update_file.suffix == '.whl':
                # Install PyPI package
                print("📦 Installing PyPI package...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    str(update_file), '--upgrade', '--force-reinstall'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ PyPI package installed successfully")
                    return True
                else:
                    print(f"❌ Installation failed: {result.stderr}")
                    return False
            
            elif update_file.suffix in ['.tar.gz', '.zip']:
                # Extract source archive
                print("📁 Extracting source archive...")
                import shutil
                import tempfile
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    shutil.unpack_archive(update_file, temp_dir)
                    
                    # Find the extracted directory
                    extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
                    if extracted_dirs:
                        source_dir = extracted_dirs[0]
                        
                        # Install from source
                        print("📦 Installing from source...")
                        result = subprocess.run([
                            sys.executable, '-m', 'pip', 'install', 
                            str(source_dir), '--upgrade', '--force-reinstall'
                        ], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            print("✅ Source installation completed successfully")
                            return True
                        else:
                            print(f"❌ Installation failed: {result.stderr}")
                            return False
                    else:
                        print("❌ Could not find extracted source directory")
                        return False
            
            else:
                # Executable file
                print("💻 Executable update detected")
                print(f"📁 Please run the executable manually: {update_file}")
                return True
                
        except Exception as e:
            print(f"❌ Installation error: {str(e)}")
            return False
    
    def auto_update(self):
        """Automatically check, download, and install updates"""
        print("🔍 Checking for updates...")
        
        update_info = self.check_for_updates()
        
        if update_info.get('error'):
            print(f"❌ Error checking updates: {update_info['error']}")
            return False
        
        if not update_info['update_available']:
            print(f"✅ You're running the latest version: {self.current_version}")
            return True
        
        print(f"🆕 Update available!")
        print(f"📋 Current version: {update_info['current_version']}")
        print(f"🆕 Latest version: {update_info['latest_version']}")
        
        download_url = update_info['download_url']
        if not download_url:
            print("❌ No download URL available")
            return False
        
        # Download update
        update_file = self.download_update(download_url)
        if not update_file:
            return False
        
        # Install update
        if self.install_update(update_file):
            print("🎉 Update completed successfully!")
            print("🔄 Please restart the application to use the new version")
            return True
        else:
            print("❌ Update installation failed")
            return False

def check_updates():
    """Simple function to check for updates"""
    checker = UpdateChecker()
    return checker.check_for_updates()

def auto_update():
    """Simple function to perform automatic update"""
    checker = UpdateChecker()
    return checker.auto_update()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='REDLINE Update Checker')
    parser.add_argument('--check', action='store_true', help='Check for updates')
    parser.add_argument('--update', action='store_true', help='Perform automatic update')
    parser.add_argument('--version', help='Specify current version')
    
    args = parser.parse_args()
    
    checker = UpdateChecker(current_version=args.version)
    
    if args.check:
        result = checker.check_for_updates()
        if result['update_available']:
            print(f"🆕 Update available: {result['latest_version']}")
            print(f"📥 Download URL: {result['download_url']}")
        else:
            print(f"✅ Up to date: {result['current_version']}")
    
    elif args.update:
        checker.auto_update()
    
    else:
        # Default: check for updates
        result = checker.check_for_updates()
        if result['update_available']:
            print(f"🆕 Update available: {result['latest_version']}")
            response = input("Would you like to download and install it? (y/N): ")
            if response.lower() in ['y', 'yes']:
                checker.auto_update()
        else:
            print(f"✅ You're running the latest version: {result['current_version']}")