#!/usr/bin/env python3
"""
Diagnose and attempt to fix filesystem issues with /Volumes/Films/AJ
This appears to be a unicode normalization or filesystem corruption problem.
"""

import os
import subprocess
import sys

AJ_PATH = "/Volumes/Films/AJ"

def diagnose_volume():
    """Run diagnostics on the volume"""
    print("="*60)
    print("FILESYSTEM DIAGNOSTICS")
    print("="*60)
    
    # Check if path exists
    if not os.path.exists(AJ_PATH):
        print(f"✗ Path does not exist: {AJ_PATH}")
        return False
    
    # Check volume type
    result = subprocess.run(
        ["diskutil", "info", "/Volumes/Films"],
        capture_output=True,
        text=True
    )
    
    print("\nVolume Information:")
    for line in result.stdout.split('\n'):
        if any(keyword in line for keyword in ['File System', 'Type', 'Name', 'Volume']):
            print(f"  {line.strip()}")
    
    # Try to count items
    print(f"\nAttempting to list directory...")
    try:
        items = os.listdir(AJ_PATH)
        print(f"  ✓ Successfully listed {len(items)} items")
        
        # Check for problematic items
        problem_count = 0
        for item in items:
            full_path = os.path.join(AJ_PATH, item)
            try:
                is_dir = os.path.isdir(full_path)
                is_file = os.path.isfile(full_path)
                if not is_dir and not is_file:
                    print(f"  ✗ PROBLEM: {item} (neither file nor directory)")
                    problem_count += 1
            except Exception as e:
                print(f"  ✗ ERROR checking {item}: {e}")
                problem_count += 1
        
        if problem_count > 0:
            print(f"\n⚠ Found {problem_count} problematic items")
            return False
        else:
            print(f"\n✓ All items appear normal")
            return True
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def suggest_fixes():
    """Suggest potential fixes"""
    print("\n" + "="*60)
    print("RECOMMENDED FIXES")
    print("="*60)
    print("""
The /Volumes/Films volume appears to have filesystem issues.

Recommended actions (in order):

1. Run First Aid on the volume:
   • Open Disk Utility
   • Select the "Films" volume
   • Click "First Aid" and run it
   
2. If that doesn't work, the volume may need to be reformatted:
   ⚠️  WARNING: This will erase all data!
   • Backup all data first
   • Reformat the volume as APFS (case-sensitive if needed)
   
3. Check if this is a unicode normalization issue:
   • The volume might be using different unicode normalization
   • Files created on different systems may use NFC vs NFD
   
4. Alternative: Copy all accessible data to a new location:
   • Create a new folder elsewhere
   • Copy all data you can access
   • Reformat the Films volume
   • Copy data back
""")

def attempt_emergency_backup_list():
    """Create a list of all accessible items"""
    print("\n" + "="*60)
    print("CREATING EMERGENCY BACKUP LIST")
    print("="*60)
    
    output_file = os.path.expanduser("~/Desktop/AJ_accessible_items.txt")
    
    try:
        with open(output_file, 'w') as f:
            items = os.listdir(AJ_PATH)
            accessible = []
            
            for item in items:
                full_path = os.path.join(AJ_PATH, item)
                try:
                    if os.path.isdir(full_path):
                        # Try to list contents
                        contents = os.listdir(full_path)
                        f.write(f"✓ {item}/ ({len(contents)} items)\n")
                        accessible.append(item)
                    elif os.path.isfile(full_path):
                        size = os.path.getsize(full_path)
                        f.write(f"✓ {item} ({size} bytes)\n")
                        accessible.append(item)
                    else:
                        f.write(f"✗ {item} (INACCESSIBLE)\n")
                except Exception as e:
                    f.write(f"✗ {item} (ERROR: {e})\n")
        
        print(f"✓ Created backup list: {output_file}")
        print(f"  Accessible items: {len(accessible)}/{len(items)}")
        
    except Exception as e:
        print(f"✗ Error creating backup list: {e}")

if __name__ == "__main__":
    diagnose_volume()
    suggest_fixes()
    
    response = input("\nCreate emergency backup list? (yes/no): ").strip().lower()
    if response == 'yes':
        attempt_emergency_backup_list()
