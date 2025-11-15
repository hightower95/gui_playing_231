#!/usr/bin/env python3
"""
Fix remaining relative import issues after package restructuring.
"""

import os
import re
from pathlib import Path


def fix_relative_imports_in_file(file_path, patterns_to_fix):
    """Fix specific relative import patterns in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        for old_pattern, new_pattern in patterns_to_fix:
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                changes_made.append(f"  {old_pattern} -> {new_pattern}")

        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed {file_path}")
            for change in changes_made:
                print(change)
            return True

        return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    # Define specific import patterns that need fixing
    patterns_to_fix = [
        # Core config imports - these are in same directory or one level down
        ("from ...core.config import", "from ..core.config import"),
        ("from ...core.config import", "from ...core.config import"),

        # Base class imports
        ("from ...core.base_model import", "from ..core.base_model import"),
        ("from ...core.base_presenter import",
         "from ..core.base_presenter import"),

        # Config manager imports
        ("from ...core.config_manager import",
         "from ..core.config_manager import"),
    ]

    # Find all Python files in the package
    package_dir = Path("productivity_app")
    if not package_dir.exists():
        print("❌ Package directory not found!")
        return

    python_files = list(package_dir.rglob("*.py"))
    files_updated = 0

    print(f"🔍 Found {len(python_files)} Python files to check...")

    for file_path in python_files:
        if fix_relative_imports_in_file(file_path, patterns_to_fix):
            files_updated += 1

    print(f"\n✅ Import fixing complete! Updated {files_updated} files.")


if __name__ == "__main__":
    main()
