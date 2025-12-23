#!/usr/bin/env python3
"""
Fix director folders that were created as files instead of directories.
This script will:
1. Find items in AJ that are files but should be directories
2. Convert them to directories with correct structure
"""

import os
import shutil

BASE_PATH = "/Volumes/Films/AJ/"

def fix_director_folders():
    """Fix files that should be directories"""
    
    if not os.path.exists(BASE_PATH):
        print(f"Error: Base path doesn't exist: {BASE_PATH}")
        return
    
    fixed_count = 0
    error_count = 0
    
    # Scan the base directory
    items = os.listdir(BASE_PATH)
    
    for item in items:
        full_path = os.path.join(BASE_PATH, item)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(full_path):
            print(f"\nFound file (should be directory): {item}")
            
            try:
                # Remove the file
                os.remove(full_path)
                print(f"  ✓ Removed file: {item}")
                
                # Create directory with the same name
                os.makedirs(full_path, exist_ok=True)
                print(f"  ✓ Created directory: {item}")
                
                fixed_count += 1
                
            except Exception as e:
                print(f"  ✗ Error fixing {item}: {e}")
                error_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Fixed: {fixed_count}")
    print(f"  Errors: {error_count}")
    print(f"{'='*60}")
    
    # Now fix permissions on all directories
    print("\nFixing directory permissions...")
    try:
        for root, dirs, files in os.walk(BASE_PATH):
            for directory in dirs:
                dir_path = os.path.join(root, directory)
                os.chmod(dir_path, 0o755)
        print("✓ Fixed permissions on all directories")
    except Exception as e:
        print(f"Warning: Could not fix all permissions: {e}")

if __name__ == "__main__":
    fix_director_folders()
