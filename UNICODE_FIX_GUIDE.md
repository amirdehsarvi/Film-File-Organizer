# Fix Unicode-Named Film Folders from Synology NAS on macOS

## Problem Summary

Your Synology NAS stores folder names with accented/special characters in **NFC Unicode form** (composed), but macOS's HFS+ filesystem expects **NFD Unicode form** (decomposed). This causes:

- Folders with names like "Andrés Borghi", "Céline Sciamma" to be **invisible** or inaccessible on macOS
- Files inside these folders cannot be accessed
- Terminal commands fail with "No such file or directory"

## Root Cause

- **Synology SMB/NFS servers** encode filenames in NFC (Composed) form
- **macOS HFS+** expects NFD (Decomposed) form
- This creates a mismatch that makes certain characters appear as different files to each OS

## Solution

There are **3 approaches** to fix this:

### Option 1: Fix at the Source (Recommended)

**Rename the folders directly on the Synology NAS** using its file manager or SSH:

1. Connect to your Synology NAS via **File Station** (web interface)
2. Navigate to the Film folders
3. Rename each problematic folder to remove accented characters:
   - `Andrés Borghi` → `Andres Borghi`
   - `Céline Sciamma` → `Celine Sciamma`
   - `Marko Röhr` → `Marko Rohr`

This is the permanent solution that fixes it for all devices.

### Option 2: Re-mount with NFD Normalization

If you have SSH access to your Synology, remount the SMB share with NFD normalization:

```bash
# Unmount current share
sudo umount /Volumes/Films-1

# Remount with NFD normalization option
sudo mount_smbfs -o nfc:off //username:password@synology.local/Films-1 /Volumes/Films-1
```

### Option 3: Copy Folders Locally

Copy the problem folders to your Mac's local storage where macOS can handle them properly:

```bash
# This will automatically convert names to NFD during copy
cp -r "/Volumes/Films-1/AJ" ~/Movies/Films-1-AJ-Local
```

##  Diagnosing the Issue

To check if a folder has Unicode issues:

```bash
python3 -c "
import os, unicodedata
folder = '/Volumes/Films-1/AJ'
items = os.listdir(folder)
problematic = [i for i in items if unicodedata.normalize('NFC', i) != unicodedata.normalize('NFD', i)]
print(f'Problem folders: {len(problematic)}')
for item in problematic[:10]:
    print(f'  - {item}')
"
```

## Files Provided

- **fix_unicode_direct.py** - Direct renaming script (limited effectiveness due to NFS mount)
- **fix_unicode_names.py** - Comprehensive scanner and fixer

## Recommendation

👉 **The best solution is Option 1**: Rename the folders on the Synology NAS itself. This fixes the problem at the source and makes them accessible on all devices.

If you need help with that, I can create a script to help bulk-rename the problematic folders while keeping your organization intact.
