#!/usr/bin/env python3
"""
Test the pip functionality verification with a corrupted venv scenario.
"""

import sys
import threading
import queue
import time
import shutil
from pathlib import Path
import tempfile

# Add the installer path
sys.path.insert(0, str(Path(__file__).parent / "alternative_app_installer" / "installer"))

from install_gui.steps.venv_step import VenvCreationWorker

def test_corrupted_venv():
    """Test pip functionality verification with a corrupted venv"""
    print("=== Testing Corrupted Venv Detection ===")
    
    # Create queues
    progress_queue = queue.Queue()
    result_queue = queue.Queue()
    
    # Create a test directory with fake venv structure
    with tempfile.TemporaryDirectory() as temp_dir:
        test_install_path = Path(temp_dir) / "test_installation"
        test_install_path.mkdir(exist_ok=True)
        venv_path = test_install_path / ".test_venv"
        
        # Create a minimal venv structure (valid folders but missing/broken pip)
        venv_path.mkdir()
        scripts_dir = venv_path / "Scripts"
        scripts_dir.mkdir()
        lib_dir = venv_path / "Lib"
        lib_dir.mkdir()
        
        # Create a fake python.exe but NO pip.exe (simulating corruption)
        python_exe = scripts_dir / "python.exe"
        python_exe.write_text("fake python")  # This won't work but exists
        
        print(f"Test venv path: {venv_path}")
        print(f"Created fake structure without pip.exe")
        
        # Test the pip functionality check directly
        worker = VenvCreationWorker(
            python_executable=sys.executable,
            venv_path=str(venv_path),
            installation_path=str(test_install_path),
            progress_queue=progress_queue,
            result_queue=result_queue
        )
        
        # Test the pip functionality method directly
        print("\n=== Testing _test_pip_functionality with corrupted venv ===")
        worker._test_pip_functionality(venv_path)
        
        # Check what messages were generated
        print("\n=== Messages from corrupted venv test ===")
        while True:
            try:
                message = progress_queue.get_nowait()
                print(f"PROGRESS: {message}")
            except queue.Empty:
                break
        
        print("\n✅ Corrupted venv detection test completed")

def test_completely_missing_venv():
    """Test with a completely missing venv directory"""
    print("\n=== Testing Missing Venv Detection ===")
    
    # Create queues
    progress_queue = queue.Queue()
    result_queue = queue.Queue()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_install_path = Path(temp_dir) / "test_installation"
        test_install_path.mkdir(exist_ok=True)
        venv_path = test_install_path / ".test_venv"
        
        # Don't create the venv directory at all
        print(f"Testing with non-existent venv: {venv_path}")
        
        worker = VenvCreationWorker(
            python_executable=sys.executable,
            venv_path=str(venv_path),
            installation_path=str(test_install_path),
            progress_queue=progress_queue,
            result_queue=result_queue
        )
        
        # Test the pip functionality method directly
        worker._test_pip_functionality(venv_path)
        
        # Check what messages were generated
        print("\n=== Messages from missing venv test ===")
        while True:
            try:
                message = progress_queue.get_nowait()
                print(f"PROGRESS: {message}")
            except queue.Empty:
                break
        
        print("\n✅ Missing venv detection test completed")

if __name__ == "__main__":
    print("Starting pip functionality verification tests...\n")
    
    test_corrupted_venv()
    test_completely_missing_venv()
    
    print(f"\n=== Summary ===")
    print("✅ All pip functionality tests completed")
    print("The new pip verification should now properly detect:")
    print("  - Missing pip executables")
    print("  - Non-functional pip installations") 
    print("  - Corrupted virtual environments")
    print("  - Empty or incomplete package installations")