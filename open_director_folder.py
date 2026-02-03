#!/usr/bin/env python3
"""
Script to open director folders and their movies in Finder.
Works around SMB permission display issues by opening subfolders directly.
"""

import os
import sys
import subprocess

def list_director_contents(director_path):
    """List all movies in a director folder."""
    if not os.path.exists(director_path):
        print(f"Error: Directory not found: {director_path}")
        return []
    
    try:
        contents = os.listdir(director_path)
        # Filter out hidden files
        contents = [item for item in contents if not item.startswith('.')]
        return sorted(contents)
    except PermissionError:
        print(f"Error: Permission denied accessing {director_path}")
        return []

def open_in_finder(path):
    """Open a path in Finder."""
    try:
        subprocess.run(['open', path], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"Error: Could not open {path}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 open_director_folder.py <director_name>")
        print("Example: python3 open_director_folder.py 'Haipeng Sun'")
        sys.exit(1)
    
    director_name = sys.argv[1]
    base_path = '/Volumes/Films/AJ/'
    director_path = os.path.join(base_path, director_name)
    
    if not os.path.exists(director_path):
        print(f"Director folder not found: {director_name}")
        sys.exit(1)
    
    print(f"Director: {director_name}")
    print(f"Path: {director_path}")
    print("\nMovies found:")
    
    contents = list_director_contents(director_path)
    
    if not contents:
        print("  (No movies found or permission denied)")
        sys.exit(1)
    
    for i, item in enumerate(contents, 1):
        print(f"  {i}. {item}")
    
    # Open all movie folders in Finder
    print(f"\nOpening {len(contents)} folder(s) in Finder...")
    for item in contents:
        item_path = os.path.join(director_path, item)
        if os.path.isdir(item_path):
            open_in_finder(item_path)
    
    print("Done!")

if __name__ == '__main__':
    main()
