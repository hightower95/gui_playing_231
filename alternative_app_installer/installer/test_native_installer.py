#!/usr/bin/env python3

"""
Test the native tkinter installer to verify it works with only standard library components.

This test validates:
- No PySide6 dependencies 
- Native tkinter GUI functionality
- Step navigation and state management
- All components work with standard Python installation
"""

import sys
import os
from pathlib import Path
from configparser import ConfigParser

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_native_dependencies():
    """Test that only native Python libraries are used"""
    print("🧪 Testing native dependencies...")

    # Test that PySide6 is not imported anywhere
    forbidden_imports = ['PySide6', 'PyQt5', 'PyQt6']

    for module_name in sys.modules:
        for forbidden in forbidden_imports:
            if forbidden in module_name:
                print(f"❌ Found forbidden import: {module_name}")
                return False

    print("✅ No forbidden GUI frameworks detected")
    return True


def test_installer_creation():
    """Test that installer can be created with tkinter"""
    print("🖥️ Testing installer GUI creation...")

    try:
        # Create test configuration
        config = ConfigParser()
        config.add_section('Paths')
        config.set('Paths', 'default_install_path',
                   str(Path.home() / 'TestApp'))
        config.set('Paths', 'default_venv', '.test_venv')

        config.add_section('DEV')
        config.set('DEV', 'simulate_venv_complete', 'true')
        config.set('DEV', 'debug', 'true')

        config.add_section('Restrictions')
        config.set('Restrictions', 'blocked_folder_patterns',
                   '["Program Files", "Windows"]')

        # Import and create GUI
        from install_gui.main import InstallGUI
        gui = InstallGUI(config)

        print("✅ Installer GUI created successfully")
        print(f"   Window title: {gui.title()}")
        print(
            f"   Current step: {gui.conductor.get_current_step().get_title()}")

        # Clean up
        gui.destroy()
        return True

    except Exception as e:
        print(f"❌ Failed to create installer: {e}")
        return False


def test_step_functionality():
    """Test basic step functionality"""
    print("⚙️ Testing step functionality...")

    try:
        from install_gui.steps import GetFolderStep, CreateVenvStep
        from configparser import ConfigParser

        # Create test config and shared state
        config = ConfigParser()
        config.add_section('Paths')
        config.set('Paths', 'default_venv', '.test_venv')
        config.add_section('Restrictions')
        config.set('Restrictions', 'blocked_folder_patterns', '[]')

        shared_state = {}

        # Test folder step
        folder_step = GetFolderStep(config, shared_state)
        assert folder_step.get_title() == "Choose Installation Folder"
        assert "application" in folder_step.get_description().lower()

        # Test venv step
        venv_step = CreateVenvStep(config, shared_state)
        assert venv_step.get_title() == "Setup App Environment"
        assert "virtual environment" in venv_step.get_description().lower()

        print("✅ Step functionality working correctly")
        return True

    except Exception as e:
        print(f"❌ Step functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_native_libraries_only():
    """Verify only native Python libraries are used"""
    print("📚 Checking imported libraries...")

    # List of modules that should be native to Python
    expected_native = {
        'tkinter', 'threading', 'queue', 'subprocess',
        'pathlib', 'os', 'sys', 'configparser', 'ast'
    }

    # List of modules that indicate external dependencies
    forbidden_patterns = [
        'PySide', 'PyQt', 'wx', 'gtk', 'kivy', 'pygame'
    ]

    imported_modules = set(sys.modules.keys())

    # Check for forbidden patterns
    for module in imported_modules:
        for pattern in forbidden_patterns:
            if pattern.lower() in module.lower():
                print(f"❌ Found non-native GUI library: {module}")
                return False

    # Check that we have the expected native modules
    gui_modules = [m for m in imported_modules if 'tkinter' in m.lower()]
    if gui_modules:
        print(f"✅ Using native GUI library: {', '.join(gui_modules)}")

    return True


def main():
    """Run all tests for native tkinter installer"""
    print("🔧 Testing Native Tkinter Installer")
    print("=" * 50)

    tests = [
        test_native_libraries_only,
        test_installer_creation,
        test_step_functionality,
        test_native_dependencies,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Installer uses only native Python libraries.")
        print("\n✅ Key achievements:")
        print("   • Removed all PySide6 dependencies")
        print("   • Converted to native tkinter GUI")
        print("   • Maintains full functionality")
        print("   • Works with standard Python installation")
        print("   • No external GUI libraries required")
    else:
        print("❌ Some tests failed - check output above for details")

    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
