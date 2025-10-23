#!/usr/bin/env python3
"""
REDLINE Update Installer
Handles automatic updates for different installation methods
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class UpdateInstaller:
    def __init__(self):
        self.platform = platform.system().lower()
        self.installation_method = self._detect_installation_method()
    
    def _detect_installation_method(self):
        """Detect how REDLINE was installed"""
        # Check if installed via pip
        try:
            import redline
            if hasattr(redline, '__file__'):
                redline_path = Path(redline.__file__).parent
                if 'site-packages' in str(redline_path):
                    return 'pip'
        except ImportError:
            pass
        
        # Check if running from source
        if Path('main.py').exists() and Path('web_app.py').exists():
            return 'source'
        
        # Check if running as executable
        if getattr(sys, 'frozen', False):
            return 'executable'
        
        # Check if running in Docker
        if os.path.exists('/.dockerenv'):
            return 'docker'
        
        return 'unknown'
    
    def install_update(self, update_file_path):
        """Install update based on detected installation method"""
        print(f"🔍 Detected installation method: {self.installation_method}")
        
        if self.installation_method == 'pip':
            return self._install_pip_update(update_file_path)
        elif self.installation_method == 'source':
            return self._install_source_update(update_file_path)
        elif self.installation_method == 'executable':
            return self._install_executable_update(update_file_path)
        elif self.installation_method == 'docker':
            return self._install_docker_update(update_file_path)
        else:
            print("❌ Unknown installation method")
            return False
    
    def _install_pip_update(self, update_file_path):
        """Install update via pip"""
        update_file = Path(update_file_path)
        
        if update_file.suffix == '.whl':
            print("📦 Installing PyPI wheel package...")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install',
                    str(update_file), '--upgrade', '--force-reinstall'
                ], check=True, capture_output=True, text=True)
                
                print("✅ PyPI package updated successfully")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Pip installation failed: {e.stderr}")
                return False
        
        elif update_file.suffix in ['.tar.gz', '.zip']:
            print("📁 Installing from source archive...")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install',
                    str(update_file), '--upgrade', '--force-reinstall'
                ], check=True, capture_output=True, text=True)
                
                print("✅ Source installation completed")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Source installation failed: {e.stderr}")
                return False
        
        else:
            print("❌ Unsupported file format for pip installation")
            return False
    
    def _install_source_update(self, update_file_path):
        """Install update for source installation"""
        update_file = Path(update_file_path)
        
        if update_file.suffix in ['.tar.gz', '.zip']:
            print("📁 Extracting source archive...")
            import shutil
            import tempfile
            
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    shutil.unpack_archive(update_file, temp_dir)
                    
                    # Find the extracted directory
                    extracted_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
                    if extracted_dirs:
                        source_dir = extracted_dirs[0]
                        
                        # Copy files to current directory
                        print("📋 Copying files...")
                        for item in source_dir.iterdir():
                            if item.is_file():
                                shutil.copy2(item, item.name)
                            elif item.is_dir():
                                if item.name != '__pycache__':
                                    shutil.copytree(item, item.name, dirs_exist_ok=True)
                        
                        print("✅ Source files updated successfully")
                        return True
                    else:
                        print("❌ Could not find extracted source directory")
                        return False
                        
            except Exception as e:
                print(f"❌ Source update failed: {str(e)}")
                return False
        
        else:
            print("❌ Source installation requires tar.gz or zip archive")
            return False
    
    def _install_executable_update(self, update_file_path):
        """Install update for executable installation"""
        update_file = Path(update_file_path)
        
        if update_file.suffix in ['.exe', ''] or update_file.is_file():
            print("💻 Executable update detected")
            print(f"📁 Please manually replace the executable: {update_file}")
            print("🔄 Restart the application after replacement")
            return True
        else:
            print("❌ Executable installation requires executable file")
            return False
    
    def _install_docker_update(self, update_file_path):
        """Install update for Docker installation"""
        print("🐳 Docker installation detected")
        print("📋 To update Docker installation:")
        print("1. Pull the latest image: docker pull redline-financial:latest")
        print("2. Stop current container: docker stop <container_name>")
        print("3. Start new container: docker run -p 8080:8080 redline-financial:latest")
        return True
    
    def get_update_instructions(self, update_file_path):
        """Get update instructions for the detected installation method"""
        update_file = Path(update_file_path)
        
        instructions = {
            'pip': f"""
📦 PyPI Installation Update Instructions:
1. Install the update: pip install {update_file} --upgrade --force-reinstall
2. Restart the application
            """,
            
            'source': f"""
📁 Source Installation Update Instructions:
1. Extract the archive: tar -xzf {update_file}
2. Copy files to your installation directory
3. Install dependencies: pip install -r requirements.txt
4. Restart the application
            """,
            
            'executable': f"""
💻 Executable Installation Update Instructions:
1. Stop the current application
2. Replace the executable with: {update_file}
3. Restart the application
            """,
            
            'docker': f"""
🐳 Docker Installation Update Instructions:
1. Pull latest image: docker pull redline-financial:latest
2. Stop current container: docker stop <container_name>
3. Start new container: docker run -p 8080:8080 redline-financial:latest
            """
        }
        
        return instructions.get(self.installation_method, "❌ Unknown installation method")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='REDLINE Update Installer')
    parser.add_argument('update_file', help='Path to update file')
    parser.add_argument('--instructions', action='store_true', help='Show update instructions')
    
    args = parser.parse_args()
    
    installer = UpdateInstaller()
    
    if args.instructions:
        print(installer.get_update_instructions(args.update_file))
    else:
        installer.install_update(args.update_file)
