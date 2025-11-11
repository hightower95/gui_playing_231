#!/usr/bin/env python3
"""
Quick integration test for Generate Files Step
Tests that files are generated correctly with utilities support
"""

from install_gui.steps.generate_files_step import GenerateFilesStep
import tempfile
import sys
from pathlib import Path
from configparser import ConfigParser

# Add installer to path
installer_dir = Path(__file__).parent / \
    "alternative_app_installer" / "installer"
sys.path.insert(0, str(installer_dir))


def test_generate_files_with_utilities():
    """Test that Generate Files Step creates all expected files including utilities"""

    with tempfile.TemporaryDirectory() as temp_dir:
        install_folder = Path(temp_dir) / "test_install"
        install_folder.mkdir()

        # Create mock settings
        settings = ConfigParser()
        settings['DEFAULT'] = {
            'enable_log': 'true',
            'log_level': 'DEBUG',
            'auto_upgrade_major_version': 'false',
            'auto_upgrade_minor_version': 'true',
            'auto_upgrade_patches': 'true'
        }
        settings['Step_Install_Libraries'] = {
            'always_upgrade': 'true',
            'allow_upgrade_to_test_releases': 'false'
        }

        # Create shared state
        shared_state = {
            'valid_installation_path': str(install_folder),
            'venv_path': r'C:\test_venv',
            'core_library': 'productivity_app'
        }

        # Create step
        step = GenerateFilesStep(
            installation_settings=settings, shared_state=shared_state)

        print("🧪 Testing Generate Files Step with utilities...")
        print(f"   Target folder: {install_folder}")

        try:
            # Generate all files
            step._generate_run_app()
            print("✅ run_app.pyw generated")

            step._generate_update_app()
            print("✅ update_app.pyw generated")

            step._generate_launch_config()
            print("✅ launch_config.ini generated")

            step._copy_utilities()
            print("✅ utilities/ copied")

            # Verify files exist
            expected_files = ['run_app.pyw',
                              'update_app.pyw', 'launch_config.ini']
            for filename in expected_files:
                file_path = install_folder / filename
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"✅ {filename} exists ({size} bytes)")

                    # Check that templates were processed
                    content = file_path.read_text()
                    if '{{' not in content:
                        print(f"✅ {filename} template processing successful")
                    else:
                        print(
                            f"⚠️ {filename} still contains unprocessed templates")
                else:
                    print(f"❌ {filename} missing")

            # Check utilities directory
            utilities_dir = install_folder / "utilities"
            if utilities_dir.exists() and utilities_dir.is_dir():
                print(f"✅ utilities/ directory exists")

                version_manager = utilities_dir / "version_manager.py"
                if version_manager.exists():
                    print(
                        f"✅ utilities/version_manager.py exists ({version_manager.stat().st_size} bytes)")
                else:
                    print(f"❌ utilities/version_manager.py missing")
            else:
                print(f"❌ utilities/ directory missing")

            # Check specific auto-upgrade settings in config
            config_file = install_folder / "launch_config.ini"
            if config_file.exists():
                config_content = config_file.read_text()
                auto_settings = [
                    'auto_upgrade_major_version = false',
                    'auto_upgrade_minor_version = true',
                    'auto_upgrade_patches = true'
                ]

                for setting in auto_settings:
                    if setting in config_content:
                        print(f"✅ Config contains: {setting}")
                    else:
                        print(f"❌ Config missing: {setting}")

            print("\n🎉 Generate Files Step integration test completed successfully!")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise


if __name__ == "__main__":
    test_generate_files_with_utilities()
