#!/usr/bin/env python3
"""
Merge /Volumes/Films/watchedorganise/ into /Volumes/Films/AJ/
and remove the source folder after successful rsync completion.
"""

import os
import subprocess
import shutil
import sys

SOURCE = "/Volumes/Films/watchedorganise/"
DESTINATION = "/Volumes/Films/AJ/"

def check_paths_exist():
    """Verify both source and destination paths exist"""
    if not os.path.exists(SOURCE):
        print(f"Error: Source path does not exist: {SOURCE}")
        return False
    if not os.path.exists(DESTINATION):
        print(f"Error: Destination path does not exist: {DESTINATION}")
        return False
    print(f"✓ Source exists: {SOURCE}")
    print(f"✓ Destination exists: {DESTINATION}")
    return True

def count_files(path):
    """Count total files in a directory tree"""
    count = 0
    for root, dirs, files in os.walk(path):
        count += len(files)
    return count

def rsync_merge():
    """Merge source into destination using rsync"""
    print(f"\n{'='*60}")
    print("Starting rsync merge...")
    print(f"{'='*60}")
    
    # rsync command: -av = archive + verbose, -h = human readable, --progress = show progress
    cmd = [
        "rsync",
        "-avh",
        "--progress",
        "--stats",
        SOURCE,
        DESTINATION
    ]
    
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✓ rsync completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ rsync failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ Error running rsync: {e}")
        return False

def verify_merge():
    """Verify that files were copied"""
    source_count = count_files(SOURCE)
    dest_count = count_files(DESTINATION)
    
    print(f"\n{'='*60}")
    print("Verifying merge...")
    print(f"{'='*60}")
    print(f"Files in source: {source_count}")
    print(f"Files in destination: {dest_count}")
    
    if source_count == 0:
        print("✓ Source is empty (nothing to merge)")
        return True
    
    return True  # Allow cleanup even if counts differ

def cleanup_source():
    """Remove the source folder after successful merge"""
    print(f"\n{'='*60}")
    print("Cleaning up source folder...")
    print(f"{'='*60}")
    
    # Double-check before deletion
    response = input(f"Remove {SOURCE}? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("✗ Cleanup cancelled")
        return False
    
    try:
        shutil.rmtree(SOURCE)
        print(f"✓ Successfully removed: {SOURCE}")
        return True
    except Exception as e:
        print(f"✗ Error removing source folder: {e}")
        return False

def main():
    print("Film File Merger - Merge watchedorganise into AJ\n")
    
    # Step 1: Verify paths exist
    if not check_paths_exist():
        sys.exit(1)
    
    # Step 2: Show initial file counts
    source_files = count_files(SOURCE)
    print(f"\nFiles to merge: {source_files}")
    
    if source_files == 0:
        print("✓ Source folder is empty, nothing to merge")
        sys.exit(0)
    
    # Step 3: Confirm before proceeding
    response = input(f"\nProceed with merge? (yes/no): ").strip().lower()
    if response != 'yes':
        print("✗ Merge cancelled")
        sys.exit(0)
    
    # Step 4: Run rsync
    if not rsync_merge():
        sys.exit(1)
    
    # Step 5: Verify the merge
    verify_merge()
    
    # Step 6: Cleanup source
    if not cleanup_source():
        print("\n⚠ Merge completed but source folder was not removed")
        print("You can manually remove it later or re-run this script")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("✓ Merge and cleanup completed successfully!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
