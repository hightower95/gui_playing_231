#!/usr/bin/env python3
"""
Quick validation script for the new file operations system
Tests that our FileOperationsManager works correctly
"""

import sys
import tempfile
from pathlib import Path

# Add the installer scripts to path
sys.path.insert(0, str(Path(__file__).parent / "productivity_app_installer" / "installer" / "scripts"))

from file_operations import FileOperationsManager


def test_file_operations():
    """Test the FileOperationsManager functionality"""
    
    # Get installer root directory
    installer_root = Path(__file__).parent / "productivity_app_installer"
    
    if not installer_root.exists():
        print(f"❌ Installer root not found: {installer_root}")
        return False
        
    print(f"✅ Found installer root: {installer_root}")
    
    # Check required directories exist
    utils_dir = installer_root / "utils"
    templates_dir = installer_root / "templates"
    
    if not utils_dir.exists():
        print(f"❌ Utils directory not found: {utils_dir}")
        return False
    print(f"✅ Found utils directory: {utils_dir}")
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return False
    print(f"✅ Found templates directory: {templates_dir}")
    
    # Initialize file operations manager
    try:
        file_ops = FileOperationsManager(installer_root)
        print("✅ FileOperationsManager initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize FileOperationsManager: {e}")
        return False
    
    # Create a temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"✅ Created temporary test directory: {temp_path}")
        
        # Test configuration
        test_config = {
            'app_name': 'TestApp',
            'python_path': sys.executable,
            'install_folder': str(temp_path)
        }
        
        # Test file setup
        try:
            success = file_ops.setup_files_in_target_folder(temp_path, test_config)
            if success:
                print("✅ File setup completed successfully")
            else:
                print("❌ File setup failed")
                return False
        except Exception as e:
            print(f"❌ File setup raised exception: {e}")
            return False
        
        # Validate created files
        expected_files = [
            temp_path / "run_app.pyw",
            temp_path / "launch_config.ini",
            temp_path / "utils"
        ]
        
        for expected_file in expected_files:
            if expected_file.exists():
                print(f"✅ Created: {expected_file.name}")
            else:
                print(f"❌ Missing: {expected_file.name}")
                return False
        
        # Check if utils directory has expected files
        utils_files = list((temp_path / "utils").glob("*.py"))
        if utils_files:
            print(f"✅ Utils contains {len(utils_files)} Python files")
        else:
            print("❌ Utils directory is empty")
            return False
        
        # Check launch_config.ini content
        config_file = temp_path / "launch_config.ini"
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                if 'TestApp' in content:
                    print("✅ launch_config.ini contains app name")
                else:
                    print("❌ launch_config.ini missing app name")
                    return False
        except Exception as e:
            print(f"❌ Failed to read launch_config.ini: {e}")
            return False
    
    print("\n🎉 All tests passed! File operations system is working correctly.")
    return True


if __name__ == "__main__":
    print("🔧 Validating File Operations System...")
    print("=" * 50)
    
    if test_file_operations():
        print("\n✅ SUCCESS: File operations system is ready for use!")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: File operations system needs fixes!")
        sys.exit(1)