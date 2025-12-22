#!/usr/bin/env python3
"""
Direct Unicode normalization fixer for NAS folders.
Renames all items with NFC encoding to NFD for macOS compatibility.
"""

import os
import unicodedata
import sys

def fix_folder(folder_path, dry_run=False):
    """
    Rename all items in a folder from NFC to NFD normalization.
    """
    items = os.listdir(folder_path)
    fixed_count = 0
    error_count = 0
    
    # Sort by depth - rename directories first before items inside them
    items_sorted = []
    for item in items:
        full_path = os.path.join(folder_path, item)
        is_dir = os.path.isdir(full_path)
        items_sorted.append((item, is_dir))
    
    # Process directories first (reverse order to handle nested items)
    for item, is_dir in sorted(items_sorted, key=lambda x: not x[1]):
        if item.startswith('.'):
            continue
        
        full_path = os.path.join(folder_path, item)
        
        # Check if needs fixing
        nfc_form = unicodedata.normalize('NFC', item)
        nfd_form = unicodedata.normalize('NFD', item)
        
        if nfc_form != nfd_form:
            new_path = os.path.join(folder_path, nfd_form)
            
            try:
                if not dry_run:
                    os.rename(full_path, new_path)
                    print(f"✓ Renamed: {item[:50]}...")
                else:
                    print(f"[DRY RUN] Would rename: {item[:50]}...")
                fixed_count += 1
            except Exception as e:
                print(f"✗ Error renaming {item}: {str(e)}")
                error_count += 1
    
    return fixed_count, error_count

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fix_unicode_direct.py <folder> [--fix]")
        sys.exit(1)
    
    folder = sys.argv[1]
    fix_mode = '--fix' in sys.argv
    
    if not os.path.isdir(folder):
        print(f"Error: Folder not found: {folder}")
        sys.exit(1)
    
    print(f"Processing: {folder}\n")
    
    if fix_mode:
        print("FIXING MODE - Renaming files...\n")
        fixed, errors = fix_folder(folder, dry_run=False)
        print(f"\nCompleted: {fixed} renamed, {errors} errors")
    else:
        print("PREVIEW MODE - No changes made\n")
        fixed, errors = fix_folder(folder, dry_run=True)
        print(f"\nWould fix: {fixed} items")
        print("\nTo apply fixes, run: python fix_unicode_direct.py '<folder>' --fix")
