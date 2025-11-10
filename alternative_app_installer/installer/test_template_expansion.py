#!/usr/bin/env python3
"""
Test script to verify template expansion and install_locations_preferences functionality
"""
from install_gui.steps.folder_step import GetFolderStep
import sys
import os
from pathlib import Path
from configparser import ConfigParser

# Add the parent directory to sys.path to import our modules
sys.path.insert(0, str(Path(__file__).parent))


def test_template_expansion():
    """Test the template expansion functionality"""
    print("Testing Template Variable Expansion")
    print("=" * 50)

    # Create a test configuration
    config = ConfigParser()
    config.read('install_settings.ini')

    # Create shared state
    shared_state = {}

    # Create folder step instance
    folder_step = GetFolderStep(config, shared_state)

    # Test template expansion
    templates = [
        "{parent_folder}",
        "C:\\Users\\{username}",
        "C:\\Användare\\{username}",
        "{parent_folder}\\TestApp"
    ]

    print(f"Current username: {os.getenv('USERNAME', 'Unknown')}")
    print(f"Parent folder: {Path.cwd().parent}")
    print()

    for template in templates:
        expanded = folder_step._expand_template_variables(template)
        accessible = folder_step._is_location_accessible(expanded)
        print(f"Template: {template}")
        print(f"Expanded: {expanded}")
        print(f"Accessible: {accessible}")
        print("-" * 30)

    print("\nDefault Installation Path:")
    default_path = folder_step._get_default_installation_folder()
    print(f"Selected: {default_path}")

    print(
        f"\nShared state installation_path: {shared_state.get('installation_path', 'Not set')}")


if __name__ == "__main__":
    test_template_expansion()
