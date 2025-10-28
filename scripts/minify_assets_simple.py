#!/usr/bin/env python3
"""
Simple asset minification for Docker builds - removes comments and whitespace
Does NOT require npm or external tools
"""

import os
import re
from pathlib import Path

def minify_js(content):
    """Minify JavaScript by removing comments and extra whitespace."""
    # Remove single-line comments
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    
    # Remove multi-line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove extra whitespace around operators
    content = re.sub(r'\s+([=+\-*/(),;{}[\]:.])', r'\1', content)
    content = re.sub(r'([=+\-*/(),;{}[\]:.])\s+', r'\1', content)
    
    # Remove extra newlines
    content = re.sub(r'\n+', '\n', content)
    content = re.sub(r'\s+$', '', content, flags=re.MULTILINE)
    
    return content

def minify_css(content):
    """Minify CSS by removing comments and extra whitespace."""
    # Remove CSS comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove extra whitespace
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*([{}:;,])\s*', r'\1', content)
    
    # Remove newlines
    content = re.sub(r'\n', '', content)
    
    return content

def minify_file(input_path, output_path):
    """Minify a single file."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if input_path.suffix == '.js':
            minified = minify_js(content)
        elif input_path.suffix == '.css':
            minified = minify_css(content)
        else:
            return False
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified)
        
        return True
    except Exception as e:
        print(f"Error minifying {input_path}: {e}")
        return False

def minify_assets():
    """Minify all JavaScript and CSS assets."""
    base_dir = Path(__file__).parent.parent
    
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
    
    success_count = 0
    
    for input_file, output_file in files_to_minify:
        input_path = base_dir / input_file
        output_path = base_dir / output_file
        
        if not input_path.exists():
            continue
        
        if minify_file(input_path, output_path):
            original_size = input_path.stat().st_size / 1024
            minified_size = output_path.stat().st_size / 1024
            reduction = (1 - minified_size / original_size) * 100
            print(f"✓ {input_file}: {original_size:.2f} KB → {minified_size:.2f} KB ({reduction:.1f}% reduction)")
            success_count += 1
    
    return success_count > 0

if __name__ == '__main__':
    minify_assets()

