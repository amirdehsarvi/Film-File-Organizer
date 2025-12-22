#!/usr/bin/env python3
"""
Fix Unicode Filename Compatibility Issues for NAS-to-macOS Transfer

This script normalizes filenames from Synology NAS to be compatible with macOS.
It converts filenames from NFC (Composed) to NFD (Decomposed) Unicode form,
which is required by macOS's HFS+ filesystem.

Usage:
    python fix_unicode_names.py /path/to/folder
"""

import os
import unicodedata
import sys
import subprocess
from pathlib import Path


def normalize_filename(filename):
    """
    Convert filename from NFC (Synology) to NFD (macOS) Unicode form.
    
    Args:
        filename: The original filename
        
    Returns:
        Tuple of (original_filename, normalized_filename, needs_change)
    """
    # Decompose to NFD form (what macOS expects)
    nfc_form = unicodedata.normalize('NFC', filename)
    nfd_form = unicodedata.normalize('NFD', filename)
    
    # Check if the filename actually changed
    needs_change = nfc_form != nfd_form
    
    return filename, nfd_form, needs_change


def get_problematic_files(folder_path):
    """
    Scan folder and find directories that need Unicode normalization.
    Focuses on top-level directories where the NAS encoding issue is most critical.
    
    Args:
        folder_path: Path to scan
        
    Returns:
        List of dicts with directory/file info
    """
    problematic_items = []
    
    print("Scanning for Unicode normalization issues...", file=sys.stderr)
    
    # Scan current directory level only (director folders)
    try:
        items = os.listdir(folder_path)
    except Exception as e:
        print(f"Error scanning: {e}")
        return []
    
    for item_name in items:
        item_path = os.path.join(folder_path, item_name)
        
        # Check the item name for NFC/NFD mismatch
        nfc_form = unicodedata.normalize('NFC', item_name)
        nfd_form = unicodedata.normalize('NFD', item_name)
        
        if nfc_form != nfd_form:  # Has a mismatch
            item_type = 'directory' if os.path.isdir(item_path) else 'file'
            problematic_items.append({
                'original': item_name,
                'normalized': nfd_form,
                'full_path': item_path,
                'directory': folder_path,
                'type': item_type
            })
        
        # For directories, also recursively check subdirectories (one level deep)
        if os.path.isdir(item_path) and not item_name.startswith('.'):
            try:
                subitems = os.listdir(item_path)
                for subitem_name in subitems:
                    subitem_path = os.path.join(item_path, subitem_name)
                    
                    # Check the subitem name for NFC/NFD mismatch
                    nfc_form = unicodedata.normalize('NFC', subitem_name)
                    nfd_form = unicodedata.normalize('NFD', subitem_name)
                    
                    if nfc_form != nfd_form:  # Has a mismatch
                        subitem_type = 'directory' if os.path.isdir(subitem_path) else 'file'
                        problematic_items.append({
                            'original': subitem_name,
                            'normalized': nfd_form,
                            'full_path': subitem_path,
                            'directory': item_path,
                            'type': subitem_type
                        })
            except (PermissionError, OSError):
                # Skip directories we can't read
                pass
    
    return problematic_items


def preview_changes(problematic_files):
    """Display a preview of changes without making them."""
    if not problematic_files:
        print("✓ No files need Unicode normalization. All filenames are macOS-compatible!")
        return False
    
    # Separate directories and files
    dirs = [f for f in problematic_files if f['type'] == 'directory']
    files = [f for f in problematic_files if f['type'] == 'file']
    
    print(f"\n🔍 Found {len(problematic_files)} item(s) that need Unicode normalization:\n")
    
    if dirs:
        print(f"📁 Directories ({len(dirs)}):")
        print("-" * 80)
        for i, item in enumerate(dirs, 1):
            print(f"{i}. OLD: {item['original']}")
            print(f"   NEW: {item['normalized']}")
            print()
    
    if files:
        print(f"📄 Files ({len(files)}):")
        print("-" * 80)
        for i, item in enumerate(files, 1):
            print(f"{i}. {item['directory']}")
            print(f"   OLD: {item['original']}")
            print(f"   NEW: {item['normalized']}")
            print()
    
    print("-" * 80)
    return True


def fix_files(problematic_files, dry_run=True):
    """
    Rename files and directories to use correct Unicode normalization.
    
    Args:
        problematic_files: List of files/dirs to fix
        dry_run: If True, only show what would be done (default: True)
    """
    if not problematic_files:
        print("✓ No files to fix.")
        return
    
    # Sort by path depth (deepest first) to rename directories before files inside them
    sorted_items = sorted(problematic_files, key=lambda x: x['full_path'].count(os.sep), reverse=True)
    
    failed = []
    succeeded = 0
    
    for item_info in sorted_items:
        old_path = item_info['full_path']
        new_path = os.path.join(item_info['directory'], item_info['normalized'])
        item_type = item_info['type']
        
        try:
            if dry_run:
                print(f"[DRY RUN] Would rename {item_type}: {item_info['original']} → {item_info['normalized']}")
            else:
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    print(f"✓ Renamed {item_type}: {item_info['original']}")
                    succeeded += 1
                else:
                    failed.append(f"{item_type.capitalize()} not found: {old_path}")
        except Exception as e:
            failed.append(f"Error renaming {item_info['original']}: {str(e)}")
    
    print()
    if not dry_run:
        print(f"✓ Successfully renamed: {succeeded} item(s)")
        if failed:
            print(f"✗ Failed: {len(failed)} item(s)")
            for error in failed:
                print(f"  - {error}")
    

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_unicode_names.py <folder_path> [--fix]")
        print()
        print("Examples:")
        print("  python fix_unicode_names.py /path/to/films")
        print("  python fix_unicode_names.py /path/to/films --fix")
        print()
        print("By default, runs in preview mode (no changes made).")
        print("Add --fix flag to actually rename the files.")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    fix_mode = '--fix' in sys.argv
    
    # Validate folder exists
    if not os.path.isdir(folder_path):
        print(f"✗ Error: Folder not found: {folder_path}")
        sys.exit(1)
    
    print(f"📁 Scanning folder: {folder_path}")
    print()
    
    # Find problematic files
    problematic_files = get_problematic_files(folder_path)
    
    # Show preview
    has_issues = preview_changes(problematic_files)
    
    if not has_issues:
        sys.exit(0)
    
    # Handle fixes
    if fix_mode:
        response = input("\n⚠️  Proceed with renaming? (yes/no): ").strip().lower()
        if response == 'yes':
            print("\n🔧 Fixing files...\n")
            fix_files(problematic_files, dry_run=False)
            print("\n✓ Done!")
        else:
            print("Cancelled.")
    else:
        print("\n💡 Tip: To apply these changes, run with --fix flag:")
        print(f"   python fix_unicode_names.py '{folder_path}' --fix")


if __name__ == '__main__':
    main()
