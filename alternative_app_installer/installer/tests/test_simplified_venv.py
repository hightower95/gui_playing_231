#!/usr/bin/env python3

"""
Test the simplified VenvStep that only stores venv_path in shared state
"""

import configparser
from install_gui.steps.venv_utils import VenvPathUtils, get_python_executable_from_shared_state
from install_gui.steps.venv_step import CreateVenvStep
import sys
from pathlib import Path

# Add installer path to sys.path
installer_path = Path(__file__).parent
sys.path.insert(0, str(installer_path))


def test_simplified_venv_step():
    """Test that VenvStep only stores venv_path and utilities can derive the rest"""
    print("=== SIMPLIFIED VENV STEP TEST ===")

    # Create test config
    config = configparser.ConfigParser()

    config.add_section('Settings')
    config.set('Settings', 'app_name', 'TestApp')

    config.add_section('Paths')
    config.set('Paths', 'default_venv', '.test_venv')

    config.add_section('DEV')
    config.set('DEV', 'simulate_venv_complete', 'true')  # Use simulation

    # Simulate previous step (folder selection)
    shared_state = {
        'valid_installation_path': 'C:\\TestInstall\\ProductivityApp'
    }

    print(f"1. Initial shared state: {shared_state}")

    # Create and complete venv step
    venv_step = CreateVenvStep(config, shared_state)

    print(f"2. Venv name from config: {venv_step._venv_name}")
    print(f"3. Calculated venv path: {venv_step._calculate_venv_path()}")
    print(f"4. Is simulation enabled: {venv_step._is_simulation_enabled()}")
    print(f"5. Can complete: {venv_step.can_complete()}")

    # Complete the step
    result = venv_step.complete_step()
    print(f"6. Step completion result: {result}")
    print(f"7. Shared state after completion: {shared_state}")

    # Show that we only store venv_path
    stored_keys = list(shared_state.keys())
    print(f"8. Keys stored in shared state: {stored_keys}")

    # Now demonstrate how to derive everything else
    print(f"\n=== DERIVING ALL INFORMATION FROM VENV_PATH ===")

    if 'venv_path' in shared_state:
        venv_path = shared_state['venv_path']
        print(f"Stored venv_path: {venv_path}")

        # Use utilities to derive everything else
        derived_info = VenvPathUtils.enrich_shared_state(shared_state)

        print(f"\nDerived information:")
        for key, value in derived_info.items():
            print(f"  {key}: {value}")

        # Test convenience functions
        print(f"\nConvenience functions:")
        print(
            f"  Python executable: {get_python_executable_from_shared_state(shared_state)}")

        # Show individual utility functions
        print(f"\nIndividual utilities:")
        print(
            f"  VenvPathUtils.get_venv_name(venv_path): {VenvPathUtils.get_venv_name(venv_path)}")
        print(
            f"  VenvPathUtils.get_installation_directory(venv_path): {VenvPathUtils.get_installation_directory(venv_path)}")
        print(
            f"  VenvPathUtils.get_venv_python_path(venv_path): {VenvPathUtils.get_venv_python_path(venv_path)}")
        print(
            f"  VenvPathUtils.is_venv_created(venv_path): {VenvPathUtils.is_venv_created(venv_path)}")


def test_shared_state_minimalism():
    """Test that we're truly minimalist with shared state"""
    print(f"\n=== SHARED STATE MINIMALISM TEST ===")

    # What we used to store (BAD)
    old_approach = {
        'valid_installation_path': 'C:\\TestInstall\\ProductivityApp',
        'venv_created': True,
        'venv_path': 'C:\\TestInstall\\ProductivityApp\\.test_venv',
        'venv_name': '.test_venv',
        'venv_python_path': 'C:\\TestInstall\\ProductivityApp\\.test_venv\\Scripts\\python.exe',
        'installation_directory': 'C:\\TestInstall\\ProductivityApp'
    }

    # What we now store (GOOD)
    new_approach = {
        'valid_installation_path': 'C:\\TestInstall\\ProductivityApp',
        'venv_path': 'C:\\TestInstall\\ProductivityApp\\.test_venv'
    }

    print(f"Old approach - stored {len(old_approach)} keys:")
    for key in old_approach.keys():
        print(f"  ❌ {key}")

    print(f"\nNew approach - store {len(new_approach)} keys:")
    for key in new_approach.keys():
        print(f"  ✅ {key}")

    print(
        f"\nSpace savings: {len(old_approach) - len(new_approach)} fewer keys")
    print(f"Maintainability: Derive values dynamically, no sync issues")


if __name__ == "__main__":
    test_simplified_venv_step()
    test_shared_state_minimalism()
