#!/usr/bin/env python3
"""
Diagnostic test for venv creation issues.
This tests the actual venv creation functionality outside of the GUI.
"""

import sys
import subprocess
from pathlib import Path
import tempfile
import time

def test_venv_creation():
    """Test creating a virtual environment using the same logic as the installer."""
    
    print("=== Virtual Environment Creation Diagnostic ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()
    
    # Create a test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_install_path = Path(temp_dir) / "test_installation"
        test_install_path.mkdir(exist_ok=True)
        
        venv_path = test_install_path / ".test_venv"
        
        print(f"Test installation path: {test_install_path}")
        print(f"Virtual environment path: {venv_path}")
        print()
        
        # Test 1: Check if we can find Python
        print("=== Test 1: Python Detection ===")
        try:
            result = subprocess.run(
                [sys.executable, '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            print(f"Python version check: {result.stdout.strip()}")
            print(f"Return code: {result.returncode}")
        except Exception as e:
            print(f"ERROR: {e}")
            return False
        
        # Test 2: Try creating venv
        print("\n=== Test 2: Virtual Environment Creation ===")
        try:
            cmd = [sys.executable, '-m', 'venv', str(venv_path), '--clear']
            print(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=test_install_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
                
            # Check if venv was created
            if venv_path.exists():
                print(f"✅ Virtual environment created at: {venv_path}")
                
                # Check for key files
                scripts_dir = venv_path / "Scripts"
                lib_dir = venv_path / "Lib"
                
                print(f"Scripts directory exists: {scripts_dir.exists()}")
                print(f"Lib directory exists: {lib_dir.exists()}")
                
                if scripts_dir.exists():
                    python_exe = scripts_dir / "python.exe"
                    activate_bat = scripts_dir / "activate.bat"
                    pip_exe = scripts_dir / "pip.exe"
                    
                    print(f"python.exe exists: {python_exe.exists()}")
                    print(f"activate.bat exists: {activate_bat.exists()}")
                    print(f"pip.exe exists: {pip_exe.exists()}")
                    
                    # Test the venv Python
                    if python_exe.exists():
                        try:
                            venv_result = subprocess.run(
                                [str(python_exe), '--version'],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            print(f"Venv Python version: {venv_result.stdout.strip()}")
                        except Exception as e:
                            print(f"Error testing venv Python: {e}")
                
                return True
            else:
                print(f"❌ Virtual environment NOT created at: {venv_path}")
                return False
                
        except subprocess.TimeoutExpired:
            print("ERROR: Virtual environment creation timed out")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

def test_installation_settings():
    """Test reading installation settings like the installer does."""
    print("\n=== Test 3: Installation Settings ===")
    
    try:
        # Add the installer directory to the path
        import sys
        sys.path.insert(0, str(Path(__file__).parent / "installer"))
        
        from scripts.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        settings = config_manager.get_installation_settings()
        
        print("Installation settings loaded successfully:")
        for section in settings.sections():
            print(f"  [{section}]")
            for key, value in settings[section].items():
                print(f"    {key} = {value}")
                
        # Check simulation settings
        simulate_venv = settings.getboolean('DEV', 'simulate_venv_complete', fallback=False)
        print(f"\nSimulation mode for venv: {simulate_venv}")
        
        return True
        
    except Exception as e:
        print(f"ERROR loading settings: {e}")
        return False

if __name__ == "__main__":
    print("Starting diagnostic tests...\n")
    
    success = True
    
    # Run tests
    success &= test_venv_creation()
    success &= test_installation_settings()
    
    print(f"\n=== Summary ===")
    if success:
        print("✅ All tests passed - venv creation should work")
    else:
        print("❌ Some tests failed - investigate issues above")