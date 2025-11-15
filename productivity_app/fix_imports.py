#!/usr/bin/env python3
"""
Script to fix absolute imports to productivity_core with relative imports
"""
import os
import re
from pathlib import Path


def calculate_relative_import(from_file, to_module):
    """Calculate the relative import path"""
    # Get the directory of the file making the import
    from_dir = from_file.parent

    # Calculate relative path to the root productivity_app directory
    productivity_app_root = Path("productivity_app")

    # Count how many levels up we need to go from the current file
    # to reach the productivity_app directory
    current_parts = from_dir.parts
    if 'productivity_core' in current_parts:
        # Find the index of productivity_core
        core_index = current_parts.index('productivity_core')
        # Number of levels below productivity_core
        levels_below = len(current_parts) - core_index - 1
        if levels_below == 0:
            # We're in productivity_core root
            prefix = "."
        else:
            # We're deeper, need to go up
            prefix = "." + "." * levels_below
    else:
        # We're in productivity_app root
        prefix = ".productivity_core"
        return prefix + to_module.replace('productivity_core', '')

    # For files inside productivity_core, convert to relative
    return prefix + to_module.replace('productivity_core', '')


def fix_file_imports(file_path):
    """Fix imports in a single file"""
    print(f"Processing {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match imports like "from productivity_core.some.module import something"
    pattern = r'from (productivity_core(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*) import'

    def replace_import(match):
        full_module = match.group(1)
        relative_import = calculate_relative_import(
            Path(file_path), full_module)
        return f'from {relative_import} import'

    original_content = content
    content = re.sub(pattern, replace_import, content)

    if content != original_content:
        print(f"  - Updated imports in {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    else:
        print(f"  - No changes needed in {file_path}")
        return False


def main():
    """Main function to process all files"""
    productivity_app_dir = Path("productivity_app")

    if not productivity_app_dir.exists():
        print("Error: productivity_app directory not found")
        return

    python_files = list(productivity_app_dir.rglob("*.py"))

    files_changed = 0
    for py_file in python_files:
        if fix_file_imports(py_file):
            files_changed += 1

    print(
        f"\nProcessed {len(python_files)} files, updated {files_changed} files")


if __name__ == "__main__":
    main()
