#!/usr/bin/env python3
"""
REDLINE Distribution Testing Suite
Tests all distribution formats and platforms
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
from pathlib import Path
import json
import time

class DistributionTester:
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_results = {}
        self.platform = platform.system().lower()
        self.architecture = platform.machine().lower()
        
    def run_test(self, test_name, test_func):
        """Run a test and record results"""
        print(f"\n🧪 Running test: {test_name}")
        try:
            result = test_func()
            self.test_results[test_name] = {
                'status': 'PASS' if result else 'FAIL',
                'platform': self.platform,
                'architecture': self.architecture,
                'timestamp': time.time()
            }
            print(f"✅ {test_name}: {'PASS' if result else 'FAIL'}")
            return result
        except Exception as e:
            self.test_results[test_name] = {
                'status': 'ERROR',
                'error': str(e),
                'platform': self.platform,
                'architecture': self.architecture,
                'timestamp': time.time()
            }
            print(f"❌ {test_name}: ERROR - {str(e)}")
            return False
    
    def test_pypi_package(self):
        """Test PyPI package installation and functionality"""
        try:
            # Check if wheel exists
            wheel_files = list(self.project_root.glob('dist/packages/*.whl'))
            if not wheel_files:
                print("⚠️  No PyPI wheel found, building...")
                subprocess.run(['python', '-m', 'build', '--outdir', 'dist/packages/'], check=True)
                wheel_files = list(self.project_root.glob('dist/packages/*.whl'))
            
            if not wheel_files:
                return False
            
            wheel_file = wheel_files[0]
            
            # Test installation in virtual environment
            with tempfile.TemporaryDirectory() as temp_dir:
                venv_path = Path(temp_dir) / 'test_venv'
                subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
                
                pip_path = venv_path / ('Scripts' if self.platform == 'windows' else 'bin') / 'pip'
                python_path = venv_path / ('Scripts' if self.platform == 'windows' else 'bin') / 'python'
                
                # Install package
                subprocess.run([str(pip_path), 'install', str(wheel_file)], check=True)
                
                # Test console commands
                result = subprocess.run([str(python_path), '-c', 'import redline; print(redline.__version__)'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    return False
                
                # Test CLI commands
                cli_result = subprocess.run([str(python_path), '-m', 'redline.cli.download', '--help'], 
                                          capture_output=True, text=True)
                return cli_result.returncode == 0
                
        except Exception as e:
            print(f"PyPI test error: {e}")
            return False
    
    def test_executables(self):
        """Test PyInstaller executables"""
        try:
            # Check if executables exist
            gui_exe = self.project_root / 'dist' / 'executables' / 'redline-gui'
            web_exe = self.project_root / 'dist' / 'executables' / 'redline-web'
            
            if self.platform == 'windows':
                gui_exe = gui_exe.with_suffix('.exe')
                web_exe = web_exe.with_suffix('.exe')
            
            if not gui_exe.exists() or not web_exe.exists():
                print("⚠️  Executables not found, building...")
                subprocess.run(['bash', 'build/scripts/build_executables.sh'], check=True)
            
            # Test GUI executable
            if gui_exe.exists():
                result = subprocess.run([str(gui_exe), '--help'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    return False
            
            # Test Web executable
            if web_exe.exists():
                result = subprocess.run([str(web_exe), '--help'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Executable test error: {e}")
            return False
    
    def test_docker_image(self):
        """Test Docker image build and run"""
        try:
            # Check if Docker is available
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
            
            # Build Docker image
            subprocess.run(['docker', 'build', '-f', 'Dockerfile.working-insights', 
                          '-t', 'redline-test', '.'], check=True)
            
            # Test Docker run
            result = subprocess.run(['docker', 'run', '--rm', '-p', '8081:8080', 
                                   'redline-test', '--help'], 
                                  capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Docker test error: {e}")
            return False
    
    def test_source_archives(self):
        """Test source archive creation and extraction"""
        try:
            # Check if archives exist
            tar_file = self.project_root / 'dist' / 'releases' / 'redline-1.0.0-source.tar.gz'
            zip_file = self.project_root / 'dist' / 'releases' / 'redline-1.0.0-source.zip'
            
            if not tar_file.exists() or not zip_file.exists():
                print("⚠️  Source archives not found, creating...")
                subprocess.run(['bash', 'build/scripts/create_release.sh'], check=True)
            
            # Test tar extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                subprocess.run(['tar', '-xzf', str(tar_file), '-C', temp_dir], check=True)
                extracted_dir = Path(temp_dir) / 'redline-1.0.0'
                
                if not extracted_dir.exists():
                    return False
                
                # Check essential files
                essential_files = ['main.py', 'web_app.py', 'requirements.txt', 'install_options_redline.sh']
                for file in essential_files:
                    if not (extracted_dir / file).exists():
                        return False
            
            # Test zip extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                subprocess.run(['unzip', str(zip_file), '-d', temp_dir], check=True)
                extracted_dir = Path(temp_dir) / 'redline-1.0.0'
                
                if not extracted_dir.exists():
                    return False
                
                # Check essential files
                essential_files = ['main.py', 'web_app.py', 'requirements.txt', 'install_options_redline.sh']
                for file in essential_files:
                    if not (extracted_dir / file).exists():
                        return False
            
            return True
            
        except Exception as e:
            print(f"Source archive test error: {e}")
            return False
    
    def test_license_system(self):
        """Test licensing system functionality"""
        try:
            # Test license validator
            validator_path = self.project_root / 'licensing' / 'client' / 'license_validator.py'
            if not validator_path.exists():
                return False
            
            result = subprocess.run([sys.executable, str(validator_path), '--help'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"License system test error: {e}")
            return False
    
    def test_update_system(self):
        """Test update system functionality"""
        try:
            # Test update checker
            checker_path = self.project_root / 'redline' / 'updates' / 'update_checker.py'
            if not checker_path.exists():
                return False
            
            result = subprocess.run([sys.executable, str(checker_path), '--help'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Update system test error: {e}")
            return False
    
    def test_build_scripts(self):
        """Test build automation scripts"""
        try:
            scripts = [
                'build/scripts/build_all.sh',
                'build/scripts/build_executables.sh',
                'build/scripts/create_release.sh'
            ]
            
            for script in scripts:
                script_path = self.project_root / script
                if not script_path.exists():
                    return False
                
                # Check if script is executable
                if not os.access(script_path, os.X_OK):
                    os.chmod(script_path, 0o755)
            
            return True
            
        except Exception as e:
            print(f"Build scripts test error: {e}")
            return False
    
    def test_github_workflows(self):
        """Test GitHub Actions workflows"""
        try:
            workflows = [
                '.github/workflows/docker-publish.yml',
                '.github/workflows/release.yml'
            ]
            
            for workflow in workflows:
                workflow_path = self.project_root / workflow
                if not workflow_path.exists():
                    return False
                
                # Basic YAML syntax check
                with open(workflow_path, 'r') as f:
                    content = f.read()
                    if 'name:' not in content or 'on:' not in content:
                        return False
            
            return True
            
        except Exception as e:
            print(f"GitHub workflows test error: {e}")
            return False
    
    def test_distribution_website(self):
        """Test distribution website"""
        try:
            website_path = self.project_root / 'dist' / 'website' / 'index.html'
            if not website_path.exists():
                return False
            
            # Check if HTML is valid
            with open(website_path, 'r') as f:
                content = f.read()
                if '<html' not in content or '</html>' not in content:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Distribution website test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all distribution tests"""
        print("🚀 Starting REDLINE Distribution Test Suite")
        print(f"📋 Platform: {self.platform} {self.architecture}")
        
        tests = [
            ('PyPI Package', self.test_pypi_package),
            ('Executables', self.test_executables),
            ('Docker Image', self.test_docker_image),
            ('Source Archives', self.test_source_archives),
            ('License System', self.test_license_system),
            ('Update System', self.test_update_system),
            ('Build Scripts', self.test_build_scripts),
            ('GitHub Workflows', self.test_github_workflows),
            ('Distribution Website', self.test_distribution_website),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        # Save results
        results_file = self.project_root / 'test_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")
        
        return passed == total

def main():
    """Main test runner"""
    tester = DistributionTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All distribution tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some distribution tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
