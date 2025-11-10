#!/usr/bin/env python3
"""
Test script to verify f-string template substitution in config
"""
import sys
import os
import getpass
from pathlib import Path

# Add the installer path to sys.path
sys.path.insert(0, str(Path(__file__).parent / "installer"))


def test_template_substitution():
    """Test that f-string templates are properly substituted"""
    print("🔧 Testing Template Substitution in Config")
    print("=" * 50)

    try:
        # Import the function from run_installer
        from run_installer import get_installation_settings

        # Get the processed configuration
        config = get_installation_settings()

        # Check the folder settings section
        if 'Step_Select_Folder' in config:
            folder_section = config['Step_Select_Folder']

            # Get the default installation folder value
            default_folder = folder_section.get(
                'default_installation_folder', '')
            fallback_folders = folder_section.get(
                'fallback_installation_folders', '')

            print(f"✅ Raw default_installation_folder: {default_folder}")
            print(f"✅ Raw fallback_installation_folders: {fallback_folders}")

            # Check if template variables were substituted
            expected_parent = str(Path(__file__).parent)
            expected_username = getpass.getuser()

            print(f"\n🎯 Expected substitutions:")
            print(f"   • {{parent_folder}} → {expected_parent}")
            print(f"   • {{username}} → {expected_username}")

            # Check if substitutions occurred
            has_parent_placeholder = "{parent_folder}" in default_folder
            has_username_placeholder = "{username}" in fallback_folders

            if not has_parent_placeholder and not has_username_placeholder:
                print("✅ Template substitution appears to have occurred!")

                # Show the substituted values
                print(f"\n📁 Processed values:")
                print(f"   • default_installation_folder: {default_folder}")
                print(
                    f"   • fallback_installation_folders: {fallback_folders}")

                return True
            else:
                print("❌ Template placeholders still present - substitution failed!")
                print(
                    f"   • Still has {{parent_folder}}: {has_parent_placeholder}")
                print(
                    f"   • Still has {{username}}: {has_username_placeholder}")
                return False
        else:
            print("❌ Step_Select_Folder section not found in config")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_template_substitution()
    print("\n" + "=" * 50)
    if success:
        print("🎉 Template substitution test PASSED!")
    else:
        print("💥 Template substitution test FAILED!")
    sys.exit(0 if success else 1)
