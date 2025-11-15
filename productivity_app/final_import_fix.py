#!/usr/bin/env python3
"""
Final comprehensive fix for remaining relative import issues.
"""

import os
import re
from pathlib import Path


def fix_file(file_path, replacements):
    """Fix specific import patterns in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        for old_pattern, new_pattern in replacements:
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
    # Define specific import patterns that need fixing for remaining issues
    fixes = [
        # Fix main_window.py in tabs/ - these should be relative to productivity_core
        ("productivity_app/productivity_core/tabs/main_window.py", [
            ("from ...epd.epd_presenter import",
             "from ..epd.epd_presenter import"),
            ("from ...presenters.connectors_presenter import",
             "from ..presenters.connectors_presenter import"),
            ("from ...presenters.fault_presenter import",
             "from ..presenters.fault_presenter import"),
            ("from ...document_scanner import", "from ..document_scanner import"),
            ("from ...connector.connector_context_provider import",
             "from ..connector.connector_context_provider import"),
            ("from ...remote_docs import", "from ..remote_docs import"),
            ("from ...devops import", "from ..devops import"),
            ("from ...tabs.settings_tab import", "from .settings_tab import"),
        ]),

        # Fix main_window.py in views/ - these should be relative to productivity_core
        ("productivity_app/productivity_core/views/main_window.py", [
            ("from ...epd.epd_presenter import",
             "from ..epd.epd_presenter import"),
            ("from ...presenters.connectors_presenter import",
             "from ..presenters.connectors_presenter import"),
            ("from ...document_scanner import", "from ..document_scanner import"),
        ]),

        # Fix presenters/ files - these should be relative to productivity_core
        ("productivity_app/productivity_core/presenters/connectors_presenter.py", [
            ("from ...connector.connector_model import",
             "from ..connector.connector_model import"),
            ("from ...connector.connector_tab import",
             "from ..connector.connector_tab import"),
        ]),

        ("productivity_app/productivity_core/presenters/fault_presenter.py", [
            ("from ...tabs.fault_finding import",
             "from ..tabs.fault_finding import"),
        ]),

        # Fix epd files - these should be relative within epd
        ("productivity_app/productivity_core/epd/epd_presenter.py", [
            ("from ...epd.epd_model import", "from .epd_model import"),
            ("from ...epd.epd_tab import", "from .epd_tab import"),
        ]),

        ("productivity_app/productivity_core/epd/epd_tab.py", [
            ("from ...epd.SearchEpd.presenter import",
             "from .SearchEpd.presenter import"),
            ("from ...epd.IdentifyBestEpd.presenter import",
             "from .IdentifyBestEpd.presenter import"),
        ]),

        # Fix document_scanner files
        ("productivity_app/productivity_core/document_scanner/__init__.py", [
            ("from ...document_scanner.document_scanner_tab import",
             "from .document_scanner_tab import"),
        ]),

        ("productivity_app/productivity_core/document_scanner/threaded_context_manager.py", [
            ("from ...document_scanner.context_provider import",
             "from .context_provider import"),
        ]),

        # Fix remote_docs presenter
        ("productivity_app/productivity_core/remote_docs/presenter.py", [
            ("from ...tabs.settings_tab import",
             "from ..tabs.settings_tab import"),
        ]),
    ]

    files_updated = 0

    for file_path, replacements in fixes:
        full_path = Path(file_path)
        if full_path.exists():
            if fix_file(full_path, replacements):
                files_updated += 1
        else:
            print(f"⚠️ File not found: {file_path}")

    print(f"\n✅ Final import fixing complete! Updated {files_updated} files.")


if __name__ == "__main__":
    main()
