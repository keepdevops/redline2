#!/usr/bin/env python3
"""
Patch TensorFlow 2.20.0 to fix TypeError on ARM64.
Fixes the issue where doc_module.__doc__ can be None.
"""

import os
import sys

def patch_tensorflow():
    """Patch TensorFlow's all_util.py file."""
    # Find TensorFlow installation
    import site
    site_packages = site.getsitepackages()
    
    tf_util_path = None
    for sp in site_packages:
        candidate = os.path.join(sp, 'tensorflow', 'python', 'util', 'all_util.py')
        if os.path.exists(candidate):
            tf_util_path = candidate
            break
    
    if not tf_util_path:
        print("⚠️  TensorFlow util file not found")
        return False
    
    print(f"Found TensorFlow util file: {tf_util_path}")
    
    # Read the file
    with open(tf_util_path, 'r') as f:
        lines = f.readlines()
    
    # Check if already patched
    content_str = ''.join(lines)
    if 'if doc_module.__doc__ is not None:' in content_str:
        print("✅ TensorFlow already patched")
        return True
    
    # Find the problematic section
    # Looking for:
    #   for doc_module in doc_string_modules:
    #     results.update([m.group(1)
    #                     for m in _reference_pattern.finditer(doc_module.__doc__)
    #                     if m.group(1) in cur_members])
    
    patched_lines = []
    i = 0
    patched = False
    
    while i < len(lines):
        line = lines[i]
        
        # Look for: for doc_module in doc_string_modules:
        if 'for doc_module in doc_string_modules:' in line:
            loop_indent = len(line) - len(line.lstrip())
            patched_lines.append(line)
            i += 1
            
            # Check if next line starts results.update
            if i < len(lines) and 'results.update' in lines[i]:
                # Add None check before results.update
                patched_lines.append(' ' * (loop_indent + 2) + 'if doc_module.__doc__ is not None:\n')
                # Add results.update with extra indent
                update_line = lines[i]
                update_indent = len(update_line) - len(update_line.lstrip())
                patched_lines.append(' ' * (update_indent + 2) + update_line.lstrip())
                i += 1
                patched = True
                
                # Continue copying remaining lines of the list comprehension with proper indent
                while i < len(lines):
                    next_line = lines[i]
                    # Stop if we hit a line with same or less indent than the for loop
                    if next_line.strip() and len(next_line) - len(next_line.lstrip()) <= loop_indent:
                        break
                    # Keep the relative indentation but ensure it's indented under the if
                    if next_line.strip():
                        current_indent = len(next_line) - len(next_line.lstrip())
                        # Maintain relative indent but add 2 more spaces for the if block
                        new_indent = ' ' * (current_indent + 2)
                        patched_lines.append(new_indent + next_line.lstrip())
                    else:
                        patched_lines.append(next_line)
                    i += 1
                continue
        
        patched_lines.append(line)
        i += 1
    
    if not patched:
        print("⚠️  Could not find pattern to patch")
        return False
    
    # Write the patched content
    with open(tf_util_path, 'w') as f:
        f.writelines(patched_lines)
    
    print("✅ Successfully patched TensorFlow all_util.py")
    return True

if __name__ == '__main__':
    success = patch_tensorflow()
    sys.exit(0 if success else 1)
