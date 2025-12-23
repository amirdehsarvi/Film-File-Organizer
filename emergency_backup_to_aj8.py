#!/usr/bin/env python3
"""
Emergency backup of /Volumes/Films/AJ to /Volumes/AJ8
Only copies accessible directories (skips corrupted entries)
"""

import os
import shutil
import sys
from datetime import datetime

SOURCE = "/Volumes/Films/AJ"
DESTINATION = "/Volumes/AJ8/AJ_BACKUP_" + datetime.now().strftime("%Y%m%d_%H%M%S")

def check_space():
    """Check if there's enough space on destination"""
    print("Checking available space...")
    
    # Get destination stats
    dest_stat = os.statvfs("/Volumes/AJ8")
    dest_available = (dest_stat.f_bavail * dest_stat.f_frsize) / (1024**4)  # TB
    
    print(f"  Destination (/Volumes/AJ8) available: {dest_available:.2f} TB")
    print(f"  Source size needed: ~2.7 TB")
    
    if dest_available < 3.0:
        print("  ⚠ Warning: Tight on space, but should work")
    else:
        print("  ✓ Sufficient space available")
    
    return True

def backup_accessible_folders():
    """Copy all accessible folders from source to destination"""
    
    print(f"\nCreating backup directory: {DESTINATION}")
    os.makedirs(DESTINATION, exist_ok=True)
    
    print(f"\nScanning source: {SOURCE}")
    items = sorted(os.listdir(SOURCE))
    
    total_items = len(items)
    accessible_count = 0
    corrupted_count = 0
    error_count = 0
    
    corrupted_list = []
    
    print(f"Found {total_items} items to process\n")
    print("="*60)
    
    for idx, item in enumerate(items, 1):
        source_path = os.path.join(SOURCE, item)
        dest_path = os.path.join(DESTINATION, item)
        
        # Progress indicator
        print(f"\n[{idx}/{total_items}] {item}")
        
        try:
            # Check if it's accessible
            if os.path.isdir(source_path):
                try:
                    # Test if we can list contents
                    contents = os.listdir(source_path)
                    
                    # Copy the directory
                    print(f"  → Copying ({len(contents)} items)...")
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    print(f"  ✓ Success")
                    accessible_count += 1
                    
                except Exception as e:
                    print(f"  ✗ Corrupted (cannot access): {e}")
                    corrupted_list.append(item)
                    corrupted_count += 1
                    
            elif os.path.isfile(source_path):
                # It's a file, copy it
                shutil.copy2(source_path, dest_path)
                print(f"  ✓ Copied file")
                accessible_count += 1
            else:
                print(f"  ✗ Corrupted (neither file nor directory)")
                corrupted_list.append(item)
                corrupted_count += 1
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "="*60)
    print("BACKUP SUMMARY")
    print("="*60)
    print(f"Total items scanned:      {total_items}")
    print(f"Successfully backed up:   {accessible_count}")
    print(f"Corrupted (skipped):      {corrupted_count}")
    print(f"Errors:                   {error_count}")
    print(f"\nBackup location: {DESTINATION}")
    
    # Save corrupted list
    if corrupted_list:
        corrupted_file = os.path.expanduser("~/Desktop/AJ_corrupted_folders.txt")
        with open(corrupted_file, 'w') as f:
            f.write("CORRUPTED FOLDERS (NOT BACKED UP):\n")
            f.write("="*60 + "\n\n")
            for item in corrupted_list:
                f.write(f"{item}\n")
        print(f"\nCorrupted folder list saved to: {corrupted_file}")
    
    return accessible_count, corrupted_count

def main():
    print("="*60)
    print("EMERGENCY BACKUP: /Volumes/Films/AJ → /Volumes/AJ8")
    print("="*60)
    
    # Check source exists
    if not os.path.exists(SOURCE):
        print(f"✗ Source does not exist: {SOURCE}")
        sys.exit(1)
    
    # Check destination exists
    if not os.path.exists("/Volumes/AJ8"):
        print(f"✗ Destination volume not mounted: /Volumes/AJ8")
        sys.exit(1)
    
    # Check space
    if not check_space():
        sys.exit(1)
    
    # Confirm
    print("\n" + "="*60)
    print("⚠  This will copy ~2.7TB of data")
    print("⚠  This may take several hours")
    print("⚠  Only accessible folders will be copied")
    print("="*60)
    response = input("\nProceed with backup? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Backup cancelled.")
        sys.exit(0)
    
    # Perform backup
    print("\nStarting backup...")
    print("(This will take a while - do not interrupt)\n")
    
    accessible, corrupted = backup_accessible_folders()
    
    print("\n" + "="*60)
    if corrupted == 0:
        print("✓ BACKUP COMPLETE - All data backed up successfully!")
    else:
        print(f"⚠ BACKUP COMPLETE - {accessible} folders backed up")
        print(f"  {corrupted} corrupted folders could not be backed up")
        print(f"  See ~/Desktop/AJ_corrupted_folders.txt for details")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Backup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        sys.exit(1)
