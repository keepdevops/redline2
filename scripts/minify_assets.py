#!/usr/bin/env python3
"""
Minify JavaScript and CSS assets for REDLINE Web Application
Reduces file sizes by 50-70% for faster page loads
"""

import os
import subprocess
import sys
from pathlib import Path

def check_tool_installed(tool_name):
    """Check if a tool is installed."""
    try:
        subprocess.run(['which', tool_name], check=True, capture_output=True)
        return True
    except:
        return False

def install_npm_packages():
    """Install npm packages needed for minification."""
    print("Installing npm packages for minification...")
    try:
        subprocess.run(['npm', 'install', '--save-dev', 'terser', 'cssnano', 'clippy'], check=True)
        print("✓ npm packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing npm packages: {e}")
        return False
    except FileNotFoundError:
        print("✗ npm not found. Please install Node.js and npm first.")
        return False

def minify_js_file(input_file, output_file):
    """Minify a JavaScript file using terser."""
    try:
        subprocess.run([
            'npx', 'terser', input_file,
            '--compress',
            '--mangle',
            '--output', output_file
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to minify {input_file}: {e}")
        return False

def minify_css_file(input_file, output_file):
    """Minify a CSS file using cssnano."""
    try:
        subprocess.run([
            'npx', 'cssnano', input_file, output_file
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to minify {input_file}: {e}")
        return False

def get_file_size(file_path):
    """Get file size in KB."""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / 1024
    return 0

def minify_assets():
    """Minify all JavaScript and CSS assets."""
    print("=" * 60)
    print("REDLINE Asset Minification")
    print("=" * 60)
    
    # Check if npm is installed
    if not check_tool_installed('npm'):
        print("\n⚠ npm not found. Installing dependencies...")
        if not install_npm_packages():
            print("\n⚠ Skipping minification - npm not available")
            print("For production, install Node.js and run: npm install --save-dev terser cssnano")
            return False
    
    # Get base directory
    base_dir = Path(__file__).parent.parent
    static_dir = base_dir / 'redline' / 'web' / 'static'
    
    # Files to minify
    files_to_minify = [
        # JavaScript files
        ('redline/web/static/js/main.js', 'redline/web/static/js/main.min.js'),
        ('redline/web/static/js/color-customizer.js', 'redline/web/static/js/color-customizer.min.js'),
        ('redline/web/static/js/virtual-scroll.js', 'redline/web/static/js/virtual-scroll.min.js'),
        
        # CSS files
        ('redline/web/static/css/main.css', 'redline/web/static/css/main.min.css'),
        ('redline/web/static/css/themes.css', 'redline/web/static/css/themes.min.css'),
        ('redline/web/static/css/virtual-scroll.css', 'redline/web/static/css/virtual-scroll.min.css'),
        ('redline/web/static/css/color-customizer.css', 'redline/web/static/css/color-customizer.min.css'),
    ]
    
    print(f"\nMinifying {len(files_to_minify)} files...\n")
    
    total_original_size = 0
    total_minified_size = 0
    success_count = 0
    
    for input_file, output_file in files_to_minify:
        input_path = base_dir / input_file
        output_path = base_dir / output_file
        
        if not input_path.exists():
            print(f"⚠ Skipping {input_file} (not found)")
            continue
        
        # Get original size
        original_size = get_file_size(input_path)
        
        # Minify
        is_js = input_file.endswith('.js')
        success = minify_js_file(str(input_path), str(output_path)) if is_js else minify_css_file(str(input_path), str(output_path))
        
        if success and output_path.exists():
            minified_size = get_file_size(output_path)
            reduction = ((original_size - minified_size) / original_size * 100) if original_size > 0 else 0
            
            print(f"✓ {os.path.basename(input_file):30} {original_size:6.2f} KB → {minified_size:6.2f} KB ({reduction:5.1f}% smaller)")
            
            total_original_size += original_size
            total_minified_size += minified_size
            success_count += 1
        else:
            print(f"✗ Failed to minify {input_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("MINIFICATION SUMMARY")
    print("=" * 60)
    print(f"Files minified: {success_count}/{len([f for f, _ in files_to_minify if (base_dir / f).exists()])}")
    print(f"Total original size: {total_original_size:.2f} KB")
    print(f"Total minified size: {total_minified_size:.2f} KB")
    
    if total_original_size > 0:
        total_reduction = ((total_original_size - total_minified_size) / total_original_size * 100)
        print(f"Total reduction: {total_reduction:.1f}%")
        print(f"Bytes saved: {total_original_size * 1024 - total_minified_size * 1024:.0f}")
    
    print("\n✓ Minification complete!")
    print("Use .min.js and .min.css files in production")
    
    return success_count > 0

def main():
    """Main entry point."""
    try:
        success = minify_assets()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠ Minification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

