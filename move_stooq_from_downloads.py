#!/usr/bin/env python3
"""
Move Stooq .txt files from Downloads to data/stooq directory.
Run this script manually to move files from your Downloads folder.
"""

import os
import shutil
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from redline.utils.stooq_file_handler import is_stooq_file, get_stooq_data_dir

def move_stooq_files_from_downloads():
    """Move Stooq .txt files from Downloads to data/stooq."""
    downloads_dir = os.path.expanduser('~/Downloads')
    stooq_dir = get_stooq_data_dir()
    moved_files = []
    skipped_files = []
    errors = []

    if not os.path.exists(downloads_dir):
        print(f"❌ Downloads directory not found: {downloads_dir}")
        return moved_files

    print(f"📂 Scanning: {downloads_dir}")
    print(f"📂 Destination: {stooq_dir}\n")

    try:
        # Get all .txt files
        txt_files = [f for f in os.listdir(downloads_dir) 
                     if f.lower().endswith('.txt') and os.path.isfile(os.path.join(downloads_dir, f))]
        
        if not txt_files:
            print("ℹ️  No .txt files found in Downloads")
            return moved_files

        print(f"Found {len(txt_files)} .txt file(s):\n")

        for filename in txt_files:
            file_path = os.path.join(downloads_dir, filename)
            dest_path = os.path.join(stooq_dir, filename)

            # Check if it's a Stooq file
            if is_stooq_file(filename):
                # Check if destination already exists
                if os.path.exists(dest_path):
                    print(f"⚠️  {filename} - Already exists in stooq directory")
                    skipped_files.append(filename)
                else:
                    try:
                        shutil.move(file_path, dest_path)
                        moved_files.append(filename)
                        file_size = os.path.getsize(dest_path)
                        size_str = f"{file_size / 1024:.1f}KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f}MB"
                        print(f"✅ {filename} ({size_str})")
                    except Exception as e:
                        print(f"❌ {filename} - Error: {e}")
                        errors.append((filename, str(e)))
            else:
                print(f"⏭️  {filename} - Not a Stooq file (skipped)")
                skipped_files.append(filename)

    except PermissionError:
        print(f"❌ Permission denied accessing Downloads directory")
        print(f"💡 Try running this script with: python3 {__file__}")
        errors.append(("Permission Error", "Cannot access Downloads directory"))
    except Exception as e:
        print(f"❌ Error: {e}")
        errors.append(("General Error", str(e)))

    # Summary
    print(f"\n{'='*50}")
    print(f"📊 Summary:")
    print(f"  ✅ Moved: {len(moved_files)} file(s)")
    print(f"  ⏭️  Skipped: {len(skipped_files)} file(s)")
    print(f"  ❌ Errors: {len(errors)} file(s)")
    
    if moved_files:
        print(f"\n✅ Successfully moved to {stooq_dir}:")
        for f in moved_files:
            print(f"   - {f}")

    return moved_files

if __name__ == '__main__':
    print("🔍 Searching Downloads for Stooq .txt files...\n")
    moved = move_stooq_files_from_downloads()
    
    if moved:
        print(f"\n✨ Done! {len(moved)} file(s) moved to data/stooq")
    else:
        print("\n✨ No files were moved")



