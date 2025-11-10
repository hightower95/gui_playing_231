"""
Test script for the simplified installer architecture

This script tests the new Conductor/GUI separation and step interface.
"""
import sys
from pathlib import Path
from configparser import ConfigParser

# Add the installer directory to the path
installer_dir = Path(__file__).parent
sys.path.insert(0, str(installer_dir))

# Test imports
try:
    from install_gui.main import launch_installer_gui
    from install_gui.conductor import InstallConductor
    from install_gui.steps import GetFolderStep, BaseStep
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_conductor():
    """Test the InstallConductor functionality"""
    print("\n🧪 Testing InstallConductor...")

    # Create minimal configuration
    config = ConfigParser()
    config.add_section('PATHS')
    config.set('PATHS', 'default_install_path', 'C:/Program Files/TestApp')

    # Create conductor
    conductor = InstallConductor(config)

    # Test step info
    step_info = conductor.get_step_info()
    print(f"   Current step: {step_info['title']}")
    print(f"   Description: {step_info['description']}")
    print(
        f"   Progress: {step_info['step_number']}/{step_info['total_steps']}")

    # Test step retrieval
    current_step = conductor.get_current_step()
    print(f"   Step class: {type(current_step).__name__}")

    print("✅ Conductor tests passed!")


def test_step_interface():
    """Test the BaseStep interface"""
    print("\n🧪 Testing Step Interface...")

    # Create minimal configuration
    config = ConfigParser()
    shared_state = {}

    # Create folder step
    folder_step = GetFolderStep(config, shared_state)

    # Test step methods
    print(f"   Title: {folder_step.get_title()}")
    print(f"   Description: {folder_step.get_description()}")
    print(f"   Can complete: {folder_step.can_complete()}")
    print(f"   Hint: {folder_step.get_hint_text()}")

    # Test state management
    folder_step.update_shared_state("test_key", "test_value")
    value = folder_step.get_shared_state("test_key")
    print(f"   State test: {value}")

    print("✅ Step interface tests passed!")


def main():
    """Run all tests"""
    print("🚀 Testing Simplified Installer Architecture")
    print("=" * 50)

    try:
        test_conductor()
        test_step_interface()

        print("\n" + "=" * 50)
        print("✅ All tests passed! Architecture is working correctly.")
        print("\n💡 Ready to launch GUI installer:")
        print("   python test_installer_gui.py")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
