#!/usr/bin/env python3
"""
REDLINE PyPI Publishing Script
Handles PyPI package building, testing, and publishing
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

class PyPIPublisher:
    def __init__(self, test_pypi=False, dry_run=False):
        self.test_pypi = test_pypi
        self.dry_run = dry_run
        self.project_root = Path.cwd()
        self.dist_dir = self.project_root / 'dist'
        self.packages_dir = self.dist_dir / 'packages'
        
    def clean_build(self):
        """Clean build artifacts"""
        print("🧹 Cleaning build artifacts...")
        
        dirs_to_clean = [
            'build',
            'dist',
            '*.egg-info',
            '.pytest_cache',
            '__pycache__',
        ]
        
        for pattern in dirs_to_clean:
            if '*' in pattern:
                # Handle glob patterns
                for path in self.project_root.glob(pattern):
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        path.unlink(missing_ok=True)
            else:
                path = self.project_root / pattern
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        path.unlink(missing_ok=True)
        
        # Clean Python cache files
        for pycache in self.project_root.rglob('__pycache__'):
            shutil.rmtree(pycache, ignore_errors=True)
        
        for pyc in self.project_root.rglob('*.pyc'):
            pyc.unlink(missing_ok=True)
        
        print("✅ Build artifacts cleaned")
    
    def check_requirements(self):
        """Check if required tools are installed"""
        print("🔍 Checking requirements...")
        
        required_tools = ['python', 'pip', 'build', 'twine']
        missing_tools = []
        
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"❌ Missing required tools: {', '.join(missing_tools)}")
            print("Install missing tools with:")
            print("pip install build twine")
            return False
        
        print("✅ All required tools available")
        return True
    
    def validate_package(self):
        """Validate package configuration"""
        print("📋 Validating package configuration...")
        
        # Check essential files
        essential_files = [
            'setup.py',
            'pyproject.toml',
            'MANIFEST.in',
            'README.md',
            'requirements.txt',
            'redline/__version__.py',
        ]
        
        missing_files = []
        for file in essential_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing essential files: {', '.join(missing_files)}")
            return False
        
        # Check package structure
        if not (self.project_root / 'redline' / '__init__.py').exists():
            print("❌ Missing redline/__init__.py")
            return False
        
        print("✅ Package configuration valid")
        return True
    
    def build_package(self):
        """Build PyPI package"""
        print("📦 Building PyPI package...")
        
        # Create packages directory
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Build wheel and source distribution
            cmd = [
                sys.executable, '-m', 'build',
                '--outdir', str(self.packages_dir),
                '--wheel',
                '--sdist'
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Package built successfully")
            
            # List built files
            built_files = list(self.packages_dir.glob('*'))
            print(f"📁 Built files: {[f.name for f in built_files]}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def check_package(self):
        """Check package with twine"""
        print("🔍 Checking package with twine...")
        
        try:
            cmd = ['twine', 'check', str(self.packages_dir / '*')]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Package check passed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Package check failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def test_install(self):
        """Test package installation"""
        print("🧪 Testing package installation...")
        
        try:
            # Find wheel file
            wheel_files = list(self.packages_dir.glob('*.whl'))
            if not wheel_files:
                print("❌ No wheel file found")
                return False
            
            wheel_file = wheel_files[0]
            
            # Test installation
            cmd = [
                sys.executable, '-m', 'pip', 'install',
                str(wheel_file), '--force-reinstall', '--no-deps'
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Package installation test passed")
            
            # Test console commands
            console_commands = ['redline-gui', 'redline-web', 'redline']
            for cmd_name in console_commands:
                try:
                    result = subprocess.run([cmd_name, '--help'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"✅ Console command '{cmd_name}' works")
                    else:
                        print(f"⚠️  Console command '{cmd_name}' returned non-zero exit code")
                except subprocess.TimeoutExpired:
                    print(f"⚠️  Console command '{cmd_name}' timed out")
                except FileNotFoundError:
                    print(f"⚠️  Console command '{cmd_name}' not found")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation test failed: {e}")
            return False
    
    def publish_package(self):
        """Publish package to PyPI"""
        if self.dry_run:
            print("🔍 DRY RUN: Would publish package to PyPI")
            return True
        
        print("🚀 Publishing package to PyPI...")
        
        try:
            # Determine repository
            if self.test_pypi:
                repository = 'testpypi'
                print("📋 Publishing to Test PyPI")
            else:
                repository = 'pypi'
                print("📋 Publishing to PyPI")
            
            # Upload package
            cmd = [
                'twine', 'upload',
                '--repository', repository,
                str(self.packages_dir / '*')
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Package published successfully")
            
            if self.test_pypi:
                print("🔗 Test PyPI URL: https://test.pypi.org/project/redline-financial/")
            else:
                print("🔗 PyPI URL: https://pypi.org/project/redline-financial/")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Publishing failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def run_full_process(self):
        """Run the complete PyPI publishing process"""
        print("🚀 Starting REDLINE PyPI Publishing Process")
        print(f"📋 Test PyPI: {self.test_pypi}")
        print(f"📋 Dry Run: {self.dry_run}")
        
        steps = [
            ("Check Requirements", self.check_requirements),
            ("Validate Package", self.validate_package),
            ("Clean Build", self.clean_build),
            ("Build Package", self.build_package),
            ("Check Package", self.check_package),
            ("Test Installation", self.test_install),
            ("Publish Package", self.publish_package),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 Step: {step_name}")
            if not step_func():
                print(f"❌ Failed at step: {step_name}")
                return False
        
        print("\n🎉 PyPI publishing process completed successfully!")
        return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='REDLINE PyPI Publishing Script')
    parser.add_argument('--test-pypi', action='store_true', 
                       help='Publish to Test PyPI instead of PyPI')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without actually publishing')
    parser.add_argument('--clean-only', action='store_true',
                       help='Only clean build artifacts')
    parser.add_argument('--build-only', action='store_true',
                       help='Only build package (no publish)')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check existing package')
    
    args = parser.parse_args()
    
    publisher = PyPIPublisher(test_pypi=args.test_pypi, dry_run=args.dry_run)
    
    if args.clean_only:
        publisher.clean_build()
        return
    
    if args.build_only:
        publisher.check_requirements()
        publisher.validate_package()
        publisher.clean_build()
        publisher.build_package()
        publisher.check_package()
        return
    
    if args.check_only:
        publisher.check_package()
        return
    
    # Run full process
    success = publisher.run_full_process()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
