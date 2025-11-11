"""
Test script for the installer GUI

This script launches the installer GUI for testing the new architecture.
"""
from install_gui.main import launch_installer_gui
import sys
from pathlib import Path
from configparser import ConfigParser

# Add the installer directory to the path
installer_dir = Path(__file__).parent
sys.path.insert(0, str(installer_dir))


def create_test_config():
    """Create a test configuration for the installer"""
    config = ConfigParser()

    # Paths section
    config.add_section('PATHS')
    config.set('PATHS', 'default_install_path',
               r'C:\Program Files\AlternativeApp')

    # App section
    config.add_section('APP')
    config.set('APP', 'name', 'Alternative Application')
    config.set('APP', 'version', '1.0.0')

    # Debug section
    config.add_section('DEBUG')
    config.set('DEBUG', 'enabled', 'true')
    config.set('DEBUG', 'log_level', 'DEBUG')

    return config


def main():
    """Launch the installer GUI with test configuration"""
    print("🚀 Launching Installer GUI Test")
    print("=" * 40)

    try:
        # Create test configuration
        config = create_test_config()
        print("✅ Test configuration created")

        # Launch the installer GUI
        print("🖼️ Launching GUI...")
        result = launch_installer_gui(config)

        if result:
            print("✅ Installation completed successfully!")
        else:
            print("❌ Installation was cancelled or failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
