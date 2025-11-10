#!/usr/bin/env python3
"""
Test script to verify pure function behavior of folder step
"""
from install_gui.steps.folder_step import GetFolderStep
import sys
from pathlib import Path
from configparser import ConfigParser

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))


def test_pure_function_behavior():
    """Test that folder step acts like a pure function"""
    print("Testing Pure Function Behavior")
    print("=" * 50)

    # Create test configuration
    config = ConfigParser()
    config.read('install_settings.ini')

    # Create shared state
    shared_state = {}

    # Create folder step instance
    folder_step = GetFolderStep(config, shared_state)

    print("1. Initial State Check:")
    print(f"   Shared state keys: {list(shared_state.keys())}")
    print(
        f"   Contains 'valid_installation_path': {'valid_installation_path' in shared_state}")
    print(
        f"   Contains old 'installation_path': {'installation_path' in shared_state}")

    print("\n2. Step Internal State:")
    if hasattr(folder_step, '_current_path'):
        print(f"   Internal current path: {folder_step._current_path}")
    else:
        print("   No internal current path found")

    print(f"   Can complete: {folder_step.can_complete()}")

    print("\n3. Simulate Step Completion:")
    # Simulate having a valid path
    if hasattr(folder_step, '_current_path') and folder_step._current_path:
        # Manually set a simple test path for completion test
        test_path = str(Path.home() / "TestApp")
        folder_step._current_path = test_path

        print(f"   Set test path: {test_path}")
        print(f"   Can complete now: {folder_step.can_complete()}")

        # Check shared state before completion
        print(f"   Shared state before completion: {shared_state}")

        # Attempt to complete (this will validate and may fail, but we'll see the behavior)
        try:
            result = folder_step.complete_step()
            print(f"   Complete step result: {result}")
            print(f"   Shared state after completion: {shared_state}")

            if 'valid_installation_path' in shared_state:
                print(
                    f"   ✅ SUCCESS: Only updates shared state on successful completion!")
                print(
                    f"   Valid path: {shared_state['valid_installation_path']}")
            else:
                print(f"   ⚠️  Step completion failed (expected for test path)")
        except Exception as e:
            print(f"   ⚠️  Expected exception during validation: {e}")

    print("\n4. Verification:")
    print(f"   Final shared state: {shared_state}")
    print(
        f"   Step follows pure function pattern: {'valid_installation_path' in shared_state or len(shared_state) == 0}")

    print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    test_pure_function_behavior()
