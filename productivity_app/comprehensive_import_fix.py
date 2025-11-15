#!/usr/bin/env python3
"""
Comprehensive Import Fixer - Final Pass
Fixes all remaining relative import issues in the productivity_app package.
"""

import os
import re
from pathlib import Path


def get_relative_import_depth(from_path, to_module):
    """Calculate the correct number of dots for relative import"""
    from_parts = from_path.parts

    # Find productivity_app root
    try:
        app_index = from_parts.index('productivity_app')
    except ValueError:
        return None

    # Get path relative to productivity_app
    relative_parts = from_parts[app_index + 1:]

    # Current directory depth from productivity_app root
    # -1 because we don't count the file itself
    current_depth = len(relative_parts) - 1

    # Parse the module path
    module_parts = to_module.split('.')

    if not module_parts:
        return None

    # If it starts with productivity_core, we need to navigate to the right level
    if module_parts[0] == 'productivity_core':
        if current_depth == 0:
            # At productivity_app root, need one dot
            return '.' + to_module
        elif current_depth == 1:
            # At productivity_app/productivity_core level, need one dot
            return '.' + '.'.join(module_parts[1:])
        elif current_depth >= 2:
            # Deeper in the tree, need to go up to productivity_core level
            dots_needed = current_depth - 1
            return ('.' * dots_needed) + '.'.join(module_parts[1:])

    return None


def fix_relative_imports_in_file(file_path):
    """Fix all relative imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Could not read {file_path}: {e}")
        return False

    original_content = content
    lines = content.split('\n')
    modified = False

    # Pattern to match imports with too many dots
    pattern = r'from\s+(\.{3,})([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'

    new_lines = []
    for line_num, line in enumerate(lines, 1):
        new_line = line

        # Check for imports with 3+ dots
        match = re.match(pattern, line.strip())
        if match:
            dots = match.group(1)
            module_path = match.group(2)

            # Calculate correct relative import
            file_path_obj = Path(file_path)
            correct_import = get_relative_import_depth(
                file_path_obj, f"productivity_core.{module_path}")

            if correct_import:
                # Extract the import part
                import_part = line.split(' import ', 1)[
                    1] if ' import ' in line else ''
                new_import = f"from {correct_import} import {import_part}"

                # Replace the line
                new_line = line.replace(line.strip(), new_import)
                print(
                    f"  {file_path_obj.name}:{line_num}: {line.strip()} -> {new_import}")
                modified = True

        # Also fix some common specific patterns
        elif 'from ...core.' in line:
            if 'productivity_core/core/' in str(file_path):
                new_line = line.replace('from ...core.', 'from .')
                modified = True
            elif 'productivity_core/' in str(file_path) and 'productivity_core/core/' not in str(file_path):
                new_line = line.replace('from ...core.', 'from ..core.')
                modified = True

        elif 'from ...document_scanner.' in line:
            if 'document_scanner/' in str(file_path):
                new_line = line.replace('from ...document_scanner.', 'from ..')
                modified = True
            elif 'productivity_core/' in str(file_path):
                new_line = line.replace(
                    'from ...document_scanner.', 'from ..document_scanner.')
                modified = True

        elif 'from ...epd.' in line:
            if 'productivity_core/' in str(file_path):
                new_line = line.replace('from ...epd.', 'from ..epd.')
                modified = True

        elif 'from ...tabs.' in line:
            if 'productivity_core/' in str(file_path):
                new_line = line.replace('from ...tabs.', 'from ..tabs.')
                modified = True

        new_lines.append(new_line)

    if modified:
        new_content = '\n'.join(new_lines)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"❌ Could not write {file_path}: {e}")
            return False

    return False


def main():
    """Main function to fix all relative imports"""
    base_dir = Path("productivity_app/productivity_app")

    if not base_dir.exists():
        print(f"❌ Directory not found: {base_dir}")
        return

    print("🔍 Finding Python files with relative import issues...")

    # Find all Python files
    python_files = list(base_dir.rglob("*.py"))

    print(f"📁 Found {len(python_files)} Python files")

    files_modified = 0
    total_files = 0

    for file_path in python_files:
        total_files += 1

        # Check if file has problematic imports
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'from ...' in content:
                print(f"\n🔧 Fixing: {file_path}")
                if fix_relative_imports_in_file(file_path):
                    files_modified += 1

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    print(f"\n✅ Processing complete!")
    print(f"📊 Processed {total_files} files, modified {files_modified} files")


if __name__ == "__main__":
    main()
