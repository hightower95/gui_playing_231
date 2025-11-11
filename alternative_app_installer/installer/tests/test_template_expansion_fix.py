#!/usr/bin/env python3
"""
Test Template Expansion Fix - Verify f-string replacement works correctly
"""

from install_gui.steps.folder_step import GetFolderStep
import sys
import os
from pathlib import Path
from configparser import ConfigParser
import tempfile

# Add the install_gui module to path
sys.path.insert(0, str(Path(__file__).parent / "install_gui"))


def test_template_expansion():
    """Test that template variables are expanded correctly"""

    # Create a test config with template variables
    config = ConfigParser()
    config.read_string("""
[Step_Select_Folder]
default_installation_folder = ["{parent_folder}"]
fallback_installation_folders = ["{parent_folder}", "C:\\Users\\{username}", "C:\\Användare\\{username}"]
""")

    # Create a folder step instance
    shared_state = {}
    step = GetFolderStep(config, shared_state)

    # Test the default path expansion
    default_path = step._get_default_installation_path()
    print(f"Default path: {default_path}")

    # Verify it's not the raw template
    assert "{parent_folder}" not in default_path, f"Template not expanded: {default_path}"
    assert "{username}" not in default_path, f"Username template not expanded: {default_path}"

    # Test direct template expansion
    template = "{parent_folder}/TestApp"
    expanded = step._expand_path_template(template)
    print(f"Expanded template '{template}' -> '{expanded}'")
    assert "{parent_folder}" not in expanded, f"Parent folder not expanded: {expanded}"

    # Test username expansion
    username_template = "C:/Users/{username}/TestApp"
    expanded_username = step._expand_path_template(username_template)
    print(
        f"Expanded username template '{username_template}' -> '{expanded_username}'")
    assert "{username}" not in expanded_username, f"Username not expanded: {expanded_username}"

    print("\n✅ All template expansion tests passed!")


def test_with_real_config():
    """Test with the actual install_settings.ini file"""

    config_path = Path(__file__).parent / "install_settings.ini"
    if not config_path.exists():
        print("⚠️  install_settings.ini not found, skipping real config test")
        return

    config = ConfigParser()
    config.read(config_path)

    shared_state = {}
    step = GetFolderStep(config, shared_state)

    default_path = step._get_default_installation_path()
    print(f"\nReal config default path: {default_path}")

    # Verify expansion happened
    assert "{parent_folder}" not in default_path, f"Template not expanded in real config: {default_path}"

    print("✅ Real config test passed!")


if __name__ == "__main__":
    print("Testing template expansion fix...")
    test_template_expansion()
    test_with_real_config()
    print("\n🎉 All tests completed successfully!")
