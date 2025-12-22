#!/usr/bin/env python3
"""
Normalize macOS-visible names and safely merge duplicates.

Use case: Synology NAS shares mounted on macOS where NFC (composed) names are
invisible or duplicated under NFD (decomposed) form.

Behaviors:
- Detect items whose name changes when normalized to NFD.
- Plan renames to NFD.
- If the NFD target already exists, merge contents without overwriting; file
  conflicts are suffixed with " (duplicate N)".
- Dry-run by default; apply with --fix.

Usage:
    python merge_normalize_unicode.py /Volumes/Films-1/AJ          # preview
    python merge_normalize_unicode.py /Volumes/Films-1/AJ --fix    # apply
"""

import os
import sys
import unicodedata
import shutil
from typing import List, Dict


def normalize_name(name: str) -> str:
    return unicodedata.normalize('NFD', name)


def list_items(folder: str) -> List[str]:
    return [i for i in os.listdir(folder) if not i.startswith('.')]


def plan_operations(folder: str) -> List[Dict]:
    ops = []
    for name in list_items(folder):
        normalized = normalize_name(name)
        if normalized != name:
            ops.append({
                'original': name,
                'normalized': normalized,
                'src': os.path.join(folder, name),
                'dst': os.path.join(folder, normalized),
                'is_dir': os.path.isdir(os.path.join(folder, name))
            })
    return ops


def ensure_dir(path: str, dry_run: bool):
    if os.path.exists(path):
        return
    if dry_run:
        print(f"[DRY] mkdir: {path}")
    else:
        os.makedirs(path, exist_ok=True)


def resolve_file_conflict(dst: str) -> str:
    base, ext = os.path.splitext(dst)
    counter = 1
    candidate = dst
    while os.path.exists(candidate):
        candidate = f"{base} (duplicate {counter}){ext}"
        counter += 1
    return candidate


def merge_directory(src: str, dst: str, dry_run: bool):
    ensure_dir(dst, dry_run)
    for entry in list_items(src):
        src_path = os.path.join(src, entry)
        dst_path = os.path.join(dst, entry)
        if os.path.isdir(src_path):
            merge_directory(src_path, dst_path, dry_run)
        else:
            final_dst = dst_path if not os.path.exists(dst_path) else resolve_file_conflict(dst_path)
            if dry_run:
                print(f"[DRY] move file: {src_path} -> {final_dst}")
            else:
                shutil.move(src_path, final_dst)
    # remove empty src
    if dry_run:
        print(f"[DRY] rmdir: {src}")
    else:
        try:
            os.rmdir(src)
        except OSError:
            pass  # non-empty or permission issues


def apply_operation(op: Dict, dry_run: bool):
    src = op['src']
    dst = op['dst']
    if not os.path.exists(src):
        print(f"[SKIP] Missing source: {src}")
        return

    if op['is_dir']:
        if os.path.exists(dst):
            print(f"[MERGE] {src} -> {dst}")
            merge_directory(src, dst, dry_run)
        else:
            if dry_run:
                print(f"[DRY] rename dir: {src} -> {dst}")
            else:
                os.rename(src, dst)
    else:
        final_dst = dst if not os.path.exists(dst) else resolve_file_conflict(dst)
        if dry_run:
            print(f"[DRY] rename file: {src} -> {final_dst}")
        else:
            os.rename(src, final_dst)


def main():
    if len(sys.argv) < 2:
        print("Usage: python merge_normalize_unicode.py <folder> [--fix]")
        sys.exit(1)

    folder = sys.argv[1]
    fix_mode = '--fix' in sys.argv

    if not os.path.isdir(folder):
        print(f"Error: folder not found: {folder}")
        sys.exit(1)

    ops = plan_operations(folder)
    if not ops:
        print("✓ No items need normalization.")
        sys.exit(0)

    print(f"Found {len(ops)} items needing normalization (top-level).")
    for op in ops[:10]:
        print(f"  {op['original']} -> {op['normalized']}")
    if len(ops) > 10:
        print(f"  ...and {len(ops) - 10} more")

    if not fix_mode:
        print("\nPreview mode: no changes made. Use --fix to apply.")
        # Show planned actions
        for op in ops[:20]:
            note = "merge" if os.path.exists(op['dst']) else "rename"
            print(f"[PLAN] {note}: {op['src']} -> {op['dst']}")
        if len(ops) > 20:
            print(f"[PLAN] ...{len(ops) - 20} more")
        sys.exit(0)

    confirm = input("\nType 'yes' to proceed with renames/merges: ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        sys.exit(0)

    for op in ops:
        apply_operation(op, dry_run=False)

    print("\n✓ Done. Re-run in preview to verify.")


if __name__ == '__main__':
    main()
